# Product Requirements Document: H-M1

**Hypothesis:** NFN equivariant layers extract permutation-invariant features architecturally without data augmentation
**Date:** 2026-08-24
**Author:** Anonymous
**Type:** MECHANISM
**Phase 2C Source:** 02c_experiment_brief.md

---

## Executive Summary

Validate that Neural Functional Networks (NFN) extract permutation-invariant features from neural network weights through architectural equivariance, not learned approximation. Building on H-E1's statistics baseline (R²=0.9995), demonstrate NFN achieves comparable accuracy prediction while guaranteeing equivariance.

---

## Problem Statement

Statistics-based features require hand-crafted aggregations (mean, std, etc.) that discard structural weight information. NFN promises architectural invariance to neuron permutations, potentially capturing richer weight-space structure. This experiment validates NFN's core mechanism works as theorized.

---

## Functional Requirements

### FR1: Data Pipeline
- **FR1.1:** Load Model Zoo ResNet-20/CIFAR-10 checkpoints (Zenodo 6620869)
- **FR1.2:** Split: 5000 train / 500 test (fixed hold-out)
- **FR1.3:** Convert state_dicts to NFN WeightSpaceFeatures format
- **FR1.4:** Batch collation for variable-size weight tensors

### FR2: Baseline Model (Statistics)
- **FR2.1:** Reuse H-E1 statistics extraction (63 dims: 7 stats × 9 layers)
- **FR2.2:** RidgeCV regression (α∈{0.01, 0.1, 1.0, 10.0})
- **FR2.3:** Evaluate on same test set for fair comparison

### FR3: Proposed Model (NFN)
- **FR3.1:** Install official NFN library (`pip install nfn`)
- **FR3.2:** Build NFNAccuracyPredictor with:
  - network_spec: ResNet-20 architecture
  - hidden_dim: 128
  - num_layers: 3
  - invariant_output: True
- **FR3.3:** Linear head: hidden_dim → 1 (accuracy prediction)

### FR4: Training Protocol
- **FR4.1:** Optimizer: Adam (lr=1e-3, weight_decay=1e-4)
- **FR4.2:** Schedule: ReduceLROnPlateau (factor=0.5, patience=10)
- **FR4.3:** Batch size: 32 models
- **FR4.4:** Epochs: 100 (early stopping patience: 20)
- **FR4.5:** Loss: MSE

### FR5: Evaluation
- **FR5.1:** Primary: R² score on 500 test models
- **FR5.2:** Secondary: MAE (accuracy points)
- **FR5.3:** Mechanism: Equivariance error (max diff under permutation)
- **FR5.4:** Mechanism: Equivariance pass rate (target: 100%)

### FR6: Equivariance Verification
- **FR6.1:** Implement `verify_equivariance(nfn, weights, permutation)`
- **FR6.2:** Test on all 500 test models with random permutations
- **FR6.3:** Tolerance: 1e-5 (numerical invariance)

### FR7: Visualization
- **FR7.1:** Gate metrics bar chart (NFN R² vs Baseline R²)
- **FR7.2:** Prediction scatter (true vs predicted accuracy)
- **FR7.3:** Equivariance verification plot
- **FR7.4:** Training curves (loss, R²)
- **FR7.5:** Residual distribution histogram

---

## Non-Functional Requirements

### NFR1: Reproducibility
- 3 random seeds for mechanism validation
- All hyperparameters logged

### NFR2: Performance
- Training: <2 hours on single GPU
- Inference: <1 second per model batch

### NFR3: Dependencies
- PyTorch ≥1.10
- nfn (official library)
- scikit-learn (baseline, metrics)

---

## Success Criteria

| Criterion | Target | Priority |
|-----------|--------|----------|
| Equivariance pass rate | 100% | P0 (MUST) |
| NFN R² | ≥0.85 | P0 (MUST) |
| Training convergence | No NaN/explosion | P0 (MUST) |
| Baseline reproduction | R²≈0.9995 | P1 (SHOULD) |

---

## Dependencies

- **H-E1:** Statistics baseline implementation (VALIDATED)
- **Dataset:** Model Zoo Zenodo 6620869 (pre-downloaded)
- **Library:** nfn PyPI package

---

## Out of Scope

- Transformer-NFN (future work)
- Model Zoo datasets beyond ResNet-20/CIFAR-10
- Data augmentation comparison (this validates NO augmentation needed)
