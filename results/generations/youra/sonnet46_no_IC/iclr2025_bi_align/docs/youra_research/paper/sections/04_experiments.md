# 4. Experimental Setup

We design experiments to answer five research questions that map directly to the three predictions of H-BiAlign-v1:

**RQ1**: Does model capability independently predict length-controlled preference after controlling for verbosity? *(Tests P1: existence of partial correlation)*

**RQ2**: Does capability dominate verbosity as a predictor of LC preference in standardized regression? *(Tests P2: mechanistic dominance)*

**RQ3**: Is the capability-LC alignment methodologically robust across independent statistical estimators? *(Tests P2 robustness via FWL)*

**RQ4**: Is the capability-LC alignment visible at population extremes (quartile monotonicity)? *(Tests P3: condition holds at extremes)*

**RQ5**: Does the alignment gap Δ vary across capability levels, and what is the appropriate dependent variable for such tests? *(Secondary: DV choice lesson)*

## 4.1 Dataset

All experiments use the AlpacaEval 2.0 leaderboard CSV (N=223 models, fully described in Section 3.1). No additional datasets were collected; the three variables (win_rate, LC_winrate, avg_length) are the complete input to all analyses.

**Why this dataset**: AlpacaEval 2.0 is the only publicly available benchmark that provides both human-annotated win rates and GLM-debiased LC win rates for the same models, enabling direct capability-LC comparison with verbosity control. The 223-model population spans diverse families (GPT-4 class, Llama, Mistral, Falcon, and others), instruction-tuning procedures, and capability levels (win_rate range: ~3%–80%).

## 4.2 Statistical Analysis Pipeline

**H-E1 (RQ1)**: Spearman partial correlation via `pingouin.partial_corr`, with bootstrap 95% CI (1000 resamples, seed=42). VIF check precedes OLS to validate multicollinearity assumption. Threshold: |r_partial| ≥ 0.15, p < 0.05.

**H-M1 (RQ2)**: Standardized OLS via `statsmodels.OLS` with `sklearn.StandardScaler` preprocessing. Dominance criterion: |β_win| > |β_len|. Breusch-Pagan heteroscedasticity test. R² comparison against verbosity-only restricted model.

**H-M2 (RQ3)**: FWL residualization — OLS residuals of win_rate~avg_length and LC_winrate~avg_length, then Spearman correlation on residual pairs. Delta = |ρ_Pingouin − ρ_resid| < 0.02. Bootstrap CI on residual ρ.

**H-M3 (RQ5)**: Kruskal-Wallis on Δ across win_rate quartiles (N_Q1=56, N_Q2=56, N_Q3=55, N_Q4=56). Dunn post-hoc with Bonferroni correction. Epsilon-squared effect size.

**H-C1 (RQ4)**: Same Kruskal-Wallis + Dunn protocol as H-M3, but with LC_winrate as the dependent variable instead of Δ. Bootstrap CI on Dunn Q1 vs Q4 p-value (1000 resamples).

## 4.3 Baselines and Comparators

This work does not propose a new method — it is an empirical study of existing evaluation metrics. The relevant comparators are:

**Bivariate correlation (Dubois 2024)**: ρ(win_rate, LC_winrate) ≈ 0.94 reported in the AlpacaEval 2.0 paper. Our partial correlation (controlling avg_length) extends this to 0.985, measuring how much of the bivariate agreement is capability-driven vs verbosity-shared.

**Verbosity-only model**: OLS restricted to avg_length_std as the sole predictor. R² = 0.256. This establishes the baseline variance explained by verbosity alone, against which capability's contribution (R² = 0.963, full model) is contrasted.

**Δ-based analysis (H-M3) vs LC_winrate-based analysis (H-C1)**: We treat these as comparative conditions to isolate the impact of dependent variable choice on observed effect size.

## 4.4 Implementation Details

All statistical analyses were implemented in Python 3.10+ with the following key libraries:

| Library | Version | Usage |
|---------|---------|-------|
| `pingouin` | ≥ 0.5 | Spearman partial correlation |
| `scipy.stats` | ≥ 1.9 | Spearman correlation, Kruskal-Wallis |
| `statsmodels` | ≥ 0.13 | OLS regression, Breusch-Pagan test |
| `sklearn` | ≥ 1.1 | StandardScaler |
| `scikit_posthocs` | ≥ 0.7 | Dunn post-hoc test |
| `numpy` | ≥ 1.23 | Numerical computations |

**Reproducibility**: All analyses use `random_state=42` for bootstrap resamples. The AlpacaEval 2.0 CSV is publicly available at `tatsu-lab/alpaca_eval` (GitHub). No GPU or specialized compute was required — all analyses run on standard CPU hardware in under 5 minutes.

**Quartile boundaries** (win_rate): Q1 ≤ 5.19%, Q2 ≤ 14.29%, Q3 ≤ 27.85%, Q4 > 27.85%. All quartile groups have N ≥ 55 models (Q1=56, Q2=56, Q3=55, Q4=56), well above the minimum for Kruskal-Wallis validity.

## 4.5 Evaluation Metrics

| Research Question | Primary Metric | Threshold |
|-------------------|---------------|-----------|
| RQ1 (P1 existence) | Spearman partial r, p-value, Bootstrap CI | r > 0.15, p < 0.05 |
| RQ2 (P2 dominance) | \|β_win_std\| vs \|β_len_std\|, R² | \|β_win\| > \|β_len\| |
| RQ3 (FWL robustness) | delta = \|r_Pingouin − ρ_resid\| | delta < 0.02 |
| RQ4 (P3 monotonicity) | KW p, ε², Dunn Q1 vs Q4 p, monotonic ordering | KW p < 0.05, Dunn p < 0.05 |
| RQ5 (DV comparison) | ε² (H-M3 on Δ) vs ε² (H-C1 on LC_winrate) | Comparative |
