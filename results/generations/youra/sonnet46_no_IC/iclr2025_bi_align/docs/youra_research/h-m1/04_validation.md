# Validation: h-m1

**Gate**: PASS
**Path**: OLS_beta
**Dominant predictor**: win_rate
**Date**: 2026-08-04

## Gate Evaluation

| Criterion | Value | Threshold | Met? |
|-----------|-------|-----------|------|
| |β_win_rate_std| > |β_avg_length_std| | 21.3391 > 4.3720 | strict > | Yes |
| p_win < 0.05 | 4.5782e-145 | < 0.05 | Yes |
| Gate overall | — | — | PASS |

## OLS Results (LC_winrate ~ win_rate_std + avg_length_std)

| Metric | Value |
|--------|-------|
| β_win_rate_std | 21.3391 |
| β_avg_length_std | -4.3720 |
| |β_win_rate_std| | 21.3391 |
| |β_avg_length_std| | 4.3720 |
| p_win | 4.5782e-145 |
| p_len | 8.0248e-30 |
| R² | 0.9628 |
| R²_adj | 0.9624 |

## Baseline OLS (verbosity-only null model: LC_winrate ~ avg_length_std)

| Metric | Value |
|--------|-------|
| β_avg_length_std | 9.6714 |
| R² | 0.2561 |
| p_value | 6.6638e-16 |

## VIF Diagnostic

| Variable | VIF | High? |
|----------|-----|-------|
| win_rate_std | 1.764 | No |
| avg_length_std | 1.764 | No |
| any_high_vif | False | — |

## OLS Diagnostics

| Test | Value |
|------|-------|
| Breusch-Pagan stat | 8.9462 |
| Breusch-Pagan p | 0.0114 |
| heteroscedastic | True |

## Comparison with h-e1

| Metric | h-e1 | h-m1 |
|--------|------|------|
| r_partial (Spearman) | 0.9851 | N/A (OLS path) |
| VIF win_rate | 1.764 | 1.764 |
| VIF avg_length | 1.764 | 1.764 |
| Dominant predictor | win_rate | win_rate |
| Gate result | PASS | PASS |

## Figures

- docs/youra_research/h-m1/figures/fig1_dominance_bar.png
- docs/youra_research/h-m1/figures/fig2_coef_plot.png
- docs/youra_research/h-m1/figures/fig3_vif_bar.png
- docs/youra_research/h-m1/figures/fig4_residuals_vs_fitted.png
- docs/youra_research/h-m1/figures/fig5_qq_plot.png
- docs/youra_research/h-m1/figures/fig6_scatter_by_length_quartile.png

## Interpretation

**h-m1 PASSED the MUST_WORK gate.**

Standardized OLS confirms: |β_win_rate_std| = 21.3391 >> |β_avg_length_std| = 4.3720 (p_win = 4.5782e-145). Capability (win_rate) dominates verbosity (avg_length) as predictor of LC_winrate. VIF = 1.764 confirms no multicollinearity (OLS path valid). This validates the mechanism chapter: capability is the dominant driver of length-debiased preference.