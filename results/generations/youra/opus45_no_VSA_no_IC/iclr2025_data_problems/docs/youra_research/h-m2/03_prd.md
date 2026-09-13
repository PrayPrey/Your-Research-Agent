# Product Requirements Document: h-m2

**Date:** 2026-08-24
**Hypothesis:** Mode profiles exhibit dissociation: inter-method variance > intra-method variance (F-ratio > 4.0, Cohen's d > 0.5)
**Type:** MECHANISM
**Phase:** 3 - Implementation Planning

---

## Executive Summary

This PRD defines requirements for validating h-m2: proving attribution methods (TRAK, TracIn, Kronfluence) produce statistically distinguishable mode profiles. The experiment measures inter-method vs intra-method variance using ANOVA F-ratio and Cohen's d effect size metrics.

**Success Criteria:** F-ratio > 4.0, Cohen's d > 0.5, p-value < 0.05

---

## Problem Statement

h-m1 established that different attribution methods create different mode sensitivities. h-m2 must prove this difference is statistically significant - that method identity explains more variance in mode profiles than random seed variation.

**Key Question:** Do attribution methods have "fingerprints" that persist across random training seeds?

---

## Functional Requirements

### FR-1: Multi-Seed Model Training
- Train ResNet-18 on CIFAR-10 with 10 different seeds
- Seeds: [42, 123, 456, 789, 1000, 1111, 2222, 3333, 4444, 5555]
- Optimizer: SGD (momentum=0.9, weight_decay=5e-4)
- LR: 0.1 with cosine annealing
- Epochs: 200 per seed
- Output: 10 trained model checkpoints

### FR-2: Attribution Score Computation
- Reuse h-m1 infrastructure (TRAK, TracIn, Kronfluence)
- Compute influence for 1000 probes per mode × 3 modes = 3000 probes
- Run all 3 methods per seed
- Total: 90,000 influence computations (3 methods × 10 seeds × 3000 probes)

### FR-3: Mode Profile Extraction
- Compute mode profile vector per method per seed
- Profile = [mem_sensitivity, transfer_sensitivity, spurious_sensitivity]
- Normalize to unit vector
- Output: 30 profile vectors (3 methods × 10 seeds)

### FR-4: Variance Decomposition (ANOVA)
- Compute between-group variance (inter-method)
- Compute within-group variance (intra-method)
- Calculate F-ratio = MS_between / MS_within
- Compute p-value from F-distribution (df_between=2, df_within=27)

### FR-5: Effect Size Computation
- Compute pairwise Cohen's d for all method pairs
- Report maximum Cohen's d across all comparisons and dimensions
- Medium effect: d > 0.5, Large effect: d > 0.8

### FR-6: Gate Evaluation
- Check F-ratio > 4.0 threshold
- Check Cohen's d > 0.5 threshold
- Report PASS/FAIL per criterion

### FR-7: Visualization
- Required: Gate metrics bar chart (F-ratio vs 4.0, Cohen's d vs 0.5)
- Optional: 3D mode profile scatter, variance box plot, Cohen's d heatmap

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- All random seeds fixed and documented
- Checkpoint saving for all 10 model runs
- Deterministic mode for PyTorch where possible

### NFR-2: Computational Efficiency
- Parallelizable: 10 seeds can train independently
- Attribution caching from h-m1 probe infrastructure
- GPU memory: Single ResNet-18 fits easily

### NFR-3: Statistical Validity
- 10 seeds provide df_within=27 (adequate for ANOVA)
- Standard scipy.stats implementation for F-test
- Manual Cohen's d with pooled standard deviation

---

## Data Requirements

### Dataset
- CIFAR-10 (standard torchvision download)
- 50,000 train / 10,000 test images

### Probe Sets (from h-m1)
- 1000 memorization probe pairs
- 1000 feature transfer probe pairs
- 1000 spurious correlation probe pairs

---

## Success Criteria

| Metric | Threshold | Interpretation |
|--------|-----------|----------------|
| F-ratio | > 4.0 | Methods differ more than random variation |
| Cohen's d | > 0.5 | Medium-to-large practical effect size |
| p-value | < 0.05 | Statistically significant |

**Overall:** Both F-ratio AND Cohen's d thresholds must be met for gate PASS.

---

## Dependencies

- h-m1 validated infrastructure (attribution methods, probe sets)
- scipy.stats for ANOVA
- numpy for variance computation
- matplotlib for visualization

---

## Out of Scope

- New attribution methods beyond TRAK/TracIn/Kronfluence
- Different model architectures
- Different datasets
- Temporal analysis of attribution stability
