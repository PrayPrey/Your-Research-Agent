# Product Requirements Document: H-M2

**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Generated:** 2026-08-24  
**Status:** Draft

---

## Executive Summary

Validate whether models fine-tuned on a single benchmark exhibit larger cross-dataset generalization gaps compared to models fine-tuned on multiple benchmarks (>5 percentage points difference). This tests the mechanism underlying benchmark fingerprinting discovered in H-E1.

---

## Problem Statement

H-E1 demonstrated that benchmark-specific fingerprints exist in fine-tuned model representations. This follow-up investigates whether training regime diversity (single vs multi-benchmark) causally affects cross-dataset generalization, providing mechanistic insight into fingerprint formation.

---

## Functional Requirements

### FR-1: Single-Benchmark Fine-tuning Pipeline

| ID | Requirement |
|----|-------------|
| FR-1.1 | Fine-tune ResNet-50 (ImageNet pretrained) on CUB-200-2011 (3 seeds) |
| FR-1.2 | Fine-tune ResNet-50 on Stanford Dogs (3 seeds) |
| FR-1.3 | Fine-tune ResNet-50 on Stanford Cars (3 seeds) |
| FR-1.4 | Fine-tune ResNet-50 on FGVC Aircraft (3 seeds) |
| FR-1.5 | Fine-tune ResNet-50 on Oxford Flowers 102 (3 seeds) |
| FR-1.6 | Total: 15 single-benchmark models |

### FR-2: Multi-Benchmark Fine-tuning Pipeline

| ID | Requirement |
|----|-------------|
| FR-2.1 | Fine-tune on 3-mix (CUB + Dogs + Cars), 3 seeds |
| FR-2.2 | Fine-tune on 4-mix (CUB + Dogs + Cars + Flowers), 3 seeds |
| FR-2.3 | Fine-tune on 5-mix (all 5 benchmarks), 3 seeds |
| FR-2.4 | Use WeightedRandomSampler for balanced sampling |
| FR-2.5 | Total: 9 multi-benchmark models |

### FR-3: Cross-Dataset Evaluation

| ID | Requirement |
|----|-------------|
| FR-3.1 | Extract 2048-d features from penultimate layer |
| FR-3.2 | k-NN classification (k=5, cosine similarity) |
| FR-3.3 | Support set: 5 examples per class from target train |
| FR-3.4 | Query set: Full target test split |
| FR-3.5 | Evaluate all 24 models on NABirds (held-out domain) |

### FR-4: Gap Computation and Statistical Analysis

| ID | Requirement |
|----|-------------|
| FR-4.1 | Compute cross-dataset gap per model |
| FR-4.2 | Independent samples t-test (single vs multi groups) |
| FR-4.3 | Cohen's d effect size |
| FR-4.4 | 95% CI via bootstrap (1000 resamples) |

### FR-5: Baseline Experiments

| ID | Requirement |
|----|-------------|
| FR-5.1 | Baseline 1: ImageNet pretrained (no fine-tuning) |
| FR-5.2 | Baseline 2: Dataset size control (subsample multi to match single) |
| FR-5.3 | Baseline 3: Random benchmark assignment shuffle |

---

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | Training completes within 24 GPU hours (single A100) |
| NFR-2 | Feature extraction cached to disk |
| NFR-3 | Reproducible with fixed seeds |
| NFR-4 | Memory-efficient batch processing |

---

## Success Criteria

| Metric | Threshold |
|--------|-----------|
| Gap Difference | Mean(Gap_single) - Mean(Gap_multi) > 5pp |
| Statistical Significance | p < 0.05 |
| Effect Size | Cohen's d > 0.5 |

---

## Datasets

| Dataset | Classes | Train | Test |
|---------|---------|-------|------|
| CUB-200-2011 | 200 | 5,994 | 5,794 |
| Stanford Dogs | 120 | 12,000 | 8,580 |
| Oxford Flowers 102 | 102 | 2,040 | 6,149 |
| Stanford Cars | 196 | 8,144 | 8,041 |
| FGVC Aircraft | 100 | 6,667 | 3,333 |
| NABirds (held-out) | 555 | - | ~24,000 |

---

## Dependencies

- Phase 2C: 02c_experiment_brief.md
- Prerequisite: H-E1 validated (fingerprints exist)
