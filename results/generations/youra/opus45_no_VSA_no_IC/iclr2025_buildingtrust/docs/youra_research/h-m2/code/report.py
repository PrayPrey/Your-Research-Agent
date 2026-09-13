"""Report generation for H-M2."""

from datetime import datetime


def write_validation_report(
    results: dict,
    gate: dict,
    ci: tuple[float, float],
    n_models: int,
    out_path: str,
) -> None:
    """Generate 04_validation.md report."""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Extract per-subtask cross-correlations
    subtask_cross = {k: v for k, v in results.items() if "truthfulqa" in k and k != "halueval_vs_truthfulqa"}
    intra_pairs = {k: v for k, v in results.items() if "truthfulqa" not in k and "_vs_" in k}

    report = f"""# H-M2 Validation Report

**Generated:** {timestamp}
**Hypothesis:** HaluEval measures generation coherence/consistency, distinct from TruthfulQA's misconception resistance

## Gate Result: {gate['status']}

| Condition | Value | Threshold | Pass |
|-----------|-------|-----------|------|
| r(HaluEval, TruthfulQA) | {gate['r_cross']:.3f} | < 0.7 | {'PASS' if gate['primary_pass'] else 'FAIL'} |
| r_intra > r_cross | {gate['r_intra_mean']:.3f} > {gate['r_cross']:.3f} | - | {'PASS' if gate['secondary_pass'] else 'FAIL'} |

## Summary Statistics

- **N models analyzed:** {n_models}
- **Primary correlation:** r(HaluEval_agg, TruthfulQA) = {results['halueval_vs_truthfulqa'][0]:.3f} (p = {results['halueval_vs_truthfulqa'][1]:.4f})
- **95% Bootstrap CI:** [{ci[0]:.3f}, {ci[1]:.3f}]
- **Intra-HaluEval mean correlation:** {gate['r_intra_mean']:.3f}

## Cross-Benchmark Correlations (HaluEval subtask vs TruthfulQA)

| Subtask | Spearman r | p-value |
|---------|-----------|---------|
"""
    for k, (r, p) in subtask_cross.items():
        name = k.replace("_vs_truthfulqa", "").replace("_", " ").title()
        report += f"| {name} | {r:.3f} | {p:.4f} |\n"

    report += """
## Intra-HaluEval Correlations

| Pair | Spearman r | p-value |
|------|-----------|---------|
"""
    for k, (r, p) in intra_pairs.items():
        name = k.replace("_", " ").title()
        report += f"| {name} | {r:.3f} | {p:.4f} |\n"

    report += f"""
## Interpretation

The cross-benchmark correlation r = {gate['r_cross']:.3f} is {'below' if gate['primary_pass'] else 'above'} the 0.7 threshold,
indicating that HaluEval and TruthfulQA measure {'partially distinct' if gate['primary_pass'] else 'largely overlapping'} capabilities.

The intra-HaluEval correlation (mean r = {gate['r_intra_mean']:.3f}) is {'higher' if gate['secondary_pass'] else 'not higher'} than
the cross-benchmark correlation, {'supporting' if gate['secondary_pass'] else 'not supporting'} the hypothesis that HaluEval subtasks
share a common coherence/consistency dimension that is distinct from misconception resistance.

## Figures

- `figures/correlation_heatmap.png`: Pairwise correlation matrix
- `figures/scatter_halueval_truthfulqa.png`: HaluEval vs TruthfulQA scatter
- `figures/gate_metrics.png`: Cross vs intra correlation comparison
"""

    with open(out_path, "w") as f:
        f.write(report)
