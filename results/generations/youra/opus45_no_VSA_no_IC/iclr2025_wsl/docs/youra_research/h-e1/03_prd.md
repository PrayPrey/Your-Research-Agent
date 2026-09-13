# Product Requirements Document: H-E1

**Hypothesis**: Model Zoo ResNet-20/CIFAR-10 weights have learnable accuracy-correlated features; Statistics baseline achieves R² > 0.85 on held-out 500 models.

**Type**: EXISTENCE (Foundation Hypothesis)  
**Generated**: 2026-08-24  

---

## 1. Executive Summary

Validate that neural network weights contain learnable accuracy-predictive features by implementing a statistics-based baseline predictor. This establishes the foundation for comparing equivariant architectures in subsequent hypotheses.

---

## 2. Problem Statement

Before investing in complex permutation-equivariant architectures (NFN), we must confirm that weight statistics alone can predict model accuracy. Prior work (Unterthiner et al. 2020) suggests R² > 0.85 is achievable.

---

## 3. Functional Requirements

### FR-1: Data Acquisition
- Download Model Zoo ResNet-18/CIFAR-10 from Zenodo (https://zenodo.org/records/6974029)
- Parse ~50,000 PyTorch state_dict checkpoints
- Extract accuracy labels (continuous, range 70-95%)

### FR-2: Feature Extraction Pipeline
Extract per-layer statistics for each weight tensor:
1. Mean, Std, Min, Max
2. L2 norm, Frobenius norm
3. Spectral norm (largest singular value)
4. Sparsity ratio

Expected: ~147 features (7 stats × 21 layers)

### FR-3: Statistics Baseline Model
- Model: Ridge Regression (sklearn)
- Hyperparameter selection: RidgeCV with α ∈ {0.01, 0.1, 1, 10, 100}
- Cross-validation: 5-fold on training split

### FR-4: Data Efficiency Evaluation
Train predictor at multiple sample sizes:
- N ∈ {100, 250, 500, 1000, 2500, 5000}
- Fixed test set: 500 models
- Seeds: 10 per N for statistical confidence

### FR-5: Results Logging
- Save features: `statistics_features.npy`
- Save results: `statistics_baseline_results.csv`
- Generate plots: R² vs N learning curves

---

## 4. Non-Functional Requirements

### NFR-1: Performance
- Total runtime: < 30 minutes
- Memory: < 16GB RAM

### NFR-2: Reproducibility
- Fixed random seeds
- Version-pinned dependencies
- Deterministic data splits

### NFR-3: Code Quality
- Type hints
- Docstrings for public functions
- Unit tests for feature extraction

---

## 5. Success Criteria

| Metric | Threshold | Expected |
|--------|-----------|----------|
| R² @ N=5000 | > 0.85 | ~0.95 |
| R² @ N=500 | Report | ~0.80 |
| Feature count | 100-200 | ~147 |
| Runtime | < 30 min | ~10 min |

**Gate**: MUST achieve R² > 0.85 at N=5000 to proceed to H-M1/H-M2.

---

## 6. Dependencies

```
torch>=1.10
numpy
scikit-learn
scipy
tqdm
matplotlib
```

---

## 7. Out of Scope

- NFN or equivariant architectures (H-M1, H-M2)
- Hyperparameter optimization beyond RidgeCV
- Multi-architecture experiments (ResNet-20 only)

---

## 8. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Zoo download fails | Low | High | torch.hub fallback |
| Low variance in zoo | Low | Medium | Verified: 70-95% range |
| Feature extraction bugs | Medium | High | Unit tests + spot checks |
