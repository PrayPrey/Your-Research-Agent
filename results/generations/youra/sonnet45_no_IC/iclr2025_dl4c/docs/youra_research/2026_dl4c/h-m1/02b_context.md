# Hypothesis Context: h-m1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-12
**Main Hypothesis:** Tri-Modal Alignment for Code Generation via Dynamic Feedback Integration
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under Phase 1 training (0-30% progress), if execution feedback weight is highest among three signals, then basic correctness (pass@1) improves fastest in early training, because functional code must be established before quality optimization can proceed.

### Type
MECHANISM

### Rationale
Tests the first step of sequential capability building mechanism. Validates that execution-heavy weighting in early training establishes the correctness foundation required for later quality optimization.

---

## Verification Protocol

### Conceptual Test
1. Monitor weight coefficients at checkpoints (0%, 10%, 20%, 30% training progress).
2. Verify execution weight > AI weight > human weight throughout Phase 1.
3. Measure pass@1 improvement rate in Phase 1 vs. Phases 2-3.
4. Compare against static-weight baseline (all weights equal throughout training).

### Success Criteria
- Primary: Execution weight is highest in Phase 1 (execution_w > max(AI_w, human_w)) AND pass@1 improvement rate in Phase 1 > Phases 2-3
- Secondary: Pearson correlation between execution weight and training step is negative (ρ < -0.6)

### Variables (if applicable)
- **Independent Variable:** Training Progress ([0-30%] range), Execution Weight (coefficient for execution feedback signal)
- **Dependent Variable:** Pass@1 trajectory (correctness improvement over training steps in Phase 1)
- **Controlled Variables:** Model Architecture (1.5B params), Dataset (HumanEval+MBPP), RL Algorithm (PPO), Evaluation Protocol (N=200 held-out, independent blind annotators)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** HumanEval + MBPP
- **Type:** standard
- **Source:** OpenAI HumanEval (164 problems) + Google MBPP (500 problems)
- **Path:** https://github.com/openai/human-eval, https://github.com/google-research/google-research/tree/master/mbpp
- **Hypothesis Fit:** Competitive programming tasks with automated test cases for execution feedback. Well-established benchmarks for code generation evaluation.

### Selected Model
- **Name:** 1.5B Parameter Code LLM
- **Type:** Transformer decoder (Codex-style architecture)
- **Source:** Pre-trained checkpoint (e.g., CodeGen, StarCoder) - use existing foundation model
- **Hypothesis Fit:** RL fine-tuning requires pre-trained code model as initialization. 1.5B size balances performance and computational cost (~5000 GPU-hours feasible).

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
- PPOCoder (execution feedback RL): ~30% absolute improvement (40% → 70% pass@1 on MBPP)
- RLHF for Code (human feedback only): Subjective quality improvement (no quantitative pass@1 reported)
- Themis (multi-criteria reward model): Multi-dimensional quality scores (correctness + style + efficiency)

### Baseline Performance
Best single-feedback baseline: PPOCoder with ~70% pass@1 on MBPP after execution feedback training

### Gap Analysis
Sequential capability building hypothesis suggests that execution-heavy weighting in early training (Phase 1: 0-30%) is critical for establishing the correctness foundation that enables later quality optimization.

---

## Dependencies and Gate Conditions

### Prerequisites
h-e1 (EXISTENCE hypothesis - tri-modal framework must be validated first)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** Weight schedule is not phase-appropriate → Revise dynamic scheduling mechanism (may need simpler schedule or different phase boundaries)

**Phase Assignment:** Phase 2C → 3 → 4

**Estimated Duration:** 1-2 weeks (mechanism validation)

---

## Dependency Context

### Relationship to Other Hypotheses
H-M1 tests the first step (Phase 1: 0-30%) of the 3-phase sequential capability building mechanism. It depends on H-E1 establishing that tri-modal integration works. H-M2 and H-M3 build on this to test Phases 2 and 3 respectively.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS
**Workflow Status:** PHASE_4_COMPLETE (h-e1 completed, h-m1 starting)

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
5. Output: h-m1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
