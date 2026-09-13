# Phase 4 Failure Record: H-E1_v7

**Date:** 2026-03-20
**Hypothesis:** H-E1_v7 — Behavioral Mode Count Non-Degeneracy Check (frac_2plus >= 0.80)
**Gate Type:** MUST_WORK
**Gate Result:** FAIL (1/5 pairs pass, threshold=4)
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Experiment Results

| Pair | frac_2plus | ci_lower | ci_upper | SD | Gate |
|------|-----------|---------|---------|-----|------|
| llama3_humaneval | 0.890 | 0.841 | 0.939 | 1.294 | PASS |
| llama3_mbpp | 0.714 | 0.668 | 0.753 | 1.238 | FAIL |
| deepseek_humaneval | 0.848 | 0.793 | 0.902 | 1.178 | FAIL (ci_lower=0.793 < 0.80) |
| deepseek_mbpp | 0.592 | 0.541 | 0.642 | 1.069 | FAIL |
| codellama_mbpp | 0.605 | 0.560 | 0.650 | 0.914 | FAIL |

## Root Causes

1. **MBPP+ pairs fail badly**: frac_2plus = 0.59-0.71, far below 0.80 threshold
   - MBPP problems produce less behavioral diversity at k=5
   - Simple MBPP problems concentrate at n_modes=1

2. **deepseek_humaneval borderline**: frac_2plus=0.848 passes frac but ci_lower=0.793 fails CI gate
   - v7's dual-threshold (frac AND ci_lower both >= 0.80) is stricter than v6

3. **HumanEval+ >> MBPP+ in behavioral diversity**: Only humaneval pairs approach threshold

## Lessons Learned

- frac_2plus >= 0.80 threshold with ci_lower >= 0.80 is too strict for MBPP+ at k=5
- Consider benchmark-specific thresholds in Phase 0 redesign
- Or lower overall threshold to 0.65 or 0.70
- Or require k>5 to increase behavioral diversity
- The n_modes_p mechanism IS activated (SD > 0.9 in all pairs, non_trivial=True)
  — the EXISTENCE threshold is simply miscalibrated

## Cascade Effects

- h-m1_v7: CASCADE_FAILED (prereq: h-e1_v7 PASS)
- h-m2_v7: CASCADE_FAILED (prereq: h-m1_v7)
- h-m3_v7: CASCADE_FAILED (prereq: h-m1_v7)
- h-e2_v7: independent (no dependency on h-e1_v7)
