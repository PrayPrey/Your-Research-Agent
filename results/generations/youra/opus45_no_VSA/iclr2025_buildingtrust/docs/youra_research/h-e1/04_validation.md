# Phase 4 Validation Report — H-E1

## Hypothesis

**ID:** H-E1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Statement:** λ₁,residual exceeds 95th percentile of permutation distribution after controlling for log(params) and release date

---

## Gate Verdict: **PASS** ✓

---

## Experiment Summary

| Metric | Value | Threshold | Pass |
|--------|-------|-----------|------|
| Sample size (N) | 4,561 models | ≥80 | ✓ |
| p-value | 0.001 | <0.05 | ✓ |
| λ₁ observed | 2.277 | >95th percentile | ✓ |
| 95th percentile null | 0.803 | — | — |
| Variance explained (PC1) | 60.0% | >20% | ✓ |

---

## Key Findings

1. **Residual latent factor exists:** λ₁=2.277 vastly exceeds null threshold (0.803), p<0.001
2. **Confound control worked:** R² ranged 0.21–0.50 across benchmarks (scale/time explain 20–50% of variance)
3. **Strong factor structure:** PC1 explains 60% of residual variance after confound removal
4. **Uniform loadings:** All 6 benchmarks load positively (0.35–0.44) on PC1, consistent with general factor

---

## Assumption Checks

| Check | Result | Threshold | Note |
|-------|--------|-----------|------|
| VIF (multicollinearity) | 1.02 | <5.0 | ✓ Confounds independent |
| KMO (sampling adequacy) | 0.83 | ≥0.6 | ✓ Data suitable for PCA |
| Shapiro-Wilk (normality) | p≈0 | — | Non-normal residuals (expected with N=4561) |

Non-normality does not invalidate permutation test (distribution-free).

---

## PC1 Loadings

| Benchmark | Loading |
|-----------|---------|
| IFEval | 0.354 |
| BBH | 0.429 |
| MATH Lvl 5 | 0.426 |
| GPQA | 0.424 |
| MUSR | 0.365 |
| MMLU-PRO | 0.444 |

All positive, roughly equal magnitude → supports general factor interpretation.

---

## Artifacts

- `outputs/h_e1_results.json` — Full results
- `outputs/permutation_dist.png` — Null distribution plot
- `outputs/scree_plot.png` — Eigenvalue scree plot
- `outputs/pc1_loadings.png` — Loadings bar chart
- `outputs/benchmark_matrix.csv` — Standardized benchmark scores
- `outputs/residualized_matrix.csv` — Confound-residualized scores

---

## Conclusion

H-E1 hypothesis **confirmed**. A dominant latent factor survives confound control (log scale + release date), supporting existence of GRC as a measurable construct. Proceed to H-M1 (mechanistic testing).
