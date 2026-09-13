---
name: "v7 behavioral mode count Phase 2B completion"
description: "Phase 2B COMPLETE 2026-03-19: H-BehavioralModeCount-v7. 5 sub-hypotheses (H-E1..M3_v7). verification_state.yaml + 02b_verification_plan.md created. Phase 2C doing."
type: project
---

Phase 2B COMPLETE 2026-03-19: H-BehavioralModeCount-v7

**Pipeline:** edcd8092-4108-4e67-bef4-27be5433503b
**Research folder:** docs/youra_research/20260316_verifia/

**Sub-hypotheses (5 total):**
- H-E1_v7: MUST_WORK, READY — frac_2plus >= 0.80 in >=4/5 pairs. Task: 4c80447c
- H-E2_v7: MUST_WORK, READY — |r(n_modes_p, pass@1)| < 0.95 all 5 pairs. Task: e3c120b0
- H-M1_v7: MUST_WORK, NOT_STARTED — OLS delta_R2 >= 0.02 in >=3/5 pairs. Task: a05e977c
- H-M2_v7: SHOULD_WORK, NOT_STARTED — Spearman rho >= 0.10 in partial-competence tier. Task: 13ca9cef
- H-M3_v7: SHOULD_WORK, NOT_STARTED — delta_R2 >= 0.005 beyond D_p in >=3/5 pairs. Task: 264df484

**Key facts:**
- 62% scope reduction via 5 BUILD_ON claims from Phase 2A
- All analyses use existing h-m1 B_p matrices (542 problems × 3 models × k=5)
- Primary risk: R5 low-temperature diversity collapse → H-E1_v7 gate
- No transfer validation needed (not cross-domain)
- Phase 5 skipped (skip_baseline_comparison=true in module.yaml)

**Archon tasks:**
- Phase 2B: 7d85e834 (done)
- Phase 2C: a6a7a630 (doing)

**Why:** Phase 2B planning for v7 after v6 H-E1 frac_3plus threshold failure. v7 recalibrates to frac_2plus >= 0.80. Eleventh iteration of the pipeline.
**How to apply:** When resuming pipeline, check verification_state.yaml for READY hypotheses. H-E1_v7 and H-E2_v7 are READY — start Phase 2C for these two in parallel.
