# Product Requirements Document: H-M2

**Hypothesis:** Spurious features are easier to learn than core features
**Type:** MECHANISM
**Date:** 2026-08-12
**Author:** Anonymous

---

## 1. Executive Summary

Validate that spurious features (background) are learned faster than core features (bird type) by tracking linear probe accuracy across all training epochs. Using epoch-by-epoch probe training on ResNet-18 representations, we measure when each feature type reaches peak accuracy. Success requires spurious probe peak occurring before core probe peak.

**Gate Condition:** SHOULD_WORK - spurious_peak_epoch < core_peak_epoch

---

## 2. Problem Statement

H-M1 established that at epoch 5, spurious features have higher probe accuracy than core features. H-M2 tests the FULL learning dynamics: when does each feature type PEAK? If spurious features are truly "easier," they should stabilize early while core features continue improving. This temporal ordering validates the simplicity bias mechanism.

---

## 3. Functional Requirements

### FR-1: Data Loading
- Load Waterbirds dataset (95% spurious correlation)
- Parse metadata for group labels (y, place, split)
- Provide both bird_label (core) and background_label (spurious) per sample
- Implement train/val/test splits (4795/1199/5794 samples)

### FR-2: Model Training with Epoch Checkpoints
- Train ResNet-18 with ERM for 100 epochs
- Save model state after EVERY epoch (100 checkpoints)
- Use SGD, lr=0.001, momentum=0.9, weight_decay=1e-4
- Batch size: 128

### FR-3: Feature Extraction Pipeline
- Create feature extractor using avgpool layer
- Extract 512-dim features for all training samples per epoch
- Cache features to disk to avoid recomputation
- Use torch.no_grad() for extraction

### FR-4: Epoch-wise Linear Probe Training
- Train spurious probe (background: water=0, land=1) per epoch
- Train core probe (bird: waterbird=0, landbird=1) per epoch
- Use sklearn LogisticRegression (L2, C=1.0, max_iter=1000)
- Record accuracy for both probes at each of 100 epochs

### FR-5: Peak Detection
- Implement smoothed peak finding (window=5 epochs)
- Identify spurious_peak_epoch and core_peak_epoch
- Compute statistical significance via Wilcoxon signed-rank test on learning curves

### FR-6: Mechanism Verification
- Primary test: spurious_peak_epoch < core_peak_epoch
- Secondary: AUC comparison for epochs 1-20
- Report peak difference in epochs

### FR-7: Visualization
- **Required:** Dual-line plot - spurious vs core probe accuracy over 100 epochs
- **Required:** Peak markers (vertical lines) at detected peak epochs
- **Optional:** Accuracy difference curve (spurious - core)
- **Optional:** First derivative of accuracy (learning speed)

---

## 4. Data Specification

### Primary Dataset
| Dataset | Source | Size | Purpose |
|---------|--------|------|---------|
| Waterbirds | WILDS or group_DRO | 11,788 | Full train/val/test |

**Group Structure:**
- Majority: landbird+land (3498), waterbird+water (1057)
- Minority: waterbird+land (56), landbird+water (184)
- Spurious correlation: 95%

**Labels Required:**
- `bird_label`: 0=landbird, 1=waterbird (core feature)
- `background_label`: 0=land, 1=water (spurious feature)

**Preprocessing:**
- Resize: 224x224
- Normalize: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
- Augmentation: RandomCrop, HorizontalFlip (training only)

---

## 5. Model Specification

### Baseline Model
| Component | Specification |
|-----------|---------------|
| Architecture | ResNet-18 (pretrained ImageNet) |
| Final Layer | nn.Linear(512, 2) |
| Framework | PyTorch + torchvision |

### Proposed Approach
ResNet-18 + EpochWiseProbeAnalysis:
- Train model for 100 epochs
- At each epoch: extract features, train spurious probe, train core probe
- Track accuracy curves for peak detection

### Linear Probe Architecture
```
Backbone (frozen per epoch): ResNet-18 → avgpool → 512-dim
Spurious Probe: LogisticRegression(512 → 2) → background
Core Probe: LogisticRegression(512 → 2) → bird type
```

---

## 6. Success Criteria

| Metric | Threshold | Priority |
|--------|-----------|----------|
| spurious_peak_epoch < core_peak_epoch | Difference ≥ 1 | PRIMARY |
| Peak difference ≥ 10 epochs | Expected | SECONDARY |
| Wilcoxon p < 0.05 on curves | Statistical | OPTIONAL |

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.9.0
torchvision>=0.10.0
numpy>=1.20.0
pandas>=1.3.0
scipy>=1.7.0
scikit-learn>=0.24.0
matplotlib>=3.4.0
Pillow>=8.0.0
tqdm>=4.60.0
pyyaml>=5.4.0
wilds>=2.0.0
```

### 7.2 External References
- H-M1 results: spurious_acc(epoch5)=91.2%, core_acc(epoch5)=80.5%
- SPARE (Yang et al., AISTATS 2024) - Simplicity bias theory
- Training dynamics literature

---

## 8. Non-Functional Requirements

### NFR-1: Single Seed
PoC uses fixed seed (42)

### NFR-2: Training Budget
- Base model: 100 epochs
- Linear probes: 100 × 2 probes (1000 iter each)
- Estimated: 3-4 hours on single GPU

### NFR-3: Hardware
Single GPU (RTX 3090 or equivalent)

### NFR-4: Storage
~10GB for 100 epoch checkpoints + cached features

---

## 9. Out of Scope

- Multiple seed runs
- Alternative architectures
- Per-layer probe analysis
- Real-time visualization

---

*Generated for Phase 3 Implementation Planning*
*Builds on H-M1 (PASSED): Simplicity bias confirmed at epoch 5*
