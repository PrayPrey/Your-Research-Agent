# Product Requirements Document: h-m2

**Hypothesis:** Probes transfer across model families with AUROC gap <0.10 (train on Model A, evaluate on Model B hidden states)

**Type:** MECHANISM (Transfer)
**Date:** 2026-08-24
**Phase 2C Source:** 02c_experiment_brief.md

---

## Executive Summary

Validate cross-model probe transfer for semantic entropy prediction. Train SEP probes on one model family's hidden states, evaluate on another. Success: mean AUROC gap <0.10 across 6 transfer pairs.

---

## Problem Statement

SEP probes from h-e1 are model-specific. If uncertainty representations are universal, probes should transfer across model families without significant performance loss.

**Research Question:** Do learned uncertainty probes generalize across model architectures?

---

## Functional Requirements

### FR-1: Hidden State Extraction
- Extract hidden states at ~2/3 depth for all 3 models
- Handle dimension mismatch (Llama/Mistral: 4096, Qwen: 3584)
- Cache extracted states for reuse

### FR-2: Per-Model SEP Training
- Train LogisticRegression probe per model (reuse h-e1 methodology)
- Binary labels from semantic entropy (median threshold)
- 80/20 train/val split

### FR-3: Transfer Matrix Evaluation
- 9 evaluations: 3 baselines + 6 cross-model transfers
- Direct transfer (no alignment) as primary method
- AUROC computation per pair

### FR-4: Affine Alignment (Fallback)
- Least-squares affine mapping (W, b) for dimension alignment
- Required for Qwen ↔ Llama/Mistral pairs
- Fit on train split, evaluate on val split

### FR-5: Results Aggregation
- Transfer matrix heatmap (3×3)
- Transfer gap bar chart
- Mean/max gap statistics

---

## Non-Functional Requirements

### NFR-1: Computational Efficiency
- Sequential model loading (memory constraint)
- Cache hidden states to disk (HDF5/NPY)

### NFR-2: Reproducibility
- Fixed random seed (42)
- Document model versions and layer indices

---

## Success Criteria

| Metric | Threshold | Type |
|--------|-----------|------|
| Mean transfer gap | <0.10 AUROC | Primary |
| Max transfer gap | <0.15 AUROC | Secondary |
| All pairs evaluated | 9/9 | Completeness |

---

## Models

| Model | HuggingFace ID | Hidden Dim | Layers |
|-------|----------------|------------|--------|
| Llama-3-8B-Instruct | meta-llama/Meta-Llama-3-8B-Instruct | 4096 | 32 |
| Mistral-7B-Instruct-v0.2 | mistralai/Mistral-7B-Instruct-v0.2 | 4096 | 32 |
| Qwen-2-7B-Instruct | Qwen/Qwen2-7B-Instruct | 3584 | 28 |

---

## Dataset

- **Name:** TruthfulQA (generation)
- **Size:** 817 questions
- **Split:** 80% train (654), 20% val (163)
- **Labels:** Binarized semantic entropy

---

## Dependencies

- **h-e1:** SEP methodology, per-model baseline AUROCs
- **Libraries:** transformers, sklearn, numpy, torch

---

## Out of Scope

- Multi-layer probing (use single layer at 2/3 depth)
- Non-linear alignment methods
- Fine-tuning models
