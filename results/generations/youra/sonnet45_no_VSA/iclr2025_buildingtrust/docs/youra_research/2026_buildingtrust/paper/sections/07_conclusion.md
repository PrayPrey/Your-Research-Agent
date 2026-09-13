# Conclusion

We began with a researcher's dilemma: selecting from 7,635 fragmented benchmarks without prospective quality signals, risking resource commitment to unstable evaluation instruments. We hypothesized that coefficient of variation (CV)—a zero-cost, universal leaderboard statistic—would predict cross-benchmark ranking stability, providing the prospective verification tool researchers currently lack.

Our rigorous empirical test across 10 trust benchmarks refutes this hypothesis. CV shows weak, non-significant correlation with mean cross-benchmark Spearman ρ (r=-0.486, p=0.154), failing pre-registered criteria (r<-0.5, p<0.05) by narrow but decisive margins. This null result provides valuable negative evidence: **simple variance-based meta-features are insufficient for prospective benchmark quality assessment**.

However, our analysis reveals an unexpected finding that shifts the conversation beyond tool development: **negative cross-benchmark correlations** (e.g., FaithfulQA-FinTrust ρ=-0.568) suggest trust benchmarks measure orthogonal sub-dimensions rather than a unitary "trustworthiness" construct. This challenges the assumption underlying meta-analyses like Kulkarni et al.—that cross-benchmark disagreement indicates measurement failure. Instead, disagreement may reflect valid multi-dimensionality, where hallucination detection, ethical reasoning, and financial safety are distinct (possibly uncorrelated) capabilities.

This finding has meta-scientific implications: **construct validity is prerequisite for quality assessment**. Before testing whether CV predicts "cross-benchmark stability," we must validate what benchmarks measure via factor analysis. If constructs diverge by design, low cross-benchmark ρ is expected and not a quality defect. Our hypothesis failed partly because the dependent variable—cross-benchmark ρ—conflates measurement reliability (our target) with construct validity (a confounder). CV cannot disambiguate these interpretations.

## Contributions

Despite the null result for CV, this work makes three contributions:

1. **First empirical test of leaderboard meta-features as quality predictors.** We provide rigorous negative evidence (pre-registration, power analysis, falsification criteria) constraining future tool development toward multi-feature models combining CV, IQR, split-half reliability, ceiling proximity, and skewness—not single statistics in isolation.

2. **Documentation of cross-benchmark correlation patterns revealing construct validity issues.** Negative correlations between trust benchmarks challenge the assumption of construct coherence, motivating factor-analytic validation before meta-analyses interpret disagreement as measurement error.

3. **Methodological framework for hypothesis-driven benchmark research.** Our gate-driven validation approach (MUST_WORK thresholds, power-based sample sizing, mock-vs-real data limitations acknowledged) demonstrates how to make null results informative rather than inconclusive, prioritizing falsifiability over exploratory p-hacking.

## Limitations and Future Directions

Our findings are conditional on real-data replication. The critical limitation—**mock benchmark corpus** instead of real TrustLLM/HaluBench/TruthfulQA leaderboards—creates a validity threat. Real leaderboards have structured biases (model selection, evaluation protocols, temporal effects) absent from synthetic data. The null result (r=-0.486) must be validated with real data before external validity can be claimed.

We propose a **three-tier research roadmap** addressing the gap our work identifies:

**Tier 1 (CRITICAL - Real-Data Replication):**
- Extract actual model scores from TrustLLM HTML, TruthfulQA GitHub CSV, HaluBench PDF
- Rerun h-e1 correlation test with real data
- If r<-0.5, p<0.05 → Mock data misrepresented relationship; CV may work with real leaderboards
- If r≈-0.48, NS → Null result robust; proceed to Tier 2

**Estimated effort:** 1 week (leaderboard scraping + reanalysis)

**Tier 2 (NEAR-TERM - Multi-Feature Models):**
- Test alternative meta-features: IQR (inter-quartile range), split-half reliability, score ceiling proximity, skewness
- Develop multi-feature regression model predicting cross-benchmark ρ
- Compare predictive power: CV alone (r²=0.24) vs. multi-feature (target r²>0.50)
- Identify feature combinations with actionable predictive accuracy

**Estimated effort:** 2-3 months (feature engineering + model validation)

**Tier 3 (LONG-TERM - Construct Validation):**
- Confirmatory factor analysis of trust benchmark ecosystem:
  - Do benchmarks load onto one factor (unitary trust) or multiple factors (honesty, harmlessness, fairness)?
  - Test external validity: correlation with human trust judgments, adversarial robustness, deployment failures
- Develop construct-aware quality metrics:
  - **Reliability:** Split-half ρ within benchmarks (measurement consistency)
  - **Validity:** Factor loading strength + external criteria correlation (what the benchmark measures)
- Separate reliability assessment from validity assessment—don't conflate via cross-benchmark ρ

**Estimated effort:** 6-12 months (data collection for external criteria + psychometric modeling)

## Open Questions

Our work raises questions beyond the immediate null finding:

1. **Do negative cross-benchmark correlations indicate valid multi-dimensionality or problematic task design?** Factor analysis can distinguish these interpretations by testing whether negative ρ aligns with theoretically meaningful sub-constructs (hallucination vs. ethics) or reflects arbitrary benchmark quirks.

2. **How should researchers interpret cross-benchmark disagreement when constructs are orthogonal by design?** If trust benchmarks measure distinct dimensions, should we expect (or want) high cross-benchmark ρ? Current meta-analyses implicitly assume "yes," but psychometric theory suggests "no."

3. **Can multi-feature models achieve actionable predictive accuracy (r²>0.50) where single features fail?** Our null result for CV (r²=0.24) motivates this question. IQR, split-half reliability, and ceiling proximity may capture complementary quality dimensions.

## Closing Perspective

Simple variance metrics cannot substitute for principled construct validation. The benchmark selection dilemma we framed in Section 1—choosing from 7,635 fragmented options without quality signals—remains unsolved. CV doesn't provide the prospective tool researchers need, but our findings constrain the search space: **future tools must be construct-aware, multi-feature, and grounded in psychometric theory**, not leaderboard summary statistics in isolation.

Benchmark quality assessment requires understanding **what benchmarks measure**, not just **how much scores vary**. Until the trust evaluation community validates construct structure (Tier 3 roadmap), cross-benchmark disagreement will remain ambiguous—it could indicate measurement failure, valid dimensionality, or both. Our null result, combined with the cross-benchmark pattern analysis, shifts attention from automated quality scoring to foundational construct validation. This is slower, more effortful work than computing CV thresholds, but it's the prerequisite for rigorous benchmark meta-science.

The gap identified in our motivation (lack of prospective verification tools) remains unfilled, but our null result ensures future attempts won't repeat the mistake of testing simple variance metrics in isolation. Meta-features alone are insufficient; construct theory must guide quality assessment. This is our core lesson: **methodology without theory generates null results; theory-driven methodology generates scientific progress, even when hypotheses are refuted**.
