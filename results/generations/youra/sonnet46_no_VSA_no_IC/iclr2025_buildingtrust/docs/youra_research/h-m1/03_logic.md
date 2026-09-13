# Logic Design: H-M1
# Partial Spearman Correlation — BBQ Fairness Cross-Split Predictive Validity

**Hypothesis:** H-M1 (MECHANISM / FULL tier)
**Date:** 2026-08-20
**Author:** Anonymous
**Budget:** 7 subtasks

Applied: Single-responsibility function decomposition
Applied: Early-exit validation pattern (assert-based mechanism verification)
Applied: Layered data assembly (import → join → validate → serialize)

---

## Codebase Analysis (Serena)

**H-E1 Code Structure (`h-e1/code/`):**
```
paper_scores.py   — TRUSTLLM_SCORES, MMLU_SCORES dicts + load_paper_scores()
config.py         — CANONICAL_MAP, REQUIRED_COLS, N_COMMON_GATE, SOURCE_PRIORITY
ingest.py         — score ingestion utilities
matrix.py         — build_matrix() producing model × benchmark DataFrame
audit.py          — audit functions (N_common count, gate check)
visualize.py      — visualization helpers
run_experiment.py — entry point
```

**Verified H-E1 API signatures (from actual code):**
- `load_paper_scores() -> dict[str, dict[str, dict[str, float]]]`
  - Returns: `{"TrustLLM": {model: {metric: float}}, "HF": {model: {"MMLU": float}}, "GLUE-X": {...}}`
- `CANONICAL_MAP: dict[str, str]` — in `h-e1/code/config.py`
- `MMLU_SCORES: dict[str, float]` — in `h-e1/code/paper_scores.py`
- `TRUSTLLM_SCORES: dict[str, dict[str, float]]` — in `h-e1/code/paper_scores.py`
  - Keys include: "BBQ-Disambig", "BBQ-Ambig" per model

**H-M1 reuse strategy:**
- Import `load_paper_scores()` and `MMLU_SCORES` directly from `h-e1/code/paper_scores.py`
- Import `CANONICAL_MAP` from `h-e1/code/config.py`
- Do NOT reimplement name standardization or score dicts

---

## External Dependencies API

### pingouin.partial_corr
```python
pingouin.partial_corr(
    data: pd.DataFrame,       # rows=models, cols include x, y, covar
    x: str,                   # predictor column name
    y: str,                   # outcome column name
    covar: list[str],         # control variable column names
    method: str = "spearman", # rank-based
    alternative: str = "greater"  # one-tailed H1: ρ > 0
) -> pd.DataFrame
# Returns 1-row DataFrame with columns: n, r, CI95%, p-val
# p-val is one-tailed Fisher z p-value
```

### scipy.stats.spearmanr
```python
scipy.stats.spearmanr(
    a: array-like,   # first variable (bbq_disambig values)
    b: array-like    # second variable (bbq_ambig values)
) -> SpearmanrResult(statistic: float, pvalue: float)
```

---

## Module: data.py

### Subtask L-2-1: build_score_dataframe()

```python
def build_score_dataframe() -> pd.DataFrame:
    """
    Assemble H-M1 score matrix by importing H-E1 data + Winogrande scores.

    Returns:
        pd.DataFrame with columns:
            model_name    : str   — canonical model identifier
            bbq_disambig  : float — BBQ disambiguated context accuracy (%)
            bbq_ambig     : float — BBQ ambiguous context accuracy (%)
            mmlu          : float — MMLU accuracy (capability control)
            winogrande    : float — Winogrande accuracy (sensitivity control)
        Shape: (N_common, 5) where N_common ≥ 10

    Side effects:
        Saves DataFrame to DATA_DIR / "h_m1_scores.csv"
        Logs N_common and list of included models

    Raises:
        AssertionError: if N_common < N_COMMON_GATE (10)
    """
    # Step 1: Load H-E1 scores (import directly — no reimplementation)
    from docs.youra_research.h_e1.code.paper_scores import (
        load_paper_scores, TRUSTLLM_SCORES, MMLU_SCORES
    )
    from docs.youra_research.h_e1.code.config import CANONICAL_MAP

    # Step 2: Extract BBQ-Disambig and BBQ-Ambig per model from TRUSTLLM_SCORES
    records = []
    for raw_name, scores in TRUSTLLM_SCORES.items():
        canonical = CANONICAL_MAP.get(raw_name.lower(), raw_name)
        bbq_dis = scores.get("BBQ-Disambig")
        bbq_amb = scores.get("BBQ-Ambig")
        mmlu = MMLU_SCORES.get(canonical) or MMLU_SCORES.get(raw_name)
        wino = WINOGRANDE_SCORES.get(canonical) or WINOGRANDE_SCORES.get(raw_name)
        if all(v is not None for v in [bbq_dis, bbq_amb, mmlu]):
            records.append({
                "model_name": canonical,
                "bbq_disambig": bbq_dis,
                "bbq_ambig": bbq_amb,
                "mmlu": mmlu,
                "winogrande": wino,  # may be None — OK for primary analysis
            })

    df = pd.DataFrame(records).drop_duplicates("model_name").reset_index(drop=True)

    # Step 3: Filter to N_common (all 3 primary scores non-null)
    df_common = df.dropna(subset=["bbq_disambig", "bbq_ambig", "mmlu"])
    n_common = len(df_common)
    assert n_common >= N_COMMON_GATE, f"N_common={n_common} < {N_COMMON_GATE}"

    # Step 4: Log and save
    logging.info(f"N_common={n_common}, models={df_common['model_name'].tolist()}")
    df_common.to_csv(DATA_DIR / "h_m1_scores.csv", index=False)

    return df_common
```

### Subtask L-2-2: canonicalize_name()

```python
def canonicalize_name(raw: str, canonical_map: dict[str, str]) -> str:
    """
    Normalize model name to canonical form using H-E1 CANONICAL_MAP.

    Args:
        raw           : raw model name string (any case/variant)
        canonical_map : dict mapping raw → canonical (from h-e1/code/config.py)

    Returns:
        str — canonical name, or raw if not in map

    Example:
        canonicalize_name("llama-2-7b-chat", CANONICAL_MAP) -> "LLaMA-2-7B-Chat"
    """
    return canonical_map.get(raw.lower(), canonical_map.get(raw, raw))
```

---

## Module: analysis.py

### Subtask L-4-1: compute_raw_spearman()

```python
def compute_raw_spearman(df: pd.DataFrame) -> dict:
    """
    Compute raw (unadjusted) Spearman ρ between BBQ-Disambig and BBQ-Ambig.

    Args:
        df : DataFrame with columns [bbq_disambig, bbq_ambig], shape (N, ≥2)

    Returns:
        dict:
            rho   : float — Spearman correlation coefficient ∈ [-1, 1]
            p     : float — two-tailed p-value
            n     : int   — number of models

    Example return:
        {"rho": 0.71, "p": 0.003, "n": 14}
    """
    from scipy.stats import spearmanr
    result = spearmanr(df["bbq_disambig"], df["bbq_ambig"])
    return {"rho": float(result.statistic), "p": float(result.pvalue), "n": len(df)}
```

### Subtask L-4-2: compute_partial_spearman()

```python
def compute_partial_spearman(
    df: pd.DataFrame,
    covar: str = "mmlu"
) -> dict:
    """
    Compute partial Spearman ρ between BBQ-Disambig and BBQ-Ambig,
    controlling for covariate (MMLU or Winogrande).

    Args:
        df    : DataFrame with columns [bbq_disambig, bbq_ambig, {covar}]
                shape (N, ≥3), N ≥ 10
        covar : control variable column name; default "mmlu"

    Returns:
        dict:
            partial_rho : float — partial Spearman ρ ∈ [-1, 1]
            p_value     : float — one-tailed p-value (H1: ρ > 0)
            ci95        : list[float, float] — 95% confidence interval [lo, hi]
            n           : int   — number of models used

    Raises:
        AssertionError: if covar not in df.columns
        ValueError: if p_value is NaN (constant scores detected)

    Mechanism verification (inline):
        assert n >= 10
        assert -1 <= partial_rho <= 1
        assert 0 <= p_value <= 1

    Example return:
        {"partial_rho": 0.58, "p_value": 0.018, "ci95": [0.12, 0.84], "n": 14}
    """
    import pingouin as pg
    assert covar in df.columns, f"covar '{covar}' not in DataFrame columns"

    sub = df[["bbq_disambig", "bbq_ambig", covar]].dropna()
    result = pg.partial_corr(
        data=sub,
        x="bbq_disambig",
        y="bbq_ambig",
        covar=[covar],
        method="spearman",
        alternative="greater",
    ).round(6)

    partial_rho = float(result["r"].iloc[0])
    p_value = float(result["p-val"].iloc[0])
    ci95 = result["CI95%"].iloc[0].tolist()
    n = int(result["n"].iloc[0])

    if pd.isna(p_value):
        raise ValueError("p_value is NaN — check for constant score columns")

    # Mechanism verification
    assert n >= 10, f"Insufficient N: {n}"
    assert -1 <= partial_rho <= 1, f"Invalid rho: {partial_rho}"
    assert 0 <= p_value <= 1, f"Invalid p-value: {p_value}"

    logging.info(f"Partial Spearman ρ computed: ρ={partial_rho:.3f}, p={p_value:.4f}, n={n}")
    return {"partial_rho": partial_rho, "p_value": p_value, "ci95": ci95, "n": n}
```

---

## Module: analysis.py (continued)

### Subtask L-5-1: run_full_analysis()

```python
def run_full_analysis(df: pd.DataFrame) -> dict:
    """
    Orchestrate complete H-M1 statistical analysis.

    Args:
        df : DataFrame from build_score_dataframe(), shape (N_common, 5)
             columns: [model_name, bbq_disambig, bbq_ambig, mmlu, winogrande]

    Returns:
        dict:
            raw          : dict — compute_raw_spearman() result
            primary      : dict — compute_partial_spearman(df, covar="mmlu") result
            sensitivity  : dict — compute_partial_spearman(df, covar="winogrande") result
                          (None if winogrande column all-null)
            gate_pass    : bool — primary.partial_rho > 0.4 AND primary.p_value < 0.05
            mmlu_explains: bool — raw.rho > primary.partial_rho (secondary criterion)

    Side effects:
        Saves results to RESULTS_DIR / "h_m1_results.json"
    """
    raw = compute_raw_spearman(df)
    primary = compute_partial_spearman(df, covar="mmlu")

    # Sensitivity: only if Winogrande available for ≥ 10 models
    wino_sub = df.dropna(subset=["winogrande"])
    if len(wino_sub) >= 10:
        sensitivity = compute_partial_spearman(wino_sub, covar="winogrande")
    else:
        sensitivity = None
        logging.warning(f"Winogrande N={len(wino_sub)} < 10, sensitivity skipped")

    gate_pass = (primary["partial_rho"] > PARTIAL_RHO_THRESHOLD and
                 primary["p_value"] < P_VALUE_THRESHOLD)
    mmlu_explains = raw["rho"] > primary["partial_rho"]

    results = {
        "raw": raw,
        "primary": primary,
        "sensitivity": sensitivity,
        "gate_pass": gate_pass,
        "mmlu_explains_variance": mmlu_explains,
    }

    import json
    with open(RESULTS_DIR / "h_m1_results.json", "w") as f:
        json.dump(results, f, indent=2)

    return results
```

---

## Module: visualize.py

### Subtask L-6-1: plot_gate_metrics()

```python
def plot_gate_metrics(
    raw_rho: float,
    partial_rho: float,
    ci95: list[float, float],
    save_dir: Path
) -> None:
    """
    Bar chart: partial_rho vs raw_rho with 95% CI error bars and gate threshold line.

    Args:
        raw_rho     : float — raw Spearman ρ (no control)
        partial_rho : float — partial Spearman ρ (MMLU-controlled)
        ci95        : [lo, hi] — 95% CI for partial_rho
        save_dir    : Path — directory for figure output

    Output:
        saves: save_dir / "gate_metrics_comparison.png"

    Layout:
        - x-axis: ["Raw ρ (no control)", "Partial ρ (MMLU control)"]
        - y-axis: correlation coefficient [-1, 1]
        - horizontal dashed line at PARTIAL_RHO_THRESHOLD (0.4), labeled "Gate: 0.4"
        - error bar on partial_rho bar only (asymmetric: [partial_rho - ci95[0], ci95[1] - partial_rho])
        - bar color: green if partial_rho > 0.4, red otherwise
    """
    ...  # matplotlib implementation
```

### Subtask L-6-2: plot_rank_scatter()

```python
def plot_rank_scatter(
    df: pd.DataFrame,
    partial_rho: float,
    save_dir: Path
) -> None:
    """
    Scatter plot of BBQ-Disambig rank vs BBQ-Ambig rank per model.

    Args:
        df          : DataFrame with [model_name, bbq_disambig, bbq_ambig]
        partial_rho : float — annotated on plot
        save_dir    : Path

    Output:
        saves: save_dir / "rank_scatter_bbq.png"

    Layout:
        - x-axis: BBQ-Disambig rank (1=highest score)
        - y-axis: BBQ-Ambig rank
        - each point labeled with model_name (annotate)
        - least-squares line overlaid (np.polyfit on ranks)
        - title: f"BBQ Rank Correlation (partial ρ={partial_rho:.3f})"
    """
    ...  # matplotlib/seaborn implementation
```

---

## Data Flow Summary

```
load_paper_scores() [h-e1]
MMLU_SCORES [h-e1]
WINOGRANDE_SCORES [h-m1/config.py]
        ↓
build_score_dataframe()
        → df: (N_common, 5)
        → saved: data/h_m1_scores.csv
        ↓
compute_raw_spearman(df)        → raw: {rho, p, n}
compute_partial_spearman(df, "mmlu")  → primary: {partial_rho, p_value, ci95, n}
compute_partial_spearman(df, "winogrande") → sensitivity: {partial_rho, p_value, ci95, n}
        ↓
run_full_analysis(df)           → results: {raw, primary, sensitivity, gate_pass, mmlu_explains}
        → saved: results/h_m1_results.json
        ↓
plot_gate_metrics(...)          → figures/gate_metrics_comparison.png
plot_rank_scatter(...)          → figures/rank_scatter_bbq.png
plot_sensitivity_comparison(...)→ figures/sensitivity_comparison.png
plot_score_distributions(...)   → figures/score_distributions.png
plot_mmlu_vs_fairness(...)      → figures/mmlu_vs_fairness.png
```
