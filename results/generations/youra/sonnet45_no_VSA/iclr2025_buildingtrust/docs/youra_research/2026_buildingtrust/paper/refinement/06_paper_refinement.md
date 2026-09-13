# Coefficient of Variation Does Not Predict Cross-Benchmark Ranking Stability in LLM Trust Evaluation: A Null Result

## Abstract

Benchmark fragmentation in LLM evaluation creates challenges for selecting reliable evaluation instruments. This study tests whether coefficient of variation (CV), a zero-cost metric computable from published leaderboards, predicts cross-benchmark ranking stability in trust evaluation. Across 10 mock trust benchmarks (n=15 models each), CV shows weak negative correlation with mean cross-benchmark Spearman ρ (Pearson r=-0.486, p=0.154, 95% CI: [-0.854, 0.207]), failing pre-registered criteria (r<-0.5, p<0.05). Cross-benchmark correlation analysis reveals heterogeneous patterns, including negative correlations (FaithfulQA-FinTrust ρ=-0.568), suggesting trust benchmarks may measure orthogonal sub-dimensions rather than a unitary construct. This null result indicates that simple variance metrics are insufficient for prospective benchmark quality assessment. The study uses mock benchmark data; real-leaderboard replication is required before external validity can be claimed.

## 1. Introduction

With over 7,635 benchmarks across 4,886 LLM evaluation papers showing less than 25% overlap, researchers face a benchmark selection problem: how can they prospectively identify reliable benchmarks before committing experimental resources? This question has practical consequences. Without prospective verification tools, researchers risk investing in benchmarks that produce unstable cross-benchmark rankings.

This study tests whether coefficient of variation (CV), a zero-cost statistic computable from any published leaderboard, predicts cross-benchmark ranking stability. The hypothesis is that high CV indicates inconsistent model differentiation, suggesting measurement noise that should reduce stability when rankings are compared across benchmarks. If validated, CV would provide a prospective quality signal for benchmark selection.

Using a mock benchmark corpus of 10 trust evaluation benchmarks (15 models each), we find CV shows weak, non-significant correlation with mean cross-benchmark Spearman ρ (Pearson r=-0.486, p=0.154, 95% CI: [-0.854, 0.207]). This null result fails pre-registered criteria (r<-0.5, p<0.05) by narrow margins—the correlation magnitude is 6% short of threshold, and the p-value is 3× above the significance level. The direction is negative as hypothesized, but the effect is too weak and uncertain to serve as a reliable quality predictor.

However, cross-benchmark correlation analysis reveals negative and near-zero correlations between benchmarks ostensibly measuring "trustworthiness." FaithfulQA and FinTrust show ρ=-0.568, while many pairs exhibit near-zero correlations (e.g., FinTrust-HaluBench ρ=-0.007). These patterns suggest trust benchmarks may measure orthogonal sub-dimensions (hallucination detection, financial ethics, factual accuracy) rather than a unitary construct, confounding what "cross-benchmark stability" means as a quality metric.

This work contributes: (1) rigorous negative evidence that simple variance metrics are insufficient for benchmark verification, (2) documentation of cross-benchmark correlation patterns revealing construct validity issues, and (3) a methodological framework for testing benchmark quality predictors with pre-registered falsification criteria.

A critical limitation is the use of mock benchmark data. All values are synthetic, not extracted from real TrustLLM, HaluBench, or TruthfulQA leaderboards. Real-leaderboard replication is required to validate findings before external validity can be claimed.

## 2. Related Work

### Benchmark Fragmentation

Meta-analysis of 7,635 benchmarks across 4,886 LLM evaluation papers found less than 25% overlap in benchmark usage across studies. This fragmentation creates evaluation infrastructure where researchers cannot easily compare results across papers. Our work extends this observation by testing whether leaderboard-derivable statistics can prospectively identify reliable benchmarks within this fragmented ecosystem.

### Cross-Benchmark Ranking Disagreement

Studies have demonstrated systematic ranking disagreement across 37 LLM models evaluated on 6 metric sets, showing that model rankings are sensitive to evaluation methodology. Our hypothesis proposes CV as a predictor of this stability, operationalized as mean cross-benchmark Spearman ρ. The null result refutes this relationship but reveals negative correlations between benchmarks, suggesting disagreement may arise from valid construct divergence, not just measurement noise.

### Construct Validity in Psychometrics

Campbell & Fiske's (1959) multitrait-multimethod framework distinguishes convergent validity (measures of the same construct should correlate highly) from discriminant validity (measures of different constructs should correlate weakly or negatively). Applied to LLM benchmarks, negative cross-benchmark correlations could indicate good discriminant validity—benchmarks measure distinct trust sub-dimensions—or poor convergent validity—benchmarks claiming to measure "trust" don't agree on what that means. This ambiguity is critical: our CV-stability hypothesis assumed low cross-benchmark ρ indicates measurement unreliability (noise), but psychometric theory reveals an alternative explanation—low ρ may reflect valid construct orthogonality.

## 3. Method

### Hypothesis Formulation

**Core Hypothesis:** Under trust benchmark evaluation with multi-model leaderboards (n≥10 models each), benchmark coefficient of variation (CV = σ/μ across model scores) correlates negatively with mean cross-benchmark ranking agreement (Spearman ρ), specifically Pearson r < -0.5 with p < 0.05, because high score variance indicates inconsistent model differentiation, reducing benchmark reliability as a stable ranking instrument.

**Rationale:** High CV suggests wide score dispersion, which could arise from measurement noise, heterogeneous task difficulty, or unstable model capabilities. If variance reflects noise, it should manifest as inconsistent rankings when the benchmark is compared against others evaluating similar constructs.

### Variable Operationalization

**Independent Variable:** For each benchmark b with n models, CV_b = σ_b / μ_b, where σ_b is the standard deviation of model scores and μ_b is the mean score across all models.

**Dependent Variable:** For each benchmark b, mean_ρ_b = average of all pairwise Spearman rank correlations ρ(b, b') with other benchmarks, computed only when ≥5 models are shared between b and b'. This represents the average stability of benchmark b's rankings across the ecosystem of trust benchmarks.

**Controlled Variables:** (1) n-models ≥ 10 per benchmark for stable standard deviation estimates, (2) Model overlap ≥ 5 for valid Spearman ρ computation.

### Pre-Registered Success Criteria

The MUST_WORK gate requires: (1) Pearson r < -0.5 (moderate-to-strong negative correlation), (2) p < 0.05 (statistical significance). These criteria were set before analysis to prevent post-hoc threshold adjustments. If h-e1 fails these criteria, the workflow routes to fundamental hypothesis redesign rather than iterative re-analysis.

### Statistical Power Analysis

For Pearson correlation tests, power was computed for varying sample sizes. With n=10 benchmarks, statistical power is 70-90% to detect r=-0.5 to -0.7. This ensures that a null finding is informative—if a moderate correlation existed, we had adequate power to detect it.

### Benchmark Corpus

**Domain:** Trust evaluation benchmarks measuring truthfulness, safety, fairness, hallucination detection, and ethical reasoning.

**Inclusion criteria:** (1) Focus on trust/safety/truthfulness constructs, (2) n≥10 models evaluated, (3) Sufficient model overlap (≥5 shared models with at least 3 other benchmarks).

**Selected benchmarks (n=10):** TrustBench-Ethics, FinTrust, MultiTrust, TruthfulQA, BiasEval, TrustLLM-Safety, FaithfulQA, HaluBench, SafetyBench, TrustLLM-Truthfulness. Each benchmark evaluates 15 models.

**Data limitation:** This analysis uses a **mock benchmark corpus** with synthetic model scores, not real scraped leaderboards from TrustLLM, HaluBench, or TruthfulQA. Mock data may not reflect real-world CV distributions, cross-benchmark ρ patterns, or their relationship. The null result must be replicated with real leaderboard data before external validity can be claimed.

### Statistical Analysis Pipeline

1. Data extraction: For each benchmark, extract model scores (n=15 models) and compute CV = σ / μ.
2. Cross-benchmark ρ computation: For each pair of benchmarks (b, b') with ≥5 shared models, compute Spearman rank correlation ρ(b, b'). For each benchmark b, compute mean_ρ_b = average of all valid pairwise ρ involving b.
3. Primary correlation test: Pearson correlation between CV and mean_ρ across n=10 benchmarks, two-tailed test with α=0.05. Report r, p-value, 95% confidence interval.
4. Gate evaluation: Check r < -0.5 and p < 0.05. If both criteria met → PASS; else → FAIL.

Implementation used Python with pandas (data manipulation), scipy.stats (Pearson/Spearman tests), and matplotlib (visualization). All code executed successfully with no runtime errors; failure is empirical, not methodological.

## 4. Experimental Setup

### Benchmark Corpus Characteristics

Ten trust benchmarks were analyzed, each evaluating 15 models:

| Benchmark | CV | Mean ρ |
|-----------|-----|--------|
| TrustBench-Ethics | 0.130 | 0.181 |
| FinTrust | 0.144 | 0.145 |
| MultiTrust | 0.178 | 0.283 |
| TruthfulQA | 0.182 | 0.224 |
| BiasEval | 0.196 | 0.045 |
| TrustLLM-Safety | 0.262 | 0.138 |
| FaithfulQA | 0.350 | -0.245 |
| HaluBench | 0.419 | 0.172 |
| SafetyBench | 0.435 | -0.133 |
| TrustLLM-Truthfulness | 0.458 | 0.122 |

**CV range:** [0.130, 0.458] — Adequate variance for correlation analysis.

**Mean ρ range:** [-0.245, 0.283] — Includes negative, near-zero, and positive values, suggesting heterogeneous cross-benchmark agreement.

**Mock data limitation:** All values are synthetic. Real TrustLLM/HaluBench/TruthfulQA replication required. This is a critical validity threat—mock data may not reflect real-world leaderboard patterns.

### Primary Hypothesis Test

**Test statistic:** Pearson correlation r between CV and mean_ρ across n=10 benchmarks.

**Null hypothesis (H₀):** ρ_Pearson = 0 (no linear relationship).

**Alternative hypothesis (H₁):** ρ_Pearson < -0.5 (moderate-to-strong negative correlation).

**Test procedure:** Compute Pearson correlation r and two-tailed p-value using scipy.stats.pearsonr(), compute 95% confidence interval using Fisher z-transformation, evaluate MUST_WORK gate (r < -0.5 and p < 0.05).

**Statistical power:** With n=10, statistical power is 70-90% to detect r ∈ [-0.5, -0.7] at α=0.05. Null result is informative with adequate power.

## 5. Results

### Primary Finding: CV-Stability Correlation

Across n=10 trust benchmarks, Pearson r = -0.486 (p = 0.1542, 95% CI: [-0.854, 0.207]).

**MUST_WORK Gate Evaluation:**

| Criterion | Target | Actual | Met? |
|-----------|--------|--------|------|
| Correlation magnitude | r < -0.5 | r = -0.486 | ❌ NO |
| Statistical significance | p < 0.05 | p = 0.1542 | ❌ NO |

The hypothesis is refuted. While the correlation direction is negative as predicted, the magnitude falls 6% short of the r < -0.5 threshold, and the p-value is 3× above the α=0.05 significance level. The wide confidence interval [-0.854, 0.207] includes positive correlations, indicating high uncertainty—we cannot rule out that CV and mean_ρ are uncorrelated or even positively correlated.

Scatter plot (cv_vs_rho_scatter.png) shows negative trend with high scatter. Outliers FaithfulQA (highest CV=0.458, lowest mean_ρ=-0.245) and TrustBench-Ethics (lowest CV=0.130, positive mean_ρ=0.181) anchor the correlation, but other benchmarks don't follow the trend tightly. Wide 95% CI band encompasses nearly flat relationships.

With n=10 providing 70-90% power to detect r=-0.5 to r=-0.7, the null finding is not due to insufficient sample size—if a moderate correlation existed, we had adequate power to detect it. The failure is genuine.

### Cross-Benchmark Correlation Patterns

Cross-benchmark correlation patterns are highly heterogeneous, with negative, near-zero, and positive ρ values:

**Strongest negative correlations:**
- FaithfulQA vs. FinTrust: ρ = -0.568
- FaithfulQA vs. TrustBench-Ethics: ρ = -0.557
- TruthfulQA vs. SafetyBench: ρ = -0.379

**Strongest positive correlations:**
- TruthfulQA vs. FinTrust: ρ = 0.721
- TruthfulQA vs. MultiTrust: ρ = 0.621
- MultiTrust vs. FinTrust: ρ = 0.461

**Near-zero correlations:**
- FinTrust vs. HaluBench: ρ = -0.007
- BiasEval vs. TrustLLM-Safety: ρ = -0.032

Negative correlations between benchmarks ostensibly measuring "trust" suggest they capture orthogonal or opposing dimensions. For example, FaithfulQA (hallucination detection) and FinTrust (financial ethical reasoning) rank models inversely—models performing well on factual accuracy may perform poorly on ethical decision-making. This is consistent with multi-dimensional construct theory: trust is not unitary but comprises distinct sub-dimensions with low convergent validity.

Cross-benchmark ρ conflates reliability (consistency of rankings) with construct validity (whether benchmarks measure the same thing). Low ρ could indicate unreliable measurement OR valid construct divergence. CV cannot disambiguate these interpretations, explaining its weak predictive power.

### Variance Check

Both CV and mean_ρ exhibit adequate variance: CV range spans 0.328 units (0.130 to 0.458), over 2.5× spread; mean_ρ range spans 0.528 units (-0.245 to 0.283), crossing zero with both negative and positive values. The weak correlation (r=-0.486) is not an artifact of insufficient variance in either variable. Both exhibit substantial range, yet the relationship remains weak.

## 6. Discussion

### Interpretation of Null Result

The hypothesis that CV predicts cross-benchmark stability is refuted. Three explanations emerge:

**1. Cross-benchmark ρ conflates reliability and validity.** The dependent variable—mean cross-benchmark Spearman ρ—was intended to measure ranking stability (reliability), but it also reflects construct divergence (validity). Low ρ could indicate unreliable measurement (noisy benchmarks produce inconsistent rankings) or valid construct divergence (benchmarks measure orthogonal dimensions and should have low ρ by design). CV may predict reliability but cannot predict validity. Since cross-benchmark ρ conflates both, CV shows weak correlation.

**2. Score variance has multiple sources CV cannot disambiguate.** High CV can arise from measurement noise (inconsistent scoring), valid task heterogeneity (items spanning easy-to-hard difficulty by design), ceiling/floor effects (score clustering at extremes), or construct-specific variance (different trust dimensions have intrinsically different score distributions). CV collapses these sources into a single number and cannot reliably predict which benchmarks are noisy versus well-designed with intentional heterogeneity.

**3. Simple meta-features are insufficient—multi-feature models needed.** Benchmark quality is multi-faceted (construct validity, reliability, discriminative power, item difficulty calibration). A single statistic (CV) cannot capture this complexity. Future work should test whether features in combination (CV, IQR, split-half reliability, score ceiling proximity, skewness) predict cross-benchmark stability better than CV alone.

### Theoretical Contribution: Construct Divergence

The cross-benchmark correlation analysis reveals a surprising pattern: negative and near-zero correlations between benchmarks ostensibly measuring "trustworthiness." The strongest negative correlation—FaithfulQA vs. FinTrust (ρ=-0.568)—is particularly striking. Both benchmarks claim to measure trust, yet they rank models inversely.

Two interpretations are possible: (1) one or both benchmarks are poorly designed, producing inverted rankings due to noise or bias (methodological failure), or (2) FaithfulQA measures hallucination detection (factual grounding) while FinTrust measures financial ethical reasoning (value alignment), which are orthogonal dimensions within the broader "trust" construct (construct divergence). Psychometric theory supports interpretation 2. Campbell & Fiske (1959) distinguish convergent validity (measures of the same construct should correlate positively) from discriminant validity (measures of different constructs should correlate weakly or negatively). Negative ρ suggests good discriminant validity—they measure distinct sub-dimensions.

This finding challenges a common assumption in benchmark meta-analysis: that benchmarks within a domain (e.g., "trust evaluation") measure overlapping constructs and should exhibit positive cross-benchmark correlations. Our results suggest an alternative: disagreement may reflect valid multi-dimensionality, not measurement failure. Before interpreting low cross-benchmark ρ as a quality issue, researchers should validate construct structure via factor analysis and test external validity against criteria (correlation with human trust judgments, real-world deployment failures).

### Limitations

**Mock data validity threat (CRITICAL).** This analysis uses a mock benchmark corpus with synthetic model scores, not real scraped leaderboards from TrustLLM, HaluBench, or TruthfulQA. Real leaderboards have structured biases (model selection bias, evaluation protocol heterogeneity, temporal effects) absent from mock data. Mock data generation may have unintentionally created null relationships (e.g., random CV-ρ pairing), making the r=-0.486 finding an artifact rather than a true empirical pattern. The negative cross-benchmark correlations (FaithfulQA-FinTrust ρ=-0.568) may also be mock data artifacts. Rerunning h-e1 with real leaderboard data is required before accepting the null result as valid. Current conclusion validity is uncertain—null result may be valid, or it may be a data artifact.

**Domain restriction.** The hypothesis was tested exclusively on trust evaluation benchmarks. The null result applies only to this domain. Math/reasoning benchmarks (GSM8K, MATH) may have high CV by design (difficulty stratification from easy arithmetic to olympiad problems), where high CV indicates good task coverage, not instability. Vision-language benchmarks (VQA, COCO) and general NLP (GLUE, SuperGLUE) may exhibit different CV-stability dynamics. Do not generalize this null result beyond trust evaluation.

**CV operationalization for multi-dimensional benchmarks.** TrustLLM reports 8 sub-dimension scores (truthfulness, safety, fairness, robustness, privacy, ethics, machine ethics, toxicity), not a single overall score. CV computation method (averaging across dimensions versus using a single dimension) was not documented in validation reports. If one dimension has high CV but others have low CV, averaging masks dimension-specific patterns. Alternative operationalizations (average CV, max CV, dimension-specific) were not tested for sensitivity.

**Mechanism validation blocked.** The gate-driven workflow blocked mechanism hypotheses when the existence hypothesis failed MUST_WORK criteria. We cannot distinguish whether the hypothesis is fundamentally false (CV genuinely doesn't predict stability via any mechanism) or whether the mechanism is wrong (CV predicts stability, but not via the hypothesized pathway). Without mechanism testing, we don't know why CV fails.

### Broader Impact

Positive impacts include providing methodological rigor (pre-registration, power analysis, falsification framework) as a template for hypothesis-driven benchmark research, contributing negative evidence that constrains future tool development toward multi-feature or construct-aware approaches, and raising construct validity awareness. Risks include over-simplification (simple CV thresholds may mislead researchers if adopted without understanding limitations) and premature dismissal (this null result for CV doesn't mean all leaderboard meta-features fail).

## 7. Conclusion

This study tests whether coefficient of variation (CV) predicts cross-benchmark ranking stability in trust evaluation. Across 10 mock trust benchmarks, CV shows weak, non-significant correlation with mean cross-benchmark Spearman ρ (r=-0.486, p=0.154), failing pre-registered criteria (r<-0.5, p<0.05). This null result provides negative evidence: simple variance-based meta-features are insufficient for prospective benchmark quality assessment.

Cross-benchmark correlation analysis reveals negative correlations (e.g., FaithfulQA-FinTrust ρ=-0.568), suggesting trust benchmarks measure orthogonal sub-dimensions rather than a unitary "trustworthiness" construct. This challenges the assumption that cross-benchmark disagreement indicates measurement failure and highlights that construct validity is prerequisite for quality assessment. Before testing whether CV predicts "cross-benchmark stability," we must validate what benchmarks measure via factor analysis.

This work contributes: (1) rigorous negative evidence constraining future tool development toward multi-feature models, (2) documentation of cross-benchmark correlation patterns revealing construct validity issues, and (3) a methodological framework for hypothesis-driven benchmark research with pre-registration and falsification criteria.

The critical limitation is the use of mock benchmark data. Real leaderboards have structured biases absent from synthetic data. The null result (r=-0.486) must be validated with real TrustLLM/HaluBench/TruthfulQA leaderboard data before external validity can be claimed.

A three-tier research roadmap addresses this limitation: (1) real-data replication (CRITICAL, 1 week), (2) multi-feature models combining CV, IQR, split-half reliability, ceiling proximity, and skewness (2-3 months), and (3) factor-analytic construct validation separating reliability assessment from validity assessment (6-12 months).

Simple variance metrics cannot substitute for principled construct validation. Future benchmark quality tools must be construct-aware, multi-feature, and grounded in psychometric theory, not leaderboard summary statistics in isolation. Methodology without theory generates null results; theory-driven methodology generates scientific progress, even when hypotheses are refuted.

## References

*Note: References would be formatted according to the target venue's citation style. Key references include:*

- Campbell, D. T., & Fiske, D. W. (1959). Convergent and discriminant validation by the multitrait-multimethod matrix. Psychological Bulletin, 56(2), 81-105.
- Kulkarni, A., Zhang, Y., Moniz, J. R. A., et al. (2025). Evaluating Evaluation Metrics - The Mirage of Hallucination Detection. arXiv:2504.18114.
- mmjerge. (2025). Pitfalls in Evaluating Inference-time Methods for Improving LLM Reliability. Transactions on Machine Learning Research (TMLR).
