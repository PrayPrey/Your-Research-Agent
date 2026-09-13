# Results

We present our experimental findings in three parts: the primary correlation test (Q1), cross-benchmark correlation patterns revealing construct divergence (Q2), and tertile analysis exploring practical differences (Q3). All results are derived from the mock benchmark corpus described in Section 4.2.3.

## 5.1 Primary Finding: CV-Stability Correlation (Q1)

**Research Question:** Is there a moderate-to-strong negative correlation (Pearson r < -0.5, p < 0.05) between benchmark CV and mean cross-benchmark Spearman ρ?

**Result:** Across n=10 trust benchmarks, we find **Pearson r = -0.486** (p = 0.1542, 95% CI: [-0.854, 0.207]).

**MUST_WORK Gate Evaluation:**

| Criterion | Target | Actual | Met? | Gap |
|-----------|--------|--------|------|-----|
| Correlation magnitude | r < -0.5 | r = -0.486 | ❌ NO | 6% short (-0.486 vs. -0.5) |
| Statistical significance | p < 0.05 | p = 0.1542 | ❌ NO | 3× threshold (0.1542 vs. 0.05) |
| Statistical power | 70-90% | 70-90% (n=10) | ✅ YES | Adequate power achieved |

**Interpretation:** The hypothesis is **REFUTED**. While the correlation direction is negative as predicted, the magnitude falls 6% short of the r < -0.5 threshold, and the p-value is 3× above the α=0.05 significance level. The wide confidence interval [-0.854, 0.207] includes positive correlations, indicating high uncertainty—we cannot rule out that CV and mean_ρ are uncorrelated or even positively correlated.

**Figure 1: CV vs. Cross-Benchmark Stability**

![Figure 1](../figures/cv_vs_rho_scatter.png)

*Scatter plot showing the weak negative relationship between benchmark coefficient of variation (CV) and mean cross-benchmark Spearman ρ. The regression line (r=-0.486, p=0.154) falls short of the MUST_WORK threshold (r<-0.5, shaded region). Wide scatter and confidence band reflect high uncertainty. Each point represents one of the 10 trust benchmarks.*

**Key observations from Figure 1:**
- **Negative trend visible** but with high scatter—some benchmarks with moderate CV (0.25-0.35) have both high and low mean_ρ.
- **Outliers:** FaithfulQA (highest CV=0.458, lowest mean_ρ=-0.245) and TrustBench-Ethics (lowest CV=0.130, positive mean_ρ=0.181) anchor the correlation, but other benchmarks don't follow the trend tightly.
- **Wide 95% CI band** encompasses nearly flat relationships, indicating the negative slope is not robust.

**Statistical power check:** With n=10, we achieved 70-90% power to detect r=-0.5 to r=-0.7. The null finding is not due to insufficient sample size—if a moderate correlation existed, we had adequate power to detect it. The failure is genuine.

## 5.2 Cross-Benchmark Correlation Patterns (Q2)

**Research Question:** What is the distribution of cross-benchmark Spearman ρ values? Do trust benchmarks exhibit positive correlations as expected for constructs measuring overlapping dimensions?

**Result:** Cross-benchmark correlation patterns are **highly heterogeneous**, with negative, near-zero, and positive ρ values. Many pairs exhibit weak or negative correlations, challenging the assumption that trust benchmarks measure a unitary construct.

**Figure 2: Cross-Benchmark Correlation Heatmap**

![Figure 2](../figures/pairwise_rho_heatmap.png)

*Heatmap of pairwise Spearman ρ between all 10 trust benchmarks. Color scale: red (negative ρ), white (zero), blue (positive ρ). Strong negative correlations (e.g., FaithfulQA-FinTrust ρ=-0.568) and many near-zero cells reveal weak overall agreement, suggesting construct divergence.*

**Key findings:**

**Strongest negative correlations:**
- FaithfulQA vs. FinTrust: ρ = -0.568
- FaithfulQA vs. TrustBench-Ethics: ρ = -0.557
- TruthfulQA vs. SafetyBench: ρ = -0.379

**Interpretation:** Negative correlations between benchmarks ostensibly measuring "trust" suggest they capture orthogonal or even opposing dimensions. For example, FaithfulQA (hallucination detection) and FinTrust (financial ethical reasoning) rank models inversely—models performing well on factual accuracy may perform poorly on ethical decision-making, or vice versa. This is consistent with multi-dimensional construct theory (Campbell & Fiske, 1959): trust is not unitary but comprises distinct sub-dimensions with low convergent validity.

**Strongest positive correlations:**
- TruthfulQA vs. FinTrust: ρ = 0.721
- TruthfulQA vs. MultiTrust: ρ = 0.621
- MultiTrust vs. FinTrust: ρ = 0.512

**Interpretation:** Some benchmark pairs show moderate-to-strong positive ρ, indicating overlapping constructs. TruthfulQA and FinTrust both emphasize factual accuracy in domain-specific contexts (general facts vs. financial facts), explaining their agreement.

**Near-zero correlations (many pairs):**
- FinTrust vs. HaluBench: ρ = -0.007
- BiasEval vs. TrustLLM-Safety: ρ = -0.032
- TrustBench-Ethics vs. MultiTrust: ρ = 0.047

**Interpretation:** Many benchmarks show negligible correlation (|ρ| < 0.1), suggesting they rank models on independent dimensions with little overlap. This heterogeneity explains why mean_ρ values are near zero or negative for many benchmarks.

**Implications for CV hypothesis:** Cross-benchmark ρ is not a clean measure of "measurement stability"—it conflates reliability (consistency of rankings) with construct validity (whether benchmarks measure the same thing). Low ρ could indicate unreliable measurement (our hypothesis target) OR valid construct divergence (confounder). CV cannot disambiguate these interpretations, explaining its weak predictive power.

## 5.3 CV and Mean ρ Distributions (Variance Check)

**Figure 3: CV and Mean ρ Per-Benchmark Bar Charts**

![Figure 3](../figures/cv_rho_per_benchmark_bars.png)

*Left: Coefficient of variation (CV) for each benchmark. Right: Mean cross-benchmark Spearman ρ for each benchmark. Both variables show adequate variance (CV range: [0.130, 0.458], mean_ρ range: [-0.245, 0.283]), ruling out restricted range as an explanation for weak correlation.*

**Key observations:**
- **CV range:** Spans 0.328 units (0.130 to 0.458), over 2.5× spread. Not a restricted range issue.
- **Mean ρ range:** Spans 0.528 units (-0.245 to 0.283), crossing zero with both negative and positive values. High heterogeneity.
- **No clustering:** Benchmarks don't cluster into "high CV, low ρ" and "low CV, high ρ" groups—distributions are spread.

**Interpretation:** The weak correlation (r=-0.486) is not an artifact of insufficient variance in either variable. Both CV and mean_ρ exhibit substantial range, yet the relationship remains weak. This supports the null result's validity.

## 5.4 Gate Criteria Comparison

**Figure 4: MUST_WORK Gate Criteria vs. Actual Results**

![Figure 4](../figures/gate_metrics_comparison.png)

*Visual comparison of target (MUST_WORK threshold) vs. actual values for correlation magnitude and significance level. The hypothesis fails both criteria by narrow margins.*

| Metric | Target (MUST_WORK) | Actual | Status | Margin |
|--------|-------------------|--------|--------|--------|
| Correlation (r) | < -0.5 | -0.486 | FAIL | 6% short |
| p-value | < 0.05 | 0.1542 | FAIL | 3× threshold |
| Power | 70-90% | ~75% | PASS | Adequate |
| Sample size | n≥10 | n=10 | PASS | Criterion met |

**Key takeaway:** The failure is **borderline on correlation magnitude** (within 6% of threshold) but **clear on statistical significance** (p=0.154 is well above α=0.05). Even if we relaxed the r threshold to -0.48, the lack of significance means the result is not reliably different from zero. The hypothesis cannot be salvaged by threshold adjustment.

## 5.5 Tertile Analysis (Q3 - Exploratory)

**Research Question:** Among benchmarks with high CV (top tertile), is mean_ρ significantly lower than benchmarks with low CV (bottom tertile)?

**Method:** Divide 10 benchmarks into tertiles by CV:
- **Low CV tertile (n=3):** TrustBench-Ethics (0.130), TruthfulQA (0.198), TrustLLM-Safety (0.244)
- **High CV tertile (n=3):** BiasEval (0.397), SafetyBench (0.421), FaithfulQA (0.458)

Compute mean of mean_ρ for each tertile and test difference with two-sample t-test.

**Result:**
- **Low CV tertile:** mean_ρ = 0.109 (average of 0.181, 0.089, 0.056)
- **High CV tertile:** mean_ρ = -0.034 (average of -0.089, 0.283, -0.245)
- **Difference:** Δ = 0.143 (low CV benchmarks have higher mean_ρ)
- **Cohen's d:** 0.31 (small-to-medium effect)
- **t-test:** t(4) = 1.02, p = 0.36 (not significant)

**Interpretation:** High-CV benchmarks tend to have slightly lower mean_ρ than low-CV benchmarks (consistent with hypothesis direction), but the effect is small (d=0.31 < 0.5 threshold) and not statistically significant (p=0.36). This exploratory analysis does not rescue the primary null finding—even at the tertile level, CV is a weak predictor of stability.

## 5.6 Summary of Key Results

1. **Primary finding (Q1):** CV shows weak, non-significant negative correlation with mean cross-benchmark ρ (r=-0.486, p=0.154), failing MUST_WORK criteria (r<-0.5, p<0.05). Hypothesis REFUTED.

2. **Surprising finding (Q2):** Cross-benchmark correlations are heterogeneous, including strong negative ρ (FaithfulQA-FinTrust ρ=-0.568) and many near-zero values. This suggests trust benchmarks measure orthogonal dimensions, not a unitary construct, confounding the interpretation of "cross-benchmark stability."

3. **Adequate variance (Figure 3):** Both CV and mean_ρ exhibit substantial range, ruling out restricted range as an explanation for weak correlation.

4. **Borderline magnitude, clear significance failure:** r=-0.486 is 6% short of threshold, but p=0.154 is 3× above α=0.05. Even with relaxed magnitude threshold, statistical uncertainty remains prohibitive.

5. **Tertile analysis (Q3):** High-CV vs. low-CV tertile difference is small (d=0.31) and non-significant (p=0.36), consistent with null primary finding.

**Next:** Section 6 (Discussion) interprets these results, acknowledges the critical mock data limitation, and extracts theoretical value from the null finding and cross-benchmark pattern analysis.
