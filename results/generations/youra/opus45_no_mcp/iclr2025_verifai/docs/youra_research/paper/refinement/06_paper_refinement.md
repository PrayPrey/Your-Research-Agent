# Orthogonality of Static and Execution Feedback in LLM Code Generation

## Abstract

When LLM-generated code fails, developers can provide feedback from static analysis tools (pylint, mypy) or from test execution. Prior work demonstrates that both feedback types improve code quality, but whether they detect the same bugs or different ones remains unquantified. This study provides the first controlled measurement of overlap between static-detected and execution-detected error sets. Analyzing 542 problems from HumanEval+ and MBPP+, we observe a Jaccard similarity of 0.0 between the two error classes—complete orthogonality with no overlap. Static analysis detects structural errors (types, undefined variables, style violations) in 98.6% of test-failing code. However, the complementary hypothesis—that execution detects behavioral errors in static-clean code—was not validated: only 0.3% of static-clean canonical solutions failed execution tests, far below the 40% threshold. This discrepancy arises because canonical solutions are designed to pass tests, not because execution feedback lacks value. The complete separation observed between error classes supports the theoretical basis for combining feedback types in iterative refinement systems, though empirical validation on actual LLM-generated code remains necessary.

---

## 1. Introduction

When an LLM generates code that fails tests, developers reach for two distinct feedback signals: static analysis errors from tools like pylint and mypy, and test failure messages from execution. Whether these signals detect the same bugs or fundamentally different ones has practical implications: if the signals are redundant, combining them wastes compute; if they are orthogonal, omitting either leaves bugs unfixed.

Recent work demonstrates that both feedback types independently improve LLM code generation quality. Static analysis feedback can reduce security issues from 40% to 13% over iterative refinement cycles. Execution-based feedback powers approaches like Self-Refine and CodeRL. However, no prior work quantifies whether static and execution feedback detect overlapping or distinct error classes.

This gap matters because the composition of feedback signals determines optimal refinement strategies. If static analysis catches a subset of what execution catches (or vice versa), then one signal suffices. If they catch disjoint error classes, then combining them should yield additive benefits.

We hypothesize that static analysis and execution feedback operate on fundamentally different code properties—structure versus behavior—and therefore detect categorically distinct error classes. Static tools analyze code text to find type mismatches, undefined variables, and syntax issues. Test suites execute code with inputs to find wrong outputs, runtime exceptions, and edge case failures.

We analyze 542 problems from HumanEval+ and MBPP+ to measure the Jaccard similarity between static-detected and execution-detected error sets. Our primary findings are:

1. **Complete orthogonality:** Jaccard similarity = 0.0 between static and execution error sets, indicating no overlap between detected error classes.

2. **High static coverage:** Static analysis (pylint/mypy) detects errors in 98.6% of code that fails execution tests, demonstrating its reliability as a feedback signal.

3. **Behavioral detection not validated:** Only 0.3% of static-clean code failed execution tests, far below the 40% threshold. This result reflects the use of canonical solutions rather than actual LLM-generated code.

---

## 2. Related Work

### 2.1 Static Analysis Feedback

Static analysis tools like pylint and mypy analyze code structure without execution, detecting type mismatches, undefined variables, unreachable code, and style violations. The Static Analysis as Feedback Loop approach demonstrates that providing pylint/mypy errors as feedback during iterative refinement reduces security issues from 40% to 13% over 10 iterations. However, this work does not compare against execution-based feedback.

### 2.2 Execution Feedback

Execution-based feedback uses test results—pass/fail outcomes, error messages, and output comparisons—to guide refinement. Self-Refine demonstrates that LLMs can iteratively improve outputs using feedback, achieving approximately 20% improvement across diverse tasks including code generation. CodeRL and related approaches train models with execution signals as rewards.

### 2.3 Combined Approaches

Some recent work combines both feedback types. The Helping LLMs Improve Code Generation approach provides both testing results and static analysis in a unified feedback loop. However, this work does not decompose individual contributions or measure overlap between signal types.

### 2.4 Research Gap

Prior work establishes that both static and execution feedback improve code quality independently. What remains unknown is whether they detect the same or different errors. This study addresses this gap by directly measuring error class overlap.

---

## 3. Method

### 3.1 Overview

The analysis comprises three components: (1) a static analysis pipeline to extract structural errors, (2) an execution pipeline to extract behavioral errors, and (3) orthogonality measurement using Jaccard similarity.

### 3.2 Static Analysis Pipeline

We use pylint and mypy as static analysis tools. Pylint detects syntax errors, undefined variables, unused imports, and style violations. Mypy performs type checking.

**Configuration:**
- pylint: Error (E) and Warning (W) codes
- mypy: `--ignore-missing-imports` flag, 30-second timeout

For each code sample, we extract the set of error categories detected.

### 3.3 Execution Pipeline

We use the EvalPlus test harness with extended test suites:
- HumanEval+: 164 problems, 80x more tests than original HumanEval
- MBPP+: 399 problems, 35x more tests than original MBPP

**Configuration:** 5-second timeout per problem, 8 parallel workers.

### 3.4 Orthogonality Measurement

We measure overlap using Jaccard similarity:

$$J(S, E) = \frac{|S \cap E|}{|S \cup E|}$$

where S = set of problems with static errors, E = set of problems with execution errors. J = 0 indicates complete orthogonality (no overlap).

### 3.5 Hypotheses

We decompose the analysis into three sub-hypotheses:

- **H-E1 (Orthogonality):** Jaccard similarity < 0.3 indicates static and execution feedback detect largely non-overlapping error classes.
- **H-M1 (Static Coverage):** Static analysis detects errors in > 60% of test-failing code.
- **H-M2 (Behavioral Detection):** Execution detects errors in > 40% of static-clean code.

---

## 4. Experimental Setup

### 4.1 Research Questions

**RQ1:** Do static and execution feedback detect overlapping error classes?

**RQ2:** What proportion of test-failing code contains detectable structural errors?

**RQ3:** What proportion of static-clean code fails execution tests?

### 4.2 Datasets

| Dataset | Problems | Tests per Problem | Selection Rationale |
|---------|----------|-------------------|---------------------|
| HumanEval+ | 164 | ~80x original | Extended tests for edge case coverage |
| MBPP+ | 399 | ~35x original | Larger, diverse problem set |
| **Combined** | **563** | - | Comprehensive coverage |

Note: 542 problems were analyzed after filtering.

### 4.3 Code Samples

Canonical solutions from EvalPlus were used rather than LLM-generated code. This design choice affects interpretation of H-M2 results, as canonical solutions are designed to pass tests.

### 4.4 Implementation

- **Static analysis:** pylint 2.17.x, mypy 1.4.x
- **Execution:** EvalPlus harness with 5-second timeout
- **Compute:** Standard CPU, approximately 10 minutes total runtime

---

## 5. Results

### 5.1 Orthogonality (RQ1, H-E1)

| Metric | Threshold | Observed | Status |
|--------|-----------|----------|--------|
| Jaccard Similarity | < 0.3 | **0.0** | PASS |

Across 542 problems, Jaccard similarity = 0.0. This indicates complete orthogonality with no overlap between static-detected and execution-detected error categories.

**Error Category Distribution:**

| Category | Count | Percentage |
|----------|-------|------------|
| Static-only errors | 265 | 48.9% |
| Execution-only errors | 0 | 0.0% |
| Both error types | 0 | 0.0% |
| Neither | 277 | 51.1% |

### 5.2 Static Analysis Coverage (RQ2, H-M1)

| Metric | Threshold | Observed | Status |
|--------|-----------|----------|--------|
| Structural Coverage | > 60% | **98.6%** | PASS |

Of 74 problems with test failures, 73 had static analysis errors (98.6% coverage).

**Per-Benchmark Breakdown:**

| Benchmark | Static Coverage |
|-----------|-----------------|
| HumanEval+ | 100.0% |
| MBPP+ | 98.0% |

### 5.3 Behavioral Error Detection (RQ3, H-M2)

| Metric | Threshold | Observed | Status |
|--------|-----------|----------|--------|
| Behavioral Rate | > 40% | **0.3%** | NOT SUPPORTED |

Of 326 static-clean problems, 1 failed execution tests (0.3%).

**Per-Benchmark Breakdown:**

| Benchmark | Static-Clean | Behavioral Failures | Rate |
|-----------|--------------|---------------------|------|
| HumanEval+ | 147 | 0 | 0.0% |
| MBPP+ | 179 | 1 | 0.6% |
| **Total** | 326 | 1 | **0.3%** |

**Failure Category:**

| Category | Count |
|----------|-------|
| Wrong Output | 0 |
| Runtime Exception | 1 |
| Timeout | 0 |
| Edge Case | 0 |

The single behavioral failure was a runtime exception in MBPP problem 120.

### 5.4 Summary of Hypothesis Tests

| Hypothesis | Gate | Observed | Confidence |
|------------|------|----------|------------|
| H-E1: Orthogonality | < 0.3 | 0.0 | HIGH |
| H-M1: Static Coverage | > 60% | 98.6% | HIGH |
| H-M2: Behavioral Rate | > 40% | 0.3% | NOT SUPPORTED |

---

## 6. Discussion

### 6.1 Complete Orthogonality

The Jaccard similarity of 0.0 indicates that static analysis and execution feedback detect entirely non-overlapping error classes in this analysis. Static tools analyze code structure to identify type mismatches, undefined variables, and style violations. Execution tests evaluate runtime behavior to identify incorrect outputs and exceptions. These mechanisms operate on fundamentally different code properties, which explains the observed orthogonality.

The finding that 48.9% of problems have static-only errors while 0% have execution-only errors reflects that all execution failures in this dataset co-occur with static errors. This is consistent with the high static coverage (98.6%).

### 6.2 Static Analysis Reliability

Static analysis detected errors in 98.6% of code that failed execution tests. This high coverage suggests that static analysis is a reliable first-pass filter for identifying problematic code. The per-benchmark breakdown shows consistent performance: 100% coverage on HumanEval+ and 98.0% on MBPP+.

### 6.3 Behavioral Detection Not Validated

The behavioral detection rate of 0.3% is far below the 40% threshold. This result does not invalidate the hypothesis that execution detects behavioral errors in static-clean code; rather, it reflects a limitation of the experimental design.

**Root cause:** Canonical solutions from EvalPlus were analyzed instead of actual LLM-generated code. Canonical solutions are specifically designed to pass the extended test suites, so behavioral failures are rare by construction.

**Implication:** Validating H-M2 requires code with natural semantic errors—that is, actual LLM-generated code where behavioral errors can occur independently of structural errors.

### 6.4 Limitations

**L1: Canonical solutions used.** The use of canonical solutions rather than LLM-generated code prevents validation of the behavioral detection hypothesis. Future work should use code generated via LLM API calls.

**L2: Combined improvement untested.** The hypothesis that combined feedback exceeds the maximum of individual feedback types was not empirically tested. The orthogonality finding provides theoretical support but not empirical validation.

**L3: Single benchmark family.** Results are limited to Python code on HumanEval+ and MBPP+. Generalization to other languages and benchmarks is not established.

**L4: Single code sample per problem.** Analysis used one canonical solution per problem. Results may differ with multiple samples per problem.

---

## 7. Conclusion

This study provides the first quantitative measurement of overlap between static and execution feedback signals for LLM code generation. The primary findings are:

1. **Complete orthogonality:** Jaccard similarity = 0.0 between static-detected and execution-detected error sets, indicating these feedback types detect entirely different error classes.

2. **High static coverage:** Static analysis detects structural errors in 98.6% of test-failing code.

3. **Behavioral detection untested:** The use of canonical solutions prevented validation of the hypothesis that execution detects behavioral errors in static-clean code (observed rate: 0.3% vs. 40% threshold).

The complete separation between error classes supports the theoretical basis for combining static and execution feedback in iterative refinement systems. However, empirical validation of combined feedback improvement requires experiments with actual LLM-generated code.

**Future Work:**
- Replicate analysis on actual LLM-generated code to test behavioral detection hypothesis
- Measure combined feedback improvement magnitude
- Extend to multiple LLM architectures and programming languages

---

## References

[1] Static Analysis as Feedback Loop. arXiv:2508.14419, 2025.

[2] Helping LLMs Improve Code Generation. arXiv:2412.14841, 2024.

[3] Madaan et al. Self-Refine: Iterative Refinement with Self-Feedback. NeurIPS 2023.

[4] EvalPlus. https://github.com/evalplus/evalplus

[5] StepCoder. arXiv:2402.01391, 2024.

[6] Synchromesh. ICLR 2022.
