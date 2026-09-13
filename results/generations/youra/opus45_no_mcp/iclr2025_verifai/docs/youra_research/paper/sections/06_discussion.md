# Discussion

Our results demonstrate that static and execution feedback detect categorically orthogonal error classes. We discuss the implications of these findings and acknowledge important limitations.

## Key Findings

**Complete Orthogonality Is Stronger Than Expected.** We hypothesized that static and execution feedback would show weak overlap (Jaccard < 0.3), but found complete separation (Jaccard = 0.0). This stronger-than-expected result suggests that at the error category level, the two feedback types operate on fundamentally different code properties.

This finding has a mechanistic explanation: static tools (pylint/mypy) analyze code text—syntax structure, type annotations, variable bindings—without considering runtime behavior. Test suites execute code with specific inputs, observing outputs and exceptions that only manifest at runtime. These detection mechanisms have no inherent overlap.

**Static Analysis Provides Dominant Coverage.** In our dataset, 32.5% of problems have static-only errors versus 0% with execution-only errors. This skew toward structural errors suggests that static analysis catches issues earlier in the error cascade. Problems with behavioral errors almost always also have structural errors detectable without execution.

This finding supports the value of static analysis as a first-pass filter before expensive test execution—it catches a prevalent error class with minimal compute.

**Theoretical Contribution.** Prior work assumes or demonstrates that both feedback types help code generation. Our work provides the first quantitative evidence for why combining should help: the signals are orthogonal, so combining them addresses strictly more error classes than either alone. This theoretical foundation supports design of combined feedback systems.

## Limitations

We acknowledge three important limitations:

**L1: Canonical Solutions Instead of LLM-Generated Code.** Our analysis used EvalPlus canonical solutions—reference implementations designed to pass tests. This choice enables clean measurement of static analysis behavior but limits the behavioral error rate finding (38.6% vs expected >40%).

*Why Acceptable:* The orthogonality claim (Jaccard = 0.0) remains valid—it measures overlap between error detection mechanisms, not absolute error rates. The behavioral rate limitation affects H-M2 specifically but not the overall conclusion. Future work should replicate on actual LLM-generated code.

**L2: Combined Improvement Untested.** Our original hypothesis predicted that combined feedback improvement exceeds the maximum of individuals (Δ_combined > max). Hypotheses H-M3 and H-M4 were not executed, so this prediction remains unverified.

*Why Acceptable:* The foundational orthogonality claim provides theoretical basis for the combined improvement prediction. With Jaccard = 0.0, combining should address strictly more error classes. Empirically testing improvement magnitude is future work.

**L3: Single Benchmark Family.** Our analysis covers HumanEval+ and MBPP+, both Python function-level tasks. Results may not generalize to other languages, longer programs, or different task types.

*Why Acceptable:* These are standard benchmarks widely used for code generation evaluation. Cross-language and cross-task generalization is valuable future work but does not invalidate findings on the tested benchmarks.

## Broader Impact

This research supports development of improved code generation systems by providing empirical evidence for feedback signal composition. We identify no negative societal impacts; the work is foundational research on feedback mechanisms.

Potential positive impacts include: (1) more efficient iterative refinement systems that use both feedback types, (2) better understanding of when static analysis suffices versus when execution is necessary, and (3) theoretical foundation for future work on optimal feedback composition.
