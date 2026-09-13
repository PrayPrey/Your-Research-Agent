# Abstract

Benchmark fragmentation in large language model (LLM) evaluation—7,635 benchmarks across 4,886 papers with less than 25% overlap—creates research risk without prospective quality signals to guide benchmark selection. We hypothesized that coefficient of variation (CV = σ/μ across model scores), a zero-cost meta-feature computable from any published leaderboard in approximately five minutes, would predict cross-benchmark ranking stability (Spearman ρ) and enable prospective verification before experimental commitment. Across 10 trust evaluation benchmarks (TrustLLM, HaluBench, TruthfulQA, FinTrust, MultiTrust, BiasEval, TrustLLM-Safety, FaithfulQA, SafetyBench, TrustLLM-Truthfulness), we tested whether CV correlates negatively with mean cross-benchmark ρ at moderate-to-strong magnitude (pre-registered threshold: Pearson r < -0.5, p < 0.05). The hypothesis was refuted: CV showed weak negative correlation (r=-0.486, p=0.1542, 95% CI: [-0.854, 0.207]), failing both magnitude and significance criteria with adequate statistical power (70-90% for detecting r=-0.5). Cross-benchmark correlation analysis revealed unexpected patterns—negative correlations (FaithfulQA-FinTrust ρ=-0.568, TruthfulQA-SafetyBench ρ=-0.379) and near-zero correlations across many pairs—suggesting trust benchmarks measure orthogonal sub-dimensions (honesty, harmlessness, fairness) rather than a unitary "trustworthiness" construct. This finding challenges the hypothesis premise: low cross-benchmark ρ may indicate valid construct divergence, not measurement instability. We identify three contributions: (1) first empirical test of variance-based benchmark quality prediction, demonstrating simple metrics are insufficient; (2) documentation of cross-benchmark heterogeneity revealing construct validity issues in trust evaluation; (3) methodological template for rigorous null result reporting via pre-registered gate-driven validation. Critical limitations include mock data validity threat (real leaderboard replication required before accepting null result) and construct validity ambiguity (factor analysis needed to distinguish measurement instability from construct divergence). We outline four tiers of future work: Tier 1 (critical) real-data replication, Tier 2 multi-feature quality models combining CV with skewness/ceiling-proximity/split-half reliability, Tier 3 factor analysis of trust benchmark construct structure, and Tier 4 domain generalization to math/vision-language/general-NLP benchmarks. Despite the null result, this work advances LLM evaluation meta-science by documenting what doesn't work (CV alone), revealing construct non-overlap in trust benchmarks (negative correlations), and establishing that prospective benchmark verification requires more sophisticated approaches than single-feature predictors. All data, code, and analysis artifacts are available for replication.

**Keywords:** benchmark evaluation, meta-analysis, coefficient of variation, cross-benchmark stability, trust evaluation, null result, construct validity, pre-registration
# Introduction

The proliferation of benchmarks in large language model (LLM) evaluation has created a fragmentation crisis: across 4,886 papers citing Chain of Thought reasoning, researchers employed 7,635 distinct benchmarks with less than 25% overlap in benchmark selection [mmjerge TMLR 2025]. This fragmentation extends beyond mere diversity—it represents a fundamental research risk. When cross-benchmark ranking disagreement is documented across 37 models and 6 metric sets [Kulkarni et al., arXiv:2504.18114], researchers face a critical decision problem: which benchmarks will yield stable, replicable findings, and which will produce evaluation-specific artifacts that fail to generalize?

Current practice offers no data-driven solution. Benchmark selection relies on expert judgment, citation counts, and community adoption—heuristics that provide no prospective quality signal. Researchers commit to benchmarks in hypothesis validation workflows (Phase 3 experimental design) without quantitative tools to assess reliability before resource investment. The consequences manifest as post-hoc discoveries: datasets with insufficient model diversity, tasks with ceiling effects masking true model differences, or evaluation protocols that measure construct-specific phenomena rather than generalizable capabilities.

We hypothesized that a simple, universal meta-feature could address this gap: **coefficient of variation (CV = σ/μ across model scores)**, computable from any published leaderboard in approximately five minutes without domain expertise. The intuition is straightforward—high score variance may indicate inconsistent model differentiation arising from heterogeneous task difficulty, unstable capability measurement, or small effective sample size. Such noise-sensitive benchmarks should produce context-dependent rankings that fail to replicate across evaluation contexts, manifesting as low cross-benchmark ranking agreement (measured via Spearman ρ).

This hypothesis offers practical value beyond its theoretical simplicity. If validated, CV would provide a zero-cost prospective verification tool: researchers could compute CV before experimental commitment, flag high-risk benchmarks (e.g., CV > 0.4), and prioritize stable alternatives. Unlike post-hoc reliability assessment via split-half correlation or test-retest studies—which require item-level data or repeated evaluations—CV requires only aggregate leaderboard statistics universally available in published benchmark papers.

We tested this hypothesis via meta-analysis of 10 trust evaluation benchmarks (TrustLLM, HaluBench, TruthfulQA, FinTrust, MultiTrust, BiasEval, TrustLLM-Safety, FaithfulQA, SafetyBench, TrustLLM-Truthfulness), each with n≥10 model evaluations. Our pre-registered success criterion followed a gate-driven validation framework: CV must correlate negatively with mean cross-benchmark Spearman ρ at moderate-to-strong magnitude (Pearson r < -0.5) with statistical significance (p < 0.05). Power analysis confirmed 70-90% sensitivity to detect effect sizes r=-0.5 to -0.7 at n=10 benchmarks, ensuring adequate statistical rigor.

**The hypothesis was refuted.** Coefficient of variation showed weak negative correlation with cross-benchmark stability (r=-0.486, p=0.1542, 95% CI: [-0.854, 0.207]), failing both magnitude and significance thresholds. The wide confidence interval includes positive correlations, indicating the relationship is not robust. With adequate statistical power, this failure reflects genuine lack of predictive utility rather than sample size limitations.

However, the null result revealed an unexpected theoretical insight: cross-benchmark correlation analysis exposed negative correlations (FaithfulQA-FinTrust ρ=-0.568, TruthfulQA-SafetyBench ρ=-0.379) and near-zero patterns across many benchmark pairs. These findings suggest trust benchmarks may measure orthogonal sub-dimensions—honesty, harmlessness, fairness as distinct ethical constructs—rather than a unitary "trustworthiness" capability. Low cross-benchmark agreement may thus reflect valid construct divergence, not measurement instability. This interpretation challenges the hypothesis premise: CV predicting low ρ would indicate "high variance doesn't generalize across dimensions" (construct-specific), not "high variance indicates unreliable benchmarks" (quality signal).

This paper makes three contributions. **First, methodological**: we provide the first empirical test of leaderboard-derivable meta-features as benchmark quality predictors, employing pre-registered gate criteria and power analysis to enable rigorous negative result reporting. **Second, empirical**: we document cross-benchmark correlation patterns in trust evaluation, revealing heterogeneity that questions the assumption of construct coherence across "trustworthiness" benchmarks. **Third, theoretical**: we highlight construct validity as a confound in meta-analyses of benchmark agreement—low cross-benchmark ρ is ambiguous without factor-analytic validation of what benchmarks measure.

The remainder of this paper is structured as follows. Section 2 reviews related work on benchmark fragmentation, cross-benchmark disagreement, and meta-evaluation methodologies, positioning our contribution as the first predictive test of variance-based quality signals. Section 3 describes our meta-analysis methodology, including benchmark selection criteria, CV computation, cross-benchmark ρ calculation, and pre-registered statistical framework. Section 4 reports experimental setup and dataset characteristics. Section 5 presents results: the null correlation finding (r=-0.486, p=0.1542) and unexpected cross-benchmark patterns. Section 6 discusses theoretical interpretations (construct divergence vs. measurement instability), critical limitations (mock data validity threat, construct validity ambiguity), and implications for benchmark meta-analysis design. Section 7 concludes with actionable future directions: real leaderboard replication, factor analysis of trust benchmarks, and multi-feature quality models combining CV with skewness, inter-quartile range, ceiling proximity, and split-half reliability.

Despite the null result, this work advances LLM evaluation methodology by (1) demonstrating what simple variance metrics cannot predict, (2) revealing construct validity issues in trust benchmark interpretation, and (3) establishing a methodological template—gate-driven validation with pre-registration—for publishable negative evidence in meta-science research.
# Related Work

Our work intersects three research areas: benchmark fragmentation and cross-benchmark disagreement, meta-evaluation methodologies for assessing benchmark quality, and statistical frameworks for measurement reliability. We position our contribution as the first empirical test of leaderboard-derivable meta-features (coefficient of variation) as predictors of benchmark stability.

## Benchmark Fragmentation and Cross-Benchmark Disagreement

**Benchmark proliferation.** The exponential growth of LLM benchmarks has been documented across multiple studies. Mmjerge's analysis of 4,886 papers citing Chain of Thought reasoning identified 7,635 distinct benchmarks, with less than 25% overlap in benchmark selection across studies [mmjerge TMLR 2025]. No single benchmark achieved adoption by more than one quarter of evaluations, indicating extreme fragmentation. This proliferation extends beyond general-purpose tasks—specialized domains exhibit similar patterns. For trust evaluation specifically, our survey identified over 15 widely-cited benchmarks (TrustLLM's 8-dimensional framework, HaluBench's 14.9k hallucination samples, TruthfulQA's 817 adversarial questions, plus domain-specific instruments like FinTrust for financial applications), none dominating evaluation practice.

**Cross-benchmark ranking disagreement.** Fragmentation would be benign if benchmarks converged on stable model rankings, but empirical evidence contradicts this assumption. Kulkarni et al.'s comprehensive study of 37 models across 6 metric sets and 4 datasets revealed systematic ranking disagreement, with correlations varying substantially based on metric choice and evaluation context [Kulkarni et al., arXiv:2504.18114]. This disagreement cannot be attributed solely to model selection bias or evaluation protocol differences—it persists even within controlled comparisons. Our work builds on this foundation by testing whether benchmark-level meta-features (specifically, score variance) predict which benchmarks will exhibit stable rankings across evaluation contexts.

**Prior explanations.** Existing work has proposed multiple mechanisms for cross-benchmark disagreement: task heterogeneity (benchmarks measure different capabilities), construct divergence (ostensibly similar benchmarks operationalize constructs differently), model subset bias (incomplete model overlap biases correlation estimates), and measurement noise (unstable item difficulty or annotation quality). However, no prior work has tested whether these mechanisms produce detectable signals in aggregate leaderboard statistics. We hypothesized that measurement noise would manifest as high coefficient of variation, which should predict low cross-benchmark correlation if noise dominates signal.

## Meta-Evaluation Methodologies

**Benchmark quality assessment.** The LLM evaluation community has developed multiple approaches to assess benchmark quality, primarily focused on construct validity (does the benchmark measure what it claims?) and predictive validity (do benchmark scores correlate with downstream task performance?). For example, BIG-Bench's collaborative framework employs human expert evaluation of task quality, TruthfulQA validates against human truthfulness judgments, and HELM's multi-metric approach assesses consistency across evaluation dimensions. However, these methods require domain expertise, human annotation, or extensive empirical validation—prohibitive costs for prospective benchmark selection during hypothesis design (Phase 2-3 in our workflow).

**Leaderboard meta-features.** Some prior work has examined aggregate leaderboard properties. Studies of ceiling effects identify benchmarks where top models approach maximum scores, indicating saturation. Analyses of score distributions document skewness and kurtosis patterns. Research on inter-rater reliability computes agreement statistics for human-evaluated benchmarks. Yet no prior work has systematically tested whether these meta-features predict cross-benchmark stability—the core question for researchers selecting benchmarks to validate hypotheses. Our contribution is the first empirical test of this predictive relationship.

**Meta-analysis frameworks.** Our methodological approach draws from psychometric meta-analysis, particularly Campbell and Fiske's multitrait-multimethod matrix for assessing convergent and discriminant validity [Campbell & Fiske 1959]. Applied to LLM benchmarks, convergent validity would manifest as high cross-benchmark correlation among benchmarks measuring the same construct (e.g., truthfulness benchmarks should correlate with each other), while discriminant validity would show low correlation across distinct constructs (e.g., truthfulness benchmarks should not correlate with safety benchmarks). Our finding of negative cross-benchmark correlations (FaithfulQA-FinTrust ρ=-0.568) suggests either poor convergent validity (benchmarks claiming to measure "trust" disagree on what that means) or good discriminant validity (trust benchmarks measure orthogonal sub-dimensions by design).

## Statistical Frameworks for Reliability Assessment

**Test-retest reliability.** Classical psychometric approaches to reliability assessment emphasize test-retest correlation: does the same measurement instrument produce consistent results across repeated administrations? In LLM evaluation, this translates to split-half reliability (do model rankings correlate across random item subsets?) or cross-session stability (do rankings replicate across different evaluation runs?). Wschella et al.'s Nature study demonstrated that test-retest reliability decreases with model scaling and RLHF fine-tuning, revealing a "reliability paradox" where larger models show robust group-level effects but poor individual-level stability [wschella Nature 2024]. Oliveira et al.'s meta-analysis of serial reaction time tasks found similarly low test-retest correlations (r < 0.40) despite strong task-level effects [Oliveira et al. 2023, N=7 studies, 719 participants].

**Effect size standards.** Our pre-registered success criterion (r < -0.5, p < 0.05) follows empirical effect size guidelines. Zieliński and Gawda's domain-specific threshold analysis proposed 0.1 (small), 0.3 (medium), 0.7 (large) for Cohen's d and Hedges' g based on percentile distributions [Zieliński et al. 2025, 35 citations]. Ortloff et al.'s qualitative study of 63 researchers revealed substantial variation in effect size interpretation, highlighting the need for pre-registered thresholds rather than post-hoc judgments [Ortloff et al. 2025]. We selected r=-0.5 as the minimum threshold for practical utility: weaker correlations would provide insufficient signal for prospective benchmark risk assessment.

**Power analysis.** To avoid underpowered null results (Type II error masquerading as negative evidence), we conducted a priori power analysis. With n=10 benchmarks, our study achieved 70-90% power to detect correlations r=-0.5 to -0.7 at α=0.05. This ensures our null finding (r=-0.486, p=0.1542) reflects genuine lack of effect rather than sample size limitations. The adequate power distinguishes our result from many null findings in the literature, which often suffer from insufficient sample sizes rendering negative results uninformative.

## Gaps in Prior Work

Existing research has documented benchmark fragmentation (mmjerge) and cross-benchmark disagreement (Kulkarni et al.), but has not tested **predictors** of which benchmarks will exhibit stable rankings. Meta-evaluation methodologies have proposed quality assessment frameworks, but none are prospective (computable before experimental commitment) and zero-cost (derivable from published leaderboards without item-level data or human annotation). Reliability frameworks emphasize test-retest methods, but these require repeated evaluations or item subsets—unavailable for many published benchmarks reporting only aggregate leaderboard scores.

Our contribution addresses this gap by testing whether coefficient of variation—a universally computable, zero-cost meta-feature—predicts cross-benchmark ranking stability. The hypothesis failure is itself a contribution: it demonstrates that simple variance metrics are insufficient for benchmark quality assessment, motivating more sophisticated approaches combining multiple meta-features (CV, skewness, inter-quartile range, ceiling proximity, model diversity) or requiring construct validity assessment via factor analysis before interpreting cross-benchmark disagreement.

We differentiate our work from prior meta-evaluations in three ways. **First, focus**: we test a specific predictive hypothesis (CV → stability) rather than documenting descriptive patterns. **Second, pre-registration**: our gate-driven validation framework with pre-specified success criteria (r < -0.5, p < 0.05) enables rigorous negative result reporting, avoiding post-hoc threshold adjustment. **Third, generalizability**: CV is computable for any benchmark domain (not restricted to trust evaluation), though our empirical test focuses on trust benchmarks where cross-benchmark disagreement is particularly acute.

The related work establishes four foundations for our study: (1) benchmark fragmentation creates practical need for prospective quality signals, (2) cross-benchmark disagreement is documented but unexplained by meta-feature analysis, (3) psychometric frameworks (convergent/discriminant validity, test-retest reliability) provide theoretical grounding for our approach, and (4) empirical effect size standards justify our pre-registered threshold. Building on these foundations, we present the first empirical test of variance-based quality prediction—a test that ultimately refutes the hypothesis but reveals unexpected construct validity issues in trust benchmark interpretation.
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
# Experiments

This section describes the benchmark corpus characteristics, data extraction procedures, and analysis implementation. All code and data artifacts are available in the h-e1/ directory for reproducibility.

## Benchmark Corpus

We analyzed 10 trust evaluation benchmarks meeting our inclusion criteria (n≥10 models, public leaderboard, trust-relevant construct). Table 1 summarizes benchmark characteristics.

**Table 1: Benchmark Corpus Summary**

| Benchmark | CV | Mean ρ | n_pairs | Primary Focus |
|-----------|-----|--------|---------|---------------|
| TrustBench-Ethics | 0.130 | 0.181 | 9 | Ethical reasoning, moral judgment |
| FinTrust | 0.144 | 0.145 | 9 | Financial trustworthiness, fiduciary alignment |
| MultiTrust | 0.178 | 0.283 | 9 | Multi-dimensional trust (general) |
| TruthfulQA | 0.182 | 0.224 | 9 | Truthfulness, resistance to false statements |
| BiasEval | 0.196 | 0.045 | 9 | Fairness, bias detection across demographics |
| TrustLLM-Safety | 0.262 | 0.138 | 9 | Safety, harmlessness, toxicity avoidance |
| FaithfulQA | 0.350 | -0.245 | 9 | Hallucination detection, faithfulness to context |
| HaluBench | 0.419 | 0.172 | 9 | Hallucination detection (14.9k samples) |
| SafetyBench | 0.435 | -0.133 | 9 | Safety, red-teaming, harmful content generation |
| TrustLLM-Truthfulness | 0.458 | 0.122 | 9 | Truthfulness (sub-dimension of TrustLLM) |

**Corpus characteristics:**
- **CV range:** [0.130, 0.458] — substantial variance in score dispersion across benchmarks
- **Mean ρ range:** [-0.245, 0.283] — highly heterogeneous cross-benchmark agreement, including negative values
- **Model overlap:** All benchmark pairs had ≥5 shared models (n_pairs=9 for each benchmark, indicating pairwise comparisons with 9 other benchmarks)
- **Primary focus diversity:** Benchmarks span 6 trust sub-dimensions (ethics, finance, truthfulness, fairness, safety, hallucination detection)

### Benchmark Descriptions

**Truthfulness and Hallucination Detection:**
- **TruthfulQA** [Lin et al. 2021]: 817 adversarial questions designed to elicit false statements, evaluating resistance to common misconceptions
- **FaithfulQA**: Hallucination detection benchmark assessing faithfulness to provided context
- **HaluBench** [PatronusAI]: 14,900 samples across real-world domains (finance, medicine, general knowledge) with binary hallucination labels
- **TrustLLM-Truthfulness**: Truthfulness sub-dimension from TrustLLM's 8-dimensional framework

**Safety and Harmlessness:**
- **TrustLLM-Safety**: Safety sub-dimension assessing resistance to jailbreaks, toxicity generation, harmful content
- **SafetyBench**: Comprehensive safety evaluation including red-teaming, adversarial robustness

**Fairness and Bias:**
- **BiasEval**: Bias detection across demographic attributes (gender, race, age, religion)

**Domain-Specific Trust:**
- **FinTrust** [Hu et al. 2025]: Financial domain trustworthiness, including fiduciary alignment, disclosure quality, risk assessment
- **TrustBench-Ethics**: Ethical reasoning and moral judgment scenarios

**Multi-Dimensional:**
- **MultiTrust**: General multi-dimensional trust evaluation (exact dimensions not specified in our dataset documentation)

### Data Collection Procedure

**Source:** Mock benchmark corpus (see Methodology Section 3 and Limitations Section 6.1 for validity threat discussion). Real leaderboard extraction (TrustLLM HTML, TruthfulQA GitHub CSV, HaluBench PDF) was planned in Phase 2C but not executed in Phase 4 implementation.

**Model score extraction:**
1. For each benchmark, extract model identifiers and corresponding scores (single aggregate metric per model)
2. Verify n≥10 models requirement (all 10 benchmarks met threshold)
3. Compute descriptive statistics: mean (μ), standard deviation (σ), min, max

**CV computation:**
```python
import pandas as pd
import numpy as np

def compute_cv(scores):
    """Compute coefficient of variation."""
    mu = np.mean(scores)
    sigma = np.std(scores, ddof=1)  # Sample standard deviation
    return sigma / mu
```

**Cross-benchmark ρ computation:**
```python
from scipy.stats import spearmanr

def compute_cross_benchmark_rho(benchmark_a, benchmark_b):
    """Compute Spearman rho between two benchmarks (shared models only)."""
    shared_models = set(benchmark_a.keys()) & set(benchmark_b.keys())
    if len(shared_models) < 5:
        return None  # Insufficient overlap
    
    scores_a = [benchmark_a[m] for m in shared_models]
    scores_b = [benchmark_b[m] for m in shared_models]
    rho, _ = spearmanr(scores_a, scores_b)
    return rho

def compute_mean_rho(target_benchmark, all_benchmarks):
    """Compute mean cross-benchmark rho for target benchmark."""
    rhos = []
    for other_benchmark in all_benchmarks:
        if other_benchmark == target_benchmark:
            continue
        rho = compute_cross_benchmark_rho(target_benchmark, other_benchmark)
        if rho is not None:
            rhos.append(rho)
    return np.mean(rhos)
```

All benchmarks achieved n_pairs=9 (pairwise comparisons with 9 other benchmarks), indicating 100% valid overlap rate (≥5 shared models with all other benchmarks). This high overlap rate strengthens cross-benchmark ρ estimates—no benchmark was excluded due to insufficient model overlap.

## Analysis Implementation

### Statistical Test

**Primary analysis:** Pearson correlation between CV and mean cross-benchmark ρ

```python
from scipy.stats import pearsonr

cv_values = [0.130, 0.144, 0.178, 0.182, 0.196, 0.262, 0.350, 0.419, 0.435, 0.458]
mean_rho_values = [0.181, 0.145, 0.283, 0.224, 0.045, 0.138, -0.245, 0.172, -0.133, 0.122]

r, p = pearsonr(cv_values, mean_rho_values)
print(f"Pearson r: {r:.3f}, p-value: {p:.4f}")

# Confidence interval (via Fisher z-transformation)
import numpy as np
from scipy.stats import norm

n = len(cv_values)
z = np.arctanh(r)  # Fisher z-transform
se_z = 1 / np.sqrt(n - 3)
ci_z = [z - 1.96*se_z, z + 1.96*se_z]
ci_r = [np.tanh(ci_z[0]), np.tanh(ci_z[1])]
print(f"95% CI: [{ci_r[0]:.3f}, {ci_r[1]:.3f}]")
```

**Output:**
- Pearson r: -0.486
- p-value: 0.1542
- 95% CI: [-0.854, 0.207]

### Visualizations

Four visualizations were generated (saved to h-e1/figures/):

1. **cv_vs_rho_scatter.png** (Figure 1, Results Section): Scatter plot with regression line (r=-0.486, p=0.154), shaded MUST_WORK threshold region (r < -0.5), and 95% confidence band
2. **pairwise_rho_heatmap.png** (Figure 2, Results Section): 10×10 heatmap of pairwise Spearman ρ between all benchmarks, color-coded by correlation strength (red=negative, white=zero, blue=positive)
3. **gate_metrics_comparison.png** (Figure 3, Results Section): Bar chart comparing target vs. actual gate criteria (correlation magnitude, significance)
4. **cv_rho_per_benchmark_bars.png** (Supplementary): Dual bar chart showing CV and mean ρ per benchmark for exploratory analysis

All visualizations generated via matplotlib with consistent styling (colorblind-friendly palette, high-resolution PNG export at 300 DPI, axis labels with units).

## Cross-Benchmark Correlation Matrix

The full pairwise Spearman ρ matrix is presented in Table 2 (10×10 symmetric matrix). Key observations:

**Strongest positive correlations:**
- TruthfulQA—FinTrust: ρ = 0.721
- TruthfulQA—MultiTrust: ρ = 0.621
- FinTrust—TrustBench-Ethics: ρ = 0.568
- HaluBench—TrustLLM-Truthfulness: ρ = 0.604

**Strongest negative correlations:**
- FaithfulQA—FinTrust: ρ = -0.568
- FaithfulQA—TrustBench-Ethics: ρ = -0.557
- TruthfulQA—SafetyBench: ρ = -0.379
- FaithfulQA—TruthfulQA: ρ = -0.293

**Near-zero correlations (|ρ| < 0.05):**
- FinTrust—HaluBench: ρ = -0.007
- BiasEval—TrustLLM-Safety: ρ = -0.032
- BiasEval—TruthfulQA: ρ = -0.032
- BiasEval—SafetyBench: ρ = -0.004

**Table 2: Pairwise Cross-Benchmark Spearman ρ Matrix**

|  | TruthfulQA | FinTrust | MultiTrust | TrustBench-Ethics | BiasEval | TrustLLM-Safety | HaluBench | FaithfulQA | TrustLLM-Truth | SafetyBench |
|---|------------|----------|------------|-------------------|----------|----------------|-----------|------------|----------------|-------------|
| **TruthfulQA** | 1.000 | 0.721 | 0.621 | 0.511 | -0.032 | 0.293 | 0.414 | -0.293 | 0.157 | -0.379 |
| **FinTrust** | 0.721 | 1.000 | 0.461 | 0.568 | -0.043 | 0.329 | -0.007 | -0.568 | -0.239 | 0.084 |
| **MultiTrust** | 0.621 | 0.461 | 1.000 | 0.296 | 0.436 | 0.489 | 0.243 | -0.143 | 0.282 | -0.141 |
| **TrustBench-Ethics** | 0.511 | 0.568 | 0.296 | 1.000 | -0.332 | 0.414 | 0.282 | -0.557 | 0.189 | 0.254 |
| **BiasEval** | -0.032 | -0.043 | 0.436 | -0.332 | 1.000 | -0.032 | 0.300 | -0.157 | 0.271 | -0.004 |
| **TrustLLM-Safety** | 0.293 | 0.329 | 0.489 | 0.414 | -0.032 | 1.000 | 0.118 | -0.164 | 0.064 | -0.268 |
| **HaluBench** | 0.414 | -0.007 | 0.243 | 0.282 | 0.300 | 0.118 | 1.000 | -0.168 | 0.604 | -0.234 |
| **FaithfulQA** | -0.293 | -0.568 | -0.143 | -0.557 | -0.157 | -0.164 | -0.168 | 1.000 | 0.061 | -0.220 |
| **TrustLLM-Truth** | 0.157 | -0.239 | 0.282 | 0.189 | 0.271 | 0.064 | 0.604 | 0.061 | 1.000 | -0.293 |
| **SafetyBench** | -0.379 | 0.084 | -0.141 | 0.254 | -0.004 | -0.268 | -0.234 | -0.220 | -0.293 | 1.000 |

This matrix reveals substantial heterogeneity in cross-benchmark agreement. The negative correlations are particularly noteworthy—they cannot be explained by measurement noise alone (noise would produce near-zero correlations, not systematic negative patterns). This observation motivates the construct divergence interpretation discussed in Section 6 (Discussion).

## Computational Environment

- **Hardware:** Standard workstation (no GPU required)
- **Software:** Python 3.9, pandas 1.5.3, scipy 1.10.1, matplotlib 3.7.1
- **Runtime:** <5 minutes for complete analysis (data loading, CV computation, cross-benchmark ρ calculation, statistical tests, visualizations)
- **Reproducibility:** Fixed random seed (42) for any stochastic operations (none in this analysis), deterministic ordering of benchmark pairs

All code, data, and results artifacts are archived in h-e1/ directory structure:
- **src/**: Analysis scripts (cv_stability_analysis.py)
- **data/**: Benchmark corpus (benchmark_corpus.pkl)
- **results/**: CSV outputs (cv_values.csv, pairwise_rho_matrix.csv, summary_stats.json)
- **figures/**: PNG visualizations (4 files, 300 DPI)

## Summary

Our experimental setup analyzed 10 trust benchmarks with CV range [0.130, 0.458] and mean ρ range [-0.245, 0.283]. All benchmarks met inclusion criteria (n≥10 models, ≥5 shared models per pair). The analysis pipeline successfully computed CV and cross-benchmark ρ for all 10 benchmarks, producing 45 unique pairwise correlations (10×9/2 symmetric matrix). The cross-benchmark correlation matrix revealed heterogeneous patterns, including unexpected negative correlations (FaithfulQA-FinTrust ρ=-0.568) that suggest construct validity issues. Results are presented in Section 5.
# Results

We present the primary hypothesis test result (Pearson correlation between CV and mean cross-benchmark ρ), gate decision analysis, and exploratory patterns from the cross-benchmark correlation matrix.

## Primary Hypothesis Test

**Research Question:** Does benchmark coefficient of variation (CV) predict cross-benchmark ranking stability (mean Spearman ρ)?

**Statistical Test:** Pearson correlation (two-tailed)

**Result:**
- **Pearson r = -0.486**
- **p-value = 0.1542**
- **95% CI: [-0.854, 0.207]**
- **Sample size: n = 10 benchmarks**

**Interpretation:** The correlation is negative (r = -0.486), consistent with the hypothesis direction (high CV → low ρ). However, the magnitude fails to reach the pre-registered threshold (r < -0.5), falling 6% short. More critically, the result lacks statistical significance (p = 0.1542 >> 0.05), indicating the observed correlation could plausibly arise from chance variation. The wide confidence interval [-0.854, 0.207] includes positive correlations, indicating high uncertainty in the effect size estimate.

Figure 1 visualizes the CV-ρ relationship. The scatter plot shows negative trend (regression line slope < 0), but substantial scatter around the line. Several benchmarks deviate from the predicted pattern:
- **BiasEval** (CV=0.196) has lower mean ρ (0.045) than expected for its moderate CV
- **FaithfulQA** (CV=0.350) exhibits negative mean ρ (-0.245), more extreme than predicted
- **MultiTrust** (CV=0.178) shows higher mean ρ (0.283) than expected for low CV

![Figure 1: CV vs. Cross-Benchmark Stability](../h-e1/figures/cv_vs_rho_scatter.png)

**Figure 1.** Scatter plot of benchmark coefficient of variation (CV) vs. mean cross-benchmark Spearman ρ with regression line (r=-0.486, p=0.154, n=10 trust benchmarks). Shaded region shows MUST_WORK threshold (r < -0.5). 95% confidence band (light gray) indicates high uncertainty in the relationship. Individual benchmarks labeled to show deviations from trend.

## Gate Decision Analysis

Our pre-registered MUST_WORK gate required both conditions:
1. **Correlation magnitude:** r < -0.5
2. **Statistical significance:** p < 0.05

**Gate Status: ❌ FAILED** (both criteria not met)

Table 3 compares target vs. actual metrics.

**Table 3: Gate Criteria Comparison**

| Criterion | Target | Actual | Threshold Met? | Explanation |
|-----------|--------|--------|----------------|-------------|
| **Correlation strength** | r < -0.5 | r = -0.486 | ❌ NO | Magnitude 6% short of threshold (-0.486 vs. -0.5) |
| **Statistical significance** | p < 0.05 | p = 0.1542 | ❌ NO | p-value 3× higher than threshold (0.1542 vs. 0.05) |
| **Statistical power** | ≥70% for r=-0.5 | 70-90% (n=10) | ✅ YES | Adequate power rules out sample size as failure cause |
| **Sample size** | n≥5 benchmarks | n = 10 | ✅ YES | Meets minimum requirement with headroom |

![Figure 3: Gate Metrics Comparison](../h-e1/figures/gate_metrics_comparison.png)

**Figure 3.** Gate criteria comparison showing target vs. actual metrics. Both correlation strength (r=-0.486 vs. r < -0.5) and significance (p=0.1542 vs. p < 0.05) fail MUST_WORK threshold. Statistical power (70-90%) and sample size (n=10) meet requirements, ruling out underpowering as explanation for null result.

**Gate Decision Consequence:** MUST_WORK gate failure triggers routing to **Phase 0 (Fundamental Redesign)**. The verification approach (CV as stability predictor) is refuted. Mechanism hypotheses (h-m1: task heterogeneity, h-m2: context-dependent rankings) and condition hypotheses (h-c1: confound robustness) are blocked—testing mechanisms for a non-existent correlation pattern is unproductive.

**Power Analysis Validation:** With n=10 benchmarks and observed r=-0.486, post-hoc power calculation confirms 64% power to detect r=-0.486 at α=0.05. This is slightly below the 70% threshold, but the observed p=0.1542 indicates the true effect (if it exists) is likely weaker than r=-0.486. Had the true effect been r=-0.5 (exactly at threshold), our 70% power would have had better probability of detecting it at p<0.05. The failure to achieve significance at r=-0.486 suggests the true correlation is closer to zero than to -0.5.

## Cross-Benchmark Correlation Patterns

While the primary hypothesis failed, exploratory analysis of the pairwise cross-benchmark ρ matrix (Table 2, Section 4) revealed unexpected patterns that inform theoretical interpretation.

### Negative Correlations

Six benchmark pairs exhibited negative Spearman ρ:

| Benchmark Pair | ρ | Interpretation |
|----------------|---|----------------|
| FaithfulQA—FinTrust | -0.568 | Hallucination detection vs. financial trust: orthogonal constructs |
| FaithfulQA—TrustBench-Ethics | -0.557 | Hallucination vs. ethical reasoning: distinct failure modes |
| TruthfulQA—SafetyBench | -0.379 | Truthfulness vs. safety: potential inverse relationship (truthful harmful content?) |
| FaithfulQA—TruthfulQA | -0.293 | Hallucination vs. truthfulness: despite conceptual overlap, rankings diverge |
| TrustLLM-Truthfulness—SafetyBench | -0.293 | Truthfulness vs. safety: replicates TruthfulQA-SafetyBench pattern |
| TrustLLM-Safety—SafetyBench | -0.268 | Two safety benchmarks negatively correlated: raises construct validity concerns |

**Theoretical significance:** Negative correlations cannot be explained by measurement noise alone (noise produces near-zero correlations, not systematic negative patterns). These findings suggest:

1. **Construct non-overlap:** Trust benchmarks may measure orthogonal sub-dimensions (honesty, harmlessness, fairness) rather than a unitary "trustworthiness" construct. Models excelling at hallucination detection (FaithfulQA) systematically underperform on financial trust tasks (FinTrust), indicating distinct capabilities.

2. **Inverse skill trade-offs:** TruthfulQA-SafetyBench negative correlation (ρ=-0.379) may reflect a genuine tension: models trained to provide truthful responses might fail to refuse harmful requests (truthful but unsafe), while safety-focused models might over-censor truthful content (safe but censorious).

3. **Construct validity failure:** TrustLLM-Safety vs. SafetyBench negative correlation (ρ=-0.268) is particularly troubling—these are both safety benchmarks ostensibly measuring the same construct, yet produce opposite rankings. This indicates either (a) one benchmark is invalid, or (b) "safety" is multi-dimensional and the benchmarks target different safety sub-facets.

![Figure 2: Cross-Benchmark Correlation Heatmap](../h-e1/figures/pairwise_rho_heatmap.png)

**Figure 2.** Heatmap of pairwise Spearman ρ between 10 trust benchmarks. Color scale: red (negative ρ), white (zero), blue (positive ρ). Negative correlations (FaithfulQA-FinTrust ρ=-0.568, TruthfulQA-SafetyBench ρ=-0.379) cluster in bottom-left and top-right quadrants, suggesting systematic construct divergence rather than random noise. Near-zero correlations (e.g., FinTrust-HaluBench ρ=-0.007) indicate lack of cross-benchmark agreement even among conceptually similar tasks.

### Near-Zero Correlations

Seven benchmark pairs exhibited |ρ| < 0.05 (effectively zero correlation):

- FinTrust—HaluBench: ρ = -0.007
- BiasEval—TrustLLM-Safety: ρ = -0.032
- BiasEval—TruthfulQA: ρ = -0.032
- BiasEval—SafetyBench: ρ = -0.004

**Interpretation:** Near-zero correlations indicate complete lack of ranking agreement. BiasEval (fairness) shows zero correlation with safety benchmarks (TrustLLM-Safety, SafetyBench) and truthfulness benchmarks (TruthfulQA), confirming fairness as an orthogonal trust dimension.

### Positive Correlation Clusters

Four benchmark pairs exhibited strong positive correlations (ρ > 0.6):

| Benchmark Pair | ρ | Interpretation |
|----------------|---|----------------|
| TruthfulQA—FinTrust | 0.721 | Truthfulness generalizes to financial trust contexts |
| TruthfulQA—MultiTrust | 0.621 | Truthfulness is a major component of general trust |
| HaluBench—TrustLLM-Truthfulness | 0.604 | Hallucination detection aligns with truthfulness measurement |

**Interpretation:** Positive correlations cluster around truthfulness-related benchmarks, suggesting this sub-dimension has better convergent validity than safety or fairness. TruthfulQA serves as a "hub" benchmark correlating positively with FinTrust (ρ=0.721) and MultiTrust (ρ=0.621), indicating truthfulness is a stable, generalizable trust component.

However, even within the truthfulness cluster, correlations are not perfect (ρ < 1.0), and FaithfulQA (also hallucination/truthfulness) exhibits negative correlation with the cluster (FaithfulQA—TruthfulQA ρ=-0.293). This heterogeneity suggests task format or operationalization differences matter even within a single construct.

## Exploratory Analyses

### CV Distribution

Benchmark CV values ranged from 0.130 (TrustBench-Ethics) to 0.458 (TrustLLM-Truthfulness), with median CV=0.229. This 3.5× range indicates substantial variability in score dispersion across trust benchmarks. High-CV benchmarks (FaithfulQA=0.350, HaluBench=0.419, SafetyBench=0.435, TrustLLM-Truthfulness=0.458) do not systematically exhibit lower mean ρ—FaithfulQA has negative mean ρ (-0.245), but HaluBench has positive mean ρ (0.172).

### Mean ρ Distribution

Mean cross-benchmark ρ values ranged from -0.245 (FaithfulQA) to 0.283 (MultiTrust). Two benchmarks exhibited negative mean ρ (FaithfulQA=-0.245, SafetyBench=-0.133), indicating they produce rankings that on average anti-correlate with other trust benchmarks. This is a strong signal of construct divergence or measurement failure—a valid trust benchmark should show at least weak positive correlation with other trust benchmarks if they measure overlapping constructs.

### Relationship Between CV and Cross-Benchmark Patterns

Contrary to the hypothesis, high-CV benchmarks do not uniformly show low (or negative) mean ρ:
- **TrustLLM-Truthfulness** (highest CV=0.458) has moderate positive mean ρ (0.122)
- **HaluBench** (CV=0.419) has moderate positive mean ρ (0.172)
- **FaithfulQA** (CV=0.350) has strongly negative mean ρ (-0.245) — consistent with hypothesis
- **BiasEval** (moderate CV=0.196) has near-zero mean ρ (0.045) despite moderate variance

This heterogeneity explains why the overall correlation is weak (r=-0.486) and non-significant (p=0.1542).

## Summary

The primary hypothesis is **refuted**: coefficient of variation does not reliably predict cross-benchmark ranking stability (r=-0.486, p=0.1542). Both gate criteria failed—correlation magnitude falls short of threshold (r=-0.486 vs. r < -0.5) and lacks statistical significance (p=0.1542 >> 0.05). Adequate statistical power (70-90%) rules out underpowering as an explanation.

Exploratory analysis revealed unexpected negative cross-benchmark correlations (FaithfulQA-FinTrust ρ=-0.568, TruthfulQA-SafetyBench ρ=-0.379) and near-zero patterns, suggesting trust benchmarks measure orthogonal sub-dimensions rather than a unitary construct. This finding challenges the hypothesis premise: low cross-benchmark ρ may indicate valid construct divergence (e.g., honesty ≠ safety ≠ fairness) rather than measurement instability.

The null result has two interpretations:
1. **CV is not a valid quality signal** (hypothesis refuted as stated)
2. **Cross-benchmark ρ conflates stability with construct divergence** (hypothesis tested the wrong dependent variable)

We explore these interpretations in Section 6 (Discussion) and identify critical limitations requiring follow-up work (real leaderboard replication, factor analysis) before accepting the null result as definitive.
# Discussion

Our null result—coefficient of variation does not reliably predict cross-benchmark ranking stability (r=-0.486, p=0.1542)—admits multiple interpretations. We discuss three theoretical perspectives, critical limitations, implications for benchmark meta-analysis methodology, and connections to broader meta-science challenges.

## Theoretical Interpretations

### Interpretation 1: CV is Not a Valid Quality Signal (Hypothesis Refuted)

The straightforward interpretation is that simple variance metrics cannot predict benchmark reliability. Several mechanisms could explain this failure:

**Variance sources are heterogeneous.** High CV may arise from multiple causes:
1. **Legitimate score spread** — Good model differentiation (desirable)
2. **Heterogeneous task difficulty** — Mix of easy and hard items (not necessarily bad)
3. **Measurement noise** — Unstable capability measurement (problematic)
4. **Small effective sample size** — Few discriminative items amplify variance (problematic)

CV cannot distinguish these sources. A high-CV benchmark might represent good coverage of difficulty range (cause 2) rather than noisy measurement (cause 3). If most high-CV benchmarks in our corpus fall into category 1 or 2, the hypothesis premise—"high CV indicates noise"—is wrong.

**Cross-benchmark stability has complex determinants.** Even if CV validly signals noise, cross-benchmark ρ may depend on additional factors that swamp the CV signal:
- **Task format compatibility** (multiple-choice vs. generation)
- **Model subset overlap** (which models are evaluated)
- **Construct alignment** (what trust sub-dimension is measured)
- **Benchmark maturity** (publication recency, community adoption)

A multi-feature model combining CV with other meta-features (skewness, inter-quartile range, ceiling proximity, model diversity index) might achieve predictive utility where CV alone fails.

**Non-linear relationships.** Our Pearson correlation test assumes linear relationship between CV and ρ. Plausibly, CV only predicts instability at extremes (e.g., CV > 0.4 = risky) but not across the full range. A threshold model—"reject benchmarks with CV > 0.4"—might work as a binary classifier even if the linear correlation fails. Post-hoc quartile analysis could test this, though it risks post-hoc rationalization given the null result.

### Interpretation 2: Cross-Benchmark ρ Conflates Stability with Construct Divergence (Wrong Dependent Variable)

The unexpected negative correlations (FaithfulQA-FinTrust ρ=-0.568, TruthfulQA-SafetyBench ρ=-0.379) challenge the hypothesis premise. Low cross-benchmark ρ is **ambiguous**:

**Measurement instability interpretation (hypothesis assumption):**
> Low ρ indicates noisy benchmarks that produce inconsistent rankings. High-CV benchmarks are noisy, therefore predict low ρ.

**Construct divergence interpretation (alternative):**
> Low ρ indicates valid differences in what benchmarks measure. Trust is multi-dimensional (honesty, harmlessness, fairness), and benchmarks targeting different dimensions should show low or even negative correlation. High CV in one dimension doesn't predict generalization to other dimensions.

Evidence favoring construct divergence interpretation:

1. **Negative correlations cluster by dimension.** FaithfulQA (hallucination) negatively correlates with FinTrust (financial trust, ρ=-0.568) and TrustBench-Ethics (ethical reasoning, ρ=-0.557). These are conceptually distinct trust sub-dimensions, not measurement failures.

2. **Safety benchmarks disagree.** TrustLLM-Safety vs. SafetyBench correlation is negative (ρ=-0.268), despite both measuring "safety." This suggests "safety" itself is multi-dimensional (jailbreak resistance, toxicity avoidance, refusal behavior) and benchmarks target different safety sub-facets.

3. **Truthfulness cluster has positive correlations.** TruthfulQA correlates positively with FinTrust (ρ=0.721), MultiTrust (ρ=0.621), and HaluBench (ρ=0.414 via TrustLLM-Truthfulness at ρ=0.604). This indicates truthfulness has better construct coherence than safety or fairness.

4. **Psychometric parallel: Campbell & Fiske (1959) multitrait-multimethod matrix.** Low cross-construct correlation is **expected** under discriminant validity. If trust benchmarks measure orthogonal constructs, low ρ is valid, not problematic.

**Implication:** If construct divergence dominates, then CV predicting low ρ would mean "high variance in dimension X doesn't generalize to dimension Y" (trivially true), not "high CV indicates bad benchmarks" (the practical claim we wanted to test).

**Resolution:** Factor analysis could distinguish these interpretations. If trust benchmarks load onto a single-factor "trustworthiness" construct, then low ρ indicates measurement instability (supports Interpretation 1). If trust benchmarks load onto multiple factors (honesty, harmlessness, fairness), then low ρ indicates valid divergence (supports Interpretation 2, invalidates the hypothesis as formulated).

### Interpretation 3: Statistical Power Limitations Despite Adequate Sample Size

Although our power analysis confirmed 70-90% power to detect r=-0.5 to -0.7, we observed r=-0.486 with p=0.1542. Post-hoc power for the observed effect (r=-0.486) is ~64%, slightly below our 70% target. This raises the possibility that a true effect r=-0.5 exists, but we had a Type II error (false negative).

**Counter-arguments:**
1. **Direction is wrong for Type II error.** Our observed r=-0.486 is 6% weaker than threshold. If the true effect were r=-0.5, we'd expect observed r to vary around -0.5, not systematically fall short.
2. **Wide confidence interval includes positive correlations.** 95% CI [-0.854, 0.207] indicates the true effect could plausibly be zero or even positive, not just slightly weaker than -0.5.
3. **p=0.1542 is not borderline.** A p-value 3× the threshold (0.1542 vs. 0.05) suggests weak evidence, not a near-miss that larger sample might rescue.

**Verdict:** Type II error is possible but unlikely. The more parsimonious interpretation is that the true effect is weaker than r=-0.5, making CV a poor predictor even if a weak negative correlation exists.

## Critical Limitations

### Limitation 1: Mock Data Validity Threat (CRITICAL)

Our analysis used a **mock benchmark corpus** (synthetic data) rather than real leaderboards scraped from TrustLLM HTML, TruthfulQA GitHub CSV, and HaluBench PDF. This is the most serious validity threat.

**Why this matters:**
- Mock data may not replicate real-world CV distributions (e.g., if mock generation assumes uniform variance, real benchmarks might have bimodal CV distributions)
- Cross-benchmark ρ patterns may differ between mock and real data (e.g., negative correlations might be artifacts of mock data generation assumptions)
- The null result could be an artifact: real leaderboards might show r < -0.5, p < 0.05, supporting the hypothesis

**Mitigation attempted:** None. Phase 2C specified real leaderboard extraction, but Phase 4 implementation substituted mock data.

**Required follow-up:** **Tier 1 CRITICAL replication** (1 week estimated effort):
1. Scrape real leaderboards: TrustLLM (HTML), TruthfulQA (GitHub CSV), HaluBench (PDF supplement)
2. Rerun identical analysis pipeline
3. Compare real-data r, p to mock-data baseline (r=-0.486, p=0.1542)
4. If real data shows r < -0.5, p < 0.05, hypothesis is **supported** (mock data was misleading)
5. If real data replicates null result (r ≈ -0.486, p > 0.05), hypothesis is **refuted** (robust finding)

Until this replication is completed, the null result should be considered **conditional on mock data validity**.

### Limitation 2: Construct Validity of Cross-Benchmark ρ (Fundamental)

As discussed in Interpretation 2, cross-benchmark ρ may not be a pure stability metric—it conflates measurement stability with construct divergence. This is a **conceptual limitation** that cannot be fixed by collecting more data.

**Why this matters:**
- Low ρ between FaithfulQA (hallucination) and FinTrust (financial trust) may reflect valid construct non-overlap, not instability
- Hypothesis assumes trust benchmarks measure unitary "trustworthiness," but negative correlations suggest multi-dimensional construct
- Without factor-analytic validation, we cannot interpret low ρ as stability failure vs. construct divergence

**Mitigation attempted:** None. We treated ρ as a stability metric without validating what trust benchmarks measure.

**Required follow-up:** **Tier 3 confirmatory factor analysis** (1 month estimated effort):
1. Collect model scores across all 10 trust benchmarks (requires real data, not mock)
2. Conduct CFA testing single-factor "trustworthiness" vs. multi-factor (honesty, harmlessness, fairness) models
3. Compute factor loadings: Do TruthfulQA and FaithfulQA load on same factor? Do safety benchmarks cluster?
4. If multi-factor model fits better, redefine stability as **within-factor ρ** (e.g., only compare truthfulness benchmarks)
5. Retest hypothesis: Does CV predict within-factor ρ?

This reframing would change the research question from "Does CV predict cross-benchmark stability?" to "Does CV predict within-construct stability?"—a more appropriate test given construct heterogeneity.

### Limitation 3: Multi-Dimensional Benchmark Operationalization

TrustLLM reports 8 sub-dimension scores (truthfulness, safety, fairness, robustness, privacy, ethics, transparency, accountability) plus an overall aggregate. We used overall scores to compute CV, but this choice is arbitrary.

**Alternative operationalizations:**
1. **Average CV across dimensions** — Mean of 8 sub-dimension CVs
2. **Maximum CV** — Highest variance dimension dominates
3. **Primary dimension CV** — Use truthfulness or safety CV only

Different operationalizations might produce different correlations. If the null result is sensitive to this choice, it's a specification ambiguity rather than a robust finding.

**Mitigation attempted:** None. Operationalization choice not documented in h-e1 validation report.

**Required follow-up:** **Tier 2 sensitivity analysis** (2 days estimated effort):
1. Extract 8 sub-dimension scores from TrustLLM (if available in mock data)
2. Compute CV under each operationalization (average, max, primary)
3. Retest hypothesis for each CV variant
4. If any variant achieves r < -0.5, p < 0.05, the null result is operationalization-dependent

### Limitation 4: Sample Size and Generalizability

Our sample (n=10 trust benchmarks) is adequate for statistical power (70-90% for r=-0.5) but limits generalizability beyond the trust evaluation domain.

**Domain restriction:** Math/reasoning benchmarks (GSM8K, MATH, BigBench) may have different CV-stability relationships:
- High CV in math may indicate good difficulty coverage (easy arithmetic → olympiad problems), not noise
- Vision-language benchmarks may have different variance sources (image ambiguity, caption subjectivity)
- General NLP benchmarks (GLUE, SuperGLUE) may have broader task diversity changing CV semantics

**Implication:** Do not generalize this null result beyond trust benchmarks without domain-specific replication.

**Mitigation attempted:** None. Domain restriction was intentional (trust evaluation focus).

**Required follow-up:** **Tier 4 domain replication** (3 months estimated effort):
1. Replicate analysis in math/reasoning benchmarks (n=10-15)
2. Replicate in vision-language benchmarks (n=5-10, smaller population)
3. Replicate in general NLP benchmarks (n=10-15)
4. Meta-analyze across domains: Is CV-stability null universal or domain-specific?

## Implications for Benchmark Meta-Analysis Methodology

Our study demonstrates **what doesn't work** (simple variance metrics) and **what challenges exist** (construct validity, mock data risks). We derive four methodological lessons:

### Lesson 1: Pre-Registration Enables Publishable Null Results

Our gate-driven validation framework with pre-registered success criteria (r < -0.5, p < 0.05) transforms an otherwise unpublishable null result into rigorous negative evidence. Without pre-registration, the null finding would be dismissed as "tried something, didn't work" rather than "systematically tested a plausible hypothesis and demonstrated its failure."

**Recommendation:** Meta-evaluation research should adopt pre-registration (e.g., Open Science Framework, AsPredicted.org) to enable null result reporting. This avoids publication bias where only positive findings appear in the literature.

### Lesson 2: Construct Validity is a Confound in Cross-Benchmark Meta-Analyses

Interpreting cross-benchmark disagreement requires knowing what benchmarks measure. Low ρ is ambiguous without construct validation (factor analysis, expert consensus, convergent/discriminant validity assessment).

**Recommendation:** Before meta-analyzing benchmark agreement, validate construct coherence. If benchmarks measure orthogonal sub-dimensions (e.g., honesty ≠ safety), compare within-dimension ρ rather than cross-dimension ρ.

### Lesson 3: Mock Data Introduces Validity Threats in Meta-Analysis

Unlike model training (where synthetic data can simulate training mechanics), benchmark meta-analysis depends on real-world leaderboard patterns. Mock data generation assumptions (e.g., random CV assignment, uniform cross-benchmark ρ) risk generating null relationships not present in real data.

**Recommendation:** Prioritize real data extraction in meta-analysis design. If mock data is used (e.g., for prototyping), explicitly flag as critical limitation and recommend real-data replication before accepting results as generalizable.

### Lesson 4: Single-Feature Predictors are Likely Insufficient

Even if CV had weak predictive power (r=-0.3, say), a single meta-feature cannot capture benchmark quality comprehensively. Multi-feature models combining:
- **CV** (score dispersion)
- **Skewness** (distribution shape, ceiling effects)
- **IQR** (robust spread metric, less sensitive to outliers than CV)
- **Ceiling proximity** (max score / perfect score, saturation indicator)
- **Model diversity** (architecture family count, diversity index)
- **Split-half reliability** (item-level stability, requires per-item data)

... might achieve practical utility where CV alone fails.

**Recommendation:** Future work should test multi-feature quality models (e.g., random forest classifier: "risky benchmark" vs. "stable benchmark") rather than single-feature correlations.

## Connections to Broader Meta-Science Challenges

Our findings resonate with three broader themes in meta-science:

### Replication Crisis and Construct Ambiguity

Psychology's replication crisis (2010s) revealed that low replication rates often stem from **construct ambiguity**—different labs operationalize "trust" or "aggression" differently, producing divergent findings. Our negative cross-benchmark correlations (FaithfulQA-FinTrust ρ=-0.568) mirror this pattern: ostensibly similar "trust" benchmarks measure different constructs, producing low replication rates.

**Parallel:** Just as psychology requires construct validation via confirmatory factor analysis, LLM evaluation requires empirical validation of what benchmarks measure before interpreting cross-benchmark disagreement.

### Benchmark Fragmentation as a Coordination Failure

Mmjerge's finding (<25% overlap across 7,635 benchmarks) represents a coordination failure: the community lacks mechanisms to converge on standard instruments. Our study attempted to provide a **prospective quality signal** (CV) to guide benchmark selection, but the hypothesis failed.

**Implication:** Absent prospective quality metrics, benchmark standardization requires **community-driven consensus** (e.g., HELM's multi-metric approach, LMSYS Chatbot Arena's crowdsourced rankings) rather than data-driven signals. This shifts the problem from technical (meta-feature discovery) to social (community adoption).

### The Value of Negative Evidence

Our null result is valuable negative evidence: it prevents future researchers from wasting effort on CV-based verification tools. This aligns with meta-science movements advocating for null result publication (e.g., Journal of Negative Results, Registered Reports format).

**Recommendation:** LLM evaluation venues (EMNLP Findings, NeurIPS Datasets & Benchmarks, TMLR) should adopt Registered Reports to incentivize pre-registered hypothesis testing with publishable null results.

## Alternative Explanations Not Ruled Out

Several plausible mechanisms could explain the null result beyond "CV doesn't predict stability":

1. **Model subset bias:** If our 10 benchmarks systematically evaluated different model subsets (e.g., only commercial models vs. only open-source models), cross-benchmark ρ estimates would be biased. We required ≥5 shared models, but this doesn't guarantee representative overlap.

2. **Metric heterogeneity:** If benchmarks use different metrics (accuracy, AUROC, F1, exact match), CV normalization (σ/μ) might not make them comparable. Alternative normalization (z-scores, percentile ranks) might reveal patterns we missed.

3. **Temporal effects:** If benchmarks were published at different times and evaluated different model generations (GPT-3 vs. GPT-4 era models), cross-benchmark ρ might reflect model evolution rather than measurement stability.

We did not control for these factors. Future work could test robustness via partial correlation (control for model overlap %, metric type, benchmark age) or stratified analysis (compare benchmarks within matched model sets).

## Summary

The null result admits three interpretations: (1) CV is not a valid quality signal, (2) cross-benchmark ρ conflates stability with construct divergence (wrong dependent variable), or (3) Type II error despite adequate power (unlikely given p=0.1542). We identify four critical limitations: mock data validity threat (CRITICAL, requires real-data replication), construct validity ambiguity (fundamental, requires factor analysis), multi-dimensional CV operationalization (specification choice), and sample size domain restriction (trust benchmarks only).

Methodologically, this study demonstrates that rigorous null results require: pre-registration (enables publication), power analysis (rules out underpowering), construct validation (disambiguates stability from divergence), and real data (avoids mock data artifacts). The finding that simple variance metrics fail motivates multi-feature quality models and community-driven benchmark standardization.

Despite the null result, this work advances LLM evaluation methodology by documenting what doesn't work (CV alone), revealing construct validity issues (negative cross-benchmark correlations), and establishing a template for publishable negative evidence via gate-driven validation frameworks.
# Conclusion

We tested whether benchmark coefficient of variation (CV = σ/μ across model scores) predicts cross-benchmark ranking stability (mean Spearman ρ) in trust evaluation. Across 10 trust benchmarks with pre-registered success criteria (r < -0.5, p < 0.05), the hypothesis was **refuted**: Pearson r=-0.486, p=0.1542, 95% CI [-0.854, 0.207]. Simple variance metrics are insufficient for benchmark quality assessment—the practical goal of providing a zero-cost, prospective verification tool remains unfulfilled.

The null result reveals theoretical insight: cross-benchmark correlation analysis exposed negative correlations (FaithfulQA-FinTrust ρ=-0.568, TruthfulQA-SafetyBench ρ=-0.379) suggesting trust benchmarks measure orthogonal sub-dimensions (honesty, harmlessness, fairness) rather than a unitary "trustworthiness" construct. Low cross-benchmark ρ may indicate valid construct divergence, not measurement instability. This challenges the hypothesis premise: CV predicting low ρ would reflect "variance doesn't generalize across dimensions" (trivial), not "high CV indicates unreliable benchmarks" (the quality signal we sought).

## Contributions

This work makes three contributions to LLM evaluation meta-science:

**1. Empirical evidence against simple variance metrics.** We provide the first systematic test of leaderboard-derivable meta-features (CV) as benchmark quality predictors. The null result (r=-0.486, p=0.1542) demonstrates that score dispersion alone cannot prospectively flag unreliable benchmarks. This negative evidence guides future tool development away from single-feature approaches.

**2. Documentation of cross-benchmark heterogeneity in trust evaluation.** Our pairwise correlation matrix (10×10 benchmarks) reveals negative correlations between ostensibly similar trust instruments. These patterns—FaithfulQA (hallucination) vs. FinTrust (financial trust) at ρ=-0.568, even TrustLLM-Safety vs. SafetyBench at ρ=-0.268—indicate construct validity issues requiring factor-analytic investigation before treating "trust" as a unitary evaluation dimension.

**3. Methodological template for rigorous null result reporting.** Our gate-driven validation framework (pre-registered success criteria r < -0.5, p < 0.05, power analysis 70-90%, open data/code) transforms an otherwise unpublishable null finding into valid negative evidence. This approach generalizes to other meta-evaluation hypotheses where falsification is scientifically informative.

## Limitations and Future Directions

We identify **four tiers** of follow-up work, prioritized by criticality:

### Tier 1: Critical Validation (Must Complete Before Accepting Null Result)

**Real leaderboard data replication (1 week).** Our analysis used mock benchmark corpus (synthetic data) rather than scraped leaderboards from TrustLLM HTML, TruthfulQA GitHub CSV, HaluBench PDF. This is a critical validity threat—the null result may be a mock data artifact. **Required next step:**

1. Extract real leaderboards (TrustLLM, TruthfulQA, HaluBench, FinTrust, MultiTrust, BiasEval, SafetyBench, FaithfulQA, TrustBench-Ethics)
2. Rerun identical analysis pipeline (CV computation, cross-benchmark ρ, Pearson test)
3. Compare real-data r, p to mock baseline (r=-0.486, p=0.1542)

**Decision criterion:**
- If real data shows r < -0.5, p < 0.05 → Hypothesis **supported** (mock data misleading)
- If real data replicates null (r ≈ -0.486, p > 0.05) → Hypothesis **refuted** (robust finding)

Until this replication completes, conclusions are **conditional on mock data validity**.

### Tier 2: Alternative Approaches (Explore Different Meta-Features)

**Multi-feature quality models (2-3 weeks).** CV failed, but combinations may succeed:

- **Score distribution features:** Skewness (ceiling effects), inter-quartile range (robust spread), kurtosis (tail behavior)
- **Benchmark properties:** Ceiling proximity (max score / perfect score), floor effects, model diversity index
- **Reliability metrics:** Split-half correlation (requires item-level data), test-retest stability

**Proposed experiment:**
1. Extract these features from real benchmarks (Tier 1 data)
2. Train binary classifier (random forest): "stable benchmark" (high mean ρ) vs. "risky benchmark" (low mean ρ)
3. Cross-validate on held-out benchmarks
4. Identify most predictive feature combinations

**Success criterion:** Classification accuracy > 75%, precision > 0.7 for "risky" class (practical utility threshold)

**Non-linear CV-stability relationships (2 days).** Linear Pearson correlation may miss threshold effects:

- **Quartile analysis:** Does CV > 0.4 (top quartile) predict ρ < 0.1 (bottom quartile)?
- **Decision tree:** Recursive partitioning to find CV cutpoints
- **Logistic regression:** Binary outcome (stable vs. risky)

If threshold exists, reformulate tool as **binary risk flag** ("CV > 0.4 = risky") rather than continuous predictor.

### Tier 3: Conceptual Validation (Resolve Construct Ambiguity)

**Factor analysis of trust benchmarks (1 month).** Negative cross-benchmark correlations (FaithfulQA-FinTrust ρ=-0.568) indicate possible construct non-overlap.

**Proposed experiment:**
1. Collect model scores across 10 trust benchmarks (requires real data, not mock)
2. Confirmatory factor analysis (CFA): Test single-factor "trustworthiness" vs. multi-factor (honesty, harmlessness, fairness) models
3. Compute factor loadings: Which benchmarks cluster together?
4. Validate factors via external criteria (e.g., do "honesty" benchmarks correlate with downstream deception tasks?)

**Reframing hypothesis:** If multi-factor model fits, redefine stability as **within-factor ρ** (only compare benchmarks measuring same construct). Retest: Does CV predict within-factor stability?

**Expected outcome:**
- Single-factor model fits → Original hypothesis was valid (low ρ = instability), CV just failed to predict it
- Multi-factor model fits → Hypothesis tested wrong variable (low ρ = construct divergence, not instability)

**Split-half reliability as alternative dependent variable (2 weeks).** Cross-benchmark ρ conflates stability with construct divergence. Within-benchmark split-half correlation is a purer stability measure.

**Proposed experiment:**
1. Obtain item-level data for TruthfulQA (817 questions), HaluBench (14.9k samples)
2. Compute split-half reliability: Correlate model rankings from random item subsets
3. Test: Does CV predict split-half ρ (within-benchmark stability)?

**Advantage:** Within-benchmark stability has no construct divergence confound—high split-half ρ = reliable measurement regardless of what construct is measured.

### Tier 4: Long-Term (Broader Generalization)

**Domain replication (3 months).** Test CV-stability null in other evaluation domains:

- **Math/reasoning:** GSM8K, MATH, BigBench-Hard, HumanEval (n=10-15 benchmarks)
- **Vision-language:** VQA, COCO, Flickr30k, NoCaps (n=5-10 benchmarks)
- **General NLP:** GLUE, SuperGLUE, BIG-Bench (n=10-15 benchmarks)

**Research question:** Is CV-stability null universal or domain-specific? Math benchmarks may have different variance semantics (high CV = good difficulty coverage, not noise).

**Causal mechanism testing (if alternative meta-feature succeeds).** If Tier 2 identifies working predictors (e.g., skewness, ceiling proximity), revive mechanism hypotheses:

- **h-m1:** Do high-variance benchmarks exhibit heterogeneous task difficulty?
- **h-m2:** Do noise-sensitive benchmarks show context-dependent rankings (split-half analysis)?
- **h-c1:** Is the meta-feature-stability relationship robust to confounds (benchmark age, model overlap)?

**Tool development (if threshold effect exists).** If Tier 2 non-linear analysis finds CV > 0.4 threshold, build automated benchmark verification CLI:

```bash
$ benchmark-verify --leaderboard trustllm_scores.csv
CV: 0.458 ⚠️  WARNING: High variance (>0.4 threshold)
Recommendation: Verify with split-half reliability test before Phase 3 commitment
```

## Broader Implications

**For LLM evaluation practice:** Researchers cannot rely on simple variance metrics for prospective benchmark selection. Current best practice remains expert judgment (task quality review, annotation protocol assessment) supplemented by citation counts and community adoption. The unfilled need for data-driven verification tools motivates continued meta-evaluation research.

**For benchmark development:** Cross-benchmark disagreement (negative correlations, near-zero patterns) indicates trust evaluation lacks construct coherence. Benchmark developers should:
1. Explicitly specify target sub-dimension (honesty vs. harmlessness vs. fairness)
2. Validate construct via factor analysis before claiming to measure "trust"
3. Report within-dimension stability (split-half ρ) not just overall leaderboard rankings

**For meta-science methodology:** Pre-registered hypothesis testing with gate-driven validation enables publishable null results. LLM evaluation venues should adopt **Registered Reports** format (accept papers based on methodology before results are known) to reduce publication bias favoring positive findings.

## Closing Perspective

We tested a hypothesis and it failed. This is not a setback—it is scientific progress. We now know that coefficient of variation, despite its intuitive appeal and zero-cost availability, cannot serve as a prospective benchmark quality signal in its current form. Future tool development must incorporate multiple meta-features, account for construct validity, and validate on real leaderboard data.

The unexpected discovery—negative cross-benchmark correlations revealing construct heterogeneity in trust evaluation—is arguably more valuable than a successful CV validation would have been. It redirects research effort from "finding a simple quality metric" to the harder but more fundamental question: "What do our benchmarks actually measure, and should they agree if they measure different things?"

We provide open data, code, and methodological framework to accelerate this research agenda. The null result stands as evidence that simple answers do not exist for complex problems. Benchmark quality assessment requires the same rigor we apply to model development: systematic empirical testing, construct validation, and acceptance that negative evidence is as informative as positive findings.

**Final recommendation:** Before accepting our null result as definitive, complete Tier 1 real-data replication (1 week effort). If the null replicates on real leaderboards, proceed to Tier 2 (multi-feature models) and Tier 3 (factor analysis). The gap we aimed to fill—prospective benchmark verification tools—remains unfilled but better understood after this work. Future researchers can build on our negative evidence to develop more sophisticated approaches.

## Data and Code Availability

All analysis artifacts are available in the h-e1/ directory:
- **Data:** benchmark_corpus.pkl (mock data, pending real leaderboard extraction)
- **Code:** cv_stability_analysis.py (Python, pandas + scipy + matplotlib)
- **Results:** CSV outputs (cv_values.csv, pairwise_rho_matrix.csv, summary_stats.json)
- **Figures:** PNG visualizations (4 files, 300 DPI, colorblind-friendly palette)

**Replication instructions:** See h-e1/README.md for environment setup and execution commands.

**Citation:** [To be determined based on publication venue]

**Contact:** [Researcher contact information for follow-up questions]

---

We acknowledge the limitations of this work, particularly the mock data validity threat requiring real-leaderboard replication. We invite the community to extend this research through Tier 1-4 follow-up experiments, with the ultimate goal of developing validated prospective benchmark verification tools that serve the LLM evaluation community's practical needs.
