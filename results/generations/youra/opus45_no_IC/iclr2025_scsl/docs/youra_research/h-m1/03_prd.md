# Product Requirements Document: H-M1

**Hypothesis:** Under ERM training, if simplicity bias operates, then early representations (epoch 5) capture spurious features while later representations (epoch 50) capture core features
**Type:** MECHANISM
**Date:** 2026-08-12
**Author:** Anonymous

---

## 1. Executive Summary

Validate the simplicity bias mechanism by measuring what features ResNet-18 representations encode at different training stages. Using linear probes on frozen features from epoch 5, 20, and 50 checkpoints, we test whether spurious features (background) are learned before core features (bird type). This mechanism explains why minority samples have higher onset delays (H-E1).

**Gate Condition:** MUST_WORK - spurious_probe_acc(epoch5) > core_probe_acc(epoch5)

---

## 2. Problem Statement

H-E1 established that onset delay differs between minority/majority groups. H-M1 tests WHY: the simplicity bias hypothesis states that neural networks learn "easy" spurious features first. If true, early representations should encode background (spurious) better than bird type (core). This is testable via linear probes.

---

## 3. Functional Requirements

### FR-1: Data Loading
- Load Waterbirds dataset from Stanford NLP URL
- Parse metadata.csv for group labels (y, place, split)
- Provide both bird_label (core) and background_label (spurious) per sample
- Implement train/val/test splits (4795/1199/5794 samples)

### FR-2: Model Checkpointing
- Train ResNet-18 with ERM (same config as H-E1)
- Save model checkpoints at epochs 5, 20, 50
- Store checkpoint paths for feature extraction

### FR-3: Feature Extraction
- Load checkpoint, freeze backbone (no grad)
- Extract 512-dim features from avgpool layer
- Use AdaptiveAvgPool2d to collapse spatial dims
- Cache features to disk per checkpoint

### FR-4: Linear Probe Training
- Train spurious probe: predict background (water/land)
- Train core probe: predict bird type (waterbird/landbird)
- Use SGD, lr=0.01, 10 epochs per probe
- Train on train set, evaluate on test set

### FR-5: Mechanism Verification
- Compute spurious_acc and core_acc at each epoch checkpoint
- Primary test: spurious_acc(epoch5) > core_acc(epoch5)
- Secondary test: core_acc(epoch50) > core_acc(epoch5)

### FR-6: Visualization
- **Required:** Line plot - spurious vs core probe accuracy across epochs (5, 20, 50)
- Per-group accuracy breakdown (optional)

---

## 4. Data Specification

### Primary Dataset
| Dataset | Source | Size | Purpose |
|---------|--------|------|---------|
| Waterbirds | https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz | 11,788 | Train/Val/Test |

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

---

## 5. Model Specification

### Baseline Model
| Component | Specification |
|-----------|---------------|
| Architecture | ResNet-18 (pretrained ImageNet) |
| Final Layer | nn.Linear(512, 2) |
| Framework | PyTorch + torchvision |

### Proposed Approach
ResNet-18 + LinearProbeAnalysis (feature extraction + separate probes for spurious/core)

### Linear Probe Architecture
```
Backbone (frozen): ResNet-18 layers [:-1] → 512-dim features
Spurious Probe: Linear(512, 2) → background prediction
Core Probe: Linear(512, 2) → bird type prediction
```

---

## 6. Success Criteria

| Metric | Threshold | Priority |
|--------|-----------|----------|
| spurious_acc(epoch5) > core_acc(epoch5) | Difference > 0 | MUST |
| core_acc(epoch50) > core_acc(epoch5) | Improvement | SHOULD |
| Mann-Whitney U test (optional) | p < 0.05 | OPTIONAL |

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
```

### 7.2 External References
- SPARE (Yang et al., AISTATS 2024) - Simplicity bias theory
- DFR (Izmailov et al., NeurIPS 2022) - Linear probe methodology
- Complexity Matters (Qiu et al., 2024) - Feature learning dynamics

---

## 8. Non-Functional Requirements

### NFR-1: Single Seed
PoC uses fixed seed (42) - no multiple runs required

### NFR-2: Training Budget
- Base model: 50 epochs (checkpoints at 5, 20, 50)
- Linear probes: 10 epochs each

### NFR-3: Hardware
Single GPU (RTX 3090 or equivalent)

---

## 9. Out of Scope

- Multiple seed runs
- Hyperparameter tuning
- CKA similarity analysis (optional extension)
- Alternative probe architectures

---

*Generated for Phase 3 Implementation Planning*
