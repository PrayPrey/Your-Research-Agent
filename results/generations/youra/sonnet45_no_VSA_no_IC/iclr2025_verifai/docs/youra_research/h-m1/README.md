# Hypothesis h-m1: NL Hint Ablation

**Type**: MECHANISM  
**Gate**: MUST_WORK  
**Status**: Phase 2C COMPLETED  
**Archon Task ID**: 100fc27f-e71c-43b4-abd4-fd896677e021

## Hypothesis Statement

NL hint removal drops LLM success by 25-35 percentage points (tests 60% contribution claim)

## Phase 2C Outputs (COMPLETE)

- `02c_experiment_brief.md` — Comprehensive experiment design specification ✅
- `02b_context.md` — Phase 2B handoff context ✅
- `dataset_spec.yaml` — miniF2F-v2c dataset specification ✅
- `evaluation_protocol.md` — Step-by-step evaluation procedures ✅
- `implementation_notes.md` — Phase 3 handoff details ✅
- `metadata.yaml` — Structured hypothesis metadata ✅
- `experiment_brief.md` — Alias pointer to 02c document ✅
- `README.md` — This file ✅

## Key Design Decisions

1. **Dataset**: miniF2F-v2c (244 test problems, Type: standard, real benchmark)
2. **Ablation Method**: Regex-based removal of `/--! ... -/` docstrings and `-- ...` comments
3. **Evaluation**: LeanCopilot with @32 sampling budget, 300s timeout per problem
4. **Pilot**: 20-problem validation before full run to verify type-checking feasibility
5. **Primary Metric**: Success rate delta (Δ), predicted 30 percentage points

## Expected Outcomes

- **PASS**: Δ ≥ 25% AND p < 0.05 → confirms 60% NL contribution
- **FAIL**: Δ < 10% OR p ≥ 0.05 → rejects NL mechanism hypothesis
- **INCONCLUSIVE**: 10% ≤ Δ < 25% → weaker effect than predicted

## Next Phase

Phase 3 Implementation Planning (PRD, Architecture, PRP generation)
