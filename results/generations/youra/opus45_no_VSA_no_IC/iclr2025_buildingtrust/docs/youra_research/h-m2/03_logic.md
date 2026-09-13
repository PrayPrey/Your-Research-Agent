# Logic Spec: H-M2 (Correlation Analysis)

**Hypothesis:** HaluEval measures generation coherence/consistency, distinct from TruthfulQA's misconception resistance.
**Gate:** r(HaluEval_agg, TruthfulQA) < 0.7

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - designing new APIs (pure statistical analysis, no model/tensor code)
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## A-1: Correlation Analysis Pipeline [Complexity: 2, Budget: 5]

**Applied:** scipy.stats.spearmanr + pandas DataFrame pattern (standard, no KB match found)

### Data Structures

```python
# model_scores: pd.DataFrame, shape [N=50, K]
# columns: model_name (str), truthfulqa_mc2 (float),
#          halueval_qa (float), halueval_dialogue (float), halueval_summarization (float)
# all score columns in [0, 1]
```

### API Signatures

```python
def load_model_scores(
    leaderboard_csv: str = "h-m1/model_scores.csv",
    halueval_csv: str | None = None,
) -> pd.DataFrame:
    """Load + merge TruthfulQA (from H-M1) and HaluEval scores on model_name."""
    ...

def compute_correlations(
    df: pd.DataFrame,
    truthfulqa_col: str = "truthfulqa_mc2",
    halueval_cols: list[str] = ["halueval_qa", "halueval_dialogue", "halueval_summarization"],
) -> dict[str, tuple[float, float]]:
    """Returns {pair_name: (spearman_r, p_value)} for cross + intra correlations."""
    ...

def bootstrap_ci(
    x: np.ndarray, y: np.ndarray,
    n_bootstrap: int = 1000, ci: float = 0.95, seed: int = 42,
) -> tuple[float, float]:
    """Percentile bootstrap CI for spearman r(x,y)."""
    ...

def check_gate(results: dict[str, tuple[float, float]]) -> dict:
    """Evaluate PASS/PARTIAL/FAIL per gate conditions."""
    ...

def generate_figures(df: pd.DataFrame, results: dict, gate: dict, out_dir: str = "h-m2/figures/") -> None:
    """Saves correlation_heatmap.png, scatter_halueval_truthfulqa.png, gate_metrics.png."""
    ...
```

### Pseudo-code

```
main():
    df = load_model_scores()                      # [50, 5]
    assert df.shape[0] >= 30, "insufficient models"

    results = compute_correlations(df)
    # results keys:
    #   "halueval_vs_truthfulqa"          -> primary (aggregate mean of 3 subtasks)
    #   "{qa,dialogue,summ}_vs_truthfulqa" -> per-subtask cross
    #   "{col1}_vs_{col2}" for each intra-HaluEval pair (3 pairs)

    halueval_agg = df[halueval_cols].mean(axis=1)
    ci_lo, ci_hi = bootstrap_ci(halueval_agg.values, df[truthfulqa_col].values)
    results["halueval_vs_truthfulqa_ci"] = (ci_lo, ci_hi)

    gate = check_gate(results)
    generate_figures(df, results, gate)
    write_report(results, gate, "h-m2/04_validation.md")
```

### Correlation Computation Logic

```
compute_correlations(df, truthfulqa_col, halueval_cols):
    halueval_agg = mean(df[halueval_cols], axis=1)          # [N]

    r_cross, p_cross = spearmanr(halueval_agg, df[truthfulqa_col])
    results["halueval_vs_truthfulqa"] = (r_cross, p_cross)

    for col in halueval_cols:                                # per-subtask cross
        r, p = spearmanr(df[col], df[truthfulqa_col])
        results[f"{col}_vs_truthfulqa"] = (r, p)

    for (col1, col2) in combinations(halueval_cols, 2):       # intra (3 pairs)
        r, p = spearmanr(df[col1], df[col2])
        results[f"{col1}_vs_{col2}"] = (r, p)

    return results
```

### Gate Check Logic

```
check_gate(results):
    r_cross = results["halueval_vs_truthfulqa"][0]
    intra_rs = [v[0] for k, v in results.items() if "_vs_" in k and "truthfulqa" not in k]
    r_intra_mean = mean(intra_rs)

    primary_pass = r_cross < 0.7
    secondary_pass = r_intra_mean > r_cross

    if primary_pass and secondary_pass:  status = "PASS"
    elif primary_pass:                   status = "PARTIAL"
    else:                                 status = "FAIL"

    return {"status": status, "r_cross": r_cross, "r_intra_mean": r_intra_mean,
            "primary_pass": primary_pass, "secondary_pass": secondary_pass}
```

### Figures

| File | Type | Content |
|------|------|---------|
| correlation_heatmap.png | seaborn heatmap | pairwise r matrix: TruthfulQA x {QA, Dialogue, Summ} |
| scatter_halueval_truthfulqa.png | scatter + regline | halueval_agg vs truthfulqa_mc2, annotate r |
| gate_metrics.png | bar chart | r_cross vs 0.7 threshold line (red dashed) |

### Subtasks [4/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A1-1 | load_model_scores | Merge H-M1 CSV + HaluEval scores on model_name |
| L-A1-2 | compute_correlations + bootstrap_ci | Spearman cross/intra + 1000-sample bootstrap CI |
| L-A1-3 | check_gate | PASS/PARTIAL/FAIL logic per PRD success criteria |
| L-A1-4 | generate_figures + write_report | 3 PNGs + 04_validation.md |
