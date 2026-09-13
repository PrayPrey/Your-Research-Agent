# Phase 2B Context: H-E1

**Hypothesis ID:** H-E1
**Type:** EXISTENCE
**Gate:** MUST_WORK

## Hypothesis Statement

Under synchronized evaluation (same checkpoint, same prompts, same generation parameters), if trustworthiness dimensions (reliability, robustness, fairness) are measured on the same LLM outputs, then synchronized multi-dimensional measurements exist with sufficient variance (σ>0.2) for correlation analysis, because dimensions can be operationalized as independent metrics on the same evaluation logs.

## Rationale

This foundational hypothesis validates that multi-dimensional trustworthiness evaluation is technically feasible on existing benchmarks. Without sufficient measurement variance, correlation analysis would be meaningless due to floor/ceiling effects.

## Variables

- **IV:** Evaluation Setup (synchronization: same model checkpoint, same prompts, fixed generation parameters)
- **DV:** Reliability Score (GPT-4-as-judge accuracy 0-1), Robustness Score (paraphrase consistency 0-1), Fairness Score (HONEST bias 0-1)
- **CV:** Generation Parameters (temp=0.7, top-p=0.9, seed fixed), Model Architecture (Llama-2 family)

## Experimental Setup (from Phase 2A)

### Dataset
- **Name:** TruthfulQA
- **Type:** standard
- **Source:** HuggingFace (truthful_qa/generation)
- **Path:** truthful_qa
- **Hypothesis Fit:** Provides 817 prompts with ground-truth reliability labels; enables stratification into factual vs. misinformation categories for moderation test; widely used trustworthiness benchmark

### Model
- **Name:** Llama-2-chat (7B, 13B, 70B)
- **Type:** decoder-only transformer
- **Source:** HuggingFace (meta-llama/Llama-2-7b-chat-hf, meta-llama/Llama-2-13b-chat-hf, meta-llama/Llama-2-70B-chat-hf)
- **Hypothesis Fit:** Open-source models with consistent architecture across scales; enables testing scale as moderator; widely used in trustworthiness research

## Verification Protocol

1. Generate outputs for all 817 TruthfulQA prompts on Llama-2 (7B, 13B, 70B) with fixed generation parameters
2. Score reliability via GPT-4-as-judge, robustness via paraphrase consistency, fairness via demographic-augmented HONEST
3. Compute variance (σ) for each dimension across all outputs
4. Validate GPT-4-as-judge on n≥100 sample (target ≥90% agreement with human labels)
5. Confirm HONEST score variance >0.2 on n≥50 demographic-augmented pilot

## Success Criteria

- **Primary:** All three dimensions show σ>0.2 (sufficient variance for correlation)
- **Secondary:** GPT-4-as-judge achieves ≥90% agreement, HONEST variance ≥0.2

## Gate Conditions

- **Type:** MUST_WORK
- **If Fail:** Abort all subsequent hypotheses (no correlation analysis possible without variance)

## Prerequisites

None (foundation hypothesis)

## Baseline Comparison

- **Method 1:** Independence baseline (r=0) - Null hypothesis test via two-tailed p-value
- **Method 2:** Random ablation - Permutation test (1000 shuffles)

## Key Assumptions

| ID | Assumption | If Violated |
|----|------------|-------------|
| A1 | GPT-4-as-judge achieves ≥90% agreement with human ground truth on TruthfulQA reliability scoring | Reliability metric has >10% noise, attenuating observed correlations and reducing power |
| A2 | Back-translation (English→French→English) preserves semantic content while changing surface form, enabling valid robustness measurement | Paraphrases may alter meaning, making robustness metric confound semantic drift with model consistency |
| A3 | Demographic augmentation (adding 'A Black doctor...' vs. 'An Asian doctor...') creates sufficient fairness signal on TruthfulQA prompts for HONEST score variance >0.2 | Floor effect: all fairness scores near 1.0, no variance for correlation analysis |
| A4 | Sample size n=817 prompts × 3 models = 2,451 provides 80% power to detect Pearson r≥0.18 at α=0.05 | Underpowered study: true correlations of r=0.2-0.3 may appear non-significant |
| A5 | Correlation patterns generalize across Llama-2 model scales (7B, 13B, 70B) and are not confounded by scale-specific effects | Observed correlations may reflect scale artifacts rather than dimensional coupling; requires separate analysis per model size |

## Source

Phase 2B Verification Plan Section 2.2 (H-E1 specification)
