# Hypothesis Context: h-c2

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-11
**Main Hypothesis:** Verifier-as-Teacher for Specification Synthesis
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Synthesized specifications achieve ≥70% mutation kill rate relative to expert-written gold specs, demonstrating non-vacuity

### Type
Condition (H-C2)

### Rationale
Guards against vacuous specifications that trivially pass proofs but lack semantic strength. This is a critical control hypothesis ensuring that synthesized specifications have real semantic content, not just syntactic correctness.

---

## Verification Protocol

### Conceptual Test
Mutation testing framework with standard mutants (arithmetic, relational, boundary). Compare synthesized vs. expert-written kill rates.

### Success Criteria
- Mutation kill rate ≥70% of gold spec baseline
- Multiple mutation operators tested
- Non-vacuity threshold empirically validated

### Variables (if applicable)
- **Independent Variable:** Specification source (Synthesized via structured feedback vs. Expert-written gold specs)
- **Dependent Variable:** Mutation kill rate (percentage of mutants killed)
- **Controlled Variables:** Mutation operators (arithmetic, relational, boundary), benchmark programs, verifier configuration

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Verified C programs with gold ACSL annotations
- **Type:** standard (Frama-C examples, Juliet verified subset)
- **Source:** Open-source verification benchmarks
- **Path:** To be determined in Phase 3
- **Hypothesis Fit:** Programs with deterministic behavior, verifiable safety/functional properties, and expert-written specifications for mutation testing baseline

### Selected Model
- **Name:** GPT-4 / Claude Opus (TBD in Phase 3)
- **Type:** Large Language Model (API-based)
- **Source:** OpenAI / Anthropic APIs
- **Hypothesis Fit:** Strong reasoning capabilities for formal specification synthesis

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
Expert-written gold specifications from verification benchmarks (Frama-C examples, Juliet verified subset)

### Baseline Performance
- Expected gold spec mutation kill rate: 80-95% (based on empirical validation by Prof. Vera and Prof. Pax)
- Target threshold for synthesized specs: ≥70% (demonstrates non-vacuity while accounting for specification synthesis challenges)

### Gap Analysis
- Gap between trivially weak specs (0-30% kill rate) and meaningful specs (≥70% kill rate)
- This threshold distinguishes specifications that capture semantic constraints from those that merely satisfy syntactic requirements

---

## Dependencies and Gate Conditions

### Prerequisites
- **H-M1**: Information Gradient Hypothesis (MUST_WORK) - Must be validated before H-C2 can proceed

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** If synthesized specs achieve <50% kill rate (specifications are vacuous), the entire approach is invalidated - structured feedback may guide syntactic correctness but not semantic strength

**Phase Assignment:** Wave 3 (Integration Layer)

**Estimated Duration:** 3 weeks (Week 14-18 in Phase 2B timeline)

---

## Dependency Context

### Relationship to Other Hypotheses
- **Depends on H-M1**: Requires validated information gradient mechanism to ensure specifications are synthesized with structured feedback
- **Complements H-C1**: While H-C1 validates that feedback provides value over single-shot sampling, H-C2 validates that the resulting specifications are semantically meaningful
- **Critical for Phase 5**: Non-vacuity validation is essential before baseline repository comparison

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
5. Output: docs/youra_research/h-c2/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
