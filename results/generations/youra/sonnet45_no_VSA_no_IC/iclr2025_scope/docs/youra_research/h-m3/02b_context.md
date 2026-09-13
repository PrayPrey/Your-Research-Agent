# Hypothesis Context: H-M3

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-20
**Main Hypothesis:** H-ProvenanceCache-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Simple queries (low entity density, short length) show higher query-token attention concentration than complex queries, validating adaptive tiering.

### Type
MECHANISM

### Rationale
Query complexity affects attention patterns. Simple queries (low entity density, short length) should show higher concentration on query tokens compared to complex queries (high entity density, long). This validates the assumption behind adaptive query-anchoring in provenance-aware cache eviction.

---

## Verification Protocol

### Conceptual Test
Pilot 1 stratified attention analysis:
- Measure query-token attention concentration by query characteristics
- Stratify queries into two groups:
  - Simple: word count < 10, entity density < 0.3
  - Complex: word count ≥ 10, entity density ≥ 0.3
- Compute attention concentration ratio: query tokens / all context tokens
- Statistical test: two-sample t-test (simple vs complex queries)

### Success Criteria
Simple queries show significantly higher query-token attention concentration (p < 0.05) compared to complex queries.

### Variables
- **Independent Variable:** Query complexity (simple vs complex, measured by word count and entity density)
- **Dependent Variable:** Query-token attention concentration ratio
- **Controlled Variables:** Model architecture (Llama-2-7B), dataset (LongBench multi-doc QA), context length (8k-32k tokens)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** LongBench multi-doc QA
- **Type:** standard
- **Source:** THUDM/LongBench (HuggingFace)
- **Path:** HuggingFace dataset repository
- **Hypothesis Fit:** Contains diverse query complexity levels (simple single-entity questions vs complex multi-hop questions), long-context QA tasks (8k-32k tokens) matching provenance-aware cache target domain

### Selected Model
- **Name:** Llama-2-7B
- **Type:** Autoregressive transformer language model
- **Source:** meta-llama/Llama-2-7b-hf (HuggingFace)
- **Hypothesis Fit:** Standard open-source LLM with accessible attention weights, representative of models targeted by KV cache optimization research

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
No direct baseline comparison for this mechanism validation hypothesis. This is an attention analysis study to validate query-anchoring assumptions before implementing adaptive tiering.

### Baseline Performance
N/A (measurement study, not performance comparison)

### Gap Analysis
This hypothesis tests whether query complexity stratification is necessary for adaptive tiering. If simple and complex queries show no attention difference, uniform query treatment suffices (simpler policy).

---

## Dependencies and Gate Conditions

### Prerequisites
- **H-E1 (Relevance-Attention Correlation)**: MUST_WORK gate, VALIDATED
  - Status: COMPLETED ✅
  - Result: PASS (Spearman ρ = 0.391-0.612 > 0.3)
  - Provides: Attention analysis infrastructure and methodology

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** Falls back to uniform tiering for all queries (conservative approach). Query-anchoring hypothesis fails but core provenance-aware eviction (H-M1, H-M4) remains valid.

**Phase Assignment:** Pilot 1 (runs in parallel with H-E1 attention analysis)

**Estimated Duration:** Included in Pilot 1 (1-2 GPU-hours total)

---

## Dependency Context

### Relationship to Other Hypotheses
- **Shares infrastructure with H-E1**: Same attention analysis pipeline, same Pilot 1 experiment
- **Refines H-M1 tiering policy**: If H-M3 passes, adaptive query-anchoring improves simple query handling; if fails, uniform tiering used
- **Independent of H-M2 (diversity) and H-M4 (integrated performance)**: Orthogonal refinement mechanism

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
5. Output: /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_scope/docs/youra_research/h-m3/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
