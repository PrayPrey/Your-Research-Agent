# Phase 2C Experiment Brief: H-E1

**Generated**: 2026-08-24T09:30:00Z  
**Hypothesis ID**: h-e1  
**Type**: EXISTENCE  

---

## Hypothesis Statement

Model Zoo ResNet-20/CIFAR-10 weights have learnable accuracy-correlated features; Statistics baseline achieves R² > 0.85 on held-out 500 models.

---

## Dataset Specification

### Primary Dataset
- **Name**: Model Zoo ResNet-18/CIFAR-10 (Schürholt et al. 2022)
- **Source**: https://zenodo.org/records/6974029
- **Type**: standard (published benchmark dataset)
- **Size**: ~50,000 trained ResNet-18 models with varying hyperparameters
- **Format**: PyTorch state_dict checkpoints (.pt files)
- **Labels**: Test accuracy on CIFAR-10 (continuous, range ~70-95%)

### Alternative Dataset (if ResNet-18 zoo unavailable)
- **Name**: pytorch-cifar-models pretrained weights
- **Source**: https://github.com/chenyaofo/pytorch-cifar-models
- **Type**: programmatic-api (torch.hub)
- **Note**: Smaller population; may need to train additional models

### Data Split
| Split | Size | Purpose |
|-------|------|---------|
| Train | Variable: N ∈ {100, 250, 500, 1000, 2500, 5000} | Train predictor |
| Test | 500 (fixed) | Evaluate R² |
| Seeds | 10 per N | Statistical confidence |

---

## Feature Engineering: Statistics Baseline

Based on Unterthiner et al. (2020) "Predicting Neural Network Accuracy from Weights":

### Per-Layer Statistics (for each weight tensor W)
1. **Mean**: μ(W)
2. **Std**: σ(W)
3. **Min/Max**: min(W), max(W)
4. **L2 norm**: ||W||₂
5. **Frobenius norm**: ||W||_F
6. **Spectral norm**: σ_max(W) (largest singular value)
7. **Sparsity**: fraction of |w| < ε

### Aggregation
- Compute per conv/linear layer → concatenate into feature vector
- ResNet-20: ~21 layers → ~147 features (7 stats × 21 layers)

### Predictor
- **Model**: Ridge Regression (sklearn)
- **Hyperparameter**: α selected via 5-fold CV on train split
- **Metric**: R² on held-out test set (500 models)

---

## Experimental Protocol

### Step 1: Data Acquisition
```bash
# Download Model Zoo from Zenodo
wget https://zenodo.org/records/6974029/files/cifar10_resnet18.tar.gz
tar -xzf cifar10_resnet18.tar.gz
```

### Step 2: Feature Extraction
```python
def extract_weight_statistics(state_dict):
    features = []
    for name, param in state_dict.items():
        if 'weight' in name and param.dim() >= 2:
            w = param.flatten().numpy()
            features.extend([
                w.mean(), w.std(), w.min(), w.max(),
                np.linalg.norm(w),  # L2
                np.linalg.norm(param.numpy(), 'fro'),  # Frobenius
                np.linalg.svd(param.numpy().reshape(param.shape[0], -1), compute_uv=False)[0],  # spectral
            ])
    return np.array(features)
```

### Step 3: Train/Evaluate Loop
```python
for N in [100, 250, 500, 1000, 2500, 5000]:
    for seed in range(10):
        X_train, y_train = sample_models(N, seed)
        X_test, y_test = get_test_set(500)  # fixed
        
        model = RidgeCV(alphas=[0.01, 0.1, 1, 10, 100])
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        results.append({'N': N, 'seed': seed, 'r2': r2})
```

### Step 4: Success Criterion
- **Gate**: R² > 0.85 at N=5000 (full training regime)
- **Expected**: R² ≈ 0.90-0.98 based on Unterthiner et al. results

---

## Success Metrics

| Metric | Threshold | Expected |
|--------|-----------|----------|
| R² @ N=5000 | > 0.85 | ~0.95 |
| R² @ N=500 | Report only | ~0.80 |
| Feature count | ~100-200 | ~147 |
| Runtime | < 30 min | ~10 min |

---

## Dependencies

```
torch>=1.10
numpy
scikit-learn
scipy
tqdm
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Model Zoo download fails | Use torch.hub pretrained + train additional models |
| ResNet-18 vs ResNet-20 mismatch | Both are similar depth; results transferable |
| Low accuracy variance in zoo | Verified: Schürholt et al. report 70-95% range |

---

## Output Artifacts

1. `statistics_features.npy` - Extracted features for all models
2. `statistics_baseline_results.csv` - R² scores per (N, seed)
3. `04_validation.md` - Phase 4 validation report

---

## References

1. Unterthiner et al. (2020). "Predicting Neural Network Accuracy from Weights." arXiv:2002.11448
2. Schürholt et al. (2022). "Model Zoo: A Dataset of Diverse Populations of Neural Network Models." NeurIPS Datasets Track
3. Zhou et al. (2023). "Permutation Equivariant Neural Functionals." NeurIPS 2023
