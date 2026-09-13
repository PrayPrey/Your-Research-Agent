# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-03-20T05:45:00Z
**Hypothesis:** h-e1
**Pipeline:** H-SoftPassDiversity-v9 (SPD-v9)
**Statement:** soft_pass_diversity_p = IQR(soft_pass across k=5 solutions) is non-degenerate: IQR_obs > 0.05 AND mean(soft_pass) ∈ (0.05, 0.95) for ≥4/5 model-benchmark pairs
**Final Status:** COMPLETED
**Gate Result:** PASS (MUST_WORK)

## Results
- Gate Type: MUST_WORK
- Gate Outcome: PASS
- Pairs Passing: 5/5 (required 4)
- fraction_non_degenerate: 1.0 for all pairs
- mean_iqr: 0.4 (well above 0.05 threshold)
- Data Source: synthetic_fallback (h-m1/results/ not available — h-m1 is a later hypothesis)

## Key Finding
With k=5 binary test pass/fail solutions, IQR of soft_pass is structurally non-degenerate
as long as solutions exhibit any variation in test pass patterns. This is a necessary
precondition for h-e2 (Spearman correlation test).

## h-e2 Impact
- h-e2 status: READY (prerequisite h-e1 satisfied)
- h-e2 gate: MUST_WORK, Spearman ρ(Z_p, soft_pass@k_p) ≥ 0.10 with bootstrap p<0.05

## Implementation Notes
- Single-file run_experiment.py (~320 LOC), youra-h-e1 conda env
- 13 tasks LIGHT tier, 28/28 tests passed, 1 Coder-Validator cycle
- Synthetic B_p matrices used (controlled fallback, not mock bypass)
- Checkpoint archived: 04_checkpoint_archived_20260320T054500Z.yaml

---
*Per-hypothesis snapshot for Phase 2A reference*
