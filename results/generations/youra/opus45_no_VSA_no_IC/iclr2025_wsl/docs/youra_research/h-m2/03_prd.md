# Product Requirements Document: H-M2

**Hypothesis:** At N=500 training models, NFN R² exceeds MLP R² by at least 0.1 (p < 0.05)
**Type:** MECHANISM
**Date:** 2026-08-24
**Author:** PrayPrey

---

## Executive Summary

This experiment tests whether NFN's architectural permutation equivariance provides a data efficiency advantage over standard MLP when predicting model accuracy from weights. At N=500 training samples, NFN should outperform MLP by at least R² = 0.1 due to not needing to learn permutation invariance from data.

---

## Problem Statement

MLPs must learn permutation invariance from data augmentation or large sample sizes. NFN architecturally encodes this invariance. At low N, NFN should generalize better because it doesn't waste capacity learning symmetries.

**Success Criteria:** NFN R² - MLP R² ≥ 0.1 at N=500 with p < 0.05 (paired t-test, 10 seeds).

---

## Functional Requirements

### FR-1: Data Pipeline
- **FR-1.1:** Load model zoo from H-M1 (`h-m1/data/model_zoo_resnet20_cifar10.pt`)
- **FR-1.2:** Support variable training sizes: N ∈ {100, 250, 500, 1000, 2500, 5000}
- **FR-1.3:** Fixed test set: 500 models (consistent across all experiments)
- **FR-1.4:** Per-layer normalization (mean=0, std=1)

### FR-2: Baseline Model (MLP)
- **FR-2.1:** 2-layer MLP with 256 hidden units
- **FR-2.2:** ReLU activation
- **FR-2.3:** Input: flattened weights (~270K dims)
- **FR-2.4:** Output: single accuracy prediction

### FR-3: Proposed Model (NFN)
- **FR-3.1:** Use official `nfn` library (pip install nfn)
- **FR-3.2:** NPLinear layers with io_embed=True
- **FR-3.3:** HNPPool for invariant pooling
- **FR-3.4:** nfn_channels=32 (from H-M1)

### FR-4: Training Protocol
- **FR-4.1:** Adam optimizer, lr=1e-3
- **FR-4.2:** Batch size 32
- **FR-4.3:** 50 epochs (convergence by 25)
- **FR-4.4:** MSE loss
- **FR-4.5:** 10 random seeds per configuration

### FR-5: Evaluation
- **FR-5.1:** Compute R² on fixed 500-model test set
- **FR-5.2:** Paired t-test across 10 seeds
- **FR-5.3:** Generate learning curves (R² vs N)
- **FR-5.4:** Save all results to `h-m2/results/`

### FR-6: Visualization
- **FR-6.1:** Bar chart: NFN vs MLP R² with error bars (N=500)
- **FR-6.2:** Learning curve: R² vs N for both methods
- **FR-6.3:** Per-seed scatter plot
- **FR-6.4:** Box plot for N=500 distribution

---

## Non-Functional Requirements

### NFR-1: Performance
- Training time < 30 min per seed per N value
- GPU memory < 8GB

### NFR-2: Reproducibility
- Fixed random seeds
- Deterministic data splits
- Version-pinned dependencies

### NFR-3: Compatibility
- Python 3.8+
- PyTorch 1.12+
- nfn library v0.1.2

---

## Dependencies

### From H-M1 (Prerequisite)
- Model zoo dataset: `h-m1/data/model_zoo_resnet20_cifar10.pt`
- Validated hyperparameters: Adam, lr=1e-3, batch=32
- NFN architecture configuration

### External
- `nfn` library (pip installable)
- `sklearn.metrics` for R²
- `scipy.stats` for paired t-test

---

## Success Metrics

| Metric | Target | Method |
|--------|--------|--------|
| R² Delta (N=500) | ≥ 0.1 | Mean(NFN) - Mean(MLP) |
| Statistical Significance | p < 0.05 | Paired t-test, 10 seeds |
| Consistency | Low variance | Std across seeds |

---

## Out of Scope

- Hyperparameter tuning (use H-M1 validated values)
- Different architectures (only MLP vs NFN)
- Different datasets (only ResNet-20/CIFAR-10 model zoo)
