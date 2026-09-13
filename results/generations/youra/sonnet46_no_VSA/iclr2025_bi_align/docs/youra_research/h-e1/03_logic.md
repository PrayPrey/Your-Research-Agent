# Logic: H-E1 — Fuzzy Join Data Infrastructure Audit

Applied: Standard Python data pipeline patterns (Archon KB: no relevant domain content)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data Acquisition [Complexity: 10, Budget: 2 subtasks]

### API Signatures

```python
def load_llm_leaderboard(
    url: str = "https://github.com/fboulnois/llm-leaderboard-csv/releases/download/v1.3.0/llm.csv",
    cache_path: str = "./data/llm_leaderboard_v1/llm.csv",
) -> pd.DataFrame:
    """Load open-weight LLM leaderboard. Returns: model_name, TruthfulQA_MC2, MMLU columns."""
    ...

def load_bbq_scores(
    cache_path: str = "./data/bbq_scores/bbq_per_model.csv",
) -> pd.DataFrame:
    """Load BBQ accuracy from HELM Lite or cache. Returns: model_name, bbq_accuracy columns."""
    ...
```

### Tensor Shapes (column schemas)

| DataFrame | Columns | Note |
|-----------|---------|------|
| df_llm | model_name (str), TruthfulQA_MC2 (float), MMLU (float) | open-weight rows only |
| df_bbq | model_name (str), bbq_accuracy (float) | per-model mean across BBQ subtasks |

### Pseudo-code: load_llm_leaderboard()

```
1. if cache_path exists: return pd.read_csv(cache_path)
2. resp = requests.head(url, timeout=10)
3. if resp.status_code != 200: raise RuntimeError(f"LLM LB URL check failed: {resp.status_code} {url}")
4. df = pd.read_csv(url)
5. PROPRIETARY = ["gpt", "claude", "gemini", "palm", "bard"]
6. mask = ~df["model_name"].str.lower().str.contains("|".join(PROPRIETARY))
7. if "proprietary" in df.columns: mask &= ~df["proprietary"].astype(bool)
8. df = df[mask][["model_name", "TruthfulQA_MC2", "MMLU"]].dropna()
9. os.makedirs(os.path.dirname(cache_path), exist_ok=True)
10. df.to_csv(cache_path, index=False)
11. return df
```

### Pseudo-code: load_bbq_scores()

```
1. if cache_path exists: return pd.read_csv(cache_path)
2. try:
   a. ds = datasets.load_dataset("stanford-crfm/helm-lite", split="test")
   b. df = ds.to_pandas()
   c. # Find BBQ rows: filter where metric/scenario column indicates BBQ
   d. bbq_df = df[df["scenario"].str.contains("bbq", case=False)]
   e. df_out = bbq_df.groupby("model_name")["mean_accuracy"].mean().reset_index()
   f. df_out = df_out.rename(columns={"mean_accuracy": "bbq_accuracy"})
3. except Exception:
   a. if cache_path exists: return pd.read_csv(cache_path)
   b. raise RuntimeError("HELM Lite unavailable and no cache found at " + cache_path)
4. os.makedirs(os.path.dirname(cache_path), exist_ok=True)
5. df_out.to_csv(cache_path, index=False)
6. return df_out
```

### Edge Cases
- HELM Lite schema may vary; assert "model_name" and score column exist before groupby
- Column names in HELM Lite: inspect `ds.features` if groupby fails, try "accuracy" fallback
- Cache must be saved even on first successful HF load (enables offline reruns)

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2 | load_bbq_scores HELM Lite | HF dataset load, BBQ row filter, column normalization, cache write |
| L-1a | load_llm_leaderboard | HEAD preflight, CSV download, proprietary filter, cache write |

---

## A-2: Exact + Fuzzy Join [Complexity: 12, Budget: 1 subtask]

### API Signatures

```python
def exact_join(df_llm: pd.DataFrame, df_bbq: pd.DataFrame) -> pd.DataFrame:
    """Inner join on model_name. Returns df with all score columns."""
    ...

def fuzzy_join(
    df_llm: pd.DataFrame,
    df_bbq: pd.DataFrame,
    threshold: int = 75,
) -> tuple[pd.DataFrame, float, pd.DataFrame]:
    """
    WRatio fuzzy join with token_set_ratio fallback.
    Returns: (df_complete, match_rate, df_matches_with_scores)
    df_complete columns: model_name, TruthfulQA_MC2, MMLU, bbq_accuracy
    df_matches_with_scores columns: bbq_name, llm_name, score
    """
    ...

def sensitivity_sweep(
    df_llm: pd.DataFrame,
    df_bbq: pd.DataFrame,
    thresholds: list[int] = [65, 70, 75, 80],
) -> pd.DataFrame:
    """Run fuzzy_join at each threshold. Returns: threshold, N_complete, match_rate."""
    ...
```

### Pseudo-code: fuzzy_join()

```
1. llm_names = df_llm["model_name"].tolist()
2. bbq_names = df_bbq["model_name"].tolist()

3. def _run_match(names_bbq, names_llm, scorer, cutoff):
      matches = []
      for bbq_name in names_bbq:
          result = process.extractOne(
              bbq_name, names_llm,
              scorer=scorer,
              processor=utils.default_process,
              score_cutoff=cutoff,
          )
          if result is not None:
              matches.append({"bbq_name": bbq_name, "llm_name": result[0], "score": result[1]})
      return matches

4. matches = _run_match(bbq_names, llm_names, fuzz.WRatio, threshold)
5. match_rate = len(matches) / len(bbq_names)

6. if match_rate < 0.55:
      for fallback_threshold in [70, 65]:
          fallback = _run_match(bbq_names, llm_names, fuzz.token_set_ratio, fallback_threshold)
          if len(fallback) / len(bbq_names) >= match_rate:
              matches = fallback
              match_rate = len(matches) / len(bbq_names)
              break

7. df_matches = pd.DataFrame(matches)  # [bbq_name, llm_name, score]

8. # Build complete df by merging on mapped names
   df_bbq_mapped = df_bbq.rename(columns={"model_name": "bbq_name"})
   df_llm_mapped = df_llm.rename(columns={"model_name": "llm_name"})
   df_merged = (
       df_matches
       .merge(df_bbq_mapped, on="bbq_name", how="left")
       .merge(df_llm_mapped, on="llm_name", how="left")
   )
   df_complete = df_merged.dropna(subset=["TruthfulQA_MC2", "bbq_accuracy", "MMLU"])

9. return (df_complete, match_rate, df_matches)
```

### Edge Cases
- Empty bbq_names: return (empty DataFrame, 0.0, empty DataFrame)
- Duplicate bbq_name matches: df_matches may map one bbq_name to multiple llm_names — keep highest score via df_matches.sort_values("score").drop_duplicates("bbq_name", keep="last")
- score_cutoff=0 in extractOne means "return best even if 0"; threshold acts as real cutoff only when passed as score_cutoff

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1 | fuzzy_join full implementation | WRatio match loop, fallback logic, merge + dropna, return triple |

---

## A-3: Gate Verification + Sensitivity [Complexity: 8]

### API Signatures

```python
def verify_mechanism_activated(
    df_complete: pd.DataFrame,
    N_complete: int,
    match_rate: float,
    N_exact: int,
) -> tuple[bool, dict]:
    """
    Check all gate conditions. Returns (all_pass, indicators).
    indicators keys: url_check_passed, join_produced_rows, fuzzy_beats_exact,
                     gate_passed, match_rate_acceptable
    """
    ...
```

### Pseudo-code: verify_mechanism_activated()

```
1. indicators = {
       "url_check_passed": True,          # set to True if load_llm_leaderboard didn't raise
       "join_produced_rows": N_complete > 0,
       "fuzzy_beats_exact": N_complete > N_exact,
       "gate_passed": N_complete >= 30,
       "match_rate_acceptable": match_rate >= 0.55,
   }
2. all_pass = all(indicators.values())
3. return (all_pass, indicators)
```

### Pseudo-code: sensitivity_sweep()

```
1. rows = []
2. for t in thresholds:
       df_c, mr, _ = fuzzy_join(df_llm, df_bbq, threshold=t)
       rows.append({"threshold": t, "N_complete": len(df_c), "match_rate": mr})
3. return pd.DataFrame(rows)
```

---

## A-4: Visualization [Complexity: 9, Budget: 1 subtask]

### API Signatures

```python
def plot_gate_metrics(
    N_complete: int,
    match_rate: float,
    out_dir: str = "./docs/youra_research/h-e1/figures/",
) -> None:
    """Figure 1: two-bar chart showing N_complete vs threshold=30, match_rate vs 0.55."""
    ...

def plot_score_histogram(
    df_matches: pd.DataFrame,   # columns: bbq_name, llm_name, score
    out_dir: str = "./docs/youra_research/h-e1/figures/",
) -> None:
    """Figure 2: histogram of WRatio match scores."""
    ...

def plot_venn(
    n_llm: int,
    n_bbq: int,
    n_matched: int,
    out_dir: str = "./docs/youra_research/h-e1/figures/",
) -> None:
    """Figure 3: two-circle Venn — LLM LB models vs BBQ models, overlap = matched."""
    ...

def plot_sensitivity(
    sweep_df: pd.DataFrame,   # columns: threshold, N_complete, match_rate
    out_dir: str = "./docs/youra_research/h-e1/figures/",
) -> None:
    """Figure 4: dual-axis line plot — N_complete and match_rate vs threshold."""
    ...
```

### Figure Specs

| Figure | File | Size | Key elements |
|--------|------|------|--------------|
| gate_metrics.png | figures/ | 6x4 | 2 grouped bars; red dashed lines at y=30 and y=0.55 |
| score_histogram.png | figures/ | 6x4 | bins=10, range=[50,100]; x-label "WRatio Score" |
| venn_diagram.png | figures/ | 5x5 | matplotlib_venn.venn2; subsets=(n_llm-n_matched, n_bbq-n_matched, n_matched) |
| sensitivity.png | figures/ | 7x4 | left y: N_complete (blue), right y: match_rate (orange), x: threshold |

### Pseudo-code: plot_gate_metrics()

```
1. fig, ax = plt.subplots(figsize=(6, 4))
2. bars = ax.bar(["N_complete", "match_rate"], [N_complete, match_rate * 100])
3. ax.axhline(30, color="red", linestyle="--", label="N>=30 threshold")
4. ax.axhline(0.55 * 100, color="orange", linestyle="--", label="rate>=0.55 threshold")
   # Note: scale match_rate to 0-100 axis same as N_complete — use twin axis if scales differ
5. # Alternative: two separate subplots side by side for cleaner y-axes
6. os.makedirs(out_dir, exist_ok=True)
7. fig.savefig(os.path.join(out_dir, "gate_metrics.png"), dpi=120, bbox_inches="tight")
8. plt.close(fig)
```

### Pseudo-code: plot_sensitivity()

```
1. fig, ax1 = plt.subplots(figsize=(7, 4))
2. ax1.plot(sweep_df["threshold"], sweep_df["N_complete"], "b-o", label="N_complete")
3. ax1.set_ylabel("N_complete", color="blue")
4. ax1.axhline(30, color="blue", linestyle="--", alpha=0.4)
5. ax2 = ax1.twinx()
6. ax2.plot(sweep_df["threshold"], sweep_df["match_rate"], "o-", color="orange", label="match_rate")
7. ax2.set_ylabel("match_rate", color="orange")
8. ax2.axhline(0.55, color="orange", linestyle="--", alpha=0.4)
9. fig.savefig(os.path.join(out_dir, "sensitivity.png"), dpi=120, bbox_inches="tight")
10. plt.close(fig)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3 | Visualizer functions | 4 figure implementations per specs above; use plt.close() after each save |

---

## Subtask Summary

| ID | Description | Parent | Complexity |
|----|-------------|--------|------------|
| L-1 | fuzzy_join() full implementation with fallback logic | A-2 | 12 |
| L-2 | load_bbq_scores() HELM Lite loading with column normalization | A-1 | 10 |
| L-3 | Visualizer — 4 figure specs and matplotlib implementation | A-4 | 9 |

---

*Generated: 2026-07-30 | Hypothesis: H-E1 | Phase: 3 - Logic*
