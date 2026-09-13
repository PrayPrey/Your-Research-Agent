# Hypothesis Context: H-E2

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-11
**Main Hypothesis:** Verifier-as-Teacher for Specification Synthesis
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Common semantic primitives exist across verifiers (Frama-C, Dafny, Why3) that can be abstracted into universal repair categories

### Type
Existence

### Rationale
Required for cross-verifier portability claim - without semantic overlap, normalization is impossible

---

## Verification Protocol

### Conceptual Test
Taxonomy analysis mapping Frama-C, Dafny, Why3 error categories to shared semantic primitives. Validate coverage of abstraction layer.

### Success Criteria
- ≥80% of error categories map to shared primitives
- Abstraction layer design is feasible (implementation-ready)
- Coverage validated across 3 verifiers

### Variables (if applicable)
- **Independent Variable:** N/A (taxonomy analysis, not experimental manipulation)
- **Dependent Variable:** Coverage percentage of error categories mapped to shared primitives
- **Controlled Variables:** Verifier versions (Frama-C WP, Dafny, Why3)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Verified C programs with gold ACSL annotations
- **Type:** standard (Frama-C examples, Juliet verified subset)
- **Source:** Open-source verification benchmarks
- **Path:** To be determined in Phase 3
- **Hypothesis Fit:** Programs with deterministic behavior, verifiable safety/functional properties. Provides diverse error categories for taxonomy mapping.

### Selected Model
- **Name:** GPT-4 / Claude Opus (TBD in Phase 3)
- **Type:** Large Language Model (API-based)
- **Source:** OpenAI / Anthropic APIs
- **Hypothesis Fit:** Strong reasoning capabilities for analyzing error patterns and abstraction design

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
Tool-specific error handling without abstraction layer. Each verifier's error messages processed independently.

### Baseline Performance
No cross-verifier portability - implementations are tool-specific.

### Gap Analysis
Current approaches lack semantic normalization, preventing knowledge transfer across verifiers. H-E2 establishes whether abstraction is viable.

---

## Dependencies and Gate Conditions

### Prerequisites
None - Foundation hypothesis (Layer 0)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** <60% semantic overlap (tool-specific semantics dominate), no viable abstraction layer design emerges, or critical categories resist abstraction → Cross-verifier portability claim fails, scope reduced to single-verifier approach

**Phase Assignment:** Wave 1 (Foundation Layer)

**Estimated Duration:** 4 weeks (Week 5-9)

---

## Dependency Context

### Relationship to Other Hypotheses
- **Enables:** H-M3 (Semantic Normalization Transfer) - requires abstraction layer from H-E2
- **Independent of:** H-E1 (can execute in parallel)
- **Critical Path:** H-E2 → H-M3 (cross-verifier portability depends on semantic primitives)

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (Phase 2C)
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
5. Output: docs/youra_research/h-e2/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
