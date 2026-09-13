# Product Requirements Document: H-M1

**Hypothesis:** Under the scope of conversion training, if task embeddings are learned from clustered hidden states, then they will encode functional specialization patterns useful for downstream adaptation.

**Date:** 2026-08-28
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Executive Summary

This experiment validates that clustered hidden states from transformer-to-SSM conversion produce task embeddings encoding discriminable functional specialization. Building on H-E1's validated cluster structure, we train a task embedding layer and evaluate via linear probing.

---

## Problem Statement

H-E1 confirmed transformer hidden states cluster with task-correlated structure. H-M1 must demonstrate these clusters yield embeddings useful for task discrimination—not just statistical artifacts.

---

## Functional Requirements

### FR-1: Hidden State Extraction
Extract hidden states from pretrained Mamba model (mamba-370m) on SuperGLUE validation sets.

### FR-2: Task Embedding Layer
Implement `TaskEmbeddingEncoder`:
- Input: Hidden states [B, seq, hidden_dim]
- Output: Task embeddings [B, embedding_dim]
- Components: Linear projection + mean pooling

### FR-3: Embedding Training
Train embedding layer with contrastive loss (InfoNCE) on cluster membership labels from H-E1.
- Optimizer: AdamW, lr=1e-4
- Batch size: 32
- Epochs: 10

### FR-4: Linear Probe Evaluation
Freeze trained embeddings, fit LogisticRegression (L2, C=1.0) for 8-way task classification.

### FR-5: Baseline - Random Embeddings
Random initialization baseline (expected ~12.5% accuracy).

### FR-6: Ablation - Embedding Dimensions
Test embedding_dim ∈ {16, 32, 64}.

---

## Data Requirements

| Dataset | Split | Samples | Source |
|---------|-------|---------|--------|
| SuperGLUE (6 tasks) | Validation | ~4,445 | HuggingFace `super_glue` |

Tasks: BoolQ, CB, COPA, RTE, WiC, WSC

---

## Evaluation Metrics

| Metric | Threshold | Type |
|--------|-----------|------|
| Linear probe accuracy | > 12.5% | Gate (MUST_WORK) |
| Per-task accuracy | Informational | Secondary |
| Silhouette score | Informational | Secondary |

---

## Success Criteria

**Gate Condition:** Linear probe accuracy > 12.5% (random baseline for 8 tasks)
**Stretch Goal:** Accuracy > 50%

---

## Non-Functional Requirements

- Training completes in < 30 minutes on single GPU
- Reproducible with fixed seeds
- Figures saved to `h-m1/figures/`

---

## Dependencies

- H-E1: Cluster assignments for training labels
- mamba-ssm package
- HuggingFace datasets
- sklearn for linear probe
