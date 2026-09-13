# Hypothesis Context: {hypothesis_id}

**Generated from:** Phase 2B Verification Plan
**Date:** {current_date}
**Main Hypothesis:** {main_hypothesis_title}
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
{hypothesis_statement_full}

### Type
{hypothesis_type}

### Rationale
{hypothesis_rationale}

---

## Verification Protocol

### Conceptual Test
{verification_protocol_description}

### Success Criteria
{success_criteria_quantitative}

### Variables (if applicable)
- **Independent Variable:** {iv}
- **Dependent Variable:** {dv}
- **Controlled Variables:** {cv}

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** {selected_dataset_name}
- **Type:** {selected_dataset_type} (standard/custom/synthetic)
- **Source:** {selected_dataset_source}
- **Path:** {selected_dataset_path}
- **Hypothesis Fit:** {dataset_hypothesis_fit}

### Selected Model
- **Name:** {selected_model_name}
- **Type:** {selected_model_type}
- **Source:** {selected_model_source}
- **Hypothesis Fit:** {model_hypothesis_fit}

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
{baseline_methods_summary}

### Baseline Performance
{baseline_best_performance}

### Gap Analysis
{gap_analysis}

---

## Dependencies and Gate Conditions

### Prerequisites
{prerequisites_list}

### Gate Information

**Gate Type:** {gate_type}
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** {consequence_if_fail}

**Phase Assignment:** {phase_number}

**Estimated Duration:** {duration}

---

## Dependency Context

### Relationship to Other Hypotheses
{relationship_description}

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
