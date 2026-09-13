# Product Requirements Document: H-E1 Crystallization Zone Detection

**Version:** 1.0
**Date:** 2026-08-19
**Hypothesis:** H-E1 - Crystallization zone exists as localized training phase where WGA decline accelerates
**Type:** EXISTENCE (PoC)

---

## 1. Executive Summary

This PRD defines requirements for detecting crystallization zones in neural network training dynamics. The experiment tests whether a localized training phase exists where Worst-Group Accuracy (WGA) decline accelerates, indicated by significant negative second derivative (d²WGA/dt²).

### Success Criteria
- Detect significant negative d²WGA/dt² peak in first 50% of training
- Peak magnitude < -0.01 threshold
- Effect present in at least 2/3 benchmarks tested

---

## 2. Problem Statement

Neural networks trained with ERM on datasets with spurious correlations exhibit declining worst-group accuracy during training. The hypothesis posits this decline is not gradual but contains a "crystallization zone" where the model commits to spurious features, detectable via acceleration in WGA decline.

---

## 3. Functional Requirements

### FR-1: Data Loading
- Load Waterbirds dataset from WILDS benchmark
- Load CelebA (Hair Color) dataset from WILDS benchmark
- Support standard train/val/test splits
- Provide group annotations for WGA computation

### FR-2: Baseline Model Training
- Train ResNet-50 with ImageNet pretrained weights
- Use SGD optimizer (momentum=0.9, weight_decay=1e-4)
- Constant learning rate (1e-3) - no scheduling
- Batch size 128
- 100 epochs for Waterbirds, 50 epochs for CelebA
- CrossEntropyLoss

### FR-3: WGA Computation
- Compute per-group accuracy at each epoch
- Track all (label, spurious_attribute) groups
- Return minimum accuracy across groups as WGA
- Store WGA history for derivative analysis

### FR-4: Crystallization Detection
- Apply 5-epoch rolling window smoothing to WGA curve
- Compute first derivative (dWGA/dt)
- Compute second derivative (d²WGA/dt²)
- Detect negative peak in first 50% of training
- Report peak epoch, magnitude, and significance

### FR-5: Visualization
- WGA curve with crystallization point marked
- Second derivative plot with peak highlighted
- Multi-benchmark comparison (normalized epoch axis)
- Per-group accuracy divergence

### FR-6: Ablation Variants
- Smoothing window sensitivity: 3, 5, 7 epochs
- Detection threshold sensitivity: -0.005, -0.01, -0.02

---

## 4. Data Specification

### Primary Dataset: Waterbirds
| Attribute | Value |
|-----------|-------|
| Source | WILDS benchmark (p-lambda/wilds) |
| Task | Binary classification (landbird vs waterbird) |
| Spurious Feature | Background (water vs land) |
| Train Samples | 4,795 |
| Val Samples | 400 |
| Test Samples | 6,593 |
| Groups | 4 (2 labels × 2 backgrounds) |
| Download | Auto via WILDS package |

### Secondary Dataset: CelebA (Hair Color)
| Attribute | Value |
|-----------|-------|
| Source | WILDS benchmark |
| Task | Binary classification (blond vs non-blond) |
| Spurious Feature | Gender |
| Total Samples | 202,599 |
| Groups | 4 (2 labels × 2 genders) |
| Download | Auto via WILDS package |

---

## 5. Model Specification

### Baseline: ResNet-50
| Attribute | Value |
|-----------|-------|
| Architecture | ResNet-50 |
| Pretrained | ImageNet |
| Final Layer | Linear(2048, 2) |
| Parameters | ~25.6M |
| Input Size | 224×224×3 |

### No Proposed Model Modification
This is a DETECTION experiment - we observe training dynamics of standard ERM, not modify the model.

---

## 6. Evaluation Metrics

### Primary Metrics
| Metric | Description |
|--------|-------------|
| WGA | Minimum accuracy across all groups |
| d²WGA/dt² | Second derivative of smoothed WGA |
| Peak Epoch | Epoch of crystallization detection |
| Peak Magnitude | Value of d²WGA/dt² at peak |

### Success Criteria
- Negative peak exists: d²WGA/dt² < -0.01
- Peak in early training: epoch < 50% of total
- Reproducible across benchmarks: 2/3 datasets

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.10.0
torchvision>=0.11.0
wilds>=2.0.0
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.4.0
tqdm>=4.62.0
pyyaml>=5.4.0
```

### 7.2 Reference Implementations
| Repository | Usage |
|------------|-------|
| p-lambda/wilds | Dataset loading, WGA baseline |
| kohpangwei/group_DRO | Training protocol reference |

---

## 8. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed (42)
- Deterministic operations where possible
- Checkpoint every epoch

### NFR-2: Compute
- Single GPU training (RTX 3090 or equivalent)
- Training time: ~4 hours Waterbirds, ~12 hours CelebA

### NFR-3: Storage
- Model checkpoints: ~100MB per epoch
- WGA logs: <1MB total

---

## 9. Out of Scope

- Multi-seed statistical analysis (EXISTENCE only needs 1 run)
- Model modification or intervention
- Comparison with Group DRO or other methods
- Theoretical analysis of crystallization mechanism

---

## 10. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| WGA proxy validity | Use multiple group definitions |
| Detection method noise | 5-epoch smoothing window |
| Threshold sensitivity | Ablation across thresholds |

---

*Generated for Phase 3 Implementation Planning*
