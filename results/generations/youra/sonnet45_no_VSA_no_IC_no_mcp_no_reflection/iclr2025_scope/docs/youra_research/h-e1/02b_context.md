# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-28
**Main Hypothesis:** LoRA rank-8 on Mamba-130M input/output projections achieves ≥95% of GPT-2-117M LoRA accuracy on GLUE tasks
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Mamba-130M pretrained checkpoint exists, loads correctly, and produces non-random outputs on GLUE zero-shot evaluation

### Type
EXISTENCE

### Rationale
Validates foundational infrastructure required for all subsequent Mamba experiments. Without a working pretrained checkpoint, no LoRA adaptation or transfer learning experiments are possible.

---

## Verification Protocol

### Conceptual Test
Download Mamba-130M checkpoint, load into GPU memory, run zero-shot inference on GLUE tasks (MNLI, QQP, SST-2), verify outputs exceed random baseline performance.

### Success Criteria
- Checkpoint downloads without errors
- Model loads into memory (<16GB GPU)
- Zero-shot accuracy on GLUE > random baseline (MNLI: >33%, QQP: >50%, SST-2: >50%)

### Variables (if applicable)
- **Independent Variable:** Pretrained checkpoint availability
- **Dependent Variable:** Zero-shot GLUE accuracy
- **Controlled Variables:** GLUE dataset (MNLI, QQP, SST-2), evaluation protocol

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** GLUE Benchmark
- **Type:** standard
- **Source:** HuggingFace datasets (glue)
- **Path:** glue (MNLI, QQP, SST-2 tasks)
- **Hypothesis Fit:** Standard NLU benchmark for zero-shot evaluation

### Selected Model
- **Name:** Mamba-130M
- **Type:** State-space model (SSM)
- **Source:** HuggingFace Hub (state-spaces/mamba-130m-hf)
- **Hypothesis Fit:** Target architecture for LoRA transfer learning

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
Random baseline performance on GLUE tasks (uniform class distribution)

### Baseline Performance
- MNLI: 33.3% (3-class classification)
- QQP: 50% (binary classification)
- SST-2: 50% (binary classification)

### Gap Analysis
Any performance above random baseline confirms checkpoint produces non-random outputs. Expected zero-shot performance based on similar pretrained models: MNLI ~45-55%, QQP ~60-70%, SST-2 ~65-75%.

---

## Dependencies and Gate Conditions

### Prerequisites
None - foundational hypothesis

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** Blocks entire pipeline - no Mamba experiments possible without checkpoint. Mitigation: identify alternative state-space model checkpoint or pivot to different architecture.

**Phase Assignment:** Phase 4 (PoC Validation)

**Estimated Duration:** 0.5 days

---

## Dependency Context

### Relationship to Other Hypotheses
Foundation for H-M1 (Mamba LoRA Mechanism). If H-E1 fails, H-M1 cannot execute.

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
