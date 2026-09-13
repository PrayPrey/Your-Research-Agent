# Hypothesis Context: h-m2

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-12
**Main Hypothesis:** Tri-Modal Alignment for Code Generation via Dynamic Feedback Integration
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under Phase 2 training (30-70% progress), if AI feedback weight peaks (highest among three signals), then quality scores improve without correctness regression, because AI feedback enables scalable quality refinement beyond what human annotation cost allows.

### Type
MECHANISM

### Rationale
Tests the second step of sequential capability building. Validates that AI feedback effectively scales human preferences for quality optimization during mid-training without sacrificing the correctness established in Phase 1.

---

## Verification Protocol

### Conceptual Test
1. Monitor weight coefficients in Phase 2 (30%, 40%, 50%, 60%, 70% checkpoints).
2. Verify AI weight peaks in Phase 2 (AI_w > max(execution_w, human_w) at some checkpoint ∈ [30%, 70%]).
3. Measure quality score improvement rate in Phase 2 vs. Phases 1 and 3.
4. Verify no correctness regression (pass@1 at 70% ≥ 0.95 × pass@1 at 30%).

### Success Criteria
- Primary: AI weight argmax ∈ [0.3, 0.7] training progress AND quality score improves in Phase 2
- Secondary: Pass@1 does not regress (pass@1_end_phase2 ≥ 0.95 × pass@1_start_phase2)

### Variables
- **Independent Variable:** Training Progress ([30-70%] range), AI Feedback Weight
- **Dependent Variable:** Human Preference Score trajectory, Pass@1 maintenance check
- **Controlled Variables:** Model Architecture (1.5B params), Dataset (HumanEval+MBPP), RL Algorithm (PPO), Evaluation Protocol (N=200 held-out)

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
- **Source:** Pre-trained checkpoint (e.g., CodeGen, StarCoder)
- **Hypothesis Fit:** RL fine-tuning requires pre-trained code model as initialization. 1.5B size balances performance and computational cost (~5000 GPU-hours feasible).

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| PPOCoder (execution feedback RL) | ~30% absolute improvement (40% → 70% pass@1 on MBPP) | MBPP |
| RLHF for Code (human feedback only) | Subjective quality improvement (no quantitative pass@1 reported) | Various code generation tasks |
| Themis (multi-criteria reward model) | Multi-dimensional quality scores (correctness + style + efficiency) | 350K+ preference pairs |

### Baseline Performance
Best single-feedback baseline: PPOCoder (70% pass@1 on MBPP)

### Gap Analysis
- Single-feedback approaches optimize one objective in isolation
- No prior work has successfully demonstrated multi-modal RL with dynamic scheduling in code generation
- Quality improvement vs. correctness trade-off not explicitly addressed in prior work

---

## Dependencies and Gate Conditions

### Prerequisites
- **h-m1**: Phase 1 Execution-Heavy Foundation (0-30% training) MUST pass

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** If AI feedback does not enable quality refinement → Re-evaluate AI reward model quality or switch to human-only Phase 2

**Phase Assignment:** Phase 2 (30-70% training progress)

**Estimated Duration:** Part of 1-2 week mechanism validation phase

---

## Dependency Context

### Relationship to Other Hypotheses
- **Depends on:** h-m1 (requires correctness foundation from Phase 1)
- **Enables:** h-m3 (provides quality-refined model for Phase 3 human feedback refinement)
- **Causal chain position:** Step 2 of 3-phase sequential capability building

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (Phase 2C experiment design)
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. Previous hypothesis (h-m1) validation results for continuation

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use h-m1 baseline to understand Phase 1 → Phase 2 transition
4. Design concrete experiment specification (Level 1.5)
5. Output: docs/youra_research/h-m2/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-M2 (Mechanism)**: Baseline to understand improvement potential in Phase 2 vs Phase 1

---

*Optimized for single-hypothesis experiment design*
