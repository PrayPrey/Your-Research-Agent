# Phase 3: Logic Design for H-M1

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: API signatures verified from actual h-e1 code (not brief/spec — spec was outdated)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**: `mode_classify.assign_modes`, `data.load_battles`, `data.filter_valid`, `data.prepare_battles`, `run.main`

**Critical finding**: The experiment brief assumes `rm_scores.parquet` / `mode_distribution.json` contain `response_a`, `response_b`, `mode_label`. **They do not.** Actual h-e1 outputs:

| File | Actual columns |
|------|----------------|
| `results.csv` | `battle_id, human_entropy, rm_variance, mode` (int 1-4) |
| `rm_scores.parquet` | `battle_id, {model}_score_a, {model}_score_b` (no text) |
| `mode_distribution.json` | `{"1": {"count", "proportion"}, ...}` (no per-battle data) |

Response text (`resp_a`, `resp_b`, `prompt`) is never persisted by h-e1 — it only exists in the in-memory `df` during `run.py main()`. `battle_id` is `range(len(df))` (positional index at filter/prepare time, not stable across raw dataset re-loads unless filtering is deterministic — it is, since `filter_valid`/`load_battles` have no randomness).

**Resolution**: `load_mode_data()` must re-load the raw dataset, re-run `filter_valid` + `prepare_battles` (identical to h-e1, giving identical `battle_id` positional index), then merge on `battle_id` with `results.csv` to recover `mode` + response text together.

---

## External Dependencies (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/code/data.py (ACTUAL CODE)
def load_battles(dataset_id: str) -> pd.DataFrame: ...       # raw HF dataset -> df
def filter_valid(df: pd.DataFrame) -> pd.DataFrame: ...      # drops empty prompt/response rows
def prepare_battles(df: pd.DataFrame) -> pd.DataFrame: ...   # adds resp_a, resp_b cols

# From: docs/youra_research/h-e1/code/config.py
CONFIG = {"dataset_id": "lmsys/lmsys-arena-human-preference-55k", ...}
```

**Verified from**: `docs/youra_research/h-e1/code/{data.py,run.py,config.py}` (actual implementation).

---

## A-1: Semantic Similarity Pipeline [Complexity: LOW, Budget: full]

**Applied**: sentence-transformers `SentenceTransformer.encode` + `util.cos_sim` (standard pattern; KB search returned no closer match, used library docs convention).

### API Signatures

```python
# config.py
CONFIG = {
    "h_e1_dir": "../h-e1/code/outputs",          # results.csv location
    "h_e1_dataset_id": "lmsys/lmsys-arena-human-preference-55k",  # must match h-e1 config.py
    "embed_model": "sentence-transformers/all-MiniLM-L6-v2",
    "batch_size": 128,
    "min_n_per_mode": 500,
    "n_bootstrap": 10000,
    "seed": 42,
    "output_dir": "outputs/",
}

# data.py
def load_mode_data(h_e1_output_dir: str, dataset_id: str) -> pd.DataFrame:
    """Re-derive battle_id -> (resp_a, resp_b) from raw dataset, join with h-e1 results.csv mode labels.
    Returns df with columns: battle_id, mode (int), resp_a (str), resp_b (str). Filtered to mode in {1,3}.
    Raises FileNotFoundError if results.csv missing; ValueError if n < min_n_per_mode for either mode.
    """
    ...

# embeddings.py
def compute_embeddings(texts: list[str], model: "SentenceTransformer", batch_size: int = 128) -> np.ndarray:
    """Encode texts to embeddings. texts: list[str] len N -> returns [N, 384] float32 array."""
    ...

def compute_pairwise_similarity(emb_a: np.ndarray, emb_b: np.ndarray) -> np.ndarray:
    """Row-wise cosine similarity. emb_a, emb_b: [N, 384] -> returns [N] float32, range [-1, 1]."""
    ...

# stats.py
def cohen_d(x: np.ndarray, y: np.ndarray) -> float:
    """Pooled-SD Cohen's d. x, y: 1D arrays of similarity scores."""
    ...

def bootstrap_ci_d(x: np.ndarray, y: np.ndarray, n_boot: int = 10000, seed: int = 42) -> tuple[float, float]:
    """95% CI for Cohen's d via percentile bootstrap. Returns (lo, hi)."""
    ...

def run_statistical_analysis(sim_mode1: np.ndarray, sim_mode3: np.ndarray) -> dict:
    """Welch's t-test + Cohen's d + bootstrap CI. Returns dict matching statistical_results.json schema."""
    ...

# run.py
def main() -> dict:
    """Orchestrate: load -> embed -> similarity -> stats -> save outputs. Returns stats_result dict."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| `emb_a`, `emb_b` | `[N, 384]` | MiniLM-L6-v2 output dim |
| `similarity` | `[N]` | cosine sim per battle |
| `sim_mode1` | `[n1]` | n1 >= 500 |
| `sim_mode3` | `[n3]` | n3 >= 500 |

### Pseudo-code: load_mode_data (non-trivial join)

```
1. results = pd.read_csv(h_e1_output_dir/results.csv)  # battle_id, human_entropy, rm_variance, mode
   if missing -> FileNotFoundError("run h-e1 first")

2. df = load_battles(dataset_id)      # same call as h-e1
   df = filter_valid(df)              # same filtering -> deterministic battle_id alignment
   df = prepare_battles(df)           # adds resp_a, resp_b
   df["battle_id"] = range(len(df))   # matches h-e1 assignment exactly

3. merged = df[["battle_id","resp_a","resp_b"]].merge(results[["battle_id","mode"]], on="battle_id", how="inner")
   assert len(merged) == len(results), "battle_id misalignment vs h-e1 - dataset or filtering changed"

4. merged = merged[merged["mode"].isin([1, 3])]
   for m in (1, 3):
       n = (merged["mode"] == m).sum()
       if n < min_n_per_mode: raise ValueError(f"mode {m} n={n} < {min_n_per_mode}")

5. return merged
```

### Pseudo-code: run_statistical_analysis

```
1. t_stat, p_value = scipy.stats.ttest_ind(sim_mode1, sim_mode3, equal_var=False)  # Welch's
2. d = cohen_d(sim_mode1, sim_mode3)
3. ci_lo, ci_hi = bootstrap_ci_d(sim_mode1, sim_mode3, n_boot, seed)
4. result = "CONFIRMED" if (d > 0.3 and p_value < 0.05) else "FALSIFIED" if (d < 0.1 or d < 0) else "INCONCLUSIVE"
5. effect = "large" if d>0.8 else "medium" if d>0.5 else "small" if d>0.2 else "negligible"
6. return {hypothesis_id, mode_1_n, mode_3_n, mode_1_mean_similarity, mode_3_mean_similarity,
           mode_1_std, mode_3_std, cohens_d: d, t_statistic: t_stat, p_value,
           ci_95_d: [ci_lo, ci_hi], result, effect_interpretation: effect}
```

### Pseudo-code: main()

```
1. df = load_mode_data(CONFIG["h_e1_dir"], CONFIG["h_e1_dataset_id"])
2. model = SentenceTransformer(CONFIG["embed_model"])
3. emb_a = compute_embeddings(df["resp_a"].tolist(), model, CONFIG["batch_size"])
4. emb_b = compute_embeddings(df["resp_b"].tolist(), model, CONFIG["batch_size"])
5. np.savez(output_dir/embeddings.npz, emb_a=emb_a, emb_b=emb_b, battle_id=df["battle_id"].values)
6. df["similarity"] = compute_pairwise_similarity(emb_a, emb_b)
7. df[["battle_id","mode","similarity"]].to_parquet(output_dir/similarity_scores.parquet)
8. sim1 = df.loc[df["mode"]==1, "similarity"].values
   sim3 = df.loc[df["mode"]==3, "similarity"].values
9. stats_result = run_statistical_analysis(sim1, sim3)
10. json.dump(stats_result, open(output_dir/statistical_results.json, "w"), indent=2)
11. return stats_result
```

### Error Handling

| Failure | Handling |
|---------|----------|
| `results.csv` missing | `FileNotFoundError` with message to run h-e1 first |
| battle_id count mismatch after merge | `AssertionError` — dataset/filter drift vs h-e1 |
| n < 500 per mode | `ValueError`, abort before embedding (fail fast, saves compute) |
| Empty/NaN response text | Drop row before encoding (`df.dropna(subset=["resp_a","resp_b"])`); log count dropped |
| CUDA OOM during encode | Catch, fallback `model = SentenceTransformer(..., device="cpu")`, retry once |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | data.py | `load_mode_data` — re-derive + join battle_id, mode, resp_a/b |
| L-1-2 | embeddings.py | `compute_embeddings`, `compute_pairwise_similarity` |
| L-1-3 | stats.py | `cohen_d`, `bootstrap_ci_d`, `run_statistical_analysis` |
| L-1-4 | run.py + config.py | `main()` orchestration, CONFIG dict |
