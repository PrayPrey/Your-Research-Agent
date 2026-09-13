# FeedbackEval: A Benchmark for Evaluating LLMs in Feedback-Driven Code Repair

## Key Metadata
- **Authors:** Dai et al.
- **Year:** 2025
- **Venue:** arXiv (2504.06939)
- **Core Contribution:** Introduces FeedbackEval, a benchmark for systematic comparison of feedback types in LLM code repair, covering HumanEval, CoderEval, and SWE-bench.

## Section Summaries

### Abstract
FeedbackEval evaluates LLMs in feedback-driven code repair by systematically comparing multiple feedback types: compiler errors, test-case results, minimal feedback, LLM-expert feedback, LLM-skilled feedback, and mixed feedback. Results show mixed feedback achieves 63.6% pass@1; test-case feedback outperforms compiler feedback alone; diminishing returns appear after 2-3 rounds of repair.

### Introduction & Motivation
Iterative LLM code repair using external feedback signals has shown promise, but no systematic head-to-head comparison across standardized benchmarks and feedback types existed. This work fills the gap by creating a multi-benchmark, multi-feedback-type evaluation framework (Repair@k metric) to measure how much each feedback type improves code correctness.

### Methodology
FeedbackEval applies each feedback type as the sole signal in a fixed repair loop (up to 5 rounds). Feedback types: (1) compiler/syntax error messages; (2) unit test execution results; (3) minimal ("your code is wrong"); (4) LLM-expert (GPT-4 quality critique); (5) LLM-skilled (GPT-3.5 quality critique); (6) mixed (compiler + test). Metric: Repair@k — the fraction of problems solved within k repair rounds. Benchmarks: HumanEval, CoderEval, SWE-bench. Models: multiple instruction-tuned LLMs.

**Critical gap:** FeedbackEval uses "compiler feedback" (syntax errors only), NOT semantic static analysis (pylint/mypy warnings about code quality, type errors, unused variables). Type-constrained decoding (hard grammar constraints at inference time) is also absent from the comparison set.

### Experiments & Results
| Feedback Type | Best pass@1 | Benchmark |
|---|---|---|
| Mixed (compiler + test) | 63.6% | HumanEval |
| Test-case feedback | ~58% | HumanEval |
| Compiler feedback | ~48% | HumanEval |
| Minimal feedback | ~42% | HumanEval |
Diminishing returns: most gains in rounds 1-2; round 3+ marginal. SWE-bench results: lower absolute performance; same relative ordering of feedback types.

### Discussion & Conclusion
FeedbackEval establishes that richer feedback (more informative signals) consistently outperforms minimal feedback. However, the benchmark does not cover semantic static analysis (pylint/mypy) or type-constrained decoding, leaving the full feedback type ranking incomplete.

## Key Contributions
- Multi-benchmark, multi-feedback-type systematic comparison
- Repair@k metric for standardized evaluation
- Evidence that test feedback > compiler feedback > minimal feedback
- Quantification of diminishing returns after 2-3 repair rounds

## Potential Relevance
FeedbackEval provides the closest existing comparison infrastructure to the Gap 3 hypothesis. Its framework is directly extensible: adding pylint/mypy as a new feedback type and type-constrained decoding as a separate condition would directly test the missing head-to-head comparison. The Repair@k metric and benchmark selection (HumanEval, CoderEval) can be adopted as-is.
