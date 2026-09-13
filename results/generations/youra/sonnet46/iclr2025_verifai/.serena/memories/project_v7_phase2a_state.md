---
name: v7 behavioral mode count Phase 2A completion
description: Phase 2A COMPLETE 2026-03-19 (Eleventh Reflection): H-BehavioralModeCount-v7. 16 exchanges, all 6 criteria met. Cross-problem OLS prediction claim. Phase 2B next.
type: project
---

Phase 2A COMPLETE 2026-03-19 (Eleventh Reflection): H-BehavioralModeCount-v7

**Hypothesis:** n_modes_p = len(np.unique(B_p, axis=0)) as cross-problem predictor of pass@1 at k=5

**Why:** v7 fix from v6 failure — replaced frac_3plus with frac_2plus threshold (structurally possible at k=5)

**Sub-hypotheses (5 total):**
- H-E1_v7: frac_2plus ≥ 0.80 with CI_lower ≥ 0.80 in ≥4/5 pairs (MUST_WORK, gate)
- H-E2_v7: |r(n_modes_p, pass@1)| < 0.95 all 5 pairs (MUST_WORK)
- H-M1_v7: OLS β > 0, p < 0.05, ΔR² ≥ 0.02 beyond LOO-difficulty in ≥3/5 pairs (MUST_WORK)
- H-M2_v7: Spearman ρ ≥ 0.10 in partial-competence tier ≥3/5 pairs (MUST_WORK)
- H-M3_v7: incremental ΔR² ≥ 0.005 beyond D_p in ≥3/5 pairs (SHOULD_WORK)

**Archon IDs:**
- Pipeline project: edcd8092-4108-4e67-bef4-27be5433503b
- Phase 2A task: 922bb14a-9bef-44e3-a243-1d2c9e4bd539 (done)

**Output files:** docs/youra_research/20260316_verifia/
- 03_refinement.yaml (25514 bytes) — primary Phase 2B input
- 03_refinement.md (8240 bytes)
- 02_synthesis.yaml (8985 bytes)
- 01_round_table/final_opinions.yaml (8087 bytes)
- discussion_log.md (57681 bytes, 16 exchanges)

**How to apply:** Phase 2B should load 03_refinement.yaml as primary input; all 5 sub-hypotheses defined with explicit gate criteria; adaptive OLS/logistic specification based on VIF diagnostic.
