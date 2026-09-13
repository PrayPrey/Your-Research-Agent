# Methodology

To measure whether static and execution feedback detect orthogonal error classes, we design an analysis that extracts error sets from both sources on the same code samples and measures their overlap.

## Overview

Our approach has three components: (1) static analysis pipeline to extract structural errors, (2) execution pipeline to extract behavioral errors, and (3) orthogonality measurement using Jaccard similarity. The key design principle is running both analyses on identical code samples to enable direct comparison.

## Static Analysis Pipeline

We use pylint and mypy, standard Python linters that together cover type errors, syntax errors, undefined variables, unused imports, and other structural issues.

**Tool Configuration:**
- pylint: Error (E) and Warning (W) codes, including E0001 (syntax), E0102 (redefined function), E0602 (undefined variable), E1101 (no member), W0611 (unused import), W0612 (unused variable)
- mypy: `--ignore-missing-imports` flag to focus on type errors in analyzed code

**Rationale:** pylint catches Python-specific issues and style problems; mypy adds static type checking. Together they represent comprehensive structural analysis without execution.

For each code sample, we extract the set of error categories detected (e.g., {syntax-error, undefined-variable}), not individual error instances. This category-level analysis measures whether the feedback types target different error classes.

## Execution Pipeline

We use the EvalPlus test harness to execute code against extended test suites. HumanEval+ provides 80x more tests than original HumanEval; MBPP+ provides 35x more than original MBPP.

**Execution Configuration:**
- Timeout: 5 seconds per problem
- Parallelization: 8 workers using ProcessPoolExecutor
- Error categories: wrong output, runtime exception, timeout

**Rationale:** Extended test suites provide comprehensive behavioral coverage, reducing false negatives where code appears correct due to limited tests.

For each code sample, we extract whether execution fails and the failure category. A sample has execution errors if any test fails.

## Orthogonality Measurement

We measure overlap between static and execution error sets using Jaccard similarity:

$$J(S, E) = \frac{|S \cap E|}{|S \cup E|}$$

where S is the set of problems with static errors and E is the set with execution errors. Jaccard ranges from 0 (no overlap) to 1 (identical sets).

**Interpretation:**
- J = 0: Complete orthogonality—no problem has both error types
- J = 1: Complete redundancy—same problems fail both
- 0 < J < 1: Partial overlap

We set a threshold of J < 0.3 for declaring orthogonality, based on standard practice for weak overlap. However, our results show J = 0.0, exceeding this threshold.

## Analysis Framework

We organize analysis into three sub-hypotheses:

**H-E1 (Existence):** Static and execution feedback detect different error classes. Gate: Jaccard < 0.3.

**H-M1 (Mechanism - Static):** Static analysis reliably detects structural errors in test-failing code. Gate: Coverage > 60%.

**H-M2 (Mechanism - Execution):** Execution reliably detects behavioral errors in static-clean code. Gate: Behavioral rate > 40%.

This decomposition allows us to verify both the overall orthogonality claim (H-E1) and the specific mechanisms (H-M1, H-M2).
