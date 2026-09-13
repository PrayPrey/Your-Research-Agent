# Product Requirements Document: H-M3

**Hypothesis:** Under QA conditions, if we combine inverse entropy and consistency via linear fusion (α·(1-entropy) + β·consistency), then the combined score is more predictive than either alone.

**Date:** 2026-08-19
**Type:** MECHANISM
**Prerequisites:** H-M2 (PASS: AUROC=0.8081, d=1.19)

---

## Executive Summary

This PRD specifies implementation of a linear fusion scoring system that combines entropy-based uncertainty signals (from H-M1) with semantic consistency signals (from H-M2) to predict hallucination-prone questions in QA tasks. The hypothesis proposes that combining complementary signals yields superior predictive performance.

---

## Problem Statement

Individual uncertainty metrics (entropy: AUROC=0.6454, consistency: AUROC=0.8081) capture different failure modes. Entropy captures token-level uncertainty; consistency captures semantic stability across responses. A combined score may leverage both signals for improved hallucination detection.

---

## Functional Requirements

### FR1: Score Fusion Module
- **FR1.1:** Implement LinearFusionScorer class
- **FR1.2:** Normalize inputs to [0,1] range via min-max normalization
- **FR1.3:** Compute inverse entropy (1 - normalized_entropy)
- **FR1.4:** Apply linear combination: α·confidence + β·consistency

### FR2: Weight Optimization
- **FR2.1:** Implement grid search over α ∈ [0.0, 0.1, ..., 1.0]
- **FR2.2:** Implement grid search over β ∈ [0.0, 0.1, ..., 1.0]
- **FR2.3:** Optimize on validation holdout (10% of data)
- **FR2.4:** Report optimal (α, β) and validation AUROC

### FR3: Evaluation Pipeline
- **FR3.1:** Compute AUROC for entropy-only baseline
- **FR3.2:** Compute AUROC for consistency-only baseline
- **FR3.3:** Compute AUROC for combined score
- **FR3.4:** Calculate improvement: AUROC_combined - max(single metrics)
- **FR3.5:** Statistical test (bootstrap CI or DeLong) for significance

### FR4: Data Pipeline
- **FR4.1:** Load TriviaQA validation set (~11,000 questions)
- **FR4.2:** Split: 10% validation (weight tuning), 90% test (final evaluation)
- **FR4.3:** Generate 10 responses per question using Llama-2-7B-chat
- **FR4.4:** Compute entropy from logits (reuse H-M1 scorer)
- **FR4.5:** Compute consistency via embeddings (reuse H-M2 scorer)
- **FR4.6:** Aggregate correctness labels from answer matching

### FR5: Ablation Study
- **FR5.1:** Entropy-only (α=1.0, β=0.0)
- **FR5.2:** Consistency-only (α=0.0, β=1.0)
- **FR5.3:** Equal weights (α=0.5, β=0.5)
- **FR5.4:** Optimal weights (from grid search)

### FR6: Visualization
- **FR6.1:** Gate metrics bar chart (3 AUROCs)
- **FR6.2:** ROC curves overlay (3 curves)
- **FR6.3:** Weight heatmap (AUROC as f(α, β))
- **FR6.4:** Scatter plot: entropy vs consistency, colored by correctness

---

## Non-Functional Requirements

### NFR1: Sample Size
- Minimum 500 questions for final evaluation (statistically meaningful)
- Full TriviaQA validation set preferred (~11,000 questions)

### NFR2: Reproducibility
- Fixed seed: 42
- Deterministic normalization
- Saved intermediate results

### NFR3: Performance
- Grid search: <5 minutes for 121 combinations
- Total pipeline: <2 hours with generation

---

## Success Criteria

| Metric | Threshold | Priority |
|--------|-----------|----------|
| AUROC_combined > max(AUROC_entropy, AUROC_consistency) | > 0 improvement | PRIMARY |
| Code runs without error | Yes | BLOCKING |
| All figures generated | Yes | REQUIRED |

---

## Dependencies

### From H-M1
- TokenEntropyScorer class
- entropy.py module
- Entropy computation logic

### From H-M2
- SemanticConsistencyScorer class
- consistency.py module
- Embedding-based similarity

### External
- TriviaQA dataset (HuggingFace)
- Llama-2-7B-chat model
- all-MiniLM-L6-v2 embeddings
- sklearn.metrics (roc_auc_score)

---

## Out of Scope

- Learned fusion weights (neural combination)
- Non-linear fusion methods
- Cross-dataset generalization (H-M4 scope)
- Alternative embedding models

---

## Appendix: Phase 2C Completeness

| Item | Included |
|------|----------|
| Dataset: TriviaQA | ✅ FR4.1 |
| Model: Llama-2-7B-chat | ✅ FR4.3 |
| Model: all-MiniLM-L6-v2 | ✅ FR4.5 |
| Metric: AUROC | ✅ FR3.1-3.4 |
| Ablation: Single metrics | ✅ FR5.1-5.2 |
| Ablation: Equal weights | ✅ FR5.3 |
| Ablation: Optimal weights | ✅ FR5.4 |
