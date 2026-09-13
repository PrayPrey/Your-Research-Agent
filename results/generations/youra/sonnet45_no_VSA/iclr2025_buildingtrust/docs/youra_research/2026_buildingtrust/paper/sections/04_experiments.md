# Experimental Setup

Our experimental design tests a single, focused question: **Does benchmark coefficient of variation (CV) correlate negatively and moderately-to-strongly with mean cross-benchmark Spearman ρ?** This section describes the benchmark corpus, experimental protocol, and evaluation metrics designed to rigorously falsify or support this hypothesis.

## 4.1 Research Questions

We structure our experimental investigation around three questions aligned with our pre-registered hypotheses:

**Q1 (Primary - Existence Hypothesis h-e1):** Is there a moderate-to-strong negative correlation (Pearson r < -0.5, p < 0.05) between benchmark CV and mean cross-benchmark Spearman ρ across trust evaluation benchmarks?

**Q2 (Secondary - Descriptive):** What is the distribution of cross-benchmark Spearman ρ values across trust benchmarks? Do benchmarks ostensibly measuring the same "trustworthiness" construct exhibit positive correlations, or are there negative/near-zero patterns suggesting construct divergence?

**Q3 (Exploratory - Pattern Analysis):** Among benchmarks with high CV (top tertile), is mean ρ significantly lower than benchmarks with low CV (bottom tertile)? This tests whether the CV-stability relationship, even if below r=-0.5 threshold, manifests as a tertile effect.

**Note:** Q1 is our MUST_WORK gate criterion. Q2 and Q3 are secondary analyses to interpret null results and generate theoretical insights.

## 4.2 Benchmark Corpus

### 4.2.1 Domain: Trust Evaluation

We restrict our analysis to **trust evaluation benchmarks**—instruments designed to assess LLM trustworthiness dimensions including truthfulness, safety, fairness, hallucination detection, and ethical reasoning. This scoping decision reflects:

1. **Hypothesis origin**: Our preliminary work (Phase 0) focused on trust-building in LLMs, making trust benchmarks the natural target domain.
2. **Construct coherence assumption**: We initially hypothesized trust benchmarks measure overlapping constructs (truthfulness, safety), predicting moderate positive cross-benchmark ρ. Our results challenge this assumption (Section 5.2).
3. **Generalizability caveat**: Findings apply to trust evaluation only. Math reasoning (GSM8K, MATH), vision-language (VQA, COCO), and general NLP (GLUE, SuperGLUE) benchmarks may exhibit different CV-stability relationships and are left for future work.

### 4.2.2 Inclusion Criteria

For each benchmark to be included in our corpus:

1. **Domain relevance**: Explicitly measures trust/safety/truthfulness/fairness constructs (not general capabilities like reasoning or world knowledge).
2. **Model coverage**: Evaluates ≥10 distinct LLM models. This threshold ensures:
   - Stable standard deviation estimates for CV computation (σ with n<10 has high variance).
   - Sufficient sample size for rank correlation (Spearman ρ requires ≥5 data points for interpretability; n≥10 provides margin).
3. **Score availability**: Model scores are publicly available or derivable from published leaderboards (TrustLLM HTML tables, TruthfulQA GitHub CSV, HaluBench PDF reports).
4. **Model overlap**: Benchmark shares ≥5 evaluated models with at least 3 other benchmarks in the corpus. This ensures cross-benchmark ρ can be computed for multiple pairs, enabling mean_ρ aggregation.

### 4.2.3 Benchmark Corpus (n=10)

Based on these criteria, we selected 10 trust benchmarks:

| Benchmark | Domain Focus | n_models | CV | Mean ρ | Source |
|-----------|--------------|----------|-----|--------|--------|
| TrustBench-Ethics | Ethical reasoning | 12 | 0.130 | 0.181 | Mock corpus |
| FinTrust | Financial safety | 15 | 0.285 | 0.145 | Mock corpus |
| MultiTrust | Multi-dimensional trust | 18 | 0.312 | -0.123 | Mock corpus |
| TruthfulQA | Factual accuracy | 20 | 0.198 | 0.089 | Mock corpus |
| BiasEval | Fairness / bias detection | 14 | 0.397 | -0.089 | Mock corpus |
| TrustLLM-Safety | Safety violations | 16 | 0.244 | 0.056 | Mock corpus |
| FaithfulQA | Hallucination detection | 11 | 0.458 | -0.245 | Mock corpus |
| HaluBench | Hallucination evaluation | 13 | 0.372 | 0.034 | Mock corpus |
| SafetyBench | Safety adherence | 10 | 0.421 | 0.283 | Mock corpus |
| TrustLLM-Truthfulness | Truthfulness | 19 | 0.289 | 0.112 | Mock corpus |

**Data source caveat:** Values in this table are derived from a **mock benchmark corpus** with synthetic model scores, not real scraped leaderboards. This is a critical limitation discussed in Section 6.1. Real-data replication is required before external validity can be claimed.

**CV range:** [0.130, 0.458] — Adequate variance for correlation analysis. No restricted range issue.

**Mean ρ range:** [-0.245, 0.283] — Includes negative, near-zero, and positive values. Heterogeneity suggests weak overall cross-benchmark agreement, consistent with our null finding.

## 4.3 Experimental Protocol

### 4.3.1 CV Computation

For each benchmark b:

1. Extract model scores for all n models evaluated on benchmark b.
2. Compute mean μ_b and standard deviation σ_b across model scores.
3. Compute CV_b = σ_b / μ_b.

**Multi-dimensional benchmarks (e.g., TrustLLM with 8 sub-dimensions):** Compute CV for each dimension separately, then average CVs across dimensions. This operationalization is acknowledged as a limitation (Section 6.1)—dimension-specific patterns may be masked by averaging.

### 4.3.2 Cross-Benchmark ρ Computation

For each pair of benchmarks (b, b'):

1. Identify shared models: models evaluated by both b and b'.
2. If |shared models| < 5, skip this pair (insufficient sample for stable rank correlation).
3. For shared models, extract scores from both benchmarks.
4. Compute Spearman rank correlation ρ(b, b') between the two score vectors.

For each benchmark b:

1. Collect all valid pairwise ρ values involving b (where ≥5 shared models exist).
2. Compute mean_ρ_b = average of all valid pairwise ρ for benchmark b.

**Rationale for ≥5 shared models threshold:** Spearman correlation with n<5 is highly unstable (single rank swap drastically changes ρ). This conservative threshold filters spurious correlations from disjoint model sets while preserving interpretable pairwise comparisons.

### 4.3.3 Primary Hypothesis Test (h-e1)

**Test statistic:** Pearson correlation r between CV and mean_ρ across n=10 benchmarks.

**Null hypothesis (H₀):** ρ_Pearson = 0 (no linear relationship between CV and mean_ρ).

**Alternative hypothesis (H₁):** ρ_Pearson < -0.5 (moderate-to-strong negative correlation).

**Test procedure:**
1. Compute Pearson correlation r and two-tailed p-value using scipy.stats.pearsonr().
2. Compute 95% confidence interval for r using Fisher z-transformation.
3. Evaluate MUST_WORK gate:
   - **Gate criterion 1:** r < -0.5
   - **Gate criterion 2:** p < 0.05
   - **Decision:** PASS if BOTH criteria met; FAIL otherwise.

**Statistical power:** With n=10, we have 70-90% power to detect r ∈ [-0.5, -0.7] at α=0.05 (Section 3.4). Null result will be informative (adequate power to detect effect if present).

## 4.4 Evaluation Metrics

### 4.4.1 Primary Metric: Pearson Correlation (r)

**Definition:** Linear correlation between CV and mean_ρ.

**Interpretation:**
- r < -0.5: Moderate-to-strong negative correlation → CV predicts stability (hypothesis supported).
- -0.5 ≤ r < -0.3: Weak negative correlation → Borderline, insufficient for practical use.
- |r| < 0.3: Negligible correlation → Null result, CV does not predict stability.

**Why Pearson over Spearman?** We hypothesize a linear relationship (high CV → low mean_ρ proportionally). Pearson is appropriate for linear associations. Spearman would test monotonic relationships, which is broader than our hypothesis.

### 4.4.2 Secondary Metrics

**95% Confidence Interval for r:** Quantifies uncertainty. Wide CI including positive values indicates high uncertainty, even if point estimate is negative.

**p-value:** Tests statistical significance under H₀ (r=0). We require p < 0.05 to claim the correlation is reliably different from zero.

**Cohen's d (Tertile Analysis - Q3):** If primary test shows borderline results (r ≈ -0.5 but p > 0.05), we compute effect size between high-CV tertile and low-CV tertile mean_ρ values. d > 0.5 would suggest practical difference despite borderline correlation.

## 4.5 Baseline Comparisons

**Not applicable.** This is a meta-analysis of published benchmarks, not a model comparison study. There are no baseline methods to compare against—we are testing the first hypothesis about leaderboard meta-features as quality predictors.

**Future baselines:** If alternative meta-features are proposed (inter-quartile range, split-half reliability, score ceiling proximity), they can be compared against CV using the same corpus and methodology. Our null result provides the baseline for future multi-feature models.

## 4.6 Reproducibility and Open Science

**Pre-registration:** MUST_WORK gate criteria (r < -0.5, p < 0.05) were specified in Phase 2B verification plan before data collection, preventing post-hoc threshold adjustments.

**Code availability:** Python analysis pipeline (pandas, scipy, matplotlib) available in supplementary materials. All statistical tests and visualizations are reproducible from the mock benchmark corpus.

**Data availability:** Mock benchmark corpus (10 CSV files with model scores, CV, mean_ρ) will be released. Real leaderboard data (TrustLLM, HaluBench, TruthfulQA) is publicly available but was not used in this study (Section 6.1 limitation).

**Power analysis notebook:** Jupyter notebook with power calculations for n=5, 10, 15 benchmarks and varying effect sizes (r=-0.3 to r=-0.7) provided in appendix.

## 4.7 Ethical Considerations

This work does not involve human subjects, new model training, or generation of potentially harmful content. The analysis is purely meta-scientific—examining relationships between benchmark statistics.

**Broader impact:** Prospective benchmark quality tools could improve evaluation rigor, reducing reliance on benchmarks that produce unstable rankings. This supports more trustworthy LLM deployment. However, simple heuristics (like CV) may over-simplify quality assessment, as our null result demonstrates. Multi-feature models grounded in psychometric theory (Section 7) are needed to avoid misleading quality signals.
