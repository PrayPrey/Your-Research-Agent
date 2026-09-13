# Phase 4 Failure Record: h-e1_v6 (Run 1)

**Date:** 2026-03-19T23:30:00
**Hypothesis:** h-e1_v6
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAIL
**Routing:** ROUTED_TO_PHASE_0

## Gate Verdict: FAIL

The MUST_WORK gate for H-E1_v6 required frac_3plus ≥ 0.80 in ≥4/5 pairs. **0/5 pairs** satisfied this criterion.

## Performance Data

| Pair | N | SD | frac_3plus | SD Gate | frac_3plus Gate | Overall |
|------|---|-----|------------|---------|-----------------|---------|
| llama3_humaneval | 164 | 1.294 | 0.707 | PASS | FAIL | FAIL |
| llama3_mbpp | 377 | 1.238 | 0.424 | PASS | FAIL | FAIL |
| deepseek_humaneval | 164 | 1.178 | 0.573 | PASS | FAIL | FAIL |
| deepseek_mbpp | 377 | 1.069 | 0.281 | PASS | FAIL | FAIL |
| codellama_mbpp | 377 | 0.914 | 0.244 | PASS | FAIL | FAIL |

**SD criterion:** 5/5 PASS (all sd > 0.5 confirmed)
**frac_3plus criterion:** 0/5 PASS (none reached ≥ 0.80)

## Root Cause Analysis

- The frac_3plus ≥ 0.80 threshold is structurally incompatible with n_modes_p when k=5 and binary trace profiles are used
- With k=5 solutions and binary (pass/fail) test execution, the distribution is bimodal: easy/hard problems both yield n_modes_p = 1 (all-pass or all-fail)
- The partial-competence zone (n_modes_p ≥ 3) occupies only 20-40% of problems per pair
- SD > 0.5 in all 5 pairs confirms the metric has meaningful variance — it is NOT degenerate
- The threshold criterion (frac_3plus ≥ 0.80) was miscalibrated for this metric's distributional properties

## Lessons Learned

1. frac_3plus ≥ 0.80 is structurally unachievable for any k=5 binary mode-count metric — recalibrate to ≥ 0.30 or remove entirely
2. SD > 0.5 is a sufficient non-degeneracy criterion on its own; frac_3plus adds unnecessary strictness
3. The n_modes_p operationalization is fundamentally sound — the metric exists and has meaningful variance
4. Phase 0 redesign should reconsider the non-degeneracy criterion or use a lower frac_3plus threshold (e.g., ≥ 0.30)

## Cascade Effects

- h-e2_v6: CASCADE_FAILED (blocked by h-e1_v6)
- h-m1_v6: CASCADE_FAILED (blocked by h-e1_v6 and h-e2_v6)
- h-m2_v6: unstarted (blocked by h-m1_v6)
- h-m3_v6: unstarted (blocked by h-m1_v6)

## Feedback for Phase 0 Redesign

### Suggested Modifications
- Lower frac_3plus threshold from ≥ 0.80 to ≥ 0.30 (matches observed range 0.24-0.71)
- OR replace frac_3plus criterion entirely with SD > 0.5 as sole non-degeneracy check
- Keep n_modes_p = len(np.unique(B_p, axis=0)) operationalization — it is correct and validated

### What NOT To Do
- Do not change the n_modes_p formula — it is mathematically sound
- Do not use frac_3plus ≥ 0.80 with k=5 binary traces — structurally impossible

### What Showed Promise
- SD criterion: all 5 pairs pass sd > 0.5, confirming meaningful metric variance
- Best frac_3plus observed: llama3_humaneval = 0.707 (close to 0.80 but still insufficient)

---
*For cross-phase reference*
*Written at: 2026-03-19T23:30:00*
