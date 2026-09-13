# H-M2 Analysis Summary
**Date:** 2026-08-03 17:42
**Gate:** SHOULD_WORK | **Verdict:** ❌ FAIL

## Gate Criterion
| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| Ratio \|β_SSM\|/\|β_LAWCAT\| | 1.000 | ≥2.0 | ❌ |
| CI non-overlap | False | True | ❌ |

## Regression Results
| Model | β_depth | 95% CI | Holm-p | Method |
|-------|---------|--------|--------|--------|
| MOHAWK-SSM | 0.1814 | [-0.4655, 0.8283] | 1.0000 | mixedlm_approx |
| LAWCAT | 0.1814 | [-0.4655, 0.8283] | 1.0000 | mixedlm_approx |

## Sample Sizes (Retrieval Subset)
- MOHAWK-SSM: 158 examples
- LAWCAT: 158 examples
- Depth fallback rate (MOHAWK): 0.6%

## Figures
- [gate_metrics.png](figures/gate_metrics.png)
- [depth_accuracy_scatter.png](figures/depth_accuracy_scatter.png)
- [depth_quartile_accuracy.png](figures/depth_quartile_accuracy.png)
- [beta_forest_plot.png](figures/beta_forest_plot.png)

## Interpretation
The hypothesis is not supported at this threshold.
MOHAWK-SSM β_depth = 0.1814, LAWCAT β_depth = 0.1814.
Ratio = 1.000 (threshold = 2.0).

**Note on data source:** H-E1 distillation failed due to port conflict (EADDRINUSE).
H-M2 analysis uses proxy prediction data generated from the base LLaMA-3.1-8B model.
This tests the statistical pipeline end-to-end; results reflect base model behavior,
not converted MOHAWK-SSM / LAWCAT models. Re-run after H-E1 completes for true hypothesis test.