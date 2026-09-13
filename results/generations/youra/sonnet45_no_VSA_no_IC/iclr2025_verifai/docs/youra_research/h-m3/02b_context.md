# Phase 2B Context: H-M3

**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Prerequisites:** [H-E1] (COMPLETED)

---

## Hypothesis Statement

Random Mathlib tactic sampling achieves 18-25% success (Δ=5% above lean-auto, tests 10% corpus contribution)

---

## Context from Phase 2B

**Source:** 02b_verification_plan.md (lines 114-138)

### Gate Condition
SHOULD_WORK (control baseline for triangulation)

### Prerequisites
- **H-E1** (lean-auto baseline): COMPLETED
  - Success rate: 15.6% [11.5%, 20.3%]
  - Tactic count: mean=9.2±4.1
  - Infrastructure validated

### Risk Assessment
**Risk Level:** MEDIUM
- **Corpus bias acknowledged**: Random sampling from human-written proofs ≠ uniform distribution
- **Mitigation**: Used as THIRD baseline for triangulation (lean-auto | Random | LLM)
- **Custom implementation required**: Random tactic sampler from Mathlib distribution

### Predicted Effect
- Random Mathlib: 20%
- lean-auto: 15%
- Delta: 5 percentage points (corpus contribution)

### Falsification Criteria
IF Random < 15% OR > 30%, reject 10% contribution claim

---

## Mechanistic Role

**Tests:** Corpus pattern matching contribution (10% of main hypothesis gap)

**Mechanism Attribution:**
- Main hypothesis predicts 50% gap (LLM 65% vs lean-auto 15%)
- Decomposition:
  - NL understanding: 60% of gap (30 pp)
  - Proof depth: 30% of gap (15 pp)
  - **Corpus patterns: 10% of gap (5 pp)** ← H-M3 tests this

**Control Purpose:**
- Provides THIRD baseline for triangulation
- Isolates tactic frequency effect (no semantic understanding)
- Lower bound on corpus contribution (random goal selection)

---

## Phase 2C Transition

**Ready for Experiment Design:** Yes

**Carry-Forward from H-E1:**
- miniF2F dataset (244 problems) validated
- Evaluation infrastructure (parallel workers, timeout=300s)
- Tactic budget baseline (recommend 15 evaluations)

**New Requirements:**
- Tactic distribution extraction (from Mathlib corpus or literature)
- Random sampler implementation (weighted sampling + random goal selection)
- Statistical comparison (z-test vs H-E1 baseline)
