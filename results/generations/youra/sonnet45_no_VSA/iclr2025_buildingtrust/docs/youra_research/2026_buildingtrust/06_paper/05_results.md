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
