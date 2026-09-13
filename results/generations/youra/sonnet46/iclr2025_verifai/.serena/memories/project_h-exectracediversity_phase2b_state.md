---
name: h-ExecTraceDiversity Phase 2B completion
description: Phase 2B COMPLETE 2026-03-19 (TEST_verifiai/20260316_verifia): 5 sub-hypotheses (H-E1 PROVEN + H-M1..H-M4). verification_state.yaml created. H-M1 READY. Phase 2C next.
type: project
---

Phase 2B COMPLETE 2026-03-19 for H-ExecTraceDiversity-v2 in TEST_verifiai pipeline.

**Why:** Phase 2A generated hypothesis H-ExecTraceDiversity-v2 (D_p as pass@k predictor). Phase 2B decomposes into sub-hypotheses and creates verification roadmap.

**How to apply:** Next phase is Phase 2C experiment design starting with H-M1 (READY, no prerequisites). Read verification_state.yaml for full state.

## Key Facts

- **Hypothesis**: H-ExecTraceDiversity-v2 (confidence 0.72)
- **Research folder**: docs/youra_research/20260316_verifia/
- **Pipeline Project ID**: 94413f02-017b-4434-b4ff-c60aef5de9bb
- **Phase 2B task ID**: eff80f1b-7fe9-43ed-9465-143244f2864d (done)
- **Phase 2C task ID**: 3ba64163-0c68-4ccf-bb5d-6f861bcdf0a2 (doing)

## Sub-Hypotheses

| ID | Type | Gate | Status | Archon Task ID |
|----|------|------|--------|----------------|
| H-E1 | EXISTENCE | MUST_WORK | VALIDATED (PROVEN) | c9887be8-e932-4f26-b178-8f85a7a72e34 |
| H-M1 | MECHANISM | MUST_WORK | READY | c80a950a-0523-4880-8462-5e525d068ce9 |
| H-M2 | MECHANISM | MUST_WORK | NOT_STARTED | 229778df-ba04-4662-a197-0a1afd19715e |
| H-M3 | MECHANISM | MUST_WORK (PRIMARY) | NOT_STARTED | fb509c55-6ea0-4fe8-8f41-6f4ba5d3b02b |
| H-M4 | MECHANISM | SHOULD_WORK | NOT_STARTED | 56db64c8-71b2-4270-ae58-a082525d8c91 |

## Scope Reduction

- 40% scope reduction: H-E1 already proven (h-e1 Phase 4 PASS), B_p matrices, pass@1, tiers are BUILD_ON
- NEW verification needed: H-M1 (pipeline), H-M2 (OLS), H-M3 (within-tier Spearman), H-M4 (entropy)

## Critical Path

H-E1[PROVEN] → H-M1 → H-M2+H-M3 (parallel) → H-M4
- H-M3 is the PRIMARY gate (MUST_WORK; fail → ROUTE_TO_PHASE_0)
- H-M4 is SHOULD_WORK (failure does not block)
- Total: 5 weeks

## Key Statistical Design

- H-M2: OLS beta(D_p) > 0, p < 0.05 after pass@1 covariate, ≥3/5 pairs
- H-M3: Spearman ρ ≥ 0.20, bootstrap CI excludes 0, ≥3/5 pairs AND ≥2/3 models (dual gate)
- H-M4: Hierarchical ΔR² — joint contribution OR D_p subsumes H_p (≥90% of combined R²)

## Files Generated

- 02b_verification_plan.md — full verification plan with DAG, Gantt, risk analysis, dialectical analysis
- verification_state.yaml — pipeline state with all 5 sub-hypotheses and hypothesis_task_mapping
