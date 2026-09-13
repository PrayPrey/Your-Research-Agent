# Phase 2B Context: H-E1

**Generated:** 2026-08-19
**Source:** 02b_verification_plan.md

---

## Hypothesis Information

- **ID:** H-E1
- **Type:** EXISTENCE
- **Title:** Existence of Orthogonal Error Classes
- **Statement:** Errors detected by static analysis (pylint/mypy) are categorically different from errors detected by execution (test failures).
- **Status:** IN_PROGRESS

---

## Gate Condition

- **Type:** MUST_WORK
- **Pass Condition:** Jaccard similarity < 0.3
- **Fail Action:** STOP - feedback types likely redundant

---

## Experimental Setup

### Dataset
- **Primary:** HumanEval+ (164 problems) + MBPP+ (399 problems)
- **Source:** evalplus
- **Total Problems:** 563

### Model
- **Type:** GPT-4 or CodeLlama-70B
- **Source:** OpenAI API or HuggingFace

---

## Verification Protocol

1. Generate initial code for 563 problems (164 HumanEval+ + 399 MBPP+) using base LLM
2. Run pylint+mypy on all generated code, categorize errors (type errors, undefined vars, unreachable code, etc.)
3. Run evalplus test suite, categorize failures (wrong output, runtime exceptions, edge cases)
4. Compute Jaccard similarity between error sets per problem
5. Statistical test: errors should be <30% overlapping

---

## Success Criteria (PoC: Direction-based)

- **Primary:** Jaccard similarity < 0.3 between static and execution error sets
- **Secondary:** At least 70% of problems show non-overlapping error types

---

## Dependencies

- **Prerequisites:** None (first in chain)
- **Dependents:** H-M1, H-M2, H-M3, H-M4

---

## Previous Context

N/A - First hypothesis in verification chain.
