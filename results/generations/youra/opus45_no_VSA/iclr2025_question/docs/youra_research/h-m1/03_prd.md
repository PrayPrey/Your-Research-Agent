# Product Requirements Document: h-m1

**Date:** 2026-08-09
**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## Executive Summary

This PRD defines requirements for validating that combining trajectory metrics (NTI, CMI) with baseline entropy (H_L) improves hallucination detection AUROC by >= 0.03 with statistical significance (LRT p < 0.05).

---

## Problem Statement

Existing hallucination detection using raw output entropy (H_L) achieves AUROC ~0.6426 on TruthfulQA MC1. This experiment tests whether trajectory-based metrics capturing internal state dynamics provide incremental predictive validity.

---

## Functional Requirements

### FR-1: Data Loading and Preprocessing
- Load TruthfulQA MC1 dataset (817 questions) from HuggingFace
- Reuse h-e1 preprocessing pipeline
- Generate 5-fold stratified CV splits (seed=42)

### FR-2: Feature Extraction (Reuse from h-e1)
- Extract hidden states from LLaMA-2-7B layers 24-32
- Compute NTI (Normalized Trajectory Instability)
- Compute CMI (Convergence Monotonicity Index)
- Compute H_L (mean entropy across layers)

### FR-3: Null Model (H_L Only)
- Train logistic regression on H_L feature only
- Compute AUROC and log-likelihood per fold

### FR-4: Full Model (H_L + NTI + CMI)
- Train logistic regression on [H_L, NTI, CMI] features
- Compute AUROC and log-likelihood per fold

### FR-5: Statistical Testing
- Compute Likelihood Ratio Test statistic: G = 2 * (LL_full - LL_null)
- Compute p-value using chi2.sf(G, df=2)
- Aggregate across folds

### FR-6: Evaluation Metrics
- Primary: AUROC gain (full - null)
- Secondary: LRT p-value
- Success: AUROC gain >= 0.03 AND p < 0.05
- Falsification: AUROC gain < 0.02 OR p >= 0.10

### FR-7: Visualization
- ROC curves: null vs full model overlay
- Bar chart: per-fold AUROC comparison
- Feature coefficients plot

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed (42) for all operations
- Deterministic model loading

### NFR-2: Reusability
- Leverage h-e1 infrastructure (NTI extraction, CV splits)
- Modular feature extraction

### NFR-3: Performance
- Complete validation within 2 hours on single GPU

---

## Success Criteria

| Metric | Threshold | Source |
|--------|-----------|--------|
| AUROC Gain | >= 0.03 | Phase 2B |
| LRT p-value | < 0.05 | Phase 2B |
| Falsification | gain < 0.02 OR p >= 0.10 | Phase 2B |

---

## Dependencies

| Dependency | Source | Status |
|------------|--------|--------|
| NTI extraction | h-e1 | VALIDATED |
| TruthfulQA MC1 | HuggingFace | Available |
| LLaMA-2-7B | meta-llama | Available |
| 5-fold CV splits | h-e1 | VALIDATED |

---

## Out of Scope

- Hyperparameter optimization for logistic regression
- Alternative classifiers (SVM, neural networks)
- Other LLM models

---

*Generated from Phase 2C experiment brief*
