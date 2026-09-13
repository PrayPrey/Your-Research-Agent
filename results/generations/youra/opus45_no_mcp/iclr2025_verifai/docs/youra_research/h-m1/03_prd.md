# Product Requirements Document: H-M1

**Hypothesis:** Static Analysis Detects Structural Errors
**Date:** 2026-08-19
**Version:** 1.0
**Type:** MECHANISM

---

## Executive Summary

H-M1 tests whether pylint+mypy detect structural errors (type mismatches, undefined variables, unreachable code) in LLM-generated code that are not caught by execution alone. This extends H-E1's finding that static and execution errors are orthogonal (Jaccard=0.0) by examining the specific mechanism: structural error detection.

**Gate Condition:** Static errors detected in >60% of test-failing problems
**Fail Action:** EXPLORE alternative static analysis tools (ruff, pyright)

---

## Problem Statement

LLM code generation produces both structural errors (detectable via static analysis) and behavioral errors (detectable via execution). Understanding which errors static analysis catches enables better feedback composition for iterative refinement.

### Hypothesis Under Test
> pylint+mypy detect structural errors (type mismatches, undefined variables, unreachable code) not caught by execution alone.

---

## Functional Requirements

### FR-01: Dataset Loading
- Load HumanEval+ (164 problems) and MBPP+ (399 problems) via evalplus
- Total: 563 problems with full test suites

### FR-02: Static Analysis Execution
- Run pylint with E/W error codes, 30s timeout per problem
- Run mypy with --ignore-missing-imports, 30s timeout per problem
- Reuse H-E1 infrastructure (static_analysis.py)

### FR-03: Structural Error Categorization
- Classify pylint codes as structural or non-structural:
  - E0001: syntax-error
  - E0602: undefined-variable
  - E1101: no-member
  - E1120: no-value-for-parameter
  - W0612: unused-variable
- Classify mypy errors by type (incompatible-type, arg-type, return-value)

### FR-04: Coverage Computation
- Count problems with test failures
- Count problems with structural errors detected
- Compute structural_coverage = has_structural / total_with_failures

### FR-05: Gate Evaluation
- Pass condition: structural_coverage > 0.60
- Generate gate result with pass/fail status and metrics

### FR-06: Visualization
- Bar chart: structural coverage vs 60% threshold
- Pie chart: structural error category distribution
- Save to h-m1/figures/

---

## Non-Functional Requirements

### NFR-01: Performance
- Process all 563 problems within 2 hours (parallelization: 8 workers)

### NFR-02: Reproducibility
- Deterministic results (no randomness in static analysis)
- Seed: 42 for any random operations

### NFR-03: Infrastructure Reuse
- Extend H-E1 validated code, do not rewrite from scratch
- Same timeout settings, same parallelization

---

## Success Criteria

| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| Structural Coverage | >60% | Primary gate metric |
| Error Categories | ≥3 types | Secondary validation |
| Code Execution | No crashes | Basic validity |

---

## Dependencies

### Prerequisite Hypotheses
- H-E1: COMPLETED, PASS (Jaccard=0.0)

### External Dependencies
- evalplus library (pip install evalplus)
- pylint, mypy (pip packages)

### Reusable Components from H-E1
- static_analysis.py: pylint+mypy runner
- exec_analysis.py: test execution (reference only)
- run_analysis.py: parallelization pipeline

---

## Data Specifications

### Input
- HumanEval+ problems (164)
- MBPP+ problems (399)

### Output
- Structural error categorization per problem
- Coverage metric
- Gate result (PASS/FAIL)

---

## Evaluation Metrics

### Primary
- **structural_coverage:** % of test-failing problems with structural errors

### Secondary
- Error type distribution
- Per-benchmark breakdown (HumanEval+ vs MBPP+)

---

## Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 3 | 1 day | PRD, Architecture, Logic, Config |
| Phase 4 | 1-2 days | Validated code, 04_validation.md |

---

## Appendix: Phase 2C Reference

Source: h-m1/02c_experiment_brief.md
- Specification Level: 1.5 (Concrete + Pseudo-code)
- Core mechanism code provided
- STRUCTURAL_ERROR_CODES dictionary defined
