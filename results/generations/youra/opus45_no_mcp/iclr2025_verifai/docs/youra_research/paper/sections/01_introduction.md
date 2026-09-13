# Introduction

When an LLM generates code that fails tests, developers reach for two distinct feedback signals: static analysis errors from tools like pylint and mypy, and test failure messages from execution. But do these signals catch the same bugs, or fundamentally different ones? This question has practical implications: if the signals are redundant, combining them wastes compute; if they are orthogonal, omitting either leaves bugs unfixed.

Recent work demonstrates that both feedback types independently improve LLM code generation quality. Static analysis feedback can reduce security issues from 40% to 13% over iterative refinement cycles. Similarly, execution-based feedback powers successful approaches like Self-Refine and CodeRL. However, a critical gap remains: no prior work quantifies whether static and execution feedback detect overlapping or distinct error classes.

This gap matters because the composition of feedback signals determines optimal refinement strategies. If static analysis catches a subset of what execution catches (or vice versa), then one signal suffices. If they catch disjoint error classes, then combining them should yield additive benefits beyond either alone. Without measuring this orthogonality, practitioners cannot make principled decisions about feedback composition.

Our key insight is that static analysis and execution feedback operate on fundamentally different code properties—structure versus behavior—and therefore detect categorically distinct error classes. Static tools analyze code text to find type mismatches, undefined variables, and syntax issues. Test suites execute code with inputs to find wrong outputs, runtime exceptions, and edge case failures. These detection mechanisms have no inherent overlap.

We provide the first quantitative evidence for this claim. Analyzing 542 problems from HumanEval+ and MBPP+, we measure the Jaccard similarity between static-detected and execution-detected error sets. Our findings are striking: the Jaccard similarity is exactly 0.0—complete orthogonality with zero overlap between error classes. Furthermore, static analysis detects structural errors in 98.6% of test-failing code, demonstrating its strong standalone coverage.

Our contributions are:

1. **First orthogonality measurement:** We provide the first quantitative measurement of overlap between static and execution feedback on standard code generation benchmarks, finding Jaccard similarity = 0.0.

2. **Structural coverage analysis:** We demonstrate that static analysis (pylint/mypy) detects errors in 98.6% of code that fails execution tests, establishing its reliability as a feedback signal.

3. **Theoretical foundation:** We provide experimental evidence supporting the theoretical basis for combining static and execution feedback in iterative refinement approaches.

The remainder of this paper is organized as follows. Section 2 reviews related work on feedback-driven code generation. Section 3 describes our methodology for measuring feedback orthogonality. Section 4 presents our experimental setup, and Section 5 reports results. Section 6 discusses implications and limitations, and Section 7 concludes with future directions.
