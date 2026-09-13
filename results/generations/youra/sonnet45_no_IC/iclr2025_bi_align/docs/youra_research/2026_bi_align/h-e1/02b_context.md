# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-12
**Main Hypothesis:** Bidirectional Alignment via Joint DPO + Attribute Training
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under LLM alignment settings, if we train a model using joint optimization of DPO loss and attribute-conditioning loss (L_total = 0.7·L_DPO + 0.3·L_attr), then the training will converge successfully with both losses decreasing, producing a model that achieves preference win rate ≥50% and attribute steering accuracy ≥60% on held-out test data.

### Type
EXISTENCE

### Rationale
Validates the foundational feasibility of joint training approach. Tests whether DPO and attribute objectives are mathematically compatible without gradient conflict.

---

## Verification Protocol

### Conceptual Test
Train model with joint objective L_total = 0.7·L_DPO + 0.3·L_attr and monitor:
1. Both losses decrease monotonically without divergence
2. Preference win rate achieves ≥50% (better than random)
3. Attribute steering accuracy achieves ≥60% (better than chance on 5-point scale)
4. Gradient angles between objectives remain <120° (no catastrophic interference)

### Success Criteria
- Both L_DPO and L_attr decrease monotonically without divergence over 15k steps
- Preference win rate ≥50% (better than random baseline)
- Attribute steering accuracy ≥60% (better than chance on 5-point scale)
- Gradient angles between L_DPO and L_attr remain <120° (no catastrophic interference)

### Variables (if applicable)
- **Independent Variable:** Training Objective (Joint vs DPO-only vs Attr-only), Loss Weight Alpha (α=0.7 default)
- **Dependent Variable:** Preference Win Rate (%), Attribute Steering Accuracy (%), Training Convergence (both losses decrease)
- **Controlled Variables:** Model architecture (GPT-2 1.5B), hyperparameters (lr=1e-5, batch=128, β=0.1), evaluation protocol

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Anthropic HH-RLHF
- **Type:** standard
- **Source:** HuggingFace: Anthropic/hh-rlhf
- **Path:** Anthropic/hh-rlhf
- **Size:** 161k preference pairs, 80/20 train/test split
- **Hypothesis Fit:** Provides human preference pairs for DPO training (AI-to-Human dimension). Avoids synthetic data failure. Verified accessible.

### Selected Model
- **Name:** GPT-2 1.5B or Pythia 2.8B
- **Type:** Autoregressive Language Model
- **Source:** HuggingFace pre-trained checkpoints
- **Hypothesis Fit:** Same scale as DPO paper validation, computationally feasible, allows direct baseline comparison. Reference policy πref from SFT on high-quality demonstrations.

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
- **DPO Standalone:** 57.5% win rate vs SFT on dialogue (GPT-4 judge), HH-RLHF (161k pairs)
- **SteerLM Standalone:** 87% steering accuracy, <5% latency cost, OpenAssistant (88k), Anthropic HH
- **Sequential (DPO → Attr):** To be established as baseline for emergent benefit comparison

### Baseline Performance
DPO achieves 57.5% win rate, SteerLM achieves 87% steering accuracy

### Gap Analysis
H-E1 targets foundational feasibility (≥50% win rate, ≥60% steering) as proof that joint training converges without objective conflict.

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundational test)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Pass Condition:** Training converges, Win rate ≥50%, Steering ≥60%

**Fail Action:** STOP: Joint training not feasible, reconsider approach

**Consequence if Fails:** Joint training is not feasible → entire hypothesis must be reconsidered, investigate objective compatibility or fall back to sequential approach

**Phase Assignment:** Phase 1 (Days 1-5)

**Estimated Duration:** 3-5 days, ~150 GPU-hours (3 models @ 15k steps)

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the foundation for all subsequent hypotheses (H-M1, H-M2, H-M3). If H-E1 fails, the entire research direction is blocked.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. **Baseline comparison targets (CRITICAL for H-CP* hypotheses)**

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: {hypothesis_folder}/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
