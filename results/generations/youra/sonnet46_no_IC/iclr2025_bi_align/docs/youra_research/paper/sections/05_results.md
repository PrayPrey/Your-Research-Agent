# 5. Results

All five sub-hypotheses passed their gates. We report results in the order of research questions, building from existence (RQ1) to mechanism (RQ2–RQ3) to population confirmation (RQ4–RQ5).

## 5.1 RQ1: Capability Independently Predicts LC Preference (H-E1)

After controlling for response verbosity (avg_length), model capability (win_rate) independently predicts length-controlled preference (LC_winrate) with:

> **r_partial = 0.9851, p = 1.69e-170, Bootstrap 95% CI [0.976, 0.988], N=223**

The VIF diagnostic confirmed no multicollinearity: VIF = 1.764 for both win_rate and avg_length (threshold: VIF < 5.0). This validates the interpretability of the partial correlation (Figure 4).

Figure 1 shows the bivariate scatter of win_rate vs LC_winrate, illustrating the strong base relationship (Spearman ρ = 0.966 bivariate). Figure 2 shows the partial regression plot after residualizing out avg_length from both variables — the near-perfect linear relationship in residual space corresponds to r_partial = 0.9851.

**Key observation**: The partial correlation (0.985) *exceeds* the bivariate correlation (0.94) reported by Dubois et al. [2024]. This counterintuitive direction — controlling for verbosity strengthens, not weakens, the capability-LC alignment — indicates that verbosity was acting as a mild suppressor. Capable models write longer responses (ρ(win_rate, avg_length) ≈ 0.63), and this shared length component partially masked the true capability signal in bivariate analysis. Once removed, the underlying capability ordering emerges more cleanly.

The bootstrap distribution (Figure 3; 1000 resamples, seed=42) confirms stability: the 95% CI [0.976, 0.988] is narrow and far from zero, ruling out that the high estimate is driven by any subset of models.

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| r_partial (Spearman) | 0.9851 | ≥ 0.15 | **EXCEEDED** |
| p-value | 1.69e-170 | < 0.05 | **EXCEEDED** |
| Bootstrap 95% CI lower | 0.976 | > 0 | **CONFIRMED** |
| VIF (both vars) | 1.764 | < 5.0 | **MET** |

## 5.2 RQ2: Capability Dominates Verbosity in Standardized OLS (H-M1)

In standardized OLS (LC_winrate ~ win_rate_std + avg_length_std), capability is the overwhelmingly dominant predictor:

> **|β_win| = 21.34 vs |β_len| = 4.37 — dominance ratio 4.88:1 (p_win = 4.58e-145)**

The full model achieves R² = 0.963, compared to R² = 0.256 for the verbosity-only restricted model. Capability adds 70.7 percentage points of explained variance over what verbosity provides alone.

Figure 6 shows the standardized coefficient comparison. Two features of the result are noteworthy:

1. **β_len = −4.37 (negative)**: Verbosity carries a *negative* standardized coefficient once capability is controlled. This is precisely what the LC correction intends — longer responses are penalized in LC evaluation after accounting for capability, confirming the GLM debiasing is functional.

2. **Scale of β_win = 21.34**: In a regression where all variables are standardized to unit variance, a coefficient of 21.34 reflects the extent to which capability variance swamps verbosity variance in predicting LC preference. The OLS R² of 0.963 approaches a near-deterministic prediction.

Breusch-Pagan heteroscedasticity test: stat = 8.946, p = 0.011 — mild heteroscedasticity present. However, β estimates are unbiased under OLS assumptions even with heteroscedasticity; only standard errors are affected. Given p_win = 4.58e-145, even substantially inflated standard errors would not alter significance.

| Metric | Value | Status |
|--------|-------|--------|
| \|β_win_std\| | 21.34 | **DOMINATES** |
| \|β_len_std\| | 4.37 | — |
| Dominance ratio | 4.88× | — |
| Full model R² | 0.963 | — |
| Verbosity-only R² | 0.256 | — |
| R² gain from capability | +70.7pp | — |

## 5.3 RQ3: FWL Theorem Robustness (H-M2)

The partial correlation result is independently replicated via Frisch-Waugh-Lovell residualization:

> **ρ_resid = 0.9739, p = 2.37e-144; delta = 0.0112 (< 0.02 threshold)**

After regressing avg_length from both win_rate and LC_winrate (OLS), the Spearman correlation of the residual pairs yields ρ = 0.9739. The delta from the Pingouin partial correlation estimate (0.9851) is 0.0112 — within the expected approximation error for Spearman's rank-based FWL extension (FWL holds exactly for Pearson; Spearman introduces a small approximation proportional to rank-transform nonlinearity).

Figure 8 shows the residual scatter (win_rate_resid vs lc_resid), and Figure 9 shows the FWL consistency comparison between the two estimators. The convergence within 1.1pp rules out that the high partial correlation is an artifact of the `pingouin` implementation or rank transformation procedure.

Bootstrap 95% CI on ρ_resid: [0.962, 0.981] — excludes zero with overwhelming margin.

| Estimator | Value | p-value |
|-----------|-------|---------|
| Pingouin partial_corr (Spearman) | 0.9851 | 1.69e-170 |
| FWL residual Spearman | 0.9739 | 2.37e-144 |
| Delta | 0.0112 | < 0.02 ✓ |

## 5.4 RQ4: Monotonic LC Ordering Across Capability Quartiles (H-C1)

The capability-LC alignment is confirmed at population extremes with large effect size:

> **KW H = 196.32, p = 2.63e-42, ε² = 0.883 (large); Dunn Q1 vs Q4 p = 1.04e-38**
> 
> **Quartile medians: Q1 = 7.14 < Q2 = 14.69 < Q3 = 26.41 < Q4 = 51.62 (fully monotonic)**

Figure 11 shows the boxplot of LC_winrate across quartiles. The separation is striking: Q4 models (highest capability quartile) show a median LC preference score of 51.62% — 7.2 times higher than Q1 models (7.14%). The Dunn post-hoc Q1 vs Q4 comparison (Bonferroni-corrected p = 1.04e-38) confirms that the extreme quartiles are unambiguously distinct. Bootstrap CI on the Dunn p-value: [1.43e-40, 2.23e-35] — the extreme significance is robust.

An epsilon-squared of 0.883 is exceptionally large by the standards of behavioral science (conventional "large" threshold is ε² ≥ 0.14). It indicates that ~88% of the variance in LC_winrate across these 223 models is explained by capability quartile membership — the remaining 12% reflects within-quartile heterogeneity.

The monotonic ordering (Q1 < Q2 < Q3 < Q4) is fully confirmed, with no inversions.

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| KW p-value | 2.63e-42 | < 0.05 | **PASS** |
| ε² (effect size) | 0.883 | — (large > 0.14) | **LARGE** |
| Dunn Q1 vs Q4 p | 1.04e-38 | < 0.05 | **PASS** |
| Monotonic ordering | True | Required | **CONFIRMED** |

## 5.5 RQ5: Alignment Gap Δ and the DV Choice Lesson (H-M3)

For comparison, we apply the same Kruskal-Wallis analysis to Δ = LC_winrate − win_rate:

> **KW H = 22.19, p = 5.97e-05, ε² = 0.088 (medium); Dunn Q1 vs Q4 p = 1.0 (n.s.)**

The KW test on Δ is significant (gate criterion met), but the effect size is 10× smaller than the LC_winrate-based analysis: ε² = 0.088 vs 0.883. Moreover, the Dunn Q1 vs Q4 comparison is non-significant after Bonferroni correction (p = 1.0), and the quartile medians are non-monotonic: Q1 = 2.19, Q2 = 2.96, Q3 = 5.43, Q4 = 0.91. Q4 (highest capability) has the *smallest* median Δ — roughly consistent with the hypothesis — but Q3 (second highest) has the *largest* Δ, breaking the expected monotonic gradient.

Figure 10 shows the Δ boxplot by quartile. Figure 12 shows the effect size comparison (ε² = 0.088 vs 0.883), with the 10× gap making the methodological lesson visually clear.

**Why Δ as DV attenuates the effect**: Δ = LC_winrate − win_rate contains −win_rate as a component. When models are grouped by win_rate quartiles, the Δ values are partially composed of the grouping variable itself. Spearman(win_rate, Δ) = −0.050 (p = 0.455) — non-significant bivariate correlation due to this mathematical dependency. This self-referential structure adds noise that attenuates the Kruskal-Wallis effect size. LC_winrate as DV avoids this issue entirely.

| DV | KW H | KW p | ε² | Monotonic | Dunn Q1 vs Q4 |
|----|------|------|----|-----------|----------------|
| LC_winrate (H-C1) | 196.32 | 2.63e-42 | 0.883 | ✓ Yes | p = 1.04e-38 |
| Δ (H-M3) | 22.19 | 5.97e-05 | 0.088 | ✗ No | p = 1.0 (n.s.) |

The comparative analysis establishes a concrete methodological lesson: for testing capability-alignment relationships at the quartile level, LC_winrate is the appropriate primary dependent variable.

## 5.6 Summary

All five sub-hypotheses passed their pre-registered gates:

| Hypothesis | Gate Type | Gate Result | Key Metric |
|------------|-----------|-------------|------------|
| H-E1 | MUST_WORK | **PASS** | r_partial = 0.985 >> 0.15 |
| H-M1 | MUST_WORK | **PASS** | \|β_win\| = 21.34 >> \|β_len\| = 4.37 |
| H-M2 | SHOULD_WORK | **PASS** | delta = 0.011 < 0.02 |
| H-M3 | SHOULD_WORK | **PASS** | KW p = 5.97e-05 < 0.05 |
| H-C1 | SHOULD_WORK | **PASS** | KW p = 2.63e-42, Dunn p = 1.04e-38 |

The aggregate picture is: capability independently predicts LC preference with near-perfect partial correlation (0.985), dominates verbosity as a predictor by ~5:1, is methodologically robust to the estimation procedure, and produces monotonic quartile ordering with large effect size (ε² = 0.883). The alignment gap Δ shows a secondary capability-modulated pattern (medium effect) that is attenuated by the mathematical composition structure.
