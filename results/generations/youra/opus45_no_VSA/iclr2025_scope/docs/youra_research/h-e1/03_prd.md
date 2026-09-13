# Product Requirements Document: H-E1

**Hypothesis:** Linear probe on frozen MiniLM embeddings achieves ≥70% oracle adapter selection accuracy (or top-3 ≥85%)
**Type:** EXISTENCE (PoC Validation)
**Date:** 2026-08-09
**Author:** Anonymous

---

## Executive Summary

Validate that a linear classifier on frozen MiniLM-L6-v2 embeddings can accurately predict the oracle adapter (best-performing LoRA) for input instructions. This tests whether instruction embeddings contain sufficient signal for adapter routing.

**Success Criteria:** Top-1 ≥70% OR Top-3 ≥85%
**Falsification:** Top-3 <60%

---

## Problem Statement

Given H-E0 validated that FLAN task families are linearly separable (macro-F1=0.995), we now test whether this structure extends to adapter selection. The oracle adapter (lowest loss on target response) may differ from task family membership.

**Key Question:** Can embedding-based routing achieve practical accuracy for adapter selection?

---

## Functional Requirements

### FR-1: Data Pipeline

| ID | Requirement | Source |
|----|-------------|--------|
| FR-1.1 | Load Open-Orca/FLAN dataset via HuggingFace streaming | Phase 2C |
| FR-1.2 | Sample 2,000-5,000 instructions for oracle labeling | Phase 2C |
| FR-1.3 | Extract instruction prefix (first sentence or 256 chars) | Phase 2C |
| FR-1.4 | Generate oracle labels via 9-adapter loss comparison | Phase 2C |
| FR-1.5 | Stratified train/val/test split (70/15/15) by oracle adapter | Phase 2C |

### FR-2: Model Components

| ID | Requirement | Source |
|----|-------------|--------|
| FR-2.1 | Load sentence-transformers/all-MiniLM-L6-v2 (frozen) | Phase 2C |
| FR-2.2 | Implement LogisticRegression classifier (max_iter=2000, solver=lbfgs) | Phase 2C |
| FR-2.3 | Load 9 FLAN-family LoRA adapters for oracle computation | Phase 2C |

### FR-3: Baseline Models

| ID | Requirement | Source |
|----|-------------|--------|
| FR-3.1 | Random selection baseline (~11% expected) | Phase 2C |
| FR-3.2 | Majority class baseline (predict most frequent adapter) | Phase 2C |

### FR-4: Evaluation

| ID | Requirement | Source |
|----|-------------|--------|
| FR-4.1 | Compute Top-1 accuracy (predicted == oracle) | Phase 2C |
| FR-4.2 | Compute Top-3 accuracy (oracle in top 3 predictions) | Phase 2C |
| FR-4.3 | Generate confusion matrix (predicted vs oracle) | Phase 2C |
| FR-4.4 | Compute oracle-vs-task-family agreement rate | Phase 2C |

### FR-5: Visualization

| ID | Requirement | Source |
|----|-------------|--------|
| FR-5.1 | Gate metrics bar chart (Top-1, Top-3 vs thresholds) | Phase 2C |
| FR-5.2 | Per-adapter accuracy breakdown | Phase 2C |
| FR-5.3 | t-SNE/UMAP of embeddings by oracle adapter | Phase 2C |

---

## Non-Functional Requirements

| ID | Requirement | Rationale |
|----|-------------|-----------|
| NFR-1 | Reproducible with random_state=42 | Scientific validity |
| NFR-2 | Runtime <30 min on single GPU | PoC efficiency |
| NFR-3 | Memory <16GB | Standard workstation |

---

## Success Criteria

| Metric | Threshold | Gate |
|--------|-----------|------|
| Top-1 Accuracy | ≥70% | PASS (either) |
| Top-3 Accuracy | ≥85% | PASS (either) |
| Top-3 Accuracy | <60% | FAIL |

---

## Dependencies

- **H-E0:** VALIDATED (prerequisite satisfied)
- **External:** HuggingFace Hub, sentence-transformers, sklearn, PEFT

---

## Out of Scope

- Adapter fusion/merging (H-M1)
- End-to-end training (H-M2)
- Baseline repository comparison (Phase 5)
