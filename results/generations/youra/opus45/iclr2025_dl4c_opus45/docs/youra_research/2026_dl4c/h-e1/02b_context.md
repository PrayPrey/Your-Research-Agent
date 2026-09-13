# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-24
**Main Hypothesis:** Alignment-Induced Error Type Divergence in Code Generation
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under code generation on HumanEval+/MBPP+, if a model is aligned with RL (binary execution reward) vs DPO (pairwise preference), then P(syntax+runtime | failure, RL) < P(syntax+runtime | failure, DPO), because RL's zero-reward basin creates pressure toward syntactic validity first.

### Type
EXISTENCE

### Rationale
This is the foundational existence test. If error type distributions don't differ between alignment methods, the entire mechanism hypothesis chain is falsified. The h-e1 gradient anti-correlation finding suggests fundamentally different optimization objectives should manifest behaviorally.

---

## Verification Protocol

### Conceptual Test
1. Generate n=10 samples per problem at T=0.8 for CodeRL-770M and CodeLlama-7B-DPO on HumanEval+/MBPP+.
2. Execute all samples using EvalPlus harness, capturing full error traces.
3. Classify failures using ICSE 2025 taxonomy via automated error message parsing (syntax, runtime, assertion).
4. Compute conditional error type proportions P(type | failure, method) for each alignment method.
5. Run chi-square test on error_type × alignment_method contingency table; compute Cramér's V.

### Success Criteria
- Primary: Chi-square test p < 0.05 AND Cramér's V > 0.05
- Secondary: Effect direction matches prediction (RL lower syntax+runtime proportion)

### Variables (if applicable)
- **Independent Variable:** alignment_method (RL_execution vs DPO_preference)
- **Dependent Variable:** error_type_distribution P(error_type | failure)
- **Controlled Variables:** evaluation_benchmark, sampling_parameters, error_taxonomy

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** HumanEval+ and MBPP+
- **Type:** standard (real benchmark)
- **Source:** evalplus/evalplus (1701 GitHub stars)
- **Path:** Loaded via evalplus library
- **Hypothesis Fit:** Provides execution-based evaluation with detailed error messages for taxonomy classification; 164 + 378 = 542 problems total

### Selected Model
- **Name:** CodeRL-770M (RL) vs CodeLlama-7B-DPO (DPO)
- **Type:** Encoder-decoder (CodeT5) vs Decoder-only (CodeLlama)
- **Source:** salesforce/CodeRL (564 stars), community DPO fine-tunes
- **Hypothesis Fit:** CodeRL explicitly uses execution-based RL; CodeLlama DPO uses preference-based alignment

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| CodeRL | 35.0% pass@1 | HumanEval |
| DPO-aligned CodeLlama | ~45% pass@1 | HumanEval |

### Baseline Performance
CodeRL: 35.0% pass@1 on HumanEval
CodeLlama-7B-DPO: ~45% pass@1 on HumanEval

### Gap Analysis
N/A - H-E1 is an EXISTENCE hypothesis testing error distribution differences, not performance comparison.

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** STOP - Reassess entire hypothesis, dependent hypotheses blocked

**Phase Assignment:** Phase 1 (Foundation)

**Estimated Duration:** 2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the foundation hypothesis with no prerequisites. All mechanism hypotheses (H-M1, H-M2, H-M3) depend on H-E1 passing. If H-E1 fails to show error distribution divergence, the entire mechanism chain is invalidated.

Dependent hypotheses:
- H-M1 (Zero-Reward Basin Effect) - Blocked until H-E1 passes
- H-M2 (Syntactic Validity Pressure) - Blocked until H-M1 passes
- H-M3 (Preference Surface Plausibility) - Blocked until H-M2 passes

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
5. Output: h-e1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
