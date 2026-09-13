# Limitation Record: h-z1 (Run 1)

**Date:** 2026-08-26T10:40:00+00:00
**Hypothesis:** h-z1
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

Z3 formal verification counterexamples did not provide additive benefit over mypy type checking alone. pass@1_C (85.7%, 96/112) was marginally lower than pass@1_B (86.6%, 97/112), delta=-0.9pp. The SHOULD_WORK gate (pass_rate_C > pass_rate_B) was not satisfied.

## Failed Checks

- pass_rate_C > pass_rate_B: 85.7% <= 86.6% (delta = -0.9pp)
- Z3 counterexample found rate was low: 16.1% (18/112), limiting Z3's opportunity to add signal
- Z3 spec validity: 91.1% (112/123), some specs were invalid reducing coverage

## Partial Results

| Metric | Value |
|--------|-------|
| pass@1_B (execution+mypy) | 86.6% (97/112) |
| pass@1_C (execution+mypy+Z3) | 85.7% (96/112) |
| delta (C - B) | -0.9pp |
| Z3 CE found rate | 16.1% (18/112) |
| Z3 spec validity rate | 91.1% (112/123) |
| HumanEval+ arithmetic subset n | 112 |

## Experiment Summary

On a curated subset of 112 arithmetic-heavy HumanEval+ problems (from 123 after Z3 spec pre-validation), Condition C (execution+mypy+Z3) achieved pass@1 of 85.7% vs Condition B (execution+mypy) at 86.6%. The Z3 counterexample signal was sparse (found in only 16.1% of cases), suggesting arithmetic problems in HumanEval+ may not have rich formal counterexample structure amenable to Z3 feedback. The marginal negative delta (-0.9pp) is within noise but directionally contrary to the hypothesis.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded with this limitation noted.

Future research attempts should consider:
1. Z3 CE found rate too low (16.1%) — arithmetic problems may not generate useful Z3 counterexamples
2. Richer Z3 spec generation (e.g., precondition/postcondition pairs) may improve CE rate
3. Alternative formal methods (property-based testing, SMT solvers with richer theories) may be more effective
4. Larger dataset or different benchmark (MBPP+, LiveCodeBench) might yield different results

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-26T10:40:00+00:00*
*For cross-phase reference*
*Note: Written as local file fallback — Serena MCP unavailable in no_MCP mode*
