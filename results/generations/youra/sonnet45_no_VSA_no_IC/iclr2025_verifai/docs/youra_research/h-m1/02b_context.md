# Phase 2B Context for h-m1
# NL Hint Ablation

**Generated**: 2026-08-20T04:17:00Z  
**From**: Phase 2B Verification Planning  
**Parent Workflow**: H-MechanisticBaseline-v1  
**Archon Task ID**: 100fc27f-e71c-43b4-abd4-fd896677e021

---

## Hypothesis Statement

**h-m1**: NL hint removal drops LLM success by 25-35 percentage points (tests 60% contribution claim)

**Type**: MECHANISM  
**Gate**: MUST_WORK  
**Priority**: HIGH (core mechanistic claim)

---

## From Phase 2B Planning

### Predicted Effect
- **Baseline (with NL)**: 65% success rate
- **Ablated (no NL)**: 35% success rate
- **Delta**: 30 percentage points

### Falsification Criterion
IF Δ < 10%, reject 60% NL contribution claim

### Risk Assessment
**Risk Level**: MEDIUM

**Key Risk**: NL comment removal may break Lean type-checking if comments are semantically load-bearing

**Mitigation**: 
- 20-problem pilot validation BEFORE full run
- Verify ablated code compiles with `lake build`
- Fallback: Pivot to informal Mathlib documentation removal (external docs only)

---

## Prerequisites

**None** — h-m1 is independent from H-E1 baseline measurement

Can execute in parallel with H-E1, H-M2, H-M3, H-C1

---

## Dependencies (Downstream)

No blocking dependencies for Phase 2C experiment design

---

## Main Hypothesis Context

**Main Hypothesis**: H-MechanisticBaseline-v1  
**Confidence**: 0.78

**Core Claim**:  
LLM-guided theorem proving (65%) vs automated provers (15%) gap explained by 3 mechanisms:
1. **Natural language understanding** (60% of gap) ← **h-m1 tests THIS**
2. **Long-range proof search** (30% of gap) ← h-m2 tests this
3. **Corpus pattern matching** (10% of gap) ← h-m3 tests this

**h-m1 Role**: Tests the PRIMARY mechanism (60% attribution) via controlled ablation

---

## Phase 2C Requirements

### Must Specify
1. **Dataset**: Real benchmark (no synthetic data)
2. **Ablation method**: How to remove NL hints without breaking Lean
3. **Pilot validation**: 20-problem feasibility check
4. **Evaluation protocol**: LeanCopilot configuration (@32 sampling, 300s timeout)
5. **Statistical analysis**: McNemar's test (paired proportions), 95% CI
6. **Falsification criteria**: Δ thresholds for PASS/FAIL/INCONCLUSIVE

### Expected Outputs
1. `02c_experiment_brief.md` (comprehensive design)
2. `dataset_spec.yaml` (miniF2F-v2c specification)
3. `evaluation_protocol.md` (step-by-step evaluation)
4. `implementation_notes.md` (Phase 3 handoff details)
5. `metadata.yaml` (structured hypothesis metadata)

---

## Phase 2C Handoff

**Status**: Phase 2B verification planning complete  
**Next Step**: Design experiment in Phase 2C (experiment_brief.md)  
**Gate**: MUST_WORK — failure blocks entire mechanistic attribution framework
