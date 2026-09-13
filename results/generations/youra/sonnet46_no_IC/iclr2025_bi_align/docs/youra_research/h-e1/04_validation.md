# H-E1 Validation Report

## Gate Result: PASS

| Criterion | Value | Threshold | Met? |
|-----------|-------|-----------|------|
| r_partial > 0 | 0.9851 | > 0 | Yes |
| p_val < 0.05 | 0.0000 | < 0.05 | Yes |
| |r_partial| >= 0.15 | 0.9851 | >= 0.15 | Yes |

## Partial Correlation Results

- **r_partial**: 0.9851
- **p_val**: 0.000000
- **CI95%**: [0.9800, 1.0000]
- **n**: 223

## Bootstrap Robustness (1000 resamples, seed=42)

- **Bootstrap CI 95%**: [0.9760, 0.9875]
- **CI lower > 0**: Yes

## VIF Diagnostic

| Variable | VIF | Multicollinearity? |
|----------|-----|-------------------|
| win_rate | 1.7640 | No |
| avg_length | 1.7640 | No |

## Figures

- docs/youra_research/h-e1/figures/fig1_scatter_winrate_lc.png
- docs/youra_research/h-e1/figures/fig2_partial_regression.png
- docs/youra_research/h-e1/figures/fig3_bootstrap_distribution.png
- docs/youra_research/h-e1/figures/fig4_vif_diagnostic.png
- docs/youra_research/h-e1/figures/fig5_delta_scatter.png

## Interpretation

**H-E1 PASSED the MUST_WORK gate.**

Spearman partial correlation ρ(win_rate, LC_winrate | avg_length) = 0.9851 (p=0.000000) demonstrates that model capability (win_rate) independently predicts length-debiased preference (LC_winrate) after controlling for response verbosity (avg_length). The effect size |r_partial| = 0.9851 exceeds the pre-registered threshold of 0.15. Bootstrap CI [0.9760, 0.9875] confirms robustness.

This validates the existence of the bidirectional alignment gap signal and enables downstream hypotheses H-M1, H-M2, H-M3, H-C1.