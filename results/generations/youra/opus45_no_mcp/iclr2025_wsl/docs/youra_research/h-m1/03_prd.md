# Product Requirements Document: H-M1

**Hypothesis:** Layer-wise Structure Advantage
**Date:** 2026-08-19
**Author:** Anonymous
**Type:** MECHANISM

---

## 1. Executive Summary

Implement and evaluate Layer-wise encoding vs Flatten+MLP baseline for accuracy prediction on CIFAR-10 Model Zoo. This MECHANISM hypothesis tests whether per-layer statistics capture layer-specific functional patterns that improve prediction accuracy.

**Gate Condition:** Δr > 0.1 with p < 0.05 (paired t-test across 5 seeds)

---

## 2. Problem Statement

Current weight embedding approaches flatten all parameters into a single vector, losing structural information about layer-specific statistics. Layer-wise encoding preserves per-layer statistics (mean, std, min, max) that may capture functional patterns.

---

## 3. Goals and Non-Goals

### Goals
- Implement Flatten+MLP baseline encoder
- Implement Layer-wise encoder with per-layer statistics
- Train accuracy prediction regressors for both methods
- Compare Pearson correlation on test set across 5 seeds
- Statistical validation with paired t-test

### Non-Goals
- Advanced architectures (attention, transformers)
- Hyperparameter optimization beyond reasonable defaults
- Cross-dataset generalization testing

---

## 4. Data Specification

### 4.1 Primary Dataset

| Property | Value |
|----------|-------|
| Name | CIFAR-10 Model Zoo (Small) |
| Source | Schurholt et al. 2022 (NeurIPS) |
| DOI | 10.5281/zenodo.6620869 |
| Format | PyTorch .pt file |
| Train | 42,650 models |
| Val | 9,340 models |
| Test | 9,345 models |
| Total | 61,335 models |

### 4.2 Data Loading

```python
from zenodo_get import zenodo_get
zenodo_get(["-d", "10.5281/zenodo.6620869", "-o", "data/"])
data = torch.load("data/dataset_cifar_small_hyp_fix.pt")
```

### 4.3 Data Schema

Each sample contains:
- `weights`: dict of layer_name → tensor (model parameters)
- `accuracy`: float (ground-truth test accuracy, 7.33% - 56.83%)

---

## 5. Functional Requirements

### FR-1: Data Pipeline
- FR-1.1: Download dataset from Zenodo (DOI: 10.5281/zenodo.6620869)
- FR-1.2: Load train/val/test splits
- FR-1.3: Create DataLoader with batch_size=256

### FR-2: Flatten+MLP Baseline
- FR-2.1: Flatten all weights into single vector
- FR-2.2: 2-layer MLP encoder (input → 256 → 128)
- FR-2.3: Regressor head (128 → 64 → 1)

### FR-3: Layer-wise Encoder
- FR-3.1: Compute per-layer statistics (mean, std, min, max)
- FR-3.2: Concatenate all layer statistics
- FR-3.3: MLP projection (stats → 256 → 128)
- FR-3.4: Regressor head (128 → 64 → 1)

### FR-4: Training Loop
- FR-4.1: AdamW optimizer, lr=1e-3, weight_decay=1e-4
- FR-4.2: MSE loss function
- FR-4.3: ReduceLROnPlateau scheduler (factor=0.5, patience=5)
- FR-4.4: Early stopping (patience=10 on val loss)
- FR-4.5: Train for max 50 epochs
- FR-4.6: Checkpoint best model by val MSE

### FR-5: Evaluation
- FR-5.1: Compute Pearson r on test set predictions
- FR-5.2: Run 5 seeds (0, 1, 2, 3, 4) for each method
- FR-5.3: Paired t-test between methods
- FR-5.4: Report Δr = mean(Layer-wise r) - mean(Flatten r)

### FR-6: Visualization
- FR-6.1: Gate metrics bar chart (Flatten r vs Layer-wise r with error bars)
- FR-6.2: Scatter plot (predicted vs actual accuracy)
- FR-6.3: Per-seed results line plot

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- Training time: < 30 minutes per seed per method (on GPU)
- Inference time: < 1 second per batch

### NFR-2: Reproducibility
- Fixed random seeds
- Deterministic operations where possible

### NFR-3: Logging
- TensorBoard or W&B logging for loss curves
- Checkpoint saving for best models

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0
numpy
scipy
matplotlib
zenodo_get
tqdm
```

### 7.2 External Repositories

- Reference: github.com/HSG-AIML/model-zoos (data format)
- Reference: github.com/HSG-AIML/hyper-representations (encoding patterns)

---

## 8. Success Criteria

| Metric | Threshold | Type |
|--------|-----------|------|
| Δr | > 0.1 | PRIMARY |
| p-value | < 0.05 | PRIMARY |
| All seeds improve | 5/5 | SECONDARY |

**Gate Decision:**
- PASS: Δr > 0.1 AND p < 0.05
- FAIL: Otherwise → PIVOT to alternative aggregation strategies

---

## 9. Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Small effect size | Medium | Baseline variance estimation first |
| Overfitting | Low | Early stopping, validation split |
| Data loading issues | Low | Zenodo fallback, local cache |

---

## 10. Timeline

| Phase | Duration |
|-------|----------|
| Implementation | 2-3 hours |
| Training (10 runs) | 5-10 hours |
| Analysis | 1 hour |
| Total | < 1 day |
