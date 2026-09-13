# Product Requirements Document: H-M2

**Hypothesis:** Execution Detects Behavioral Errors
**Date:** 2026-08-19
**Version:** 1.0
**Type:** MECHANISM

---

## Executive Summary

H-M2 tests whether test suites detect behavioral errors (wrong output, runtime exceptions, edge cases) in LLM-generated code that are NOT caught by static analysis. This complements H-M1's finding (98.6% structural coverage) by examining the orthogonal mechanism: behavioral error detection in static-clean code.

**Gate Condition:** Test failures in >40% of problems with zero pylint+mypy errors
**Fail Action:** Document as limitation (SHOULD_WORK gate)

---

## Problem Statement

LLM code generation produces both structural errors (pylint/mypy-detectable) and behavioral errors (test-detectable). H-M1 showed static analysis catches structural errors. H-M2 validates that execution catches different errors - behavioral ones in code that passes static analysis.

### Hypothesis Under Test
> Test suites detect behavioral errors (wrong output, runtime exceptions, edge cases) not caught by static analysis alone.

---

## Functional Requirements

### FR-01: Dataset Loading
- Load HumanEval+ (164 problems) and MBPP+ (399 problems) via evalplus
- Total: 563 problems with full test suites
- Reuse dataset infrastructure from H-E1/H-M1

### FR-02: Static Analysis Execution
- Run pylint with E/W error codes, 30s timeout per problem
- Run mypy with --ignore-missing-imports, 30s timeout per problem
- Identify problems with ZERO static errors (static-clean code)
- Reuse H-M1 infrastructure (static_analysis.py)

### FR-03: Test Execution on Static-Clean Code
- Execute evalplus tests on all static-clean problems
- Use evaluate_functional_correctness with timeout=3.0s
- Capture pass/fail status per problem

### FR-04: Behavioral Error Categorization
- Classify test failures into categories:
  - wrong_output: AssertionError, expected vs actual mismatch
  - runtime_exception: TypeError, ValueError, IndexError, etc.
  - timeout: execution exceeds time limit
  - edge_case: corner case failures

### FR-05: Behavioral Rate Computation
- Count static-clean problems (zero pylint+mypy errors)
- Count static-clean problems that fail tests
- Compute behavioral_rate = test_failures / static_clean_count

### FR-06: Gate Evaluation
- Pass condition: behavioral_rate > 0.40
- Generate gate result with pass/fail status and metrics

### FR-07: Visualization
- **Required:** Bar chart - behavioral rate vs 40% threshold
- Pie chart: failure category distribution
- Per-benchmark breakdown: HumanEval+ vs MBPP+ behavioral rates
- Save to h-m2/figures/

---

## Non-Functional Requirements

### NFR-01: Performance
- Process all 563 problems within 2 hours
- Parallelization: 8 workers for static analysis, 4 for test execution

### NFR-02: Reproducibility
- Deterministic results (no randomness)
- Use evalplus built-in evaluation
- Seed: 42 for any random operations

### NFR-03: Infrastructure Reuse
- Extend H-E1/H-M1 validated code
- Same timeout settings, same parallelization patterns
- Do NOT rewrite static_analysis.py

### NFR-04: Data Scale
- Use FULL test sets (no sampling)
- Minimum 500+ evaluation samples per benchmark

---

## Success Criteria

| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| Behavioral Rate | >40% | Primary gate metric |
| Static-Clean Count | Report | Denominator for rate |
| Category Distribution | ≥3 types | Secondary validation |
| Code Execution | No crashes | Basic validity |

---

## Dependencies

### Prerequisite Hypotheses
- H-E1: COMPLETED, PASS (Jaccard=0.0)
- H-M1: COMPLETED, PASS (98.6% structural coverage)

### External Dependencies
- evalplus library (pip install evalplus)
- pylint, mypy (pip packages)

### Reusable Components from H-M1
- static_analysis.py: pylint+mypy runner
- run_analysis.py: parallelization pipeline
- Error classification infrastructure

---

## Data Specifications

### Input
- HumanEval+ problems (164)
- MBPP+ problems (399)
- Code samples from H-E1 generation

### Output
- Static-clean problem identification
- Behavioral error categorization per problem
- Behavioral rate metric
- Gate result (PASS/FAIL)

---

## Evaluation Metrics

### Primary
- **behavioral_rate:** % of static-clean problems that fail tests

### Secondary
- Failure category distribution (wrong_output, exception, edge_case)
- Per-benchmark breakdown (HumanEval+ vs MBPP+)
- Total static-clean count

---

## Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 3 | 1 day | PRD, Architecture, Logic, Config |
| Phase 4 | 1-2 days | Validated code, 04_validation.md |

---

## Appendix: Phase 2C Reference

Source: h-m2/02c_experiment_brief.md
- Specification Level: 1.5 (Concrete + Pseudo-code)
- Core mechanism: analyze_behavioral_errors()
- Gate: behavioral_rate > 0.40
