# h-e1_v6 Phase 4 FAIL - frac_3plus threshold too strict

**Status:** Phase 4 COMPLETE 2026-03-19: gate FAIL (MUST_WORK).
**Hypothesis:** H-E1_v6 — n_modes_p Non-Degeneracy Check
**Pipeline:** YouRA / TEST_verifiai / 20260316_verifia / H-BehavioralModeCount-v6
**Archon project_id:** 5b6df674-c051-4a66-99e6-286d9379070b
**Archon hypothesis_task_id:** e61e435b-6f99-4287-aece-5c94d5cfb0fb

## Gate Result: FAIL (0/5 pairs pass frac_3plus ≥ 0.80)

| Pair | N | SD | frac_3plus | Gate |
|------|---|-----|------------|------|
| llama3_humaneval | 164 | 1.294 | 0.707 | FAIL |
| llama3_mbpp | 377 | 1.238 | 0.424 | FAIL |
| deepseek_humaneval | 164 | 1.178 | 0.573 | FAIL |
| deepseek_mbpp | 377 | 1.069 | 0.281 | FAIL |
| codellama_mbpp | 377 | 0.914 | 0.244 | FAIL |

- All 5 pairs PASS sd > 0.5 (metric is non-degenerate in variance sense)
- 0/5 pairs PASS frac_3plus ≥ 0.80 (best: llama3_humaneval = 0.707)

## Root Cause

n_modes_p skews toward 1-2 modes for most problems. With k=5 binary trace profiles:
- Easy problems: all-pass → n_modes_p = 1
- Hard problems: all-fail → n_modes_p = 1
- Partial-competence zone only: n_modes_p ≥ 3
- The partial-competence zone is too narrow (20-40% of problems) for frac_3plus ≥ 0.80 to be achievable.

The 80% threshold was structurally too strict for the discrete binary trace profile construction.

## Routing: ROUTED_TO_PHASE_0

h-e2_v6: CASCADE_FAILED
h-m1_v6: CASCADE_FAILED

## Phase 0 Redesign Suggestions
- Relax to frac_2plus ≥ 0.80 (at least 2 modes)
- Use SD-only non-degeneracy criterion (already passes)
- Redefine n_modes_p with richer trace representation (continuous Hamming diversity)
