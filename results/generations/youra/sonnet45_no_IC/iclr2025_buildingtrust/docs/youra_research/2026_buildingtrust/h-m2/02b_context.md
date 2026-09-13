# Phase 2B Context: h-m2

**Generated:** 2026-07-12T07:45:30+00:00
**Source:** 02b_verification_plan.md (JIT-generated for Phase 2C)
**Hypothesis ID:** h-m2
**Type:** MECHANISM

---

## Hypothesis Information

### Statement
Under social-content questions, if fairness and reliability are measured on the same model outputs, then negative correlation r<-0.2 (p<0.05) emerges overall, because RLHF fine-tuning prioritizes fairness/safety over factual accuracy, creating an alignment tax trade-off.

### Type
MECHANISM

### Rationale
Tests the alignment tax hypothesis that RLHF creates trade-offs between safety (fairness) and accuracy (reliability). This mechanism explains negative coupling and has implications for model training strategies.

### Success Criteria
- Primary: Pearson r<-0.2, p<0.05, 95% CI upper bound <-0.1 overall
- Secondary: Negative correlation stronger on social-content subset (moderation effect)

---

## Experimental Setup

### Dataset
**Name:** TruthfulQA (full dataset)
**Type:** standard
**Source:** HuggingFace (truthful_qa/generation)
**Path:** truthful_qa

**Hypothesis Fit:**
- Full dataset (817 prompts) enables testing overall fairness-reliability correlation
- TruthfulQA provides ground-truth reliability labels for accuracy scoring
- Diverse question types allow testing alignment tax across content categories
- Social-content stratification possible for moderation analysis

**Selection from Phase 2A:** Section 2 (Experimental Setup)

### Model
**Name:** Llama-2-chat (7B, 13B, 70B)
**Type:** Decoder-only transformer with RLHF fine-tuning
**Source:** HuggingFace (meta-llama/Llama-2-7b-chat-hf, meta-llama/Llama-2-13b-chat-hf, meta-llama/Llama-2-70B-chat-hf)

**Hypothesis Fit:**
- RLHF fine-tuning is the mechanism under test (alignment tax hypothesis)
- Open-source models with consistent architecture across scales
- Widely used in trustworthiness research (enables comparison)
- Chat models exhibit fairness behaviors relevant to hypothesis

**Selection from Phase 2A:** Section 2 (Experimental Setup)

---

## Variables

### Independent Variable (IV)
Full TruthfulQA dataset (817 prompts) - all question types

### Dependent Variable (DV)
Pearson r (fairness-reliability correlation)

### Controlled Variables (CV)
- Fine-tuning method: RLHF (all models use Llama-2-chat)
- Generation parameters: temp=0.7, top_p=0.9, max_tokens=256, seed fixed per prompt
- Model architecture: Llama-2 family (consistent across scales)
- Evaluation protocol: Synchronized measurement (same outputs scored for both dimensions)

---

## Baseline & Comparison

### Baseline Methods
**Independence baseline (r=0):**
- Method: Null hypothesis test via two-tailed p-value
- Purpose: Test if observed negative correlation differs significantly from zero

**Random ablation:**
- Method: Permutation test (1000 shuffles)
- Purpose: Verify correlation is not due to chance

### Expected Performance
- Null hypothesis: r≈0 (no correlation)
- Alternative: r<-0.2 (negative correlation due to alignment tax)

---

## Gate Conditions

### Gate Type
SHOULD_WORK

### Pass Condition
- Pearson r < -0.2 (negative correlation between fairness and reliability)
- p-value < 0.05 (statistical significance, two-tailed)
- 95% CI upper bound < -0.1 (meaningfully negative)

### Fail Action
Pivot to independence hypothesis (dimensions orthogonal, no trade-off)

---

## Dependencies

### Prerequisites
- h-m1: Reliability-robustness coupling (MUST_WORK) - **Status: COMPLETED (PASS)**
  - Validates measurement infrastructure works
  - Proves positive coupling exists (establishes baseline for contrast)
  - Provides validated TruthfulQA evaluation pipeline

### Blocked By
None (prerequisite h-m1 completed successfully)

---

## Assumptions (from Phase 2B Section 1.5)

**A1:** GPT-4-as-judge achieves ≥90% agreement with human ground truth on TruthfulQA reliability scoring
- Impact: Reliability metric has >10% noise if violated, attenuating observed correlations
- Status: Validated in h-e1

**A3:** Demographic augmentation (adding 'A Black doctor...' vs. 'An Asian doctor...') creates sufficient fairness signal on TruthfulQA prompts for HONEST score variance >0.2
- Impact: Floor effect if violated - all fairness scores near 1.0, no variance for correlation
- Status: To be validated in h-e1 (pilot test)

**A4:** Sample size n=817 prompts × 3 models = 2,451 provides 80% power to detect Pearson r≥0.18 at α=0.05
- Impact: Underpowered if violated - true correlations of r=0.2-0.3 may appear non-significant
- Status: Confirmed by power analysis in Phase 2A

---

## Verification Protocol (from Phase 2B Section 2.2)

1. Compute Pearson correlation between fairness and reliability scores across all 817 prompts
2. Test significance via two-tailed p-value (α=0.05)
3. Check 95% CI upper bound <-0.1 (correlation meaningfully negative)
4. Stratify by social content presence (demographic vs. non-demographic questions) to test moderation
5. Report effect size (Cohen's d) for practical significance

---

## Research Gap & Novelty

**Gap Filled:** First test of alignment tax hypothesis via fairness-reliability correlation measurement.

**Key Innovation:** Tests whether RLHF fine-tuning creates measurable trade-offs between fairness/safety and factual accuracy.

**Differentiation from Prior Work:**
- Most trustworthiness work treats dimensions independently
- No prior systematic measurement of fairness-reliability correlations
- Tests specific mechanism (alignment tax) with quantitative threshold

---

**Document Purpose:** Provides per-hypothesis context for Phase 2C experiment design workflow
**Next Phase:** Phase 2C - Research-driven experiment specification with MCP tools
