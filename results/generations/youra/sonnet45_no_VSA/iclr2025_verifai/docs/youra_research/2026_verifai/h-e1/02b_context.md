# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-11
**Main Hypothesis:** Verifier-as-Teacher for Specification Synthesis
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
LLMs can utilize structured verifier feedback (witness + obligation + dependency dimensions) to iteratively refine formal specifications, achieving measurable improvement in proof discharge rate

### Type
Existence (Foundation hypothesis)

### Rationale
Foundation hypothesis - if LLMs cannot use structured feedback, entire approach fails. This is the minimal working example demonstrating that the core feedback → refinement loop is viable.

---

## Verification Protocol

### Conceptual Test
Minimal working example with single C function, ACSL annotations, Frama-C WP feedback, and LLM refinement loop. Measure proof discharge improvement across iterations.

### Success Criteria
- LLM demonstrates iterative improvement (iteration N+1 > iteration N)
- Achieves ≥50% proof discharge on minimal benchmark (5-10 functions)
- Feedback dimensions are utilized (evidence in LLM responses)

### Variables (if applicable)
- **Independent Variable:** FeedbackCondition (Type of feedback provided to LLM)
- **Dependent Variable:** ProofDischargeRate (Percentage of proof obligations successfully discharged, 0-100%)
- **Controlled Variables:** ComputeBudget (tokens + verifier time), BenchmarkPrograms (verified C programs with ACSL), VerifierToolVersion (Frama-C WP, Z3/Alt-Ergo), LLMModel (GPT-4 / Claude Opus)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Verified C programs with gold ACSL annotations
- **Type:** standard (Frama-C examples, Juliet verified subset)
- **Source:** Open-source verification benchmarks
- **Path:** To be determined in Phase 3
- **Hypothesis Fit:** Programs with deterministic behavior, verifiable safety/functional properties

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
- **PropertyGPT**: RAG-based specification synthesis (requires domain-specific knowledge base)
- **Astrogator**: Expert-written query-based specification generation
- **AutoSpec**: Single-shot LLM synthesis without feedback iteration

### Baseline Performance
- PropertyGPT: Requires expert knowledge base construction (not directly comparable)
- Astrogator: Requires expert queries (bottleneck issue)
- AutoSpec: No reported proof discharge metrics available
- General baseline: 0% proof discharge for unguided LLM synthesis (starting point)

### Gap Analysis
Prior work assumes specifications exist (verification-in-loop) or requires expert intervention (PropertyGPT, Astrogator). This hypothesis tests whether **verifier feedback alone** (no expert knowledge base) can guide LLM specification synthesis.

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundation hypothesis - first in execution order)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** Entire verification approach is invalid. If LLMs cannot utilize structured verifier feedback for iterative refinement, then the core thesis (verifier-as-teacher) fails. All downstream hypotheses (H-M1, H-M2, H-C1, H-C2) depend on this foundation.

**Phase Assignment:** Wave 1 (Foundation Layer)

**Estimated Duration:** 4 weeks (Week 5-9)
- Week 5-6: Frama-C WP feedback parser
- Week 6-7: LLM refinement loop implementation
- Week 7-9: Minimal benchmark validation (5-10 functions)

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is a **foundation hypothesis** that enables:
- **H-M1** (Information Gradient): Depends on H-E1 proving feedback refinement works
- **H-M2** (Staged vs Complete): Depends on H-E1 proving iterative refinement is viable
- **H-C1** (Compute-Matched Control): Depends on H-E1 for baseline comparison
- **H-C2** (Mutation Non-Vacuity): Depends on H-E1 for synthesized specs to validate

H-E1 can execute **in parallel** with H-E2 (Cross-Verifier Primitives) since they have no mutual dependencies.

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
5. Output: /workspace/TEST_verifai/docs/youra_research/h-e1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
