# Experimental Setup

We design experiments to answer three research questions about feedback orthogonality.

## Research Questions

**RQ1:** Do static and execution feedback detect overlapping error classes? (Orthogonality test)

**RQ2:** What proportion of test-failing code contains structural errors detectable by static analysis? (Static coverage)

**RQ3:** What proportion of static-clean code fails execution tests? (Behavioral error rate)

These questions decompose the orthogonality claim: RQ1 measures overall overlap, RQ2 validates the static mechanism, and RQ3 validates the execution mechanism.

## Datasets

We evaluate on HumanEval+ and MBPP+ from the EvalPlus benchmark suite.

| Dataset | Problems | Tests per Problem | Total Tests | Why Chosen |
|---------|----------|-------------------|-------------|------------|
| HumanEval+ | 164 | ~80x original | ~13,000 | Extended tests catch edge cases missed by original |
| MBPP+ | 399 | ~35x original | ~14,000 | Larger problem set, diverse complexity |
| **Combined** | **563** | - | ~27,000 | Comprehensive coverage of code generation tasks |

**Rationale:** Original HumanEval and MBPP have sparse test coverage, allowing incorrect code to appear correct. Extended test suites from EvalPlus provide rigorous behavioral evaluation, essential for accurate orthogonality measurement.

## Analysis Targets

We analyze canonical solutions provided by EvalPlus—reference implementations designed to pass all tests. This choice enables clean measurement of static analysis tool behavior, though it limits behavioral error rate findings (addressed in Discussion).

## Evaluation Metrics

**Jaccard Similarity (RQ1):**
$$J = \frac{|S \cap E|}{|S \cup E|}$$
where S = problems with static errors, E = problems with execution errors. Threshold: J < 0.3 indicates orthogonality.

**Structural Coverage (RQ2):**
$$\text{Coverage} = \frac{\text{Problems with static errors AND test failures}}{\text{Problems with test failures}}$$
Threshold: > 60% indicates static analysis reliably detects errors in failing code.

**Behavioral Rate (RQ3):**
$$\text{Rate} = \frac{\text{Static-clean problems with test failures}}{\text{Static-clean problems}}$$
Threshold: > 40% indicates execution catches errors static analysis misses.

## Implementation Details

**Static Analysis:**
- Tools: pylint 2.17.x, mypy 1.4.x
- Timeout: 30 seconds per problem
- Output: Error categories (syntax-error, type-mismatch, undefined-variable, etc.)

**Execution:**
- Framework: EvalPlus test harness
- Timeout: 5 seconds per problem
- Parallelization: 8 workers (ProcessPoolExecutor)
- Output: Pass/fail with failure category (wrong output, runtime exception, timeout)

**Compute:** Analysis runs on standard CPU (no GPU required). Full analysis completes in approximately 10 minutes.

**Reproducibility:** Analysis scripts and intermediate results available in supplementary materials.
