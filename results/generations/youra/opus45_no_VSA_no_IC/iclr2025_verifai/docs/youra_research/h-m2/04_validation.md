# Validation Report: H-M2

**Hypothesis:** A weighted ensemble of SA metrics achieves higher correlation with pass@1 than any single metric (r_ensemble > max(r_individual)).

**Date:** 2026-08-24
**Gate Type:** SHOULD_WORK

---

## Executive Summary

**Result: FAIL**

The weighted ensemble of pylint_score and radon_cc metrics did NOT achieve higher correlation with pass@1 than the best individual metric. The optimal ensemble (w_pylint=0.9, w_radon=0.1) achieved r=0.861 compared to the pylint baseline of r=0.873.

---

## Experiment Results

### Gate Evaluation

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| r_ensemble | 0.8608 | > 0.873 | NO |
| p-value | 1.1e-124 | < 0.05 | YES |

**Gate Decision:** FAIL (r_ensemble ≤ max_r_individual)

### Optimal Weights

| Metric | Weight |
|--------|--------|
| pylint_score | 0.90 |
| radon_cc | 0.10 |

### Weight Sensitivity Analysis

| w_pylint | r_ensemble |
|----------|-----------|
| 0.1 | -0.392 |
| 0.2 | -0.116 |
| 0.3 | 0.217 |
| 0.4 | 0.493 |
| 0.5 | 0.664 |
| 0.6 | 0.759 |
| 0.7 | 0.811 |
| 0.8 | 0.842 |
| 0.9 | 0.861 |

The correlation monotonically increases with w_pylint, peaking at the grid boundary (0.9). This indicates pylint_score dominates the signal, and adding radon_cc does not improve correlation.

### Data Summary

- **Dataset:** H-M1 validated results
- **Samples:** 421 (HumanEval + MBPP subset)
- **Metrics:** pylint_score, radon_cc, LOC (covariate)

---

## Interpretation

1. **Pylint dominates:** The optimal weight assignment (90% pylint, 10% radon) indicates radon_cc provides minimal complementary signal.

2. **Ensemble degradation:** Adding any radon_cc weight reduces correlation from the pylint-only baseline (0.873), suggesting the metrics capture redundant rather than orthogonal quality dimensions.

3. **Grid boundary effect:** The best weights are at the grid edge (0.9), suggesting w_pylint=1.0 (pure pylint) would perform even better — consistent with h-m1 findings.

---

## Artifacts

- `code/results/h_m2_ensemble.json` — full results
- `code/results/h_m2_data.csv` — dataset with ensemble scores
- `code/results/h_m2_summary.json` — summary
- `code/figures/gate_comparison.png` — bar chart
- `code/figures/weight_sensitivity.png` — sensitivity curve

---

## Gate Verdict

**SHOULD_WORK gate: NOT_SATISFIED**

The hypothesis that weighted ensemble improves over individual metrics is rejected. Pylint score alone (r=0.873) outperforms all tested ensemble configurations.
