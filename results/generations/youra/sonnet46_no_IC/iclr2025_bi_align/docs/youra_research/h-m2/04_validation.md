# Phase 4 Validation Report: h-m2

**Hypothesis:** h-m2 — Residual Capability Signal Confirmation (FWL Theorem)
**Gate Type:** SHOULD_WORK
**Gate Result:** PASS
**FWL Consistency:** CONSISTENT

---

## 1. Gate Evaluation

| Criterion | Value | Threshold | Status |
|-----------|-------|-----------|--------|
| ρ(win_rate_resid, lc_resid) | 0.9739 | > 0 | PASS |
| p-value | 2.3707e-144 | < 0.05 | PASS |
| Bootstrap CI lower | 0.9619 | > 0 | PASS |

**Gate reason:** rho=0.9739>0, p=2.37e-144<0.05, CI_lower=0.9619>0

---

## 2. Primary Results

| Metric | Value |
|--------|-------|
| Spearman ρ | 0.9739 |
| p-value | 2.3707e-144 |
| Bootstrap 95% CI | [0.9619, 0.9806] |
| N (models after dropna) | 223 |

---

## 3. OLS Residualization Diagnostics

| Regression | R² |
|------------|-----|
| win_rate ~ avg_length | 0.4331 |
| lc_winrate ~ avg_length | 0.2561 |

---

## 4. FWL Consistency Check

| Metric | Value |
|--------|-------|
| H-E1 r_partial | 0.9851 |
| H-M2 ρ (residuals) | 0.9739 |
| FWL delta (|ρ − 0.9851|) | 0.0112 |
| FWL consistent (delta < 0.02) | True |

---

## 5. Pingouin Cross-Validation

| Metric | Value |
|--------|-------|
| Pingouin partial_corr r (Spearman) | 0.9851 |
| Pingouin p-value | 3.3813e-170 |
| Consistent with residual ρ | False |

---

## 6. Figures

1. `docs/youra_research/h-m2/figures/fig1_residuals_scatter.png`
2. `docs/youra_research/h-m2/figures/fig2_residual_distributions.png`
3. `docs/youra_research/h-m2/figures/fig3_partial_regression.png`
4. `docs/youra_research/h-m2/figures/fig4_fwl_consistency.png`
5. `docs/youra_research/h-m2/figures/fig5_bootstrap_distribution.png`

---

## 7. Interpretation

The Spearman correlation of OLS residuals (ρ=0.9739) confirms that after explicitly removing
verbosity (avg_length) from both win_rate and LC_winrate, a strong positive residual capability
signal remains. This is the explicit mechanistic demonstration of the FWL theorem applied to
the AlpacaEval 2.0 leaderboard data.

FWL theorem prediction: ρ_H-M2 ≈ r_partial_H-E1 = 0.9851. Observed delta: 0.0112.

**SHOULD_WORK Gate: PASS** — Pipeline continues normally.