# Hypothesis Context: h-m1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-24
**Main Hypothesis:** H-FailureRouting-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Attention entropy classification (low vs high threshold) correctly identifies failure types with ≥70% accuracy compared to gold-labeled entity-error vs non-entity-error categories.

### Type
MECHANISM

### Rationale
Tests causal mechanism Step 2 (Diagnostic Routing). Validates that entropy difference is actionable for classification, not just statistically significant.

---

## Verification Protocol

### Conceptual Test
Use attention entropy values computed in H-E1 to train/validate a binary classifier (low vs high threshold). Classify entity-error vs non-entity-error on held-out test set. Measure classification accuracy.

### Success Criteria
Classification accuracy ≥70% on held-out test set in either GPT-3.5 or Llama-2-7B.

### Variables
- **Independent Variable:** Attention entropy over entity spans
- **Dependent Variable:** Classification accuracy (entity-error vs non-entity-error)
- **Controlled Variables:** TruthfulQA single-entity subset, GPT-3.5 and Llama-2-7B, NER (spaCy), N=100 samples

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** TruthfulQA single-entity factual questions subset
- **Type:** standard
- **Source:** HuggingFace datasets (truthful_qa)
- **Path:** `datasets.load_dataset("truthful_qa", "generation")`
- **Hypothesis Fit:** Provides gold-labeled model failures (entity-error vs non-entity-error) with single-entity questions for unambiguous classification

### Selected Model
- **Name:** GPT-3.5 and Llama-2-7B
- **Type:** Pretrained language models
- **Source:** OpenAI API / HuggingFace transformers
- **Hypothesis Fit:** Multi-model replication reduces architecture-specific pattern risk

---

## Baseline & Comparison Targets

### Baseline Methods
Random guessing (50% accuracy baseline for binary classification)

### Baseline Performance
50% accuracy (coin flip)

### Gap Analysis
Hypothesis requires ≥70% accuracy — 20 percentage point improvement over random baseline demonstrates actionable classification utility.

---

## Dependencies and Gate Conditions

### Prerequisites
- **h-e1** (VALIDATED): Entity-substitution errors exhibit significantly lower attention entropy over NER-identified entity spans compared to non-entity errors

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** If classification accuracy < 70% on held-out test set in either model, entropy difference (h-e1) exists but is not actionable for automated routing — entire failure-type routing framework invalidated.

**Phase Assignment:** Phase 2C → 3 → 4

**Estimated Duration:** 5-8 minutes (experiment design) + implementation

---

## Dependency Context

### Relationship to Other Hypotheses
- **Depends on:** h-e1 (proved attention entropy difference exists)
- **Required by:** h-m2 (matched correction effectiveness — requires classification capability to route failures)
- **Causal chain:** H-C1 (measurement) → H-E1 (pattern detection) → **H-M1 (classification)** → H-M2 (correction)

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
5. Baseline comparison targets (CRITICAL for H-CP* hypotheses)

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: docs/youra_research/h-m1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
