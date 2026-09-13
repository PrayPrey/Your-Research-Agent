# Hypothesis Context: h-m-integrated

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-17
**Main Hypothesis:** H-AgencyRLHF-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under HH-RLHF evaluation conditions, if linguistic agency markers are extracted from 161K chosen-rejected response pairs, then chosen responses will exhibit systematically lower marker frequencies (modal verbs, hedging, alternatives) with small-to-medium effect (Cohen's d ≥ 0.15, p < 0.05, chosen < rejected), internal consistency across markers (Cronbach's α > 0.7), and cross-dataset replication (2/3 splits), because the 4-step causal chain (RLHF optimization → efficiency preference → directness priority → reduced markers) operates as theorized.

### Type
MECHANISM

### Rationale
This integrated hypothesis tests the full causal mechanism linking RLHF optimization to linguistic manifestations of agency preservation. It validates the core theoretical claim that RLHF's preference for efficient task resolution systematically reduces autonomy-preserving language. Success provides the first computational operationalization of Human→AI alignment dimension (bidirectional framework). Includes construct validation (Cronbach's α) and robustness checks (cross-split replication).

---

## Verification Protocol

### Conceptual Test
1. Extract markers from all chosen and rejected responses using H-E1 validated pipeline (161K pairs).
2. Conduct paired t-test on modal verb frequency (within-pair differences, test if mean < 0).
3. Calculate Cohen's d effect size for paired samples (mean difference / SD of differences).
4. Compute Cronbach's alpha across three marker types to test internal consistency as construct.
5. Partial correlation analysis to control for response length, conversation turn, topic category.
6. Cross-validation: repeat paired t-test separately for each split (helpful-base, helpful-online, helpful-RS).
7. Visualize results: forest plot of effect sizes by split, density plots of marker distributions by preference status.

### Success Criteria
- **Primary (P1):** Modal verb frequency chosen < rejected, p < 0.05, Cohen's d ≥ 0.15
- **Secondary (P2):** Internal consistency Cronbach's α > 0.7 (convergent validity across markers)
- **Tertiary (P3):** Replication in at least 2 of 3 splits (p < 0.05, d ≥ 0.15)

### Variables
- **Independent Variable:** RLHF_preference_status (chosen=1, rejected=0)
- **Dependent Variable (Primary):** modal_verb_frequency (per 100 words, chosen vs rejected)
- **Dependent Variable (Secondary):** hedging_marker_frequency, alternative_framing_frequency
- **Controlled Variables:** response_length (via normalization + paired design), conversation_turn (partial correlation), topic_category (stratified analysis)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Anthropic HH-RLHF
- **Type:** standard
- **Source:** HuggingFace: Anthropic/hh-rlhf
- **Path:** https://huggingface.co/datasets/Anthropic/hh-rlhf
- **Hypothesis Fit:** Contains 161K preference pairs (chosen vs rejected) with conversation context - perfect for matched-pair linguistic analysis. Three splits (base, online, RS) enable cross-validation. Publicly available, peer-reviewed methodology, widely used in alignment research.

### Selected Model
- **Name:** N/A - Analysis only
- **Type:** linguistic_analysis
- **Source:** No model training - pure NLP feature extraction from existing text
- **Hypothesis Fit:** This is a measurement study, not a model training study. We extract linguistic features from static text data.

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
Standard RLHF evaluation (helpfulness, harmlessness, honesty metrics) - Measures AI-side properties only on datasets like AlpacaEval, MT-Bench, HH-RLHF annotations

### Baseline Performance
0% coverage of Human→AI alignment dimension (no existing metrics for agency preservation)

### Gap Analysis
No metrics for human-side effects (agency preservation, critical thinking capacity) - misses bidirectional dimension

---

## Dependencies and Gate Conditions

### Prerequisites
- **h-e1** (MUST be completed first)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** Mechanism doesn't operate as theorized OR proxy validity invalid → PIVOT to direct user studies for agency measurement OR EXPLORE alternative linguistic markers OR ABANDON computational proxy approach entirely

**Phase Assignment:** Phase 2 - Mechanism

**Estimated Duration:** 1 week

---

## Dependency Context

### Relationship to Other Hypotheses
This hypothesis DEPENDS on h-e1 (Linguistic Marker Extraction Feasibility). It uses the validated extraction pipeline from h-e1 to test the full causal mechanism. Success establishes the first computational operationalization of Human→AI alignment dimension via linguistic proxies.

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
5. Output: h-m-integrated/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
