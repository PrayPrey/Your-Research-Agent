# 3. Methodology

## 3.1 Motivation: Why Partial Spearman?

If MMLU functions as a shared scale covariate for alignment benchmarks — because larger models tend to score higher on all metrics simultaneously — then raw Spearman correlations between alignment benchmarks will be inflated by this shared variance. The appropriate correction is partial Spearman rank correlation: compute the rank correlation between two alignment benchmarks while removing the MMLU component from both.

Formally, partial Spearman correlation between X (TruthfulQA) and Y (BBQ) controlling for Z (MMLU) is computed via the inverse of the rank-based correlation matrix Σ:

> partial_rho(X, Y | Z) = −Σ⁻¹_{XY} / √(Σ⁻¹_{XX} · Σ⁻¹_{YY})

We use `pingouin.partial_corr(x='TruthfulQA_MC2', y='BBQ_accuracy', covar=['MMLU'], method='spearman')` (Vallat, 2018), which implements this via the inverse covariance approach and returns exact p-values. This provides a single-number summary of alignment-specific co-movement after scale removal.

The Fisher z difference test then formalizes whether the confound is statistically significant:

> z = (z_raw − z_partial) / √(1/(N−3−1) + 1/(N−3−1))

where z_raw and z_partial are the Fisher z transforms of the respective Spearman estimates. A significant z test (p < 0.05) indicates that MMLU control meaningfully changed the correlation — confirming that scale confounding was present and quantifiable.

## 3.2 Data Assembly

**Data Source.** We use Open LLM Leaderboard v1 (Beeching et al., 2023), a publicly available CSV containing performance scores for approximately 500 open-weight language models. This source provides MMLU aggregate accuracy, TruthfulQA MC2 accuracy, and ARC Challenge normalized accuracy in a single file, enabling exact model-name joins without fuzzy matching.

**BBQ Proxy.** HELM Lite BBQ per-model accuracy (the intended data source) was unavailable in our execution environment: `lighteval/bbq_helm` on HuggingFace is a QA item corpus rather than per-model scores (format mismatch identified in H-E1), and `stanford-crfm/helm-lite` was inaccessible due to DNS restrictions. We substitute ARC Challenge normalized accuracy as a bias proxy for the following reason: ARC measures logical reasoning in a multiple-choice format structurally similar to BBQ; however, it does not measure social bias specifically, and we accordingly qualify all claims about "bias avoidance" as reflecting performance on this proxy. This is a principal limitation discussed in Section 6.

**Fuzzy Join.** Model names across sources were matched using rapidfuzz WRatio similarity (threshold=75) via a fuzzy join procedure (H-E1). A sensitivity sweep across thresholds 65–80 confirmed N=297 complete rows at all tested thresholds, indicating robust matching. The final analysis dataset contains N=296 models with complete TruthfulQA, BBQ-proxy, and MMLU scores after dropping missing values (one model dropped with NaN on TruthfulQA).

**Model Families.** We identified 51 model families by prefix-splitting model names (e.g., "llama-2-7b" and "llama-2-13b" map to family "llama-2"). Thirty families contained at least 3 models. Family labels were used for clustered BCa bootstrap to account for within-family correlation.

## 3.3 MMLU Covariate Verification (H-M1)

Before computing partial correlations, we verify that MMLU is a substantive scale covariate for both alignment benchmarks — a prerequisite for the partial Spearman analysis to be meaningful. We compute Spearman rho and the coefficient of determination R² for both MMLU × TruthfulQA and MMLU × BBQ-proxy, with a gate criterion R² > 0.05 for each pair.

This step corresponds to sub-hypothesis H-M1 in our verification pipeline. The gate result determines whether partial Spearman is necessary: if MMLU explained less than 5% of variance in either alignment benchmark, scale control would be inconsequential.

## 3.4 Partial Spearman + Fisher Z Test (H-M2)

The primary analysis computes:

1. Raw Spearman rho between TruthfulQA and BBQ-proxy (N=296)
2. Partial Spearman rho controlling for MMLU via pingouin 0.6.1 (column name `p_val`, not `p-val`)
3. BCa 95% confidence intervals for both via cluster-bootstrap (B=5000, seed=42, clustered by model family)
4. Fisher z difference test between raw and partial estimates

**Success criterion (pre-registered):** p < 0.05 OR non-overlapping BCa CIs (either criterion sufficient). Both are reported; the study is powered to detect the primary claim with either confirmation.

**Implementation.** Analysis code follows a flat single-file structure: `analyze.py` contains `load_data()`, `compute_correlations()`, `fisher_z_difference()`, and BCa bootstrap functions. The entry point `main.py` orchestrates the pipeline and exits with code 0 on PASS, 0 on publishable null, and 1 on execution error.

## 3.5 Scenario Classification (H-M3)

We pre-register three structural scenarios for the residual partial_rho:

- **Scenario (a):** |partial_rho| < 0.20 — independent constructs (factuality and bias are orthogonal in scale-free space)
- **Scenario (b):** partial_rho > 0.40 — scale-free coherence (factuality and bias co-move even after MMLU control)
- **Scenario (c):** partial_rho < −0.20 — tradeoff (factuality and bias move oppositely after MMLU control)
- **AMBIGUOUS:** partial_rho ∈ (−0.20, +0.40) — grey zone; insufficient N for scenario assignment

**Rationale.** We pre-register AMBIGUOUS as a valid and informative outcome. If partial_rho falls in the grey zone at the available N, this itself constitutes a finding: the residual coupling is neither confidently independent nor confidently coherent, and a larger study is required for resolution. We additionally compute BCa 95% CI for partial_rho; a CI spanning the 0.40 boundary signals insufficient power for scenario assignment.

## 3.6 Robustness Analysis

We perform three robustness checks:

**Threshold sensitivity.** The fuzzy join threshold was swept from 65 to 80; N remained 297 across all tested values, confirming match stability.

**Family-weighted Fisher z.** A family-weighted version of the Fisher z test was computed using model-family means, confirming that the primary result is not driven by within-family replication of similar models.

**Boundary sensitivity (H-M3).** The scenario classification boundary (0.40) was varied; all variants returned AMBIGUOUS, confirming the grey-zone result is robust to boundary choice.

## 3.7 Scope and Limitations

**Study scope:** Observational, cross-sectional, open-weight LLMs from the LLM LB v1 era (approximately 2022–2024). Results characterize cross-model population-level correlation structure; causal claims about training procedures require controlled experiments.

**BBQ proxy limitation:** ARC Challenge measures logical reasoning, not social bias. The TruthfulQA × ARC partial correlation may reflect shared reasoning demands rather than alignment-specific factuality-vs-bias coupling. This limitation is acknowledged explicitly in the results; all claims about "bias avoidance" are qualified accordingly.

**Safety dimension excluded:** HarmBench Table 2 returned N=0 model matches with LLM LB v1 after fuzzy join (threshold=75), due to name format incompatibility (chat vs base variants) and temporal cohort mismatch. The three-benchmark partial Spearman matrix (factuality × bias × safety) could not be computed; this study is limited to two alignment dimensions.
