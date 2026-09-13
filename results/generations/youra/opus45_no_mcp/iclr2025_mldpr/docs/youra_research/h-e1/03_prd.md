# Product Requirements Document: H-E1

**Version:** 1.0
**Date:** 2026-08-19
**Hypothesis:** H-E1
**Status:** Draft

---

## 1. Executive Summary

This PRD defines requirements for validating hypothesis H-E1: "Models trained on high-popularity datasets show larger generalization gaps to held-out same-domain datasets compared to low-popularity datasets."

**Objective:** Measure and compare generalization gaps between high-popularity (CIFAR-10) and low-popularity (SVHN) training conditions using held-out same-domain test sets (CINIC-10 and SVHN-Extra respectively).

**Success Criteria:** Cohen's d > 0.3, p < 0.05 for the difference in generalization gaps between conditions.

---

## 2. Problem Statement

Benchmark datasets with high research popularity may exhibit inflated performance due to extensive architecture and hyperparameter optimization specifically targeting those benchmarks. This creates a "generalization gap" when models are evaluated on held-out same-domain datasets that lack these optimizations.

**Hypothesis:** High-popularity datasets (CIFAR-10) will show larger generalization gaps than low-popularity datasets (SVHN) when evaluated on distribution-matched held-out test sets.

---

## 3. Goals and Non-Goals

### Goals
- Train ResNet-18 on CIFAR-10 (high-popularity condition)
- Train ResNet-18 on SVHN (low-popularity condition)
- Measure generalization gap for each condition
- Statistically compare gaps using Cohen's d and t-test

### Non-Goals
- Architectural modifications or novel model development
- Hyperparameter optimization studies
- Multi-seed statistical validation (PoC uses single seed)

---

## 4. Data Specification

### 4.1 High-Popularity Condition

**Training Dataset: CIFAR-10**
- Source: `torchvision.datasets.CIFAR10`
- Auto-download: Yes
- Classes: 10
- Train: 50,000 images (32x32 RGB)
- Test: 10,000 images
- Normalization: (0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)

**Held-Out Test: CINIC-10**
- Source: Manual download from https://datashare.ed.ac.uk/bitstream/handle/10283/3192/CINIC-10.tar.gz
- Auto-download: No (requires manual download)
- Classes: 10 (same as CIFAR-10)
- Test: 90,000 images (full test split for statistical power)
- Format: ImageFolder structure

### 4.2 Low-Popularity Condition

**Training Dataset: SVHN**
- Source: `torchvision.datasets.SVHN`
- Auto-download: Yes
- Classes: 10 (digits 0-9)
- Train: 73,257 images (32x32 RGB)
- Test: 26,032 images

**Held-Out Test: SVHN-Extra (sampled)**
- Source: `torchvision.datasets.SVHN(split='extra')`
- Auto-download: Yes
- Sample: 26,032 images (matched to test set size for fair comparison)
- Purpose: Held-out same-domain evaluation

### 4.3 Data Augmentation (Training Only)
- RandomCrop(32, padding=4)
- RandomHorizontalFlip()
- ToTensor()
- Normalize()

---

## 5. Functional Requirements

### FR-1: Data Pipeline
- **FR-1.1:** Load CIFAR-10 train/test splits via torchvision
- **FR-1.2:** Load SVHN train/test/extra splits via torchvision
- **FR-1.3:** Download and load CINIC-10 test split (manual download required)
- **FR-1.4:** Apply consistent normalization across all datasets
- **FR-1.5:** Create DataLoaders with batch_size=128

### FR-2: Model Training
- **FR-2.1:** Train ResNet-18 on CIFAR-10 for 200 epochs
- **FR-2.2:** Train ResNet-18 on SVHN for 200 epochs
- **FR-2.3:** Use SGD optimizer (lr=0.1, momentum=0.9, weight_decay=5e-4)
- **FR-2.4:** Apply MultiStepLR scheduler (milestones=[100, 150], gamma=0.1)
- **FR-2.5:** Save model checkpoints for evaluation

### FR-3: Evaluation
- **FR-3.1:** Evaluate CIFAR-10 model on CIFAR-10 test set
- **FR-3.2:** Evaluate CIFAR-10 model on CINIC-10 test set
- **FR-3.3:** Evaluate SVHN model on SVHN test set
- **FR-3.4:** Evaluate SVHN model on SVHN-Extra sample
- **FR-3.5:** Compute generalization gap for each condition

### FR-4: Statistical Analysis
- **FR-4.1:** Compute Cohen's d for gap difference
- **FR-4.2:** Perform independent samples t-test
- **FR-4.3:** Report p-value and effect size

### FR-5: Visualization
- **FR-5.1:** Generate bar chart comparing generalization gaps
- **FR-5.2:** Generate accuracy comparison plots
- **FR-5.3:** Save figures to hypothesis_folder/figures/

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- Training should complete within 4 hours on single GPU
- Evaluation should complete within 10 minutes per condition

### NFR-2: Reproducibility
- Fixed random seed (42) for reproducibility
- Model checkpoints saved for verification

### NFR-3: Logging
- Training loss and accuracy logged per epoch
- Evaluation metrics logged with timestamps

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.12.0
torchvision>=0.13.0
torchmetrics>=0.11.0
scipy>=1.9.0
matplotlib>=3.5.0
numpy>=1.21.0
pyyaml>=6.0
```

### 7.2 External Data
- CINIC-10: https://datashare.ed.ac.uk/bitstream/handle/10283/3192/CINIC-10.tar.gz

### 7.3 Hardware
- GPU with ≥8GB VRAM recommended
- ~5GB disk space for datasets

---

## 8. Success Criteria

### Gate Metrics (from Phase 2B)
| Metric | Threshold | Type |
|--------|-----------|------|
| Cohen's d | > 0.3 | MUST_WORK |
| p-value | < 0.05 | MUST_WORK |
| Direction | gap_high > gap_low | PoC check |

### PoC Pass Conditions
1. Code runs without error
2. Both conditions produce valid accuracy measurements
3. gap_high_use > gap_low_use (direction check)

---

## 9. Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Data Setup | 0.5 days | Datasets downloaded and verified |
| CIFAR-10 Training | 1 day | Trained model checkpoint |
| SVHN Training | 1 day | Trained model checkpoint |
| Evaluation | 0.5 days | Accuracy metrics for all conditions |
| Analysis | 0.5 days | Statistical results and figures |

**Total:** ~3.5 days

---

## 10. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| CINIC-10 download fails | Provide manual download instructions |
| GPU unavailable | Support CPU training (slower) |
| Effect size too small | Report actual effect size for interpretation |

---

*Generated from Phase 2C Experiment Brief: 02c_experiment_brief.md*
