# Phase 4 Failure Record: h-e1 (Run 2)

**Date:** 2026-08-22T15:20:00+00:00
**Hypothesis:** h-e1
**Run:** 2
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Performance Gap

| Metric | Value | Gate | Result |
|--------|-------|------|--------|
| HumanEval+ fire_rate | 0.324 | ≥0.50 | FAIL |
| MBPP+ fire_rate | 0.160 | ≥0.50 | FAIL |

## Root Cause Analysis

- GPT-4o-mini round-0 failures on EvalPlus are predominantly **semantic errors** (wrong algorithm, wrong edge-case handling), not syntactic or type errors
- ruff detects only lint/style violations; it cannot detect algorithmic incorrectness
- mypy detects type annotation issues; generated code rarely has type annotations, so mypy rarely fires (0% on MBPP+, 2.9% on HumanEval+)
- The fundamental assumption that static analysis (ruff+mypy) correlates with functional correctness is falsified: SA fires on only 16–32% of failures, far below the 50% threshold
- MBPP+ tasks produce simpler, shorter code (mostly one-liners) with fewer lint opportunities, explaining the especially low 16% rate

## Lessons Learned

1. Static analysis tools (ruff/mypy) are insufficient as a proxy for functional correctness in code generation benchmarks
2. EvalPlus failures are almost entirely semantic — the generated code is syntactically valid Python
3. mypy is nearly useless as an oracle for this task (0–3% fire rate on failures)
4. ruff provides slightly more signal (12–26%) but still far below the 50% threshold
5. Execution-based feedback (test failures, tracebacks from EvalPlus) is the appropriate oracle for code repair loops, not SA
6. A future hypothesis should replace the SA oracle with execution-based feedback (e.g., use failing test cases from EvalPlus as the repair signal)

## Feedback for Next Phase (Phase 0 Redesign)

### Suggested Modifications
- Replace ruff+mypy oracle with execution-based feedback (failing test cases from EvalPlus)
- Consider hypothesis: "Iterative repair using EvalPlus test failure messages improves pass@1 by ≥5%"
- Consider hypothesis: "LLM-generated error explanations from test failures are more actionable than SA diagnostics"

### What NOT To Do
- Do not use ruff+mypy as a proxy for code correctness on EvalPlus-style benchmarks
- Do not assume SA fire rate correlates with repair opportunity rate

### What Showed Promise
- GPT-4o-mini achieves reasonable round-0 pass rates (79.3% on HumanEval+, 73.5% on MBPP+)
- The failure set is meaningful in size (34 HE+, 100 MBPP+) — enough for a repair study
- The experimental setup (EvalPlus + OpenAI API + subprocess oracle) is clean and reusable

---
*For cross-phase reference*
*Written at: 2026-08-22T15:20:00+00:00*
