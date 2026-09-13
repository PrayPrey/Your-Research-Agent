# Phase 2B Context: h-m1

**Generated**: 2026-08-09
**Hypothesis ID**: h-m1
**Type**: MECHANISM
**Gate**: SHOULD_WORK

---

## Hypothesis Statement

Combined model [H_L + NTI + CMI] improves AUROC >= 0.03 over H_L alone with LRT p < 0.05

---

## Rationale

This hypothesis tests whether trajectory metrics (NTI, CMI) provide incremental predictive validity beyond raw output entropy (H_L). If trajectory instability and convergence monotonicity capture distinct epistemic signals, combining them with H_L should improve hallucination detection.

---

## Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| AUROC Gain | >= 0.03 over H_L alone |
| Statistical Significance | LRT p < 0.05 |

## Falsification Boundary

| Criterion | Threshold |
|-----------|-----------|
| AUROC Gain | < 0.02 |
| P-value | >= 0.10 |

---

## Prerequisites

| ID | Status | Gate | Result |
|----|--------|------|--------|
| h-e1 | VALIDATED | MUST_WORK | AUROC 0.5657 > 0.55 threshold |

---

## Experimental Setup (Inherited)

### Dataset
- **Name**: TruthfulQA MC1
- **Source**: HuggingFace datasets (truthful_qa)
- **Size**: 817 questions
- **Labels**: Binary correctness

### Model
- **Name**: LLaMA-2-7B
- **Source**: meta-llama/Llama-2-7b-hf
- **Layers**: 32 total, analysis on layers 24-32

### Controlled Variables
- Decoding: Greedy (temperature=0)
- Sequence length: Median aggregation per token
- Layer range: 24-32

### Baseline
- H_L (raw mean entropy): AUROC 0.6426

---

## Continuation Context

This hypothesis builds on h-e1 which validated that NTI discriminates hallucinations (AUROC 0.5657). Now testing whether combining trajectory metrics with H_L improves detection.

### From h-e1 Validation
- NTI extraction validated on layers 24-32
- Mean AUROC 0.5657 across 5 folds
- All folds > 0.52 falsification boundary
- Preprocessing pipeline established

### Key Components to Reuse
- NTI extraction code from h-e1
- Dataset loading and preprocessing
- Model loading with hooks for hidden states
- 5-fold CV infrastructure
