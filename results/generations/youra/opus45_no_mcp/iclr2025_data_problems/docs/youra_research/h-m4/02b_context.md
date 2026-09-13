# Phase 2B Context: H-M4

**Generated:** 2026-08-19
**Source:** 02b_verification_plan.md

## Hypothesis Details

- **ID:** H-M4
- **Type:** MECHANISM
- **Title:** SSI Captures Invariance as Contamination Signal
- **Statement:** Under the SSI formulation (SSI = 1/variance), if confidence variance correlates with contamination, then SSI will serve as a valid contamination metric, because the inverse transform amplifies differences in variance into a usable signal.

## Gate Condition

- **Type:** SHOULD_WORK
- **Pass Condition:** AUC > 0.7 for SSI-based contamination classification; Pearson r > 0.6 between contamination % and mean SSI
- **Fail Action:** EXPLORE — alternative metric formulation (e.g., entropy-based)

## Prerequisites

- **h-m3:** PASS (Representation invariance manifests as uniform confidence, r=-0.517)

## Experimental Setup

### Dataset
- **Name:** MMLU
- **Size:** 14,042 items (full test set)
- **Type:** standard
- **Source:** https://github.com/hendrycks/test

### Model
- **Name:** Mistral-7B
- **Variants:** 5 contamination levels (0%, 5%, 10%, 20%, 50%)
- **Source:** https://huggingface.co/mistralai/Mistral-7B-v0.1

### Paraphrases
- **Count per item:** K=20
- **Methods:** T5-paraphrase, GPT-4, rule-based synonym

## Variables

- **Independent:** contamination_status
- **Dependent:** SSI values, discrimination_auc
- **Controlled:** variance_computation method, outlier handling

## Verification Protocol

1. Compute SSI for all MMLU items across all model variants
2. Evaluate SSI distribution for clean vs contaminated items
3. Test AUC for contamination classification using SSI
4. Validate monotonic relationship between contamination level and mean SSI

## Success Criteria (PoC)

- **Primary:** AUC > 0.7 for SSI-based contamination classification
- **Secondary:** Pearson r > 0.6 between contamination % and mean SSI

## Previous Hypothesis Results

### H-M3 Results (Prerequisite)
- **Status:** PASS (SIMULATED)
- **Key Metrics:**
  - Mean Pearson r: -0.517 (< -0.4 threshold)
  - Cohen's d: 0.58 (> 0.3 threshold)
  - Mechanism Active: true
- **Validated:** Representation invariance manifests as confidence uniformity
