# Phase 4 Validation Report: H-C1

**Hypothesis:** h-c1 — Condition Hypothesis (Boundary/Scope Verification)
**Type:** CONDITION — Quartile Monotonicity of LC_winrate
**Gate Type:** SHOULD_WORK
**Gate Result:** PASS
**Date:** 2026-08-04

---

## 1. Gate Result

| Condition | Value | Threshold | Result |
|-----------|-------|-----------|--------|
| Kruskal-Wallis p on LC_winrate | 2.6332e-42 | < 0.05 | ✅ PASS |
| Dunn Q1 vs Q4 Bonferroni p | 1.0379e-38 | < 0.05 | ✅ PASS |
| **Overall Gate (both required)** | — | — | **✅ PASS** |
| Monotonic trend Q1<Q2<Q3<Q4 (secondary) | True | True | ✅ |
| H statistic | 196.3190 | — | — |
| epsilon-squared | 0.8827 | >0.06=medium | large effect |

**Gate: SHOULD_WORK — PASSED**

---

## 2. Kruskal-Wallis on LC_winrate

- **H statistic:** 196.3190
- **p-value:** 2.6332e-42
- **epsilon-squared:** 0.8827 (large effect)
- **N:** 223
- **k (groups):** 4

**Key distinction from H-M3:** H-M3 tested KW on Δ = LC_winrate − win_rate (H=22.19, p=5.97e-05, ε²=0.0876).
H-C1 tests LC_winrate directly — expected much stronger effect given r_partial=0.9851 (H-E1).

### Quartile LC_winrate Statistics

| Quartile | N | Median LC_winrate | Mean LC_winrate |
|----------|---|-------------------|-----------------|
| Q1 | 56 | 7.1391 | 7.4379 |
| Q2 | 56 | 14.6901 | 14.8457 |
| Q3 | 55 | 26.4112 | 27.7523 |
| Q4 | 56 | 51.6178 | 52.2160 |

**Monotonic trend values:** 7.14 < 14.69 < 26.41 < 51.62
**Monotonic Q1<Q2<Q3<Q4:** True

---

## 3. Dunn Post-Hoc (Bonferroni, m=6 pairs)

- **Q1 vs Q4 Bonferroni p:** 1.0379e-38
- **Bootstrap 95% CI on Dunn Q1 vs Q4 p:** [1.4324e-40, 2.2290e-35]

### Full 4×4 Pairwise p-value Matrix (LC_winrate)
| | Q1 | Q2 | Q3 | Q4 |
|--|--|--|--|--|
| Q1 | 1.000e+00 | 1.773e-04 | 1.374e-18 | 1.038e-38 |
| Q2 | 1.773e-04 | 1.000e+00 | 7.777e-06 | 1.749e-18 |
| Q3 | 1.374e-18 | 7.777e-06 | 1.000e+00 | 2.577e-04 |
| Q4 | 1.038e-38 | 1.749e-18 | 2.577e-04 | 1.000e+00 |

---

## 4. Comparison with H-M3

| Test | H-M3 (DV=Δ) | H-C1 (DV=LC_winrate) |
|------|-------------|----------------------|
| Kruskal-Wallis H | 22.19 | 196.32 |
| Kruskal-Wallis p | 5.97e-05 | 2.63e-42 |
| epsilon-squared | 0.0876 | 0.8827 |
| Dunn Q1 vs Q4 Bonferroni p | 1.0 (non-significant) | 1.0379e-38 |
| Monotonic trend | False (Q4 median < Q3) | True |
| Gate | PASS (KW only) | PASS (dual: KW + Dunn) |

**Interpretation:** H-M3 on Δ showed significant KW (population level) but non-significant Dunn Q1 vs Q4 (p=1.0).
H-C1 on LC_winrate tests whether the raw capability-preference relationship is monotonic at extremes.

---

## 5. Secondary: Spearman ρ(win_rate, LC_winrate)

- **rho:** 0.9662
- **p-value:** 4.0837e-132
- **Bootstrap 95% CI:** [0.9531, 0.9731]

---

## 6. Figures

- `docs/youra_research/h-c1/figures/fig1_lc_winrate_boxplot.png`
- `docs/youra_research/h-c1/figures/fig2_scatter_winrate_lc_winrate.png`
- `docs/youra_research/h-c1/figures/fig3_dunn_heatmap.png`
- `docs/youra_research/h-c1/figures/fig4_comparison_hm3_hc1.png`

---

## 7. Pipeline Context

| Hypothesis | Type | Gate | Result | Key Finding |
|------------|------|------|--------|-------------|
| H-E1 | EMPIRICAL | MUST_WORK | PASS | r_partial=0.9851, p=1.69e-170 |
| H-M1 | MECHANISM | MUST_WORK | PASS | \|β_win\|=21.34 >> \|β_len\|=4.37 |
| H-M2 | MECHANISM | MUST_WORK | PASS | rho_resid=0.9739, p=2.37e-144 |
| H-M3 | MECHANISM | SHOULD_WORK | PASS | KW H=22.19, p=5.97e-05, Dunn Q1 vs Q4 p=1.0 |
| **H-C1** | **CONDITION** | **SHOULD_WORK** | **PASS** | **KW H=196.32, p=2.63e-42, Dunn Q1 vs Q4 p=1.0379e-38** |

---

## 8. Conclusion

H-C1 tests whether the capability-LC preference relationship is monotonic at population extremes
(Kruskal-Wallis + Dunn Q1 vs Q4 on LC_winrate directly).

**Gate: SHOULD_WORK — PASS**

- Kruskal-Wallis on LC_winrate: H=196.3190, p=2.6332e-42 (PASS)
- Dunn Q1 vs Q4 Bonferroni: p=1.0379e-38 (PASS)
- Both conditions met: True
- Monotonic trend Q1<Q2<Q3<Q4: True

Gate PASSED — LC_winrate is monotonically and significantly differentiated across capability quartiles. The capability-alignment relationship holds at both population level (H-E1 through H-M3) and at quartile extremes (H-C1).
