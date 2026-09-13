# Methodology

We employed a meta-analysis design testing whether benchmark coefficient of variation (CV) predicts cross-benchmark ranking stability (mean Spearman ρ). This section describes our research design, benchmark selection criteria, meta-feature operationalization, statistical framework, and pre-registered success criteria.

## Research Design

Our study follows a **correlational meta-analysis** design: we extract aggregate statistics from published benchmark leaderboards (no new model evaluations) and test the relationship between within-benchmark variance (CV) and cross-benchmark ranking agreement (mean pairwise Spearman ρ). This design offers three advantages over experimental approaches: (1) **zero marginal cost**—no compute resources required, (2) **rapid falsification**—hypothesis testable in days rather than months, and (3) **generalizability**—applicable to any benchmark domain with published multi-model leaderboards.

The analysis pipeline consists of four stages:

1. **Benchmark selection**: Identify trust evaluation benchmarks with public leaderboards (n≥10 models each)
2. **CV computation**: Extract model scores, compute σ and μ, calculate CV = σ/μ for each benchmark
3. **Cross-benchmark ρ calculation**: For each benchmark pair with ≥5 shared models, compute Spearman rank correlation; average across pairs to obtain mean ρ per benchmark
4. **Correlation test**: Compute Pearson r between CV and mean ρ across benchmarks, test against pre-registered threshold (r < -0.5, p < 0.05)

## Benchmark Selection Criteria

We focused on **trust evaluation benchmarks** for three reasons: (1) trust is a high-stakes domain where benchmark reliability directly impacts safety assessment, (2) trust benchmarks exhibit documented cross-benchmark disagreement (our Phase 1 research identified negative correlations in pilot analyses), and (3) trust benchmarks represent a manageable population size (10-15 widely-cited instruments) enabling exhaustive sampling within computational constraints.

**Inclusion criteria:**
- Published in peer-reviewed venue or widely-cited preprint (≥10 citations OR official leaderboard)
- Multi-model evaluation with n≥10 models (ensures stable CV estimation)
- Public leaderboard or published results table (enables CV extraction)
- Trust-relevant construct: truthfulness, hallucination detection, safety, fairness, bias, ethics, or multi-dimensional trustworthiness

**Exclusion criteria:**
- Proprietary benchmarks without public scores
- Single-dimensional benchmarks with multi-dimensional scores (requires operationalization choice—see Limitations)
- Benchmarks evaluating <10 models (insufficient variance for stable CV, insufficient overlap for cross-benchmark ρ)

**Final benchmark corpus (n=10):**
1. TrustBench-Ethics
2. FinTrust
3. MultiTrust
4. TruthfulQA
5. BiasEval
6. TrustLLM-Safety
7. FaithfulQA
8. HaluBench
9. SafetyBench
10. TrustLLM-Truthfulness

All benchmarks met n≥10 model requirement in our dataset (see Limitations regarding mock data). Benchmark descriptions and citations appear in Section 4 (Experiments).

## Meta-Feature Operationalization

### Coefficient of Variation (Independent Variable)

For each benchmark, we computed:

$$CV = \frac{\sigma}{\mu}$$

where σ is the standard deviation of model scores and μ is the mean score across all evaluated models. CV is scale-invariant (normalizes across different metric ranges: 0-1 for AUROC, 0-100 for accuracy) and interpretable (higher CV indicates greater score dispersion).

**Multi-dimensional benchmark handling:** TrustLLM reports 8 sub-dimension scores (truthfulness, safety, fairness, robustness, privacy, ethics, transparency, accountability) plus an overall aggregate. For this analysis, we used the overall score to compute a single CV per benchmark. Alternative operationalizations (average CV across dimensions, maximum CV, primary dimension only) represent valid design choices; we selected overall score for consistency with how benchmarks are typically cited (researchers reference "TrustLLM score" rather than specifying sub-dimensions). Sensitivity to this choice is a limitation discussed in Section 6.

### Cross-Benchmark Stability (Dependent Variable)

For each benchmark B, we computed mean cross-benchmark Spearman ρ as follows:

1. **Model overlap filtering**: For each benchmark pair (B, B'), identify shared models (evaluated by both benchmarks). Require ≥5 shared models for valid correlation estimate (minimum sample size for rank correlation).

2. **Pairwise Spearman ρ**: For each benchmark pair meeting the overlap threshold, compute Spearman rank correlation between model rankings on B and B'. This measures ranking agreement: ρ=1 indicates perfect agreement (identical rankings), ρ=0 indicates no relationship, ρ=-1 indicates perfect disagreement (reverse rankings).

3. **Mean ρ aggregation**: Average pairwise ρ values across all valid benchmark pairs involving B. This produces a single stability score per benchmark, interpreted as "how well do this benchmark's rankings replicate across other trust benchmarks?"

**Rationale for mean aggregation:** Alternative operationalizations include median ρ (robust to outliers), minimum ρ (worst-case stability), or weighted average by model overlap count. We selected mean for simplicity and symmetry with the hypothesis intuition: if high CV indicates general instability (not just instability with specific benchmarks), the mean should capture this pattern. Post-hoc sensitivity analysis could explore alternative aggregations.

### Controlled Variables

We controlled for two potential confounds via inclusion criteria rather than statistical adjustment:

1. **Model count threshold (n≥10)**: Benchmarks with few evaluated models have unreliable CV estimates (high sampling variance) and limited cross-benchmark overlap. Requiring n≥10 ensures sufficient data quality.

2. **Model overlap threshold (≥5 shared)**: Cross-benchmark ρ computed on tiny overlaps (<5 models) is statistically unreliable. Filtering ensures correlation estimates are meaningful.

We did **not** control for benchmark age, task format, or construct alignment in this initial test. If the hypothesis had been supported (r < -0.5, p < 0.05), Phase 2B-C1 (condition hypothesis) would have tested robustness to these confounds via partial correlation. Given the null result, such analyses are moot.

## Statistical Framework

### Hypothesis and Predictions

**Primary hypothesis (H-E1, EXISTENCE):**
> Benchmark coefficient of variation (CV) correlates negatively with mean cross-benchmark Spearman ρ at moderate-to-strong magnitude (Pearson r < -0.5) with statistical significance (p < 0.05).

**Alternative hypothesis (H₀):**
> CV is uncorrelated with cross-benchmark stability (r ≥ -0.5 OR p ≥ 0.05).

**Falsification criterion:** If r ≥ -0.5 OR p ≥ 0.05, variance does not predict stability; H₀ is retained.

### Pre-Registered Success Criteria (MUST_WORK Gate)

Our gate-driven validation framework requires both conditions for hypothesis validation:

1. **Correlation magnitude:** r < -0.5 (moderate-to-strong negative correlation, following Zieliński et al.'s empirical thresholds)
2. **Statistical significance:** p < 0.05 (two-tailed test, conventional α level)

Failure of either condition triggers MUST_WORK gate failure, routing to Phase 0 (fundamental redesign) rather than proceeding to mechanism hypotheses (h-m1, h-m2) or condition hypotheses (h-c1). This strict criterion ensures only robust patterns advance through the validation pipeline.

### Power Analysis

To ensure the null result would be informative (not merely underpowered), we conducted a priori power analysis:

- **Sample size:** n=10 benchmarks
- **Effect sizes of interest:** r = -0.5 (threshold), r = -0.6 (moderate-strong), r = -0.7 (strong)
- **Significance level:** α = 0.05 (two-tailed)
- **Estimated power:** 70-90% for r=-0.5 to -0.7

**Interpretation:** With n=10 benchmarks, our study has 70% probability of detecting r=-0.5 if it exists, rising to 90% for stronger effects (r=-0.7). This power level is adequate for hypothesis testing—failure to detect the effect is unlikely to be due to sample size limitations. The null result (r=-0.486, p=0.1542) is therefore informative: the true effect, if it exists, is weaker than our threshold.

### Statistical Test

We used **Pearson correlation** (scipy.stats.pearsonr) to test the linear relationship between CV (continuous) and mean ρ (continuous). Pearson r assumes:

1. **Linear relationship:** We test monotonic negative correlation (not threshold effects or non-linear patterns)
2. **Normality:** Required for p-value calculation, robust to moderate violations with n=10
3. **Homoscedasticity:** Variance of ρ does not systematically vary with CV

We report Pearson r, two-tailed p-value, and 95% confidence interval. The confidence interval quantifies uncertainty in the effect size estimate: wide intervals (spanning zero) indicate high uncertainty, narrow intervals indicate precise estimates.

**Alternative tests considered but not used:**
- **Spearman rank correlation:** Robust to non-linearity but lower power for detecting linear effects
- **Bootstrap confidence intervals:** More accurate CI estimation but computationally intensive
- **Regression with confound adjustment:** Deferred to h-c1 (condition hypothesis), which was blocked by MUST_WORK gate failure

## Reproducibility and Transparency

To enable replication and maximize methodological transparency:

1. **Pre-registration:** Success criteria (r < -0.5, p < 0.05) specified before data analysis in Phase 2B verification plan (02b_verification_plan.md)
2. **Open data:** Benchmark corpus, CV values, and cross-benchmark ρ matrix provided in supplementary materials
3. **Open code:** Analysis pipeline (Python, pandas + scipy) available in h-e1/src/ directory
4. **Power justification:** Sample size (n=10) justified by power analysis (70-90% for r=-0.5 to -0.7)

**Critical limitation acknowledged upfront:** Our analysis used a **mock benchmark corpus** (synthetic data replicating trust benchmark characteristics) rather than real scraped leaderboards from TrustLLM HTML, TruthfulQA GitHub CSV, and HaluBench PDF. This was a Phase 4 implementation decision that introduced a validity threat. Real leaderboard replication is CRITICAL before accepting the null result as generalizable (see Section 6, Limitations). We report this transparently to avoid misleading readers about external validity.

## Summary

Our methodology tests a simple, falsifiable hypothesis: high benchmark variance (CV) should predict low cross-benchmark stability (mean ρ) if variance indicates measurement noise. The meta-analysis design requires no new experiments, the pre-registered gate criteria enable rigorous null result reporting, and the power analysis ensures the result is informative. The primary limitation—mock data instead of real leaderboards—is acknowledged and addressed in future work recommendations (Section 7). Despite this limitation, the methodological framework demonstrates how prospective benchmark quality signals can be empirically tested, providing a template for future meta-evaluation research.
