# Phase 2B Context: h-m2

**Generated:** 2026-03-24 (JIT by Phase 2C step-01)
**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Hypothesis Statement

> Margin inflation decouples confidence-correctness relationship, measurable via attenuated percentile-normalized slope (β_percentile_instruct < β_percentile_base) under 2x2 prompt controls.

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset

| Field | Value |
|-------|-------|
| **Name** | MMLU (Massive Multitask Language Understanding) |
| **Type** | standard |
| **Source** | HuggingFace (cais/mmlu) |
| **Path** | cais/mmlu |
| **Splits** | test (14,042 samples) |
| **Hypothesis Fit** | MCQ format enables clean confidence extraction via logit margins; 57 domains enable stratified analysis |

### Model

| Field | Value |
|-------|-------|
| **Name** | Qwen2.5-7B, Mistral-7B (base + instruct pairs) |
| **Type** | Causal LLM |
| **Source** | HuggingFace Model Hub |
| **Hypothesis Fit** | Base + instruct pairs enable within-family RLHF effect measurement |

### Note: Continuation Experiment

This hypothesis reuses cached inference results from H-E1:
- **H-E1**: Collected logit margins for all 14,042 MMLU test samples
- **H-M1**: Performed conditional margin analysis on same cached data
- **H-M2**: Will fit logistic regression on same cached data with percentile normalization

No new model inference required - statistical reanalysis only.

---

## Verification Protocol (from Phase 2B)

1. Z-score normalize margins within each model (percentile normalization)
2. Fit logistic regression Pr(correct) = σ(α + β·z-score(margin)) per model
3. Extract β_percentile coefficients with bootstrap 95% CIs
4. Compare across 2×2 conditions (base/instruct × zero-shot/few-shot)
5. Verify effect persists across prompt formats (robustness check)

---

## Success Criteria

- **Primary**: β_percentile_instruct < β_percentile_base with p < 0.05
- **Secondary**: Effect survives 2×2 prompt design controls

---

## Gate Condition

**Type:** MUST_WORK
**Pass Criteria:** Statistically significant β_percentile attenuation (p < 0.05)
**Failure Response:** EXPLORE alternative normalization schemes

---

## Prerequisites

| Prerequisite | Status | Key Finding |
|--------------|--------|-------------|
| h-e1 | PASS | AUROC degradation confirmed: Qwen +0.0222, Mistral +0.0385 |
| h-m1 | PASS | Margin inflation confirmed: Qwen 3.06x, Mistral 16.79x |
