# Product Requirements Document: h-e1

**Date:** 2026-08-09
**Hypothesis:** NTI (layers 24-32) achieves AUROC > 0.55 on TruthfulQA MC1
**Type:** EXISTENCE (PoC Validation)

---

## Executive Summary

This PRD specifies implementation requirements for validating the Normalized Trajectory Instability (NTI) metric as a hallucination detector. NTI measures the coefficient of variation of entropy across layers 24-32 in LLaMA-2-7B's logit-lens trajectory. Success criterion: AUROC > 0.55 on TruthfulQA MC1.

---

## Problem Statement

Current hallucination detection methods rely on output-level signals. This experiment tests whether internal representation instability (measured via NTI) provides discriminative signal for hallucination detection.

---

## Functional Requirements

### FR-1: Data Pipeline
- **FR-1.1:** Load TruthfulQA MC1 dataset (817 samples) from HuggingFace
- **FR-1.2:** Extract question + answer pairs with correctness labels
- **FR-1.3:** Implement 5-fold stratified cross-validation splits

### FR-2: Model Infrastructure
- **FR-2.1:** Load LLaMA-2-7B via TransformerLens HookedTransformer
- **FR-2.2:** Configure activation caching for layers 24-32
- **FR-2.3:** Support float16 inference on CUDA

### FR-3: NTI Metric Extraction
- **FR-3.1:** Extract residual stream at each layer (24-32)
- **FR-3.2:** Apply logit-lens transformation (ln_final + W_U)
- **FR-3.3:** Compute entropy at last token position per layer
- **FR-3.4:** Calculate NTI = std(entropy) / mean(entropy) across layers

### FR-4: Evaluation Pipeline
- **FR-4.1:** Train logistic regression classifier on NTI scores per fold
- **FR-4.2:** Compute AUROC for each fold
- **FR-4.3:** Calculate mean AUROC, min AUROC, pass rate (folds > 0.55)

### FR-5: Visualization
- **FR-5.1:** Gate metrics bar chart (AUROC per fold + mean)
- **FR-5.2:** Entropy trajectory heatmap (layer × sample)
- **FR-5.3:** NTI distribution histogram (correct vs hallucinated)
- **FR-5.4:** ROC curves (per-fold + mean)

---

## Non-Functional Requirements

### NFR-1: Performance
- Single GPU inference (16GB+ VRAM recommended)
- Process all 817 samples within 2 hours

### NFR-2: Reproducibility
- Fixed random seed (42) for all operations
- Deterministic 5-fold splits

### NFR-3: Dependencies
- TransformerLens >= 2.0.0
- PyTorch >= 2.1.0
- scikit-learn >= 1.4.0
- HuggingFace datasets, transformers

---

## Success Criteria

| Metric | Threshold | Gate |
|--------|-----------|------|
| Mean AUROC | > 0.55 | MUST_WORK |
| Min Fold AUROC | > 0.52 | Falsification boundary |
| Pass Rate | >= 4/5 folds | Required |

---

## Out of Scope

- Training or fine-tuning models
- Multiple model comparisons (future hypothesis)
- Real-time inference optimization

---

## Dependencies

- Phase 2C experiment brief (02c_experiment_brief.md) ✓
- HuggingFace Hub access for model/dataset
- CUDA-capable GPU

---

*Generated from Phase 2C Experiment Brief*
