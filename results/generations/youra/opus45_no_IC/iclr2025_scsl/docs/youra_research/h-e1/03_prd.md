# Product Requirements Document: H-E1

**Hypothesis:** Onset delay d_i differs systematically between minority and majority group samples
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-12
**Author:** Anonymous

---

## 1. Executive Summary

Validate that per-sample onset delay d_i (first epoch where loss drops below 90% of initial) differs systematically between minority and majority groups in Waterbirds dataset. Success enables downstream spurious correlation detection via training dynamics.

**Gate Condition:** MUST_WORK - Precision > 0.5 AND Recall > 0.3 for minority detection

---

## 2. Problem Statement

Deep learning models trained with ERM learn spurious correlations (e.g., background features) before core features. We hypothesize that minority samples (misaligned spurious correlation) have higher onset delays than majority samples. This PoC validates the existence of this signal.

---

## 3. Functional Requirements

### FR-1: Data Loading
- Load Waterbirds dataset from Stanford NLP URL
- Parse metadata.csv for group labels (y, place, split)
- Implement train/val/test splits (4795/1199/5794 samples)

### FR-2: Per-Sample Loss Tracking
- Track individual sample losses every epoch
- Store initial loss L_i(0) for each sample
- Compute onset delay d_i = min{t : L_i(t) < 0.9 * L_i(0)}

### FR-3: Minority Detection
- Predict minority: samples with d_i > T_early (T_early=20)
- Compute precision/recall against ground truth group labels

### FR-4: Statistical Validation
- Mann-Whitney U test: minority d_i > majority d_i (p < 0.05)
- Generate distribution histograms

### FR-5: Visualization
- **Required:** Gate metrics bar chart (precision/recall vs thresholds)
- Onset delay distribution histogram by group
- Loss trajectories (sample of 20)
- Precision-Recall curve as T_early varies

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
ResNet-18 + OnsetDelayTracker (per-sample loss logging + d_i computation)

---

## 6. Success Criteria

| Metric | Threshold | Priority |
|--------|-----------|----------|
| Precision@T_early | > 0.5 | MUST |
| Recall@T_early | > 0.3 | MUST |
| Mann-Whitney U p-value | < 0.05 | MUST |

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
- kohpangwei/group_DRO - Waterbirds dataset handling
- anniesch/jtt - Per-sample identification methodology
- BigML-CS-UCLA/SPARE - Simplicity bias detection theory

---

## 8. Non-Functional Requirements

### NFR-1: Single Seed
PoC uses fixed seed (42) - no multiple runs required

### NFR-2: Training Budget
100 epochs maximum, T_early=20 for detection

### NFR-3: Hardware
Single GPU (RTX 3090 or equivalent)

---

## 9. Out of Scope

- Multiple seed runs (not PoC)
- Hyperparameter tuning
- Comparison with other methods
- Production deployment

---

*Generated for Phase 3 Implementation Planning*
