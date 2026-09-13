# Phase 2B Context: H-M2

**Hypothesis ID:** H-M2
**Title:** Execution Detects Behavioral Errors
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Prerequisites:** H-M1 (COMPLETED, PASS)

---

## Hypothesis Statement

Under LLM code generation, if test suites are run on generated code, then they detect behavioral errors (wrong output, runtime exceptions, edge case failures) that would not be caught by static analysis alone, because tests execute code paths with specific inputs.

---

## Gate Condition

- **Pass Condition:** Test failures in >40% of problems with zero pylint/mypy errors
- **Fail Action:** Document limitation

---

## Verification Protocol

1. Generate code for full HumanEval+/MBPP+ test set
2. Run evalplus test suite, record all failures
3. Categorize failures as behavioral (wrong output, exception, edge case)
4. Verify behavioral errors are present where static analysis found no issues

---

## Success Criteria

- **Primary:** Test failures occur in >40% of problems with zero pylint/mypy errors
- **Secondary:** Behavioral categories (wrong output, exception) are dominant failure modes

---

## Previous Hypothesis Results

### H-M1 Results (Prerequisite - PASS)
- Structural Coverage: 98.6%
- Failing Problems: 74
- With Structural Errors: 73
- HumanEval+ Coverage: 100.0%
- MBPP+ Coverage: 98.0%

**Implication for H-M2:** H-M1 established that static analysis catches structural errors. H-M2 must now show the converse: execution catches behavioral errors that static analysis misses.

---

## Experimental Setup

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval+ (164) + MBPP+ (399) | Standard code generation benchmarks |
| **Model** | GPT-4 or CodeLlama-70B | Capable of following instructions |
| **Static Tools** | pylint + mypy | Standard Python static analysis |
| **Execution** | evalplus test suite | 80x/35x more tests than originals |

---

## Key Metrics to Collect

1. Total problems with zero static errors
2. Of those, how many have test failures
3. Categories of test failures (wrong output, exception, edge case)
4. Comparison with H-M1 error distribution

---

*Generated: 2026-08-19*
*Phase: 2C (Experiment Design)*
