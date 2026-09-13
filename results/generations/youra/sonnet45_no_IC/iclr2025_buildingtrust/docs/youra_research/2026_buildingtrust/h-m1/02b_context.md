# Hypothesis Context: h-m1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-12
**Main Hypothesis:** Cross-Dimensional Trustworthiness Correlations Under Synchronized Evaluation
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under factual prompts where memorization is expected, if reliability and robustness are measured on the same model outputs, then positive correlation r>0.3 (p<0.05) emerges, because shared training dynamics create correlations between factual correctness (reliability) and consistent retrieval (robustness) for memorized content.

### Type
MECHANISM

### Rationale
Tests the mechanism that memorized facts enable both reliability (correct retrieval) and robustness (consistent across paraphrases). Validates correlation arises from training dynamics, not measurement artifacts.

---

## Verification Protocol

### Conceptual Test
1. Stratify TruthfulQA into factual vs. misinformation prompts based on question category
2. Compute Pearson correlation between reliability and robustness scores for factual stratum
3. Test significance via two-tailed p-value (α=0.05)
4. Check 95% CI lower bound >0.2 (correlation meaningfully positive)
5. Permutation test (1000 shuffles) to confirm observed r exceeds 95th percentile of null distribution

### Success Criteria
- Primary: Pearson r>0.3, p<0.05, 95% CI lower bound >0.2 on factual prompts
- Secondary: At least one model shows r>0.4 (strong coupling)

### Variables
- **Independent Variable:** Prompt Type (factual subset from TruthfulQA, ~400 prompts)
- **Dependent Variable:** Pearson r (reliability-robustness correlation)
- **Controlled Variables:** Generation Parameters (temp=0.7, top-p=0.9, seed fixed), Model Architecture (Llama-2 family)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** TruthfulQA (factual stratum)
- **Type:** standard
- **Source:** HuggingFace (truthful_qa/generation)
- **Path:** truthful_qa
- **Hypothesis Fit:** Provides 817 prompts with ground-truth reliability labels; enables stratification into factual vs. misinformation categories

### Selected Model
- **Name:** Llama-2-chat (7B, 13B, 70B)
- **Type:** decoder-only transformer
- **Source:** HuggingFace (meta-llama/Llama-2-7b-chat-hf, meta-llama/Llama-2-13b-chat-hf, meta-llama/Llama-2-70B-chat-hf)
- **Hypothesis Fit:** Open-source models with consistent architecture across scales; enables testing scale as moderator

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
- Independence baseline (r=0): Null hypothesis test via two-tailed p-value
- Random ablation: Permutation test (1000 shuffles)

### Baseline Performance
- Null hypothesis: r≈0, p>0.05 (no significant correlation)

### Gap Analysis
- Target: Demonstrate r>0.3 (positive coupling) vs. null hypothesis r=0
- Statistical framework: Two-tailed significance test + 95% CI + permutation test

---

## Dependencies and Gate Conditions

### Prerequisites
- h-e1 (MUST_WORK gate satisfied)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** Explore alternative mechanisms (retrieval quality, model calibration)

---

## Dependency Context

### Relationship to Other Hypotheses
- Depends on h-e1: Measurements must exist with sufficient variance (σ>0.2)
- Prerequisite for h-m2: Reliability-robustness coupling must be established before testing fairness-reliability trade-off
- Tests Causal Step 1: Shared training dynamics create correlations via memorization mechanism

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
5. Output: docs/youra_research/h-m1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
