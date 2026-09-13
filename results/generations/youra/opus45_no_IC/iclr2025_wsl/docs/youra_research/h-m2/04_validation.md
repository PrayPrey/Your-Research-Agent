# Phase 4 Validation Report: H-M2

**Date:** 2026-08-12
**Hypothesis:** NFN predictions identical under weight permutation (diff < 1e-5)
**Type:** MECHANISM
**Gate Type:** SHOULD_WORK

---

## Executive Summary

**GATE RESULT: PASSED**

All NFN predictions are identical under weight-space permutations within floating-point tolerance. Max deviation (1.19e-07) is well below the 1e-5 threshold.

---

## Experiment Results

### Predictions (Original + 10 Permuted)

| Configuration | Prediction Value |
|---------------|------------------|
| original | 0.87597257 |
| perm_0 | 0.87597263 |
| perm_1 | 0.87597263 |
| perm_2 | 0.87597257 |
| perm_3 | 0.87597257 |
| perm_4 | 0.87597263 |
| perm_5 | 0.87597269 |
| perm_6 | 0.87597263 |
| perm_7 | 0.87597263 |
| perm_8 | 0.87597263 |
| perm_9 | 0.87597263 |

### Invariance Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Max Deviation | 1.19e-07 | < 1e-5 | PASS |
| Std | 8.22e-08 | - | - |
| Invariance Score | 1.0 | - | - |
| Invariance Correlation | 0.9999999 | - | - |

---

## Gate Evaluation

**Gate Type:** SHOULD_WORK
**Criteria:** max_deviation < 1e-5

| Check | Expected | Actual | Result |
|-------|----------|--------|--------|
| max_deviation < 1e-5 | < 1e-5 | 1.19e-07 | PASS |

**Conclusion:** NFN prediction invariance is verified. The HNPPool layer correctly produces permutation-invariant features that propagate through the final linear layer.

---

## Code Artifacts

- `h-m2/code/test_predictions.py` — Main experiment script
- `h-m2/results.json` — Structured results
- `h-m2/figures/predictions_bar.png` — Bar chart
- `h-m2/figures/deviation_heatmap.png` — Pairwise deviations
- `h-m2/figures/prediction_histogram.png` — Distribution

---

## Reused Components (from H-M1)

| Module | Source | Functions Used |
|--------|--------|----------------|
| test_data.py | h-m1/code/ | generate_test_mlp |
| permute.py | h-m1/code/ | generate_permutations, permute_state_dict |
| metrics.py | h-m1/code/ | compute_invariance_metrics, gate_passed |
| test_invariance.py | h-m1/code/ | load_nfn_model, state_dict_to_wsfeat, run_predictions, plotting functions |

---

## Next Phase

With H-M2 validated, proceed to H-M3 (untrained MLP baseline).

---

*Generated: 2026-08-12 | Phase 4 Validation Complete*
