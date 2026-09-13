# Hypothesis Context: H-M3

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-12
**Main Hypothesis:** Tri-Modal Alignment for Code Generation via Dynamic Feedback Integration
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under Phase 3 training (70-100% progress), if human feedback weight increases, then edge case performance improves (conflict cases resolve to intermediate preference scores [0.1-0.4], not extreme collapse to execution-only behavior), because human feedback corrects systematic AI biases and fine-tunes quality on difficult cases.

### Type
MECHANISM

### Rationale
Tests the third step of sequential capability building. Validates that human feedback provides precision refinement in late training, preventing AI reward model biases from dominating final model behavior, particularly on conflict cases where code is correct but low-quality.

---

## Verification Protocol

### Conceptual Test
1. Monitor weight coefficients in Phase 3 (70%, 80%, 90%, 100% checkpoints).
2. Verify human weight increases in Phase 3 (positive correlation with training progress in [70%, 100%]).
3. Identify 50 conflict cases (pass@1 = 1.0, human_preference < 0.3 in execution-only baseline).
4. Measure tri-modal model preference scores on conflict cases and compare distribution to execution-only baseline.

### Success Criteria
- Primary: Human weight shows positive correlation in Phase 3 AND conflict case median preference ∈ [0.1, 0.4] (not collapsed to [0.0, 0.1])
- Secondary: Human weight at 100% > human weight at 70%

### Variables
- **Independent Variable:** Training Progress ([70-100%] range), Human Feedback Weight
- **Dependent Variable:** Edge Case Performance (preference scores on conflict cases where pass@1=1.0 but human_preference_baseline < 0.3)
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
- **Hypothesis Fit:** Competitive programming tasks with automated test cases (execution feedback available). Well-established benchmarks for code generation evaluation.

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
- **PPOCoder (execution feedback RL):** ~30% absolute improvement (40% → 70% pass@1 on MBPP)
- **RLHF for Code (human feedback only):** Subjective quality improvement (no quantitative pass@1 reported)
- **Themis (multi-criteria reward model):** Multi-dimensional quality scores (correctness + style + efficiency) on 350K+ preference pairs

### Baseline Performance
Execution-only baseline expected: ~70% pass@1 on MBPP, low human preference scores on conflict cases (median < 0.3)

### Gap Analysis
Current single-feedback approaches lack precision on edge cases. Execution-only models produce correct but low-quality code. Human feedback is needed to fine-tune quality on difficult cases.

---

## Dependencies and Gate Conditions

### Prerequisites
- H-M2 (Phase 2 AI-feedback quality refinement must be validated first)

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** If human feedback is not improving edge cases → Investigate annotation quality (check inter-annotator agreement) or increase human feedback sample size

**Phase Assignment:** Phase 3 (70-100% training progress)

**Estimated Duration:** 1-2 weeks (part of mechanism validation phase)

---

## Dependency Context

### Relationship to Other Hypotheses
H-M3 is the third step in a linear causal chain: H-E1 → H-M1 → H-M2 → H-M3. It tests the final phase of sequential capability building (correctness → quality → edge cases). Requires H-M2 to pass first (quality refinement must be established before edge case precision can be tested).

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** Will be updated by Phase 2C
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
