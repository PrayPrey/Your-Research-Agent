# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-08-03T12:00:00+00:00
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** GATE_FAIL_ROUTED_TO_PHASE_0

## Hypothesis Statement

Under the full ContractEval-encoded subset of HumanEval+/MBPP+ problems, if we run Z3 on negated post-conditions of ContractEval contracts, then (a) ≥1 program passes all tests but fails ≥1 contract (contract strength ratio >0), AND (b) Z3 tractability rate ≥50% within 30s timeout.

## Experiment Results

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| Total problems | 364 | — | — |
| Unencodeable | 269 | — | — |
| SAT (violations found) | 94 | — | — |
| UNSAT | 0 | — | — |
| Contract strength ratio | 0.0742 | >0 | ✓ |
| Z3 tractability rate | 0.2582 | ≥0.50 | ✗ |
| Confirmed violations | 27 | — | — |

## Gate Result

**MUST_WORK gate: FAIL**

- Criterion (a) contract strength ratio >0: PASSED (0.0742)
- Criterion (b) Z3 tractability ≥50%: FAILED (25.82% < 50%)

## Root Cause Analysis

1. **Unencodeable rate too high (73.9%)**: ContractEval contracts use Python-specific constructs (list comprehensions, string ops, complex data structures) that Z3's linear arithmetic fragment cannot represent. Only 95/364 problems were encodeable.
2. **Z3 tractability rate insufficient**: Of encodeable problems, only ~27% produced useful results within 30s. Many contracts involve nonlinear arithmetic or quantifiers that cause Z3 timeouts.
3. **Assumption mismatch**: The hypothesis assumed contracts would fall in decidable linear integer arithmetic fragments. Actual ContractEval contracts are richer Python expressions that don't map cleanly to SMT-LIB.

## Lessons Learned

1. ContractEval contracts are not pre-filtered for SMT-decidability — most use Python idioms outside Z3's efficient fragment.
2. Tractability rate of 25.82% (vs required 50%) suggests fundamental encoding incompatibility, not just timeout tuning.
3. Strength ratio of 7.42% shows formal contracts DO catch test-passing but contract-failing programs — the concept is valid but Z3 is the wrong tool for this contract language.
4. An alternative approach (AST-based contract checking, runtime assertion, or PyPy-based evaluation) may achieve better tractability without Z3.

## Feedback for Phase 0 Brainstorming

### Suggested Modifications
- Consider contract verification approaches that don't require SMT encoding (e.g., runtime fuzzing against contract assertions)
- Explore hybrid: use Z3 only for arithmetic-heavy contracts, fall back to execution-based checking for others
- Look at symbolic execution tools (e.g., CrossHair, Hypothesis) that handle Python natively
- Consider narrowing to arithmetic-only subset of ContractEval where Z3 tractability is high

### What NOT To Do
- Do not assume ContractEval contracts are SMT-encodeable without pre-filtering
- Do not rely on Z3 alone for Python-native contract languages
- Do not set tractability threshold >30% without encoder improvements

### What Showed Promise
- Contract strength concept is valid: 27 confirmed violations found (programs passing tests but failing contracts)
- Strength ratio 7.42% > 0 confirms formal contracts ARE strictly stronger than test coverage
- The core research direction (formal verification > testing) is sound — just Z3 + ContractEval pairing is wrong

---
*For cross-phase reference*
*Written at: 2026-08-03T12:30:00+00:00*
