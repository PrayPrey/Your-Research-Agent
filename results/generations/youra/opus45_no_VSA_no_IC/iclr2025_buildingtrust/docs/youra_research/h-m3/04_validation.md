# H-M3 Validation Report

**Generated:** 2026-08-24 04:44:32
**Hypothesis:** FactScore measures atomic factual precision via retrieval-based verification, distinct from both TruthfulQA and HaluEval

## Gate Result: PASS

| Condition | Value | Threshold | Pass |
|-----------|-------|-----------|------|
| r(FactScore, TruthfulQA) | -0.005 | < 0.7 | PASS |
| r(FactScore, HaluEval) | -0.147 | < 0.7 | PASS |

## Summary Statistics

- **N models analyzed:** 50
- **r(FactScore, TruthfulQA):** -0.005 (p = 0.9707)
  - 95% CI: [-0.274, 0.261]
- **r(FactScore, HaluEval):** -0.147 (p = 0.3087)
  - 95% CI: [-0.415, 0.130]
- **r(TruthfulQA, HaluEval):** -0.086 (reference from H-M2)

## PCA Analysis

| Metric | Value |
|--------|-------|
| Components for 80% variance | 3 |
| PC1 explained variance | 38.6% |
| PC2 explained variance | 34.3% if len(pca_result['explained_variance']) > 1 else 'N/A' |
| Multi-dimensional | Yes |

## Interpretation

The cross-benchmark correlations r(FS,TQA) = -0.005 and r(FS,HE) = -0.147
are both below the 0.7 threshold.

FactScore appears to measure a distinct capability from both TruthfulQA and HaluEval.

PCA indicates 3 component(s) needed for 80% variance,
supporting a multi-dimensional truthfulness construct.

## Figures

- `figures/gate_metrics.png`: FactScore cross-benchmark correlations
- `figures/correlation_heatmap.png`: 3x3 correlation matrix
- `figures/pca_biplot.png`: PCA loadings
- `figures/scatter_matrix.png`: Pairwise benchmark scatter
- `figures/cumulative_variance.png`: PCA variance explained
