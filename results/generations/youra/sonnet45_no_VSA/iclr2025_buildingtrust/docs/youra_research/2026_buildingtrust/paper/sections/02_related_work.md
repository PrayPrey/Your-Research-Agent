# Related Work

Our work intersects three research threads: benchmark fragmentation in LLM evaluation, cross-benchmark ranking disagreement, and construct validity theory from psychometrics. We position our contribution as the first attempt to move from *documenting* benchmark ecosystem problems to *predicting* benchmark reliability using prospective signals.

## Benchmark Fragmentation and Ecosystem Analysis

**mmjerge (TMLR 2025)** conducted a comprehensive meta-analysis of 7,635 benchmarks across 4,886 LLM evaluation papers, finding less than 25% overlap in benchmark usage across studies. This fragmentation creates evaluation infrastructure where researchers cannot easily compare results across papers, as each study uses a disjoint set of benchmarks. Our work extends this observation by testing whether leaderboard-derivable statistics (coefficient of variation) can prospectively identify which benchmarks in this fragmented ecosystem are reliable, before experimental commitment.

The key difference: mmjerge documents *what* is fragmented but does not propose predictive tools for benchmark selection. We hypothesize CV as a universal quality signal, find it insufficient, but reveal construct validity issues (negative cross-benchmark correlations) explaining why fragmentation persists—benchmarks may measure orthogonal dimensions by design, not measurement failure.

## Cross-Benchmark Ranking Disagreement

**Kulkarni et al. (arXiv:2504.18114)** demonstrated systematic ranking disagreement across 37 LLM models evaluated on 6 metric sets, showing that model rankings are highly sensitive to evaluation methodology. Their work establishes that cross-benchmark agreement cannot be assumed, raising the question: which benchmarks produce stable rankings, and which do not?

Our hypothesis proposes CV (score variance within a benchmark) as a predictor of this stability, operationalized as mean cross-benchmark Spearman ρ. The null result (r=-0.486, p=0.154) refutes this relationship but reveals an unexpected pattern—negative correlations between benchmarks (e.g., FaithfulQA-FinTrust ρ=-0.568) suggest cross-benchmark disagreement arises not just from measurement noise but from valid construct divergence. This finding extends Kulkarni's descriptive work with a mechanistic explanation grounded in construct validity theory.

## Psychometric Foundations: Construct Validity

Our interpretation of negative cross-benchmark correlations draws on classical psychometric theory, particularly **Campbell & Fiske's (1959) multitrait-multimethod framework**. They distinguish:
- **Convergent validity**: Measures of the same construct should correlate highly.
- **Discriminant validity**: Measures of different constructs should correlate weakly or negatively.

Applied to LLM benchmarks, negative cross-benchmark correlations (FaithfulQA vs. FinTrust) could indicate *good discriminant validity*—these benchmarks measure distinct trust sub-dimensions (hallucination detection vs. financial ethical reasoning) rather than a unitary "trustworthiness" construct. Alternatively, it could indicate *poor convergent validity*—benchmarks claiming to measure "trust" don't agree on what that means.

This ambiguity is critical: our CV-stability hypothesis assumed low cross-benchmark ρ indicates measurement unreliability (noise). Psychometric theory reveals an alternative explanation—low ρ may reflect valid construct orthogonality. CV cannot disambiguate these interpretations, explaining its failure as a quality signal.

**Classical Test Theory (Reliability vs. Validity)** further clarifies this issue:
- **Reliability**: Consistency of measurement (do rankings replicate across item subsets?). Testable via split-half correlation.
- **Validity**: Does the benchmark measure what it claims? Requires external criteria (e.g., correlation with human trust judgments).

CV may predict reliability (measurement noise reduces consistency) but not validity (construct alignment with external criteria). Our cross-benchmark ρ metric conflates both, making it an unreliable CV target. This suggests future work should separate reliability assessment (split-half ρ within benchmarks) from validity assessment (factor analysis with external criteria).

## Benchmark Quality Assessment

Prior work on benchmark quality focuses on annotation protocols, task design, and dataset curation [Bowman et al., 2015; Dua et al., 2019], requiring domain expertise and manual inspection. Our approach targets **leaderboard-derivable meta-features** computable without domain knowledge:
- **Strengths**: Zero-cost, universal (applicable to any benchmark with published scores), prospective (available before experimental validation).
- **Limitations**: As our null result shows, simple statistics (CV) are insufficient. Quality assessment likely requires multi-feature models combining CV, inter-quartile range (IQR), score ceiling proximity, skewness, and split-half reliability.

**Positioning:** We are the first to empirically test whether a leaderboard statistic can prospectively predict benchmark reliability. The negative result is valuable—it rules out CV as a standalone tool and motivates construct-aware approaches grounded in psychometric theory.

## Related Failures and Lessons

Our preliminary work experienced a benchmark dataset with only 2 models versus 8 expected, motivating this investigation into prospective quality signals. We hypothesized CV would have flagged this risk (high CV with n=2 suggests unstable estimates). However, our finding that CV doesn't predict cross-benchmark stability suggests the 2-model failure was a dataset availability issue (not enough models evaluated) rather than a variance pattern CV would detect. A simpler heuristic—**n-models ≥ 10 threshold**—remains the more reliable check, consistent with our experimental inclusion criterion.

## Gap Addressed

**What's Missing:** No empirical test exists for whether leaderboard statistics predict benchmark quality. Prior work is either descriptive (mmjerge, Kulkarni—documenting problems) or prescriptive (annotation guidelines—requiring expertise).

**Our Contribution:** Rigorous falsification test of CV as a quality predictor. The null result (r=-0.486, NS) provides negative evidence constraining future tool development, while the cross-benchmark correlation analysis reveals construct validity confounds requiring factor-analytic approaches. We shift the conversation from "benchmarks disagree" (known) to "disagreement has complex causes CV can't capture" (novel theoretical contribution).
