# Validation Report: H-M1 (NFN Equivariant Feature Extraction)

**Date:** 2026-08-24
**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Gate Type:** MUST_WORK

## Executive Summary

**Gate Result: PASSED**

NFN-style equivariant feature extraction successfully demonstrates permutation-invariant features for neural network weight accuracy prediction. The model achieves R² = 0.9952 on 500 test models while maintaining 100% equivariance pass rate under neuron permutations.

## Hypothesis Statement

> NFN equivariant layers extract permutation-invariant features architecturally without data augmentation

## Results Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| NFN R² | 0.9952 | ≥ 0.85 | ✅ PASS |
| Baseline R² | 0.9996 | - | Reference |
| Equivariance Pass Rate | 100.0% | ≥ 95% | ✅ PASS |
| Max Equivariance Error | 8.94e-08 | < 1e-05 | ✅ PASS |

## Experimental Setup

### Dataset
- **Source:** Synthetic Model Zoo (same as H-E1)
- **Train Set:** 2000 ResNet-20 checkpoints
- **Test Set:** 500 held-out models (fixed split, seed=42)
- **Features:** Raw weight tensors from 21 layers

### Model Architecture
- **Type:** DeepSets-style equivariant predictor
- **Hidden Dimension:** 64
- **Layers:** 2 equivariant processing layers
- **Pooling:** Mean pooling (permutation-invariant)

### Training Configuration
- **Optimizer:** Adam (lr=1e-3, weight_decay=1e-4)
- **Batch Size:** 64
- **Epochs:** 30 (with early stopping, patience=10)
- **Seeds:** [42]

## Key Findings

### 1. Equivariance Verification (Primary Mechanism)
- **Pass Rate:** 100% (500/500 test samples × 5 permutation trials each)
- **Max Error:** 8.94e-08 (well below 1e-5 tolerance)
- **Conclusion:** Model output is invariant to neuron permutations, confirming architectural equivariance

### 2. Prediction Performance
- NFN achieves R² = 0.9952, slightly below statistics baseline (0.9996)
- MAE = 0.004 (accuracy prediction within 0.4 percentage points)
- Comparable performance with fundamentally different approach (learned vs. hand-crafted features)

### 3. Training Dynamics
- Rapid convergence: R² > 0.98 by epoch 5
- Stable training without NaN/explosion
- Early stopping triggered at optimal checkpoint

## Gate Evaluation

### MUST_WORK Criteria
1. **Equivariance test passes on ALL test models:** ✅ PASSED (100%)
2. **NFN R² ≥ 0.85 on held-out 500 test models:** ✅ PASSED (0.9952)
3. **Training converges without NaN/explosion:** ✅ PASSED

### Gate Verdict: **PASSED**

The NFN mechanism successfully extracts permutation-invariant features architecturally, as demonstrated by:
- Perfect equivariance pass rate (100%)
- Near-baseline prediction accuracy (R² = 0.9952 vs 0.9996)
- Stable training dynamics

## Figures

| Figure | Description |
|--------|-------------|
| `figures/gate_comparison.png` | NFN vs Baseline R² bar chart |
| `figures/prediction_scatter.png` | True vs predicted accuracy scatter |
| `figures/equivariance_test.png` | Equivariance pass rate and error |
| `figures/training_curve.png` | Loss and R² over epochs |
| `figures/residuals.png` | Prediction residual distribution |

## Implications for Main Hypothesis

H-M1 validation confirms:
- Permutation equivariance can be achieved architecturally (not via data augmentation)
- Equivariant features maintain high predictive accuracy
- Foundation established for data efficiency comparisons in H-M2

## Code Artifacts

- `code/nfn_model.py` - NFNAccuracyPredictor implementation
- `code/equivariance.py` - Permutation and verification utilities
- `code/train.py` - Training loop with early stopping
- `code/run_experiment.py` - Full experiment orchestration
- `code/results.json` - Structured results

## Next Steps

→ Proceed to H-M2: Compare data efficiency of NFN vs MLP baselines across training sizes
