"""Report generation for H-M3."""

from datetime import datetime


def verify_mechanism_activation(results: dict, pca_result: dict) -> dict:
    """Verify H-M3 mechanism: FactScore distinct from TruthfulQA and HaluEval."""
    verification = {
        "mechanism_activated": False,
        "gate_passed": False,
        "details": {},
    }

    r_fs_tqa = results.get("fs_tqa", (None, None))[0]
    r_fs_he = results.get("fs_he", (None, None))[0]
    n_80 = pca_result.get("n_components_80pct", 1)

    if r_fs_tqa is not None and r_fs_he is not None:
        verification["mechanism_activated"] = True
        verification["details"]["r_factscore_truthfulqa"] = r_fs_tqa
        verification["details"]["r_factscore_halueval"] = r_fs_he
        verification["details"]["n_components_80pct"] = n_80

        # Gate: both r < 0.7
        if abs(r_fs_tqa) < 0.7 and abs(r_fs_he) < 0.7:
            verification["gate_passed"] = True
            verification["details"]["conclusion"] = (
                "FactScore measures distinct construct from both TruthfulQA and HaluEval"
            )
        else:
            overlaps = []
            if abs(r_fs_tqa) >= 0.7:
                overlaps.append("TruthfulQA")
            if abs(r_fs_he) >= 0.7:
                overlaps.append("HaluEval")
            verification["details"]["conclusion"] = f"FactScore overlaps with: {', '.join(overlaps)}"

    return verification


def write_validation_report(
    results: dict,
    gate: dict,
    pca_result: dict,
    ci_fs_tqa: tuple,
    ci_fs_he: tuple,
    n_models: int,
    out_path: str,
) -> None:
    """Generate 04_validation.md report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# H-M3 Validation Report

**Generated:** {timestamp}
**Hypothesis:** FactScore measures atomic factual precision via retrieval-based verification, distinct from both TruthfulQA and HaluEval

## Gate Result: {gate['status']}

| Condition | Value | Threshold | Pass |
|-----------|-------|-----------|------|
| r(FactScore, TruthfulQA) | {gate['r_fs_tqa']:.3f} | < 0.7 | {'PASS' if gate['cond_tqa_pass'] else 'FAIL'} |
| r(FactScore, HaluEval) | {gate['r_fs_he']:.3f} | < 0.7 | {'PASS' if gate['cond_he_pass'] else 'FAIL'} |

## Summary Statistics

- **N models analyzed:** {n_models}
- **r(FactScore, TruthfulQA):** {results['fs_tqa'][0]:.3f} (p = {results['fs_tqa'][1]:.4f})
  - 95% CI: [{ci_fs_tqa[0]:.3f}, {ci_fs_tqa[1]:.3f}]
- **r(FactScore, HaluEval):** {results['fs_he'][0]:.3f} (p = {results['fs_he'][1]:.4f})
  - 95% CI: [{ci_fs_he[0]:.3f}, {ci_fs_he[1]:.3f}]
- **r(TruthfulQA, HaluEval):** {results['tqa_he'][0]:.3f} (reference from H-M2)

## PCA Analysis

| Metric | Value |
|--------|-------|
| Components for 80% variance | {pca_result['n_components_80pct']} |
| PC1 explained variance | {pca_result['explained_variance'][0]:.1%} |
| PC2 explained variance | {pca_result['explained_variance'][1]:.1%} if len(pca_result['explained_variance']) > 1 else 'N/A' |
| Multi-dimensional | {'Yes' if pca_result['n_components_80pct'] >= 2 else 'No'} |

## Interpretation

The cross-benchmark correlations r(FS,TQA) = {gate['r_fs_tqa']:.3f} and r(FS,HE) = {gate['r_fs_he']:.3f}
are {'both below' if gate['cond_tqa_pass'] and gate['cond_he_pass'] else 'not both below'} the 0.7 threshold.

{'FactScore appears to measure a distinct capability from both TruthfulQA and HaluEval.' if gate['status'] == 'PASS' else 'Some overlap detected between FactScore and other benchmarks.'}

PCA indicates {pca_result['n_components_80pct']} component(s) needed for 80% variance,
{'supporting' if pca_result['n_components_80pct'] >= 2 else 'not supporting'} a multi-dimensional truthfulness construct.

## Figures

- `figures/gate_metrics.png`: FactScore cross-benchmark correlations
- `figures/correlation_heatmap.png`: 3x3 correlation matrix
- `figures/pca_biplot.png`: PCA loadings
- `figures/scatter_matrix.png`: Pairwise benchmark scatter
- `figures/cumulative_variance.png`: PCA variance explained
"""

    with open(out_path, "w") as f:
        f.write(report)
