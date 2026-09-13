# Hypothesis Context: h-e1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-18
**Main Hypothesis:** Sequential Single-Source Feedback Routing
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under HumanEval benchmark conditions with K=20 baseline sample classification, dual-sensitive programming tasks (where ≥1 solution fails mypy but passes visible tests AND ≥1 passes mypy but fails visible tests) exist in sufficient quantity (N ≥ 20) with adequate within-task paired variance (SD ≤ 1.0) to support paired-comparison experimental design for feedback routing causality testing.

### Type
EXISTENCE

### Rationale
This hypothesis validates the foundational assumption that a sufficient pool of dual-sensitive tasks exists. Without N≥20 qualifying tasks with controlled variance, the entire cascade routing research program cannot proceed. The dual-sensitivity requirement ensures tasks are amenable to static vs. execution feedback differentiation.

---

## Verification Protocol

### Conceptual Test
1. Run K=20 baseline samples per HumanEval task using CodeLlama-7B
2. Classify each sample with mypy --strict and pytest (HumanEval+ augmented tests)
3. Identify dual-sensitive tasks: ≥1 solution fails mypy but passes tests AND ≥1 passes mypy but fails tests
4. Compute within-task variance (SD) across K=20 samples
5. Count qualifying tasks (N) meeting both dual-sensitivity AND SD≤1.0

### Success Criteria
- **Primary:** N ≥ 20 dual-sensitive tasks identified
- **Secondary:** Within-task SD ≤ 1.0 (power assumption for paired tests)
- **Expected:** ~30-50 tasks qualify (HumanEval has 164 total tasks)

### Variables
- **Independent Variable:** Task selection from HumanEval (164 tasks)
- **Dependent Variable:** Dual-sensitivity classification outcome (binary per task)
- **Controlled Variables:** K=20 samples, CodeLlama-7B model, mypy --strict, HumanEval+ tests

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** HumanEval with HumanEval+ augmented tests
- **Type:** standard
- **Source:** evalplus Python package (pip install evalplus)
- **Path:** Built-in task loader from evalplus
- **Hypothesis Fit:** 164 tasks with 80+ robustness tests per task. HumanEval+ provides classification-evaluation decoupling (classify with K=20 baseline, evaluate with 80+ tests).

### Selected Model
- **Name:** CodeLlama-7B
- **Type:** Base code generation model (7B parameters)
- **Source:** HuggingFace: codellama/CodeLlama-7b-hf
- **Hypothesis Fit:** Base model tests feedback routing mechanism without instruction-tuning confounds. Widely used baseline with <30min inference time.

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
- **Naive Aggregation (Both-Source Concatenation):** Run mypy --strict + pytest each iteration, concatenate both outputs
- **Single-Source Execution-Only (PerfCodeGen methodology):** Execution feedback only (pytest), matching prior work

### Baseline Performance
- Expected iterations-to-solution: 3-5 iterations (PerfCodeGen reports σ≈1.0)
- HumanEval pass@k baseline: ~13% for CodeLlama-7B base model

### Gap Analysis
No prior work tests feedback routing policies. All 22 directly relevant sources (Phase 1) use single feedback type only. This research fills the orchestration gap.

---

## Dependencies and Gate Conditions

### Prerequisites
None (Level 0 - Root hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** STOP - Insufficient task pool for experimental design

**Phase Assignment:** Phase 1: Foundation

**Estimated Duration:** 2 weeks (Week 1-2)

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the root hypothesis (Level 0). All downstream hypotheses (H-M1, H-M2, H-M3, H-C1) depend on H-E1 validation. If H-E1 fails, the entire verification pipeline stops.

**Blocks:**
- H-M1 (Level 1): Mypy error detection rate mechanism
- H-M2 (Level 2): Sequential presentation attention economy
- H-M3 (Level 2): Conditional gating token efficiency
- H-C1 (Level 3): Model size boundary conditions

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

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
