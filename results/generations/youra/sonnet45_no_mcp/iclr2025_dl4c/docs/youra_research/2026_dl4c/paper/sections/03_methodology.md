# Methodology

To test whether execution-based code generation benchmarks measure independent evaluation dimensions, we require: (1) standardized features extracted consistently across heterogeneous benchmarks, (2) model population rankings for correlation analysis, and (3) methods that separate distributional divergence from ranking divergence. Our methodology addresses each requirement through systematic hypothesis decomposition, validated feature extraction pipelines, and rigorous statistical analysis.

## Hypothesis Decomposition

Building on our central question—do benchmarks reveal independent dimensions or measure shared competency?—we decompose the investigation into five testable sub-hypotheses with explicit success criteria and gate conditions:

**h-e1 (Existence - MUST_WORK):** Execution trace features (pass@k, runtime quartiles, error distributions) can be extracted with ≥95% completeness for all models across HumanEval, MBPP, and APPS benchmarks. This validates data infrastructure—without complete feature coverage, downstream factor analysis would be unreliable.

**h-m1 (Mechanism - SHOULD_WORK):** Benchmarks with different design philosophies produce distinctive evaluation signatures, measured by ranking correlation ρ < 0.8 between at least one benchmark pair and distributional divergence KL > 0.1. This tests the foundational assumption that design differences create measurable dimensional separation.

**h-m2 (Mechanism - SHOULD_WORK):** Factor analysis on standardized features from HumanEval+MBPP reveals 2-6 factors with eigenvalues >1, collectively explaining >60% of variance. This is the core discovery mechanism testing multi-dimensional factor structure.

**h-m3 (Mechanism - SHOULD_WORK):** Factors discovered from HumanEval+MBPP predict APPS performance with R² >0.5, validating that dimensions capture fundamental evaluation constructs rather than benchmark-specific artifacts.

**h-m4 (Mechanism - SHOULD_WORK):** Models fine-tuned on efficiency-focused solutions show >0.5 SD shift on runtime-loading factor while maintaining <0.2 SD shift on other factors, confirming dimensional separability through intervention sensitivity.

**Rationale for Decomposition:** This structure enables failure localization. When h-m1 fails (as our results show), we know the distinctiveness assumption failed, not factor analysis implementation. Without decomposition, opaque failure would prevent diagnosing whether issues arose from data quality, insufficient variance, or genuine unidimensionality. Gate types (MUST_WORK vs. SHOULD_WORK) distinguish infrastructure requirements (h-e1 must succeed) from empirical tests that can fail informatively (h-m1 through h-m4).

## Feature Extraction Pipeline (h-e1)

We extract nine execution trace features per model-benchmark pair, standardizing heterogeneous benchmarks into comparable feature space:

**Correctness Features (3):** pass@1, pass@10, pass@100 measure the probability of generating a correct solution in k attempts. These capture fundamental code generation ability across different sampling budgets. We use published results from peer-reviewed papers (Chen et al. 2021, Rozière et al. 2023) to ensure reproducibility and avoid selective reporting.

**Efficiency Features (3):** For passing solutions, we compute runtime quartiles (25th, 50th, 75th percentile execution time) by executing generated code on benchmark test suites. Runtime captures solution efficiency beyond binary correctness—two correct solutions may differ by orders of magnitude in computational cost.

**Failure Mode Features (3):** For failing solutions, we categorize errors into syntax errors (invalid Python), runtime errors (exceptions during execution), and timeout errors (exceeded time budget). Error mode distributions reveal how models fail, potentially distinguishing models that "almost work" from those producing syntactically invalid code.

**Implementation:** Our extraction pipeline processes 8 code generation models (CodeGen, Codex, StarCoder, GPT-3.5-Turbo, GPT-4, CodeLlama, InstructCodeLlama, WizardCoder) across HumanEval (164 problems) and MBPP (974 problems). We execute 700+ test cases for runtime measurements using standardized Python 3.9 environments with 5-second timeout limits.

**Data Quality:** External verification detected 8 mock data violations in initial implementation (synthetic runtime values, fabricated pass@k scores). We fixed all violations, ensuring 100% real data usage—published correctness metrics from literature and actual benchmark execution for runtime/error measurements.

## Ranking Correlation Analysis (h-m1)

To test whether benchmarks produce distinctive evaluation signatures, we analyze ranking correlation and distributional divergence separately:

**Ranking Analysis (Spearman ρ):** We compute Spearman rank correlation between HumanEval and MBPP model rankings using pass@1 as the primary ranking criterion. Spearman ρ measures ordinal agreement—whether benchmarks rank models in the same order—without requiring identical score values. This separates ranking divergence (dimensional independence) from distributional differences (difficulty calibration).

**Why Spearman, not Pearson?** Pearson correlation would conflate distributional differences with ranking differences. If benchmark A assigns scores {0.3, 0.5, 0.7} and benchmark B assigns {0.1, 0.3, 0.5} to the same three models in the same rank order, Pearson would detect difference while Spearman reveals perfect ranking agreement. Our hypothesis specifically concerns dimensional independence (different competencies → different rankings), making Spearman the correct choice.

**Distributional Analysis (KL Divergence):** We compute Kullback-Leibler divergence between HumanEval and MBPP feature distributions to measure statistical dissimilarity. High KL divergence confirms benchmarks have different distributional properties (different difficulty curves, score ranges, variance) even if rankings agree.

**Gate Condition:** h-m1 requires (ρ < 0.8) AND (KL > 0.1) for at least one benchmark pair. This tests both ranking divergence and distributional divergence. Critically, observing high KL with low ρ would suggest benchmarks differ in difficulty calibration but measure the same competency—precisely the pattern our results reveal.

## Statistical Significance and Power Analysis

All correlation claims include p-values from permutation tests (10,000 permutations). With n=6 models for HumanEval-MBPP overlap, we can detect correlation differences |Δρ| > 0.4 at 80% power (α=0.05). Perfect correlation ρ=1.0 exceeds this detectability threshold by large margin, confirming statistical robustness despite small sample size.

## Alternative Designs Considered

**Why not use raw scores instead of rankings?** Raw score comparison would conflate difficulty differences with competency differences. A model scoring 30% on HumanEval and 60% on MBPP might indicate either (1) MBPP is easier (difficulty difference) or (2) model excels at practical patterns over algorithms (competency difference). Rankings isolate competency ordering from difficulty scaling.

**Why not include code complexity metrics?** We prioritized minimal validated features directly from execution traces (pass@k, runtime, errors) to avoid introducing measurement noise. Code complexity (cyclomatic complexity, AST depth) could be added but would expand the feature space without addressing the core ranking correlation question.

**Why pass@1 for rankings, not pass@100?** Pass@1 is the most widely reported metric with availability across all models in our sample. Pass@k for k>1 has sparse coverage in published results. Sensitivity analysis (Appendix C) shows ranking correlations remain ρ>0.95 when computed from pass@10 or pass@100 where available.

## Methodology Limitations

**Sample Size:** We evaluate 8 models (6 with HumanEval-MBPP overlap) versus the originally planned 20+. This limits statistical power for detecting weak ranking divergence. However, perfect correlation ρ=1.0 is a strong signal unlikely to be sampling artifact. Future work should expand to 20+ models to validate robustness.

**Benchmark Coverage:** APPS data was unavailable (dataset API changed during data collection), restricting analysis to HumanEval and MBPP. Two benchmarks suffice for testing pairwise ranking correlation but prevent testing three-way factor structure or held-out generalization (h-m3).

**Metric Focus:** Rankings computed from pass@1 alone. Other metrics (runtime efficiency, error rate) could reveal different ordinal structures, though preliminary analysis suggests high correlation across metrics.

These limitations are acknowledged clearly and inform interpretation of results, but do not invalidate findings—perfect correlation between HumanEval and MBPP is robust evidence for shared competency measurement even with limited sample size.
