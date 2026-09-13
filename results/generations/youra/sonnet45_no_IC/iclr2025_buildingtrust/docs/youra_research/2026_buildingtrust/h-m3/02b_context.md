# Phase 2B Context: h-m3

**Generated:** 2026-07-12T08:40:00+00:00
**Source:** 02b_verification_plan.md (JIT-generated for Phase 2C)
**Hypothesis ID:** h-m3
**Type:** MECHANISM

---

## Hypothesis Information

### Statement
Under stratified prompt types (factual vs. misinformation), if reliability-robustness correlations are computed separately per stratum, then correlation magnitudes differ significantly (Fisher z-test p<0.05), because factual prompts show stronger coupling (r>0.4) than reasoning/misinformation prompts (r<0.3) due to different retrieval vs. computation mechanisms.

### Type
MECHANISM

### Rationale
Tests moderation hypothesis that correlation structure depends on cognitive task type. Factual tasks use memorization (strong coupling), reasoning tasks use computation with multiple paths (weak coupling). This validates mechanistic interpretation.

### Success Criteria
- Primary: Fisher z-test p<0.05 (significant moderation effect)
- Secondary: Factual stratum r>0.4, Misinformation stratum r<0.3

---

## Experimental Setup

### Dataset
**Name:** TruthfulQA (stratified: factual vs. misinformation)
**Type:** standard
**Source:** HuggingFace (truthful_qa/generation)
**Path:** truthful_qa

**Hypothesis Fit:**
- Full dataset (817 prompts) with natural stratification into factual vs. misinformation categories
- TruthfulQA metadata provides question categories for stratification
- Factual stratum (~400 prompts): questions with ground-truth factual answers
- Misinformation stratum (~417 prompts): questions designed to elicit common misconceptions
- Enables testing whether correlation strength varies by cognitive task type

**Selection from Phase 2A:** Section 2 (Experimental Setup)

### Model
**Name:** Llama-2-chat (7B, 13B, 70B)
**Type:** Decoder-only transformer with RLHF fine-tuning
**Source:** HuggingFace (meta-llama/Llama-2-7b-chat-hf, meta-llama/Llama-2-13b-chat-hf, meta-llama/Llama-2-70B-chat-hf)

**Hypothesis Fit:**
- Open-source models with consistent architecture across scales
- Enables testing moderation effect across model sizes
- Widely used in trustworthiness research (enables comparison)
- Chat models exhibit both retrieval (factual) and reasoning (misinformation) behaviors

**Selection from Phase 2A:** Section 2 (Experimental Setup)

---

## Variables

### Independent Variable (IV)
Prompt Stratum (Factual vs. Misinformation from TruthfulQA)

### Dependent Variable (DV)
Correlation Difference (Fisher z-test statistic)

### Controlled Variables (CV)
- Correlation computation method: Pearson (same for both strata)
- Generation parameters: temp=0.7, top_p=0.9, max_tokens=256, seed fixed per prompt
- Model architecture: Llama-2 family (consistent across scales)
- Evaluation protocol: Synchronized measurement (same outputs scored for both dimensions)

---

## Baseline & Comparison

### Baseline Methods
**Homogeneous correlation:**
- Method: No significant difference between strata (Fisher z-test p>0.05)
- Purpose: Test if observed correlation difference is significant

**Permutation test:**
- Method: Shuffle stratum labels (1000 permutations)
- Purpose: Verify moderation effect is not due to chance

### Expected Performance
- Null hypothesis: r_factual ≈ r_misinfo (no moderation)
- Alternative: |r_factual - r_misinfo| ≥ 0.1 AND Fisher z p<0.05 (significant moderation)

---

## Gate Conditions

### Gate Type
SHOULD_WORK

### Pass Condition
- Fisher z-test p < 0.05 (significant difference between strata)
- r_factual - r_misinfo ≥ 0.1 (meaningful difference magnitude)
- r_factual > 0.4 AND r_misinfo < 0.3 (directional pattern matches theory)

### Fail Action
Report homogeneous correlations (mechanism not moderated by prompt type)

---

## Dependencies

### Prerequisites
- h-m2: Fairness-reliability trade-off (SHOULD_WORK) - **Status: COMPLETED (PASS)**
  - Validates multi-dimensional measurement infrastructure works across all three dimensions
  - Establishes baseline correlation patterns
  - Provides validated TruthfulQA evaluation pipeline for all dimensions

### Blocked By
None (prerequisite h-m2 completed successfully)

---

## Assumptions (from Phase 2B Section 1.5)

**A1:** GPT-4-as-judge achieves ≥90% agreement with human ground truth on TruthfulQA reliability scoring
- Impact: Reliability metric has >10% noise if violated, attenuating observed correlations
- Status: Validated in h-e1

**A2:** Back-translation (English→French→English) preserves semantic content while changing surface form, enabling valid robustness measurement
- Impact: Paraphrases may alter meaning if violated, confounding robustness metric
- Status: Validated in h-e1

**A4:** Sample size n=817 prompts × 3 models = 2,451 provides 80% power to detect Pearson r≥0.18 at α=0.05
- Impact: Underpowered if violated - true correlations of r=0.2-0.3 may appear non-significant
- Status: Confirmed by power analysis in Phase 2A

---

## Verification Protocol (from Phase 2B Section 2.2)

1. Compute reliability-robustness correlation separately for factual stratum (~400 prompts) and misinformation stratum (~417 prompts)
2. Apply Fisher z-transformation to both correlations
3. Test difference via Fisher z-test (α=0.05)
4. Confirm factual stratum r > misinformation stratum r by at least 0.1
5. Visualize with forest plot showing correlations per stratum with 95% CIs

---

## Research Gap & Novelty

**Gap Filled:** First test of prompt-type moderation of reliability-robustness coupling using TruthfulQA stratification.

**Key Innovation:** Tests whether correlation structure depends on cognitive task type (retrieval vs. reasoning), validating mechanistic interpretation of dimensional coupling.

**Differentiation from Prior Work:**
- Most correlation studies report overall correlations without moderation analysis
- No prior systematic measurement of how correlation structure varies by prompt type
- Tests specific mechanism (retrieval vs. computation) with quantitative threshold

---

## Continuation Context

This hypothesis builds on H-M1 (reliability-robustness coupling via memorization) and tests whether this coupling strength varies by prompt type. H-M1 established r=0.7233 (p<0.001) on factual stratum. H-M3 tests if misinformation stratum shows significantly weaker coupling.

### Previous Hypothesis Results

**From H-M2 (PASS):**
- Fairness-Reliability correlation: r=-0.2450, p=0.000100
- HONEST bias metric successfully implemented with demographic augmentation
- Sample size: 817 prompts across 3 model sizes
- All outputs already generated and cached from H-E1/H-M1

**From H-M1 (PASS):**
- Factual stratum correlation: r=0.7233, p<0.001
- Misinformation stratum correlation: r=0.2798 (mechanism specificity observed)
- 95% CI for factual: [0.6730, 0.7670]
- Baseline outputs and metrics already computed

---

**Document Purpose:** Provides per-hypothesis context for Phase 2C experiment design workflow
**Next Phase:** Phase 2C - Research-driven experiment specification with MCP tools
