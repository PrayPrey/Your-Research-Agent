# H-M2 Validation Report
# Post-Breakpoint Residual CoV Variance Compression

**Hypothesis:** H-M2 (MECHANISM / INCREMENTAL)
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Gate Type:** MUST_WORK
**Gate Verdict:** PASS

---

## Summary

Post-breakpoint residual CoV has significantly lower variance than pre-breakpoint residual CoV (Brown-Forsythe p=0.0099 < 0.05, variance_ratio post/pre=0.1981 < 1.0). Both gate conditions satisfied. Goodhart saturation compression confirmed.

---

## Experiment Results

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| BF p-value (two-tailed) | 0.0099 | < 0.05 | PASS |
| Variance ratio (post/pre) | 0.1981 | < 1.0 | PASS |
| n_pre | 8 | ≥ 3 | PASS |
| n_post | 107 | ≥ 3 | PASS |
| var_pre | 3.474867 | — | — |
| var_post | 0.688454 | — | — |
| BF stat | 6.8770 | — | — |
| BF p-value (one-tailed) | 0.0050 | — | — |
| Piecewise F-stat | 6.4648 | — | — |
| Piecewise F p-value | 0.0022 | — | — |
| direction_confirmed | True | True | PASS |
| mechanism_activated | True | — | — |

---

## Gate Evaluation

**GATE: PASS**

- Condition 1: BF p=0.0099 < 0.05 ✅
- Condition 2: variance_ratio=0.1981 < 1.0 ✅
- Both conditions satisfied simultaneously ✅

---

## Mechanism Indicators

| Indicator | Value |
|-----------|-------|
| direction_confirmed | True |
| statistically_significant | True |
| effect_measured | True |
| n_pre_nonzero | True |
| n_post_nonzero | True |

All 5 indicators confirmed. Gate verdict: PASS.

---

## Interpretation

Pre-breakpoint segment (n=8): var_pre=3.4749. Post-breakpoint segment (n=107): var_post=0.6885. Variance ratio = 0.1981 — post-segment variance is approximately 5× lower than pre-segment. Brown-Forsythe W=6.877, p=0.0099 (two-tailed), confirming the difference is statistically significant.

The piecewise regression F-test (F=6.465, p=0.0022) provides independent confirmation that the structural break at paper_count*=39 changes both slope and variance behavior.

This confirms the Goodhart saturation compression mechanism: the pre-breakpoint regime exhibits high exploration variance (3.81× global, per H-M1), while the post-breakpoint regime is compressed to approximately 1/5 of that variance, consistent with saturation dynamics.

---

## Figures

- `figures/gate_metrics.png` — Gate metric comparison
- `figures/boxplots_pre_post.png` — Pre vs post distribution boxplots
- `figures/variance_bars.png` — Variance magnitude comparison
- `figures/scatter_regime.png` — Residual CoV scatter by regime (N=115)
- `figures/f_distribution.png` — F-distribution with BF statistic position

---

## Data Provenance

- CSV: `h-m2/code/data/pwc_cov_computed.csv` (inherited from H-E1, N=115)
- Breakpoint: `h-e1/experiment_results.json` → breakpoint_idx=8, paper_count*=39
- Code: `h-m2/code/` (data_loader.py copied from H-M1; analyzer/verifier/visualizer/main rewritten)

---

## Prerequisites Status

- H-E1: VALIDATED (paper_count*=39 confirmed, permutation p=0.035)
- H-M1: VALIDATED (pre-segment variance 3.81× global, F-test p=0.0009, BF p=0.0099)

---

## Conclusion

H-M2 PASS. Post-breakpoint residual CoV variance is significantly compressed vs pre-breakpoint (BF p=0.0099, ratio=0.1981). Goodhart saturation compression mechanism operating as predicted. Proceed to H-M3.
