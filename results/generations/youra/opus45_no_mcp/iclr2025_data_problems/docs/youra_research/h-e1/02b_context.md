# Phase 2B Context: H-E1

**Generated:** 2026-08-19
**Source:** 02b_verification_plan.md

## Hypothesis Information

- **ID:** H-E1
- **Type:** EXISTENCE
- **Title:** SSI Discriminates Contamination Status
- **Statement:** Under standard FM evaluation on MMLU, if SSI is computed for benchmark items, then SSI will differ significantly between clean and contaminated models, because contaminated models exhibit uniform confidence across paraphrases.

## Success Criteria

- **Primary:** AUC > 0.7 for clean vs contaminated classification
- **Secondary:** Effect size (Cohen's d) > 0.5

## Gate Condition

- **Type:** MUST_WORK
- **Failure Response:** ABANDON — core mechanism invalid

## Experimental Setup

### Dataset
- **Name:** MMLU
- **Size:** 14,042 items
- **Type:** standard
- **Source:** https://github.com/hendrycks/test

### Model
- **Name:** Mistral-7B
- **Variants:** 5 (contamination levels: 0%, 5%, 10%, 20%, 50%)
- **Source:** https://huggingface.co/mistralai/Mistral-7B-v0.1

### Paraphrases
- **Count per item:** 20
- **Methods:** T5-paraphrase, GPT-4, rule-based synonym

## Verification Protocol

1. Fine-tune Mistral-7B variants with 0%, 10%, 50% MMLU contamination
2. Generate K=20 paraphrases per MMLU item using multi-method approach
3. Extract confidence scores on original + paraphrases for each item
4. Compute SSI = 1/variance(confidence) for each item per model
5. Evaluate AUC for binary classification (clean vs contaminated)

## Variables

- **Independent:** contamination_status (clean vs contaminated)
- **Dependent:** semantic_saturation_index (SSI = 1/variance)
- **Controlled:** model_architecture (Mistral-7B), paraphrase_method, K=20

## Dependencies

- **Prerequisites:** None
- **Dependent hypotheses:** H-M1, H-M2, H-M3, H-M4

## Baseline Methods (Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| 13-gram overlap (GPT-3 style) | Fails completely on paraphrased contamination | MMLU |
| DCQ (Data Contamination Quiz) | Partial paraphrase resistance, per-item detection | Various benchmarks |
