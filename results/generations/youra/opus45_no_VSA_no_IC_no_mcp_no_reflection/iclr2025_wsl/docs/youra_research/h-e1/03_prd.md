# Product Requirements Document: H-E1

**Date:** 2026-08-29
**Hypothesis:** H-E1 (EXISTENCE)
**Version:** 1.0

---

## Executive Summary

Validate that heavy-tailed exponents (α) can be computed with bounded variance (σ < 0.5) for ViT attention weight matrices using the Hill estimator across 100+ pretrained ViT models from Hugging Face Model Hub.

---

## Problem Statement

Heavy-Tailed Self-Regularization (HT-SR) theory (Martin & Mahoney) provides quality metrics for neural network weight matrices. Before building downstream hypotheses that use α values for ViT analysis, we must verify:
1. WeightWatcher can extract α from ViT attention layers
2. α variance across diverse ViT models remains bounded (σ < 0.5)

---

## Functional Requirements

### FR-1: Model Collection
- Query HuggingFace Hub API for ViT image-classification models
- Collect 100+ unique model checkpoints
- Include families: google/vit-*, facebook/deit-*, microsoft/swin-*
- Sort by downloads, filter working checkpoints

### FR-2: Weight Extraction
- Load each model via `transformers.AutoModel.from_pretrained()`
- Extract attention layer weight matrices (query, key, value projections)
- Handle architecture variations (standard ViT, DeiT, Swin)

### FR-3: Heavy-Tail Computation
- Initialize WeightWatcher for each model
- Compute α (power-law exponent) per attention layer
- Use Hill estimator (WeightWatcher default)
- Aggregate per-model mean α

### FR-4: Statistical Analysis
- Compute global σ(α) across all models
- Compute α distribution statistics (mean, median, range)
- Group analysis by model family

### FR-5: Visualization
- Gate metric bar chart: σ(α) vs threshold 0.5
- Histogram of α values
- Box plot by model family
- Scatter: α vs model size

---

## Non-Functional Requirements

### NFR-1: Performance
- Process 100+ models within 4 hours
- Memory: handle models up to 1B parameters

### NFR-2: Reliability
- Graceful skip for failed model loads
- Minimum 100 successful models required

### NFR-3: Reproducibility
- Deterministic computation (no random seeds needed)
- Log all model IDs and versions

---

## Success Criteria

| Metric | Target | Priority |
|--------|--------|----------|
| σ(α) | < 0.5 | **GATE** |
| Models processed | ≥ 100 | Required |
| α range | [1.5, 4.0] | Expected |

---

## Dependencies

- `weightwatcher>=0.7.0`
- `transformers>=4.30.0`
- `huggingface_hub>=0.16.0`
- `numpy`, `pandas`, `matplotlib`

---

## Out of Scope

- Training any models
- Comparing α to generalization metrics
- Modifying WeightWatcher internals

---

## Data Requirements

### Input
- HuggingFace Model Hub API access
- No local datasets required

### Output
- `results.json`: per-model α values
- `figures/`: visualization outputs
- `04_validation.md`: gate result

---

*Source: 02c_experiment_brief.md*
