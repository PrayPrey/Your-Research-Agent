# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-28
**Main Hypothesis:** Incremental SMT Verification for LLM Code Repair
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under LLM code generation in statically-typed languages (Rust, typed Python), if type annotations are present, then static analyzers can extract SMT constraints from the generated code because type annotations provide structured contracts that map directly to formal verification predicates.

### Type
EXISTENCE

### Rationale
This existence hypothesis validates the foundational assumption that LLM-generated code in typed languages can serve as input to formal verification toolchains. Without extractable constraints, the entire incremental SMT approach fails. Phase 2A identified this as BUILD_ON (established capability for human code via Prusti/Pyre), but needs verification for LLM-generated code specifically.

---

## Verification Protocol

### Conceptual Test
1. Generate 100 typed Python programs using GPT-4/Claude Sonnet 3.5 from HumanEval prompts with Pydantic type extensions
2. Extract SMT constraints from each program using Pyre static analyzer
3. Measure extraction success rate (% of programs with usable constraints extracted)
4. Verify extracted constraints are semantically meaningful (not trivial/empty)
5. Compare extraction success between LLM code and equivalent human-written code

### Success Criteria
- **Primary:** Extraction success ≥ 90% (threshold from Phase 2A assumption A1)
- **Secondary:** No significant difference vs human code (statistical equivalence test)

### Variables
- **Independent Variable:** Code generation method (LLM vs human-written)
- **Dependent Variable:** Constraint extraction success rate (%)
- **Controlled Variables:** Language (typed Python with Pydantic), static analyzer (Pyre), code complexity (10-50 LOC)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** HumanEval + Pydantic Type Extensions
- **Type:** standard (to be extended)
- **Source:** OpenAI HumanEval benchmark extended with Pydantic type annotations
- **Path:** N/A - to be created
- **Hypothesis Fit:** Provides code generation benchmark with existing test suites; type extension enables static analysis

### Selected Model
- **Name:** GPT-4 or Claude Sonnet 3.5
- **Type:** Code generation LLM
- **Source:** OpenAI API / Anthropic API
- **Hypothesis Fit:** State-of-the-art code LLMs capable of generating typed Python with Pydantic annotations

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
- **Batch SMT Verification (Z3 on full program):** Verification time scales O(n²) with codebase size - infeasible for large LLM outputs
- **Test-Suite-Only Validation:** Fast but incomplete - misses edge cases not covered by tests

### Baseline Performance
- **Batch SMT:** Verification time scales O(n²) with codebase size
- **Test-Suite-Only:** Fast execution, no formal guarantees

### Gap Analysis
- Batch SMT re-verifies unchanged code on every iteration (no incremental solving)
- Test-Suite validation provides no formal guarantees - LLM can pass tests while having subtle bugs

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** PIVOT to neural constraint extraction (H2 future work from Phase 2A)

**Phase Assignment:** Phase 1 - Foundation

**Estimated Duration:** 2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the foundation hypothesis. All subsequent mechanism hypotheses (H-M1, H-M2, H-M3) depend on H-E1 validation. If H-E1 fails, the entire incremental SMT verification approach is abandoned in favor of alternative approaches (neural constraint extraction).

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
5. Output: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_verifai/docs/youra_research/h-e1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
