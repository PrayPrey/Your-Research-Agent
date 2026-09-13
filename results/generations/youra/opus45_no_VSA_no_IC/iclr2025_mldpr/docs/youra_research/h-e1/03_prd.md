# Product Requirements Document: H-E1 Benchmark Fingerprint Detection

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Generated:** 2026-08-24

---

## Executive Summary

Validate that fine-tuning on different image classification benchmarks leaves detectable "fingerprints" in model representations. A linear classifier on penultimate layer features should predict the training benchmark with >60% accuracy (chance=20% for 5 benchmarks).

---

## Problem Statement

**Research Question:** Do fine-grained classification benchmarks leave distinguishable traces in learned representations?

**Hypothesis:** Fine-tuning creates benchmark-specific feature patterns detectable via simple linear probing.

**Success Threshold:** >60% 5-class accuracy on held-out domain (NABirds).

---

## Functional Requirements

### FR1: Model Fine-tuning Pipeline

| ID | Requirement |
|----|-------------|
| FR1.1 | Fine-tune ResNet-50 (ImageNet pretrained) on 5 benchmarks |
| FR1.2 | Train 3 seeds per benchmark (15 total models) |
| FR1.3 | Use SGD optimizer (lr=0.01, cosine annealing, 30 epochs) |
| FR1.4 | Save model checkpoints with metadata |

**Benchmarks:**
1. CUB-200-2011 (200 bird classes)
2. Stanford Dogs (120 dog breeds)
3. Oxford Flowers 102 (102 flower types)
4. Stanford Cars (196 car models)
5. FGVC Aircraft (100 aircraft variants)

### FR2: Feature Extraction

| ID | Requirement |
|----|-------------|
| FR2.1 | Extract 2048-d features from avgpool layer |
| FR2.2 | Process full NABirds test set (~24k images) per model |
| FR2.3 | Label features by source benchmark |
| FR2.4 | Store features efficiently (memory-mapped or batched) |

### FR3: Linear Probe Training

| ID | Requirement |
|----|-------------|
| FR3.1 | Train LogisticRegression classifier (5 classes) |
| FR3.2 | Use 70/15/15 train/val/test split (by model) |
| FR3.3 | Apply L2 regularization (C=1.0) |
| FR3.4 | Report accuracy with 95% CI |

### FR4: Baseline Experiments

| ID | Requirement |
|----|-------------|
| FR4.1 | Random baseline: untrained ResNet-50 features |
| FR4.2 | Shuffled labels: permutation test |
| FR4.3 | Same-domain: probe on fine-tuning benchmark (not NABirds) |

### FR5: Statistical Analysis

| ID | Requirement |
|----|-------------|
| FR5.1 | 3-fold CV with models as units |
| FR5.2 | Bootstrap CI (1000 resamples) |
| FR5.3 | One-sample t-test vs 20% chance |
| FR5.4 | Report Cohen's d effect size |

---

## Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR1 | Performance | Complete fine-tuning in <12 GPU hours |
| NFR2 | Memory | Handle 360k feature vectors efficiently |
| NFR3 | Reproducibility | Seed all random operations |
| NFR4 | Modularity | Separate data/model/training/eval modules |

---

## Success Criteria

| Metric | Target | Falsification |
|--------|--------|---------------|
| Probe Accuracy | >60% | ≤25% |
| Random Baseline | ~20% | - |
| Shuffled Baseline | ~20% | - |
| Statistical Significance | p<0.05 | p≥0.05 |

---

## Dependencies

- PyTorch ≥2.0
- torchvision ≥0.15
- timm ≥0.9
- scikit-learn ≥1.3
- Dataset downloads: CUB, Stanford Dogs/Cars, Flowers, Aircraft, NABirds

---

## Output Artifacts

1. `models/finetuned/` — 15 model checkpoints
2. `features/` — Extracted feature matrices
3. `results/h_e1_results.json` — Accuracy, CI, p-value
4. `figures/confusion_matrix.png` — 5×5 benchmark confusion
5. `04_validation.md` — Validation report
