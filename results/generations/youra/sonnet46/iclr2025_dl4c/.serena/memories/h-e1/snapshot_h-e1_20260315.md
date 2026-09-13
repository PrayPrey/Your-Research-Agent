# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-03-15T01:30:00Z
**Hypothesis:** h-e1
**Statement:** Under GRPO-based RLEF training with Qwen2.5-Coder-7B on high-S_term APPS problems (S_term > 0.85), substituting R_binary with R_ratio decreases the fraction of training batches receiving zero-reward signal by >=20% and increases gradient SNR by >=1.5x in the first 25% of training steps, because partial-pass solutions receive non-zero R_ratio whereas they receive zero under R_binary.
**Final Status:** FAILED
**Gate Result:** FAIL
**Gate Type:** MUST_WORK
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Results

- Validation: FAIL (both criteria missed)
- Gate 1 (ZRF reduction ≥20%): 0% actual (FAIL)
- Gate 2 (SNR ratio ≥1.5x): 0/0 = undefined (FAIL)
- Reflection: Mechanism not activated — k_pass=0 for all rollouts on competition+interview APPS
- Lessons: S_term >0.85 selects completely intractable problems; R_ratio needs partial solutions to exist

## Cascade

- h-m1: CASCADE_FAILED (blocked by h-e1)
- h-m2: CASCADE_FAILED (blocked by h-e1)
- h-m3: CASCADE_FAILED (blocked by h-e1)

## Next Action

Phase 0 redesign. See failure_h-e1 memory for detailed lessons and redesign recommendations.

---
*Per-hypothesis snapshot for Phase 2A reference*
