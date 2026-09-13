# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-08-22T15:20:00+00:00
**Hypothesis:** h-e1
**Statement:** ruff+mypy fires on ≥50% of GPT-4o-mini round-0 failures on both HumanEval+ and MBPP+ subsets of EvalPlus (n=538)
**Final Status:** FAILED
**Gate Result:** FAIL
**Gate Type:** MUST_WORK

## Results

- HumanEval+ fire_rate: 0.324 (34 failures, 11 SA fired)
- MBPP+ fire_rate: 0.160 (100 failures, 16 SA fired)
- Overall gate: FAIL (neither subset reached 0.50)

## Reflection

- Reflection triggered: True
- Outcome: ROUTED_TO_PHASE_0
- Meaningful findings: False (structural failure, not marginal)
- Root cause: SA cannot detect semantic errors — EvalPlus failures are algorithmic, not syntactic

## Lessons

1. Static analysis (ruff+mypy) is insufficient oracle for code generation repair loops
2. Execution-based feedback required for meaningful repair signal
3. GPT-4o-mini failure set (34 HE+, 100 MBPP+) is reusable for revised hypothesis

---
*Per-hypothesis snapshot for Phase 2A reference*
*Written at: 2026-08-22T15:20:00+00:00*
