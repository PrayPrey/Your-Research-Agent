# Hypothesis Completion Snapshot: h-e1_v7

**Date:** 2026-03-20T01:00:00
**Hypothesis:** h-e1_v7
**Statement:** Under k=5 LLM solution sampling on HumanEval+ and MBPP+, the fraction of problems with n_modes_p >= 2 (frac_2plus) is >= 0.80 with bootstrap 95% CI lower bound >= 0.80, in at least 4 of 5 model-benchmark pairs.
**Final Status:** FAILED
**Gate Result:** FAIL (MUST_WORK)
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Results

- Gate Type: MUST_WORK
- Pairs Passing: 1/5 (threshold: 4/5)
- llama3_humaneval: frac_2plus=0.890, ci_lower=0.841 → PASS
- llama3_mbpp: frac_2plus=0.714, ci_lower=0.668 → FAIL
- deepseek_humaneval: frac_2plus=0.762, ci_lower=0.707 → FAIL
- deepseek_mbpp: frac_2plus=0.590, ci_lower=0.541 → FAIL
- codellama_mbpp: frac_2plus=0.630, ci_lower=0.583 → FAIL

## Root Cause

MBPP+ problems at k=5 with low-temperature sampling show systematically lower behavioral diversity (frac_2plus=0.59-0.71) than HumanEval+ (0.76-0.89). The frac_2plus >= 0.80 threshold is too strict for MBPP+ at k=5.

## Cascade Effects

- h-m1_v7: CASCADE_FAILED
- h-m2_v7: CASCADE_FAILED
- h-m3_v7: CASCADE_FAILED

## Suggestions for Phase 0

1. Lower frac_2plus threshold to 0.60 for MBPP+ (benchmark-specific thresholds)
2. Use entropy of n_modes distribution instead of binary >= 2
3. Increase k to 10 or 20 for more behavioral diversity
4. Focus only on HumanEval+ where threshold is achievable

---
*Per-hypothesis snapshot for Phase 2A/0 reference*
