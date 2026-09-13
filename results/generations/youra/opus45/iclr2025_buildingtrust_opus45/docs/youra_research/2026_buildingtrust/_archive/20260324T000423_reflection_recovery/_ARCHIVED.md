# Archive Record

**Archived:** 2026-03-24T00:04:23 (Reflection Recovery)
**Reason:** ROUTE_TO_0 - Previous run artifacts archived before new Reflection
**Failure Context:**
- h-e1: FAILED (residualized entropy variance 4.98% < 10% threshold, confounds R²=0.9999)
- h-m2: PARTIAL (H_rest mechanism falsified - CoT increases entropy)
- h-e1 limitation: CFS AUROC=0.55 but CI [0.47, 0.63] includes random chance
- h-e1 superseded: Behavioral assumptions invalid (R²=0.877 from confounds)
- SCDM approach (5th attempt): Routed back from Phase 4/5 failure

**Recovery:** Reflection archive recovery executed at Phase 0 re-entry (Section 0.3.5 v7.5.0)

## Previous Attempts Summary

| Attempt | Approach | Failure Mode |
|---------|----------|--------------|
| 1-2 | Entropy residualization | Confounds explain 87.7-99.99% |
| 3 | H_rest sharpening | Wrong direction (CoT increases H_rest) |
| 4 | Attention consistency (CFS) | Marginal signal, CI includes 0.50 |
| 5 | SCDM error detection | Pipeline routed to Phase 0 |

## Archive Contents

- 00_brainstorm_session.md (SCDM approach)
- 01_targeted_research.md, 01_targeted_research_full.md
- 02_synthesis.yaml, 02b_verification_plan.md
- 03_refinement.yaml, 03_refinement.md
- discussion_log.md
- verification_state.yaml
- paper_config.yaml
- phase2a_step_tasks.yaml
- stage1_context_gap1.yaml
- 01_round_table/
- papers/
