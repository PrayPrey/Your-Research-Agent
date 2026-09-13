# Phase 4 Validation Report: H-M3

**Hypothesis:** h-m3 — Capability-Quartile Delta Distribution Test
**Gate Type:** SHOULD_WORK
**Gate Result:** PASS
**Date:** 2026-08-04

---

## 1. Gate Result

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| Kruskal-Wallis p | 5.9691e-05 | < 0.05 | ✅ PASS |
| Monotonic trend Q1<Q2<Q3<Q4 | False | True | ⚠️ |
| H statistic | 22.1852 | — | — |
| epsilon-squared | 0.0876 | >0.06=medium | medium effect |

**Gate: SHOULD_WORK — PASSED**

---

## 2. Kruskal-Wallis Results

- **H statistic:** 22.1852
- **p-value:** 5.9691e-05
- **epsilon-squared:** 0.0876
- **N:** 223
- **k (groups):** 4

### Quartile Delta Statistics

| Quartile | N | Median Δ | Mean Δ |
|----------|---|----------|--------|
| Q1 | 56 | 2.1896 | 2.4975 |
| Q2 | 56 | 2.9588 | 3.6959 |
| Q3 | 55 | 5.4332 | 5.4359 |
| Q4 | 56 | 0.9137 | 0.4896 |

**Interpretation:** Q1 (lowest capability) has most-negative Δ; Q4 (highest capability) has least-negative Δ.
Monotonic trend: False.

---

## 3. Dunn Post-Hoc (Bonferroni)

Run conditionally (only if KW p < 0.05): Yes

- **Q1 vs Q4 pairwise p:** 1.0000e+00

### Full 4×4 Pairwise p-value Matrix
| | Q1 | Q2 | Q3 | Q4 |
|--|--|--|--|--|
| Q1 | 1.000e+00 | 7.931e-01 | 5.625e-03 | 1.000e+00 |
| Q2 | 7.931e-01 | 1.000e+00 | 4.219e-01 | 4.944e-02 |
| Q3 | 5.625e-03 | 4.219e-01 | 1.000e+00 | 5.397e-05 |
| Q4 | 1.000e+00 | 4.944e-02 | 5.397e-05 | 1.000e+00 |

---

## 4. Secondary: Spearman ρ(win_rate, Δ)

> ⚠️ **NOTE: Mathematical dependency present** — Δ = LC_winrate − win_rate contains −win_rate,
> creating non-causal dependency. This is a secondary supporting analysis only.

- **rho:** -0.0503
- **p-value:** 4.5514e-01
- **Bootstrap 95% CI:** [-0.1872, 0.0825]

---

## 5. Secondary: OLS Δ ~ win_rate_std + avg_length_std

| Coefficient | Value | p-value |
|-------------|-------|---------|
| β_win_rate_std | 1.8174 | 1.0274e-07 |
| β_avg_length_std | -4.3720 | 8.0248e-30 |
| R² | 0.4680 | — |

---

## 6. Figures

- `docs/youra_research/h-m3/figures/fig1_boxplot_delta_by_quartile.png`
- `docs/youra_research/h-m3/figures/fig2_scatter_winrate_delta.png`
- `docs/youra_research/h-m3/figures/fig3_dunn_heatmap.png`
- `docs/youra_research/h-m3/figures/fig4_bar_quartile_medians.png`

---

## 7. Pipeline Context

| Hypothesis | Result | Key Finding |
|------------|--------|-------------|
| H-E1 | PASS | r_partial=0.9851, p=1.69e-170 |
| H-M1 | PASS | \|β_win\|=21.34 >> \|β_len\|=4.37 |
| H-M2 | PASS | rho_resid=0.9739, p=2.37e-144 |
| **H-M3** | **PASS** | **KW H=22.19, p=5.97e-05, ε²=0.0876** |

---

## 8. Conclusion

H-M3 tests whether the bidirectional alignment gap (Δ = LC_winrate − win_rate) differs significantly
across capability quartiles (Kruskal-Wallis SHOULD_WORK gate).

**Result:** Kruskal-Wallis H=22.1852, p=5.9691e-05.
Gate: **PASS** — SHOULD_WORK satisfied, pipeline proceeds to H-C1.

Effect size epsilon-squared=0.0876 (medium effect).
Monotonic trend Q1 < Q2 < Q3 < Q4: False.
