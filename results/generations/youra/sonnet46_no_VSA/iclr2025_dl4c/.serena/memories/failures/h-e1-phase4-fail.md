# Failure Record: h-e1 — Phase 4 MUST_WORK Gate FAIL

**Date:** 2026-08-02
**Hypothesis:** h-e1
**Phase:** Phase 4
**Gate Type:** MUST_WORK
**Gate Result:** FAIL
**Outcome:** ROUTED_TO_PHASE_0

## Hypothesis Statement
EvalPlus+ fractional reward produces significantly higher per-prompt reward variance than binary reward, confirming reward signal density as prerequisite for mechanistic sub-hypotheses.

## Failed Checks
- mean_binary_var=0.0, mean_fractional_var=0.0 (both zero — EvalPlus returned no partial scores)
- t_stat=NaN, p_value=NaN (no variance to compare)
- relative_diff=0.0 (below 0.1 threshold)
- mechanism check: evalplus_returns_partial=false, fractional_has_variance=false

## Root Cause
EvalPlus does not return partial/fractional scores. Fractional reward (mean over test cases) collapses to binary behavior because each test case is pass/fail only — no intermediate partial credit exists. Both reward modes produce identical 0.0 variance distributions across 542 prompts.

## Lessons Learned
1. EvalPlus evaluates each test case as binary pass/fail; averaging over test cases does NOT produce fractional reward with meaningful variance unless prompts partially pass some tests
2. With 542 prompts all failing (0 test cases passing), both binary and fractional reward = 0.0 for all prompts — zero variance is inevitable
3. The existence prerequisite for h-m1/h-m2/h-c1 is NOT established
4. To get fractional variance, need: (a) model capable of partially solving HumanEval problems, OR (b) reward defined at sub-test granularity in a different framework

## Routing
ROUTED_TO_PHASE_0 — fundamental assumption invalid; requires brainstorm-level redesign
