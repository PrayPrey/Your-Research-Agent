# Hypothesis Context: h-m1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-18
**Main Hypothesis:** H-SeqRouting-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under dual-sensitive programming task conditions (N=20 from H-E1), if mypy --strict static analysis is applied before execution feedback in cascade routing, then ~30-40% of errors are caught instantly with zero execution cost, because mypy provides compositional type safety guarantees (type errors, null safety, signature mismatches) without requiring test execution.

### Type
MECHANISM

### Rationale
This hypothesis tests the foundational mechanism of cascade routing: whether static analysis provides sufficient early error detection to justify the cascade approach. If mypy cannot catch a meaningful proportion of errors, the entire cascade strategy loses its primary value proposition.

---

## Verification Protocol

### Conceptual Test
Run mypy --strict on dual-sensitive tasks and measure the proportion of errors caught before test execution. Compare error detection rate against execution feedback to validate the "instant catch with zero execution cost" claim.

### Success Criteria
- Mypy error detection rate ≥30% (MUST_WORK gate threshold)
- Target: 30-40% error detection
- Measured on N=20 dual-sensitive tasks from H-E1

### Variables
- **Independent Variable:** Feedback source (mypy --strict vs pytest execution)
- **Dependent Variable:** Error detection rate (%)
- **Controlled Variables:** Task set (N=20 dual-sensitive), model (CodeLlama-7B), token budget (1000/source)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** HumanEval with HumanEval+ augmented tests
- **Type:** standard
- **Source:** evalplus Python package (pip install evalplus)
- **Path:** Built-in task loader
- **Hypothesis Fit:** 164 tasks with 80+ robustness tests per task, classification-evaluation decoupling enables dual-sensitive task identification

### Selected Model
- **Name:** CodeLlama-7B
- **Type:** Base code generation model (7B parameters)
- **Source:** HuggingFace: codellama/CodeLlama-7b-hf
- **Hypothesis Fit:** Tests feedback routing on base models (not instruction-tuned), <30min inference time

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
- Naive Aggregation (Both-Source Concatenation): Run mypy --strict + pytest each iteration, concatenate both outputs
- Single-Source Execution-Only (PerfCodeGen methodology): Execution feedback only (pytest), matching prior work

### Baseline Performance
PerfCodeGen reports σ ≈ 1.0 for iteration variance on HumanEval tasks. No prior work has measured static analysis error detection rate in LLM code generation.

### Gap Analysis
No existing work quantifies mypy's contribution to error detection in LLM-generated code. This hypothesis fills that gap by measuring the proportion of errors catchable without test execution.

---

## Dependencies and Gate Conditions

### Prerequisites
- h-e1 (EXISTENCE): COMPLETED ✅
  - Validated: N=35 dual-sensitive tasks (target: 20)
  - Task pool available for mechanism testing

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** PIVOT - Static analysis provides minimal value, cascade loses justification. Consider execution-first routing or abandon cascade hypothesis.

**Phase Assignment:** Phase 2 (Mechanisms)

**Estimated Duration:** 2 weeks (W3-4 from timeline)

---

## Dependency Context

### Relationship to Other Hypotheses
h-m1 is the foundational mechanism hypothesis that blocks all downstream hypotheses:
- h-m2 (Sequential presentation) depends on h-m1's validation that static analysis provides value
- h-m3 (Conditional gating efficiency) depends on h-m1's validation that mypy catches errors
- h-c1 (Boundary conditions) requires all mechanisms (h-m1, h-m2, h-m3) to validate scope

If h-m1 FAILS (mypy error detection <20%), the entire cascade routing hypothesis loses justification and workflow STOPS.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (set by hypothesis loop)
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation (h-e1 COMPLETED)
3. Dependency information for controlled experiments
4. Success criteria for evaluation design (≥30% error detection)
5. Baseline comparison targets (aggregation vs execution-only)

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: h-m1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential ← THIS HYPOTHESIS
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
