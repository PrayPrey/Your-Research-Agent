# Product Requirements Document: H-E1

**Hypothesis:** Behavioral Information Exists Beyond Accuracy
**Date:** 2026-08-19
**Author:** Anonymous
**Type:** EXISTENCE (PoC)
**Phase:** Phase 3 Implementation Planning

---

## 1. Executive Summary

This PRD specifies implementation requirements for validating hypothesis H-E1: that class-wise accuracy profiles across CNN models exhibit variance beyond what overall accuracy alone explains. This is a statistical analysis task on pre-trained model predictions, not a model training task.

**Core Question:** Does meaningful behavioral variance exist in class-wise accuracy profiles beyond overall accuracy + per-class difficulty?

**Success Criterion:** Residual variance ratio > 0.05 (5% of variance unexplained by stratified baseline).

---

## 2. Problem Statement

Current model evaluation relies primarily on aggregate accuracy metrics, potentially missing behavioral differences in how models handle individual classes. This hypothesis tests whether meaningful class-wise behavioral patterns exist that warrant further investigation into weight-space representations.

**Gate Type:** MUST_WORK - If this fails, the entire research direction (behavioral fingerprinting via neural functionals) is invalidated.

---

## 3. Functional Requirements

### FR-1: Dataset Loading
- **ID:** FR-1
- **Description:** Load Small CNN Zoo dataset from Zenodo
- **Source:** Zenodo DOI: 10.5281/zenodo.6620868
- **File:** `dataset_cifar_small_hyp_rand.pt`
- **Expected:** ~3000 CNN models with stored predictions

### FR-2: Ground Truth Loading
- **ID:** FR-2
- **Description:** Load CIFAR-10 test set ground truth labels
- **Source:** torchvision.datasets.CIFAR10
- **Size:** 10,000 test samples, 10 classes

### FR-3: Class-wise Accuracy Computation
- **ID:** FR-3
- **Description:** Compute per-class accuracy for each model
- **Input:** Model predictions (10,000 per model), ground truth labels
- **Output:** Matrix of shape (N_models, 10) with per-class accuracies

### FR-4: Stratified Baseline Implementation
- **ID:** FR-4
- **Description:** Implement baseline predictor
- **Formula:** `class_acc_pred[i] = overall_acc * class_difficulty[i] / mean(class_difficulty)`
- **Where:** `class_difficulty[c] = mean accuracy on class c across all models`

### FR-5: Variance Analysis
- **ID:** FR-5
- **Description:** Compute residual variance after removing baseline
- **Metrics:**
  - Total variance of class-wise accuracy matrix
  - Residual variance after subtracting baseline prediction
  - Residual ratio = residual_variance / total_variance
  - R² of baseline fit

### FR-6: Visualization Generation
- **ID:** FR-6
- **Description:** Generate required figures
- **Required:** Gate metrics bar chart (residual_ratio vs 0.05 threshold)
- **Optional:** 
  - Class-wise accuracy heatmap
  - Variance decomposition pie chart
  - Per-class variance bar plot
  - Model clustering scatter (PCA)

### FR-7: Result Reporting
- **ID:** FR-7
- **Description:** Generate structured result output
- **Output:** JSON/YAML with all metrics, pass/fail determination, figure paths

---

## 4. Data Specification

### Primary Dataset

| Attribute | Value |
|-----------|-------|
| Name | Small CNN Zoo - CIFAR-10 (Hyperparameter Random) |
| Source | Zenodo DOI: 10.5281/zenodo.6620868 |
| File | dataset_cifar_small_hyp_rand.pt |
| Size | ~2.0 GB compressed |
| Models | ~3000 small CNNs (4970 params each) |
| Training | CIFAR-10, 86 epochs |
| Contents | Weights, metrics, predictions |

### Download Method
```python
# Manual download from Zenodo
# wget https://zenodo.org/records/6620869/files/dataset_cifar_small_hyp_rand.pt
import torch
dataset = torch.load("dataset_cifar_small_hyp_rand.pt")
```

### Ground Truth
```python
from torchvision.datasets import CIFAR10
test_dataset = CIFAR10(root='./data', train=False, download=True)
ground_truth = np.array(test_dataset.targets)  # shape: (10000,)
```

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Analysis should complete within 10 minutes on standard hardware
- Memory usage should not exceed 8GB RAM

### NFR-2: Reproducibility
- All random seeds fixed
- Results deterministic given same input

### NFR-3: Output Format
- Figures saved as PNG (300 DPI)
- Metrics saved as YAML/JSON
- Code documented with docstrings

---

## 6. Success Criteria

### Primary Gate Criterion
| Metric | Threshold | Interpretation |
|--------|-----------|----------------|
| Residual Variance Ratio | > 0.05 | PASS: Proceed to H-M1 |
| Residual Variance Ratio | ≤ 0.05 | FAIL: Stop research direction |

### Secondary Metrics (Informational)
- R² of stratified baseline (lower = more unexplained variance = good)
- Per-class variance distribution
- Model clustering quality (optional)

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.9.0
torchvision>=0.10.0
numpy>=1.20.0
scikit-learn>=0.24.0
matplotlib>=3.4.0
seaborn>=0.11.0
pyyaml>=5.4.0
```

### 7.2 External Data
- Zenodo: dataset_cifar_small_hyp_rand.pt (DOI: 10.5281/zenodo.6620868)
- CIFAR-10 test set (auto-download via torchvision)

### 7.3 Reference Implementations
- ModelZoos/ModelZooDataset (MIT License)
- HSG-AIML/SANE (reference for weight processing)

---

## 8. Constraints

### 8.1 Scope Constraints
- This is a STATISTICAL ANALYSIS task, not model training
- No neural network training required
- All models are pre-trained and frozen

### 8.2 Tier Constraints
- Task Budget: LIGHT (15 tasks max)
- Epic Range: 4-8 implementation tasks
- Infrastructure: Minimal (no distributed computing needed)

---

## 9. Assumptions

- A1: Small CNN Zoo contains meaningful variation in class-wise performance
- A2: Predictions are stored in dataset or can be computed from weights
- A3: Class difficulty is relatively stable across model architectures

---

## 10. Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| No class-wise variance exists | Critical | This is what we're testing |
| Dataset format incompatible | Medium | Verify format before full analysis |
| Missing predictions in dataset | Medium | Compute from weights if needed |

---

*Generated: Phase 3 Implementation Planning*
*Source: Phase 2C Experiment Brief*
