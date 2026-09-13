# Hypothesis Context: H-M1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-20
**Main Hypothesis:** H-ProvenanceCache-v1 (Provenance-Aware KV Cache Management for RAG-Based Long-Context QA)
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Provenance-aware tiered eviction (query > high-rel > low-rel) achieves ≥5% accuracy gain at 25% cache budget on single-hop QA vs H2O baseline.

### Type
MECHANISM

### Rationale
After H-E1 validates that retrieval relevance scores correlate with attention weights, H-M1 tests whether this correlation can be exploited for practical KV cache eviction. Single-hop QA provides a controlled setting to validate the core tiering mechanism (query tokens → high-relevance passages → low-relevance passages) without multi-hop complexity. This is the foundational mechanism test - if tiering fails on simple single-hop questions, it won't work on complex multi-hop scenarios.

---

## Verification Protocol

### Conceptual Test
Implement three-tier eviction policy (Tier 0: query + top-1 passage, Tier 1: high-relevance passages, Tier 2: low-relevance passages) and compare against H2O baseline on LongBench single-hop QA subset at 25% cache budget retention.

### Success Criteria
≥5% relative accuracy gain vs H2O baseline at 25% cache budget (measured via exact match or F1 score).

### Variables (if applicable)
- **Independent Variable:** Eviction policy (ProvenanceCache tiered vs H2O attention-based)
- **Dependent Variable:** Answer accuracy (exact match / F1 score)
- **Controlled Variables:** Model (Llama-2-7B), dataset (LongBench single-hop subset), cache budget (25%), context length (8k-32k tokens)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** LongBench (single-hop QA subset)
- **Type:** standard
- **Source:** THUDM/LongBench (HuggingFace)
- **Path:** LongBench QA tasks filtered for single-hop questions
- **Hypothesis Fit:** Controlled single-hop setting isolates tiering mechanism from multi-hop reasoning complexity. Multi-document contexts (8k-32k tokens) require aggressive KV cache eviction at 25% budget.

### Selected Model
- **Name:** Llama-2-7B
- **Type:** Causal LM with attention weights accessible for analysis
- **Source:** meta-llama/Llama-2-7b-hf
- **Hypothesis Fit:** Standard long-context QA model with proven performance on LongBench. 7B parameter size allows fast iteration (5-8 GPU-hours for full experiment). Attention weights needed for H2O baseline comparison.

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
- **Primary Baseline:** H2O (Zhang et al., NeurIPS 2023) - evicts tokens with lowest accumulated attention scores, retains 20-30% cache while maintaining accuracy on generation tasks
- **Upper Bound:** FullKV (no eviction) - theoretical maximum accuracy
- **Lower Bound:** Random eviction - sanity check baseline

### Baseline Performance
H2O maintains ~95% of FullKV accuracy at 20-30% cache retention on generation tasks (extrapolated from H2O paper). For LongBench single-hop QA, expect ~60-70% baseline accuracy at 25% cache budget.

### Gap Analysis
H2O uses accumulated attention scores (uniform token treatment) and ignores RAG provenance structure. ProvenanceCache exploits retrieval metadata (relevance scores, passage boundaries, query/passage token types) to predict utility before attention computation. Expected 5% relative gain = absolute 3-4% accuracy improvement (60% → 63-64%).

---

## Dependencies and Gate Conditions

### Prerequisites
- **H-E1 (EXISTENCE):** Validates that retrieval relevance scores correlate moderately (Spearman ρ > 0.3) with attention weights during answer generation. **STATUS: VALIDATED ✅** (ρ = 0.391 for BM25, ρ = 0.612 for Contriever)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** If gain < 5% or ProvenanceCache performs worse than H2O, core tiering mechanism fails → Phase 2A-Dialogue modification (adjust tiering policy or test alternative metadata).

**Phase Assignment:** Pilot 2 (mechanism validation before multi-hop complexity)

**Estimated Duration:** 5-8 GPU-hours

---

## Dependency Context

### Relationship to Other Hypotheses
H-M1 is the critical path mechanism test. It blocks:
- **H-M2 (Diversity Ablation):** Diversity-aware scoring builds on tiered eviction
- **H-M4 (Integrated Performance):** Full policy validation requires H-M1 + H-M2 passing

H-M1 is independent of:
- **H-M3 (Query Complexity):** Query stratification is orthogonal to tiering mechanism

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (experiment_design.status = NOT_STARTED)
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation (H-E1 VALIDATED)
3. Dependency information for controlled experiments
4. Success criteria for evaluation design (≥5% gain at 25% budget)
5. **Baseline comparison targets** (H2O primary, FullKV upper bound, Random lower bound)

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: docs/youra_research/h-m1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-M* (Mechanism)**: Baseline (H2O ~60-70% accuracy) to understand 5% relative improvement target (63-74% absolute)

---

*Optimized for single-hypothesis experiment design*
