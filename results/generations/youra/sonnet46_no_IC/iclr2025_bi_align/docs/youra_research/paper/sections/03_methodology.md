# 3. Methodology

Building on our observation that the capability-LC alignment question is inherently a partial correlation problem, we design a multi-layer statistical analysis that establishes existence (P1), mechanism (P2), and population-level confirmation (P3) of the relationship.

## 3.1 Dataset

We use the publicly available AlpacaEval 2.0 leaderboard CSV (accessed August 2026), which contains pairwise preference evaluation results for 223 diverse LLMs compared against a GPT-4o reference model on 805 instruction-following prompts. The three variables of interest are:

- **win_rate**: Fraction of pairwise comparisons where human annotators prefer the model over GPT-4o (range: ≈3–80%)
- **length_controlled_winrate (LC_winrate)**: Win rate after GLM-based length debiasing [Dubois et al., 2024] (range: ≈2–95%)  
- **avg_length**: Mean response token count per model (range: ≈400–2200 tokens)

All 223 rows in the loaded CSV have complete data; no imputation was required.

**Verbosity Separability Check**: Before analysis, we verify that win_rate and avg_length are separable (not multicollinear) by computing the Variance Inflation Factor (VIF). VIF = 1.764 for both variables (well below the threshold of 5), confirming that standardized OLS coefficients and partial correlations are interpretable. Figure 4 shows the VIF diagnostic.

## 3.2 Primary Analysis: Partial Correlation (H-E1)

**Design Rationale**: We seek ρ(win_rate, LC_winrate | avg_length) — the Spearman partial correlation between capability and LC preference after controlling for verbosity. This is the appropriate estimand because it removes the confounding effect of the moderate capability-verbosity co-variance (ρ(win_rate, avg_length) ≈ 0.63).

**Implementation**:
- Library: `pingouin v0.5+` — `partial_corr(method='spearman')`
- Covariate: avg_length
- Significance threshold: α = 0.05 (two-tailed)
- Pre-registered threshold: |r_partial| ≥ 0.15

**Robustness via Bootstrap**: We compute bootstrap 95% confidence intervals for the partial correlation via 1000 resamples with replacement (random_state = 42), using `pingouin`'s bootstrapped CI method. This provides a stable estimate of precision for the extreme r_partial value.

## 3.3 Mechanism Analysis: Standardized OLS (H-M1)

**Design Rationale**: If capability dominates verbosity as a predictor of LC preference, the standardized regression coefficient for win_rate (β_win) should exceed that for avg_length (|β_len|) in the regression LC_winrate ~ win_rate_std + avg_length_std.

**Implementation**:
- Standardization: `sklearn.preprocessing.StandardScaler` applied to all variables before OLS
- Library: `statsmodels.OLS` with full summary statistics
- Dominance criterion: |β_win| > |β_len| (strict inequality)
- Diagnostics: Breusch-Pagan test for heteroscedasticity; R² comparison vs verbosity-only model (LC_winrate ~ avg_length_std)

**Verbosity-Only Baseline**: We fit a restricted model with only avg_length_std as predictor to quantify how much variance capability adds beyond verbosity (R² gain = full R² − verbosity-only R²).

## 3.4 Robustness: FWL Theorem Verification (H-M2)

**Design Rationale**: The Frisch-Waugh-Lovell (FWL) theorem states that for Pearson partial correlation, partial_corr(X, Y | Z) equals the correlation of the OLS residuals of X~Z and Y~Z. We apply this to Spearman correlation as an approximate FWL check.

**Implementation**:
1. Regress win_rate on avg_length (OLS); compute residuals win_rate_resid
2. Regress LC_winrate on avg_length (OLS); compute residuals lc_resid
3. Compute Spearman ρ(win_rate_resid, lc_resid)
4. Compare to Pingouin partial_corr estimate; compute delta = |ρ_Pingouin − ρ_resid|
5. FWL consistency criterion: delta < 0.02

**Rationale for threshold**: FWL holds exactly for Pearson; Spearman introduces approximation error from rank-transform nonlinearity. A delta < 0.02 is within expected approximation error and confirms the partial correlation is not an artifact of the implementation.

## 3.5 Population-Level Confirmation: Kruskal-Wallis + Dunn (H-M3, H-C1)

**Design Rationale**: We test whether the capability-LC relationship manifests at quartile extremes, where capability differences are unambiguous. This non-parametric test avoids normality assumptions and provides an effect size estimate (epsilon-squared) for practical significance.

**Implementation**:
- Quartile assignment: win_rate quartiles (Q1: lowest 25%, Q4: highest 25%)
- Kruskal-Wallis test: `scipy.stats.kruskal` on LC_winrate across Q1–Q4
- Post-hoc: `scikit_posthocs.posthoc_dunn` with Bonferroni correction, Q1 vs Q4 comparison
- Effect size: ε² = (H − k + 1) / (N − k), where k = 4 quartiles
- Bootstrap validation of Dunn p-values: 1000 resamples to confirm CI excludes 0

**Two Dependent Variables**: We conduct this analysis for both LC_winrate (H-C1) and Δ (H-M3) as separate tests, enabling a comparative effect-size analysis that reveals the impact of DV choice on observed effect magnitude.

## 3.6 Sub-Hypothesis Structure

The full verification plan decomposes H-BiAlign-v1 into five sub-hypotheses:

| Hypothesis | Type | Gate | Test |
|------------|------|------|------|
| H-E1 | Existence | MUST_WORK | Partial correlation ρ(win_rate, LC_winrate \| avg_length) > 0.15 |
| H-M1 | Mechanism | MUST_WORK | \|β_win\| > \|β_len\| in standardized OLS |
| H-M2 | Mechanism | SHOULD_WORK | FWL residual ρ consistent with H-E1 (delta < 0.02) |
| H-M3 | Mechanism | SHOULD_WORK | KW on Δ across quartiles, p < 0.05 |
| H-C1 | Condition | SHOULD_WORK | KW on LC_winrate across quartiles, p < 0.05 AND Dunn Q1 vs Q4 p < 0.05 |

All five hypotheses used the same AlpacaEval 2.0 CSV (N=223), with code built on a shared data loader and statistical pipeline. No model training was required — all analyses are statistical tests on the pre-computed leaderboard scores.
