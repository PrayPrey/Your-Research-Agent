# Hypothesis Context: h-m3

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-18
**Main Hypothesis:** Sequential Single-Source Feedback Routing
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under cascade routing conditions (N=20 from H-E1), if pytest execution is conditionally gated (run only when mypy clean) instead of always running (aggregation), then tokens-per-successful-task remains within 15% of aggregation baseline, because conditional gating skips expensive 5-10 second test execution when static errors exist without excessive verbosity trade-off.

### Type
MECHANISM

### Rationale
This hypothesis tests whether the efficiency gains of cascade routing (conditional gating) come at a token cost penalty. The 15% threshold represents acceptable overhead - more would indicate cascade verbosity negates computational savings. This validates the "efficiency" component of the cascade advantage claim.

---

## Verification Protocol

### Conceptual Test
Measure total tokens consumed per successfully solved task under both conditions:
1. **Cascade**: Run pytest only when mypy passes (conditional gating)
2. **Aggregation**: Run both mypy + pytest every iteration (simultaneous)

Compare tokens-per-task between conditions. Success = cascade within ≤15% of aggregation.

### Success Criteria
- **Primary Metric**: Mean tokens-per-successful-task
- **Gate Threshold**: Cascade ≤ 1.15 × Aggregation baseline
- **Sample**: N=20 dual-sensitive tasks from H-E1
- **Statistical Test**: None (PoC directional comparison)

### Variables
- **Independent Variable:** Feedback routing policy (cascade vs aggregation)
- **Dependent Variable:** Total tokens consumed per successful task completion
- **Controlled Variables:** Model (CodeLlama-7B), task set (N=20 from H-E1), token limits (1000/source/iter)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** HumanEval with HumanEval+ augmented tests
- **Type:** standard
- **Source:** evalplus Python package (pip install evalplus)
- **Path:** Built-in task loader
- **Hypothesis Fit:** 164 tasks with 80+ robustness tests per task; enables classification-evaluation decoupling for dual-sensitive task identification

### Selected Model
- **Name:** CodeLlama-7B
- **Type:** Base 7B code generation model
- **Source:** HuggingFace: codellama/CodeLlama-7b-hf
- **Hypothesis Fit:** Tests feedback routing on base model (not instruction-tuned); 7B size provides <30min inference while testing routing policy effects

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
**Aggregation Baseline:** Simultaneous multi-source feedback (mypy + pytest concatenated each iteration)
- Run mypy --strict + pytest every iteration
- Concatenate both outputs as single feedback message
- Token limit: 1000 tokens per source (2000 total per iteration)

### Baseline Performance
Expected from prior work (PerfCodeGen methodology):
- Execution-only feedback: ~5-10 iterations to solution
- Token consumption: ~3000-8000 tokens per task (estimated)

### Gap Analysis
Cascade routing should match or slightly exceed aggregation token usage due to:
- Additional routing overhead (condition checks)
- Potentially more verbose single-source messages
- But offset by skipping execution when mypy fails

---

## Dependencies and Gate Conditions

### Prerequisites
- **h-m1 (COMPLETED)**: Validates that mypy catches ~30-40% of errors, justifying the cascade gating strategy

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** EXPLORE - Alternative token normalization strategies

**Phase Assignment:** Phase 2 (Mechanisms)

**Estimated Duration:** 1 week

---

## Dependency Context

### Relationship to Other Hypotheses
- **Depends on H-M1:** Mypy error detection rate justifies conditional gating
- **Parallel with H-M2:** H-M2 tests attention economy (iteration reduction), H-M3 tests efficiency (token conservation)
- **Feeds into H-C1:** Efficiency boundary condition testing (7B vs larger models)

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
5. Output: h-m3/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
