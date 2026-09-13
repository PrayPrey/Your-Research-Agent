# Hypothesis Context: h-m4

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-25
**Main Hypothesis:** Constraint-Satisfiability Verification for DL Hypothesis Testability
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under post-hoc experimental validation, if a sample of system-classified "testable" hypotheses are actually tested, then ≥65% yield p < 0.05 results (ground truth confirmation), because the system's (D,B,M) existence checks correctly predict experimental feasibility.

### Type
MECHANISM

### Rationale
This is the ultimate ground truth test. If <65% of "testable" classifications result in successful experiments, the system's predictions don't match reality.

---

## Verification Protocol

### Conceptual Test
1. System classifies 100 hypotheses as testable/not-testable
2. Randomly sample 20 hypotheses from "testable" group
3. Actually run experiments for each (simplified PoC experiments, not full-scale)
4. Measure: (# experiments with p < 0.05) / 20

### Success Criteria
- Primary: Success rate ≥65% (13/20 hypotheses yield significant results)

### Variables (if applicable)
- **Independent Variable:** System classifications ("testable" vs "not testable")
- **Dependent Variable:** Experimental success rate (p < 0.05 results)
- **Controlled Variables:** Random sample size (20 hypotheses)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** System-Classified Hypothesis Pool (100 hypotheses)
- **Type:** custom
- **Source:** Generated from constraint-satisfiability system output
- **Path:** To be created in Phase 4
- **Hypothesis Fit:** Test set of hypotheses classified by the (D,B,M) existence verification system, required to validate post-hoc experimental success rates

### Selected Model
- **Name:** Formal Constraint-Satisfiability Verifier
- **Type:** symbolic reasoning system
- **Source:** Custom implementation (no pre-trained model required)
- **Hypothesis Fit:** The verification system under test; its classifications are the independent variable being validated against experimental outcomes

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
Random classification baseline (50% expected success rate)

### Baseline Performance
50% accuracy (random classification)

### Gap Analysis
Target improvement: 65% vs 50% random baseline = +15 percentage points absolute improvement

---

## Dependencies and Gate Conditions

### Prerequisites
H-M3 (Confound Flagging Precision)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** ABANDON post-hoc validation claim, revert to expert agreement baseline

**Phase Assignment:** Phase 4

**Estimated Duration:** 15-25 minutes

---

## Dependency Context

### Relationship to Other Hypotheses
H-M4 depends on H-M3's confound detection capability. The post-hoc validation tests whether hypotheses that pass both (D,B,M) existence checks AND confound screening actually produce significant experimental results. This validates the entire verification system pipeline.

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
5. Output: h-m4/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
