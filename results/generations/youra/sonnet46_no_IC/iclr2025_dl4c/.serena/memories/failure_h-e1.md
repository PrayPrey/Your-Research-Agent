# Phase 4 Failure Record: H-E1

**Date:** 2026-08-04
**Hypothesis:** H-E1 (EXISTENCE)
**Gate Type:** MUST_WORK
**Gate Result:** PIVOT (FAILED)

## Failure Summary

Signal density feasibility scan for APPS interview problems failed to find a matched subset
where both compile_rate AND test_pass_rate fall in [0.15, 0.45] with Qwen2.5-Coder-7B (G=8).

## Key Metrics

- Sample size: 200 APPS interview problems (seed=42)
- Matched problems (both signals in window): 0 / 200
- Estimated N: 0.0 (threshold: 1000)
- Compile rate mean: 11.6% (11/200 problems in [0.15, 0.45] window)
- Test-pass rate mean: 0.0% (APPS harness environment issue)

## Root Causes

1. **APPS harness environment issue:** `testing_util.reliability_guard()` blocks subprocess
   execution in nested agent context — all unit tests returned False/error.
2. **Compile rate too low:** Mean 11.6% compile rate; only 11/200 problems in the [0.15,0.45]
   window. Even compile-only extrapolates to ~110 problems (below 500 EXPLORE threshold).
3. **Joint window constraint too strict:** Requiring BOTH signals in [15%,45%] simultaneously
   is not achievable given the model's generation quality on APPS interview problems.

## Recommendation for Phase 2A Redesign

1. Widen signal density window to [10%, 55%] — more permissive
2. Switch to APPS `advanced` split — different difficulty distribution
3. Fix APPS harness: use subprocess isolation or alternative test execution
4. Consider compile-only signal density as a proxy metric initially

## Routing

- Routed to: Phase 2A (hypothesis redesign)
- reflection_outcome: ROUTED_TO_PHASE_2A
