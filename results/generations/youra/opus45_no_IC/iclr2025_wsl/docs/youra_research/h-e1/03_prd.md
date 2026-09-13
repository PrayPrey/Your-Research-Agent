# Product Requirements Document: H-E1

**Hypothesis:** At N=1K, NFN R² > MLP-Matched R² + 0.05 (p<0.05)
**Type:** EXISTENCE (Proof of Concept)
**Date:** 2026-08-12
**Source:** Phase 2C Experiment Brief

---

## Executive Summary

Validate that Neural Functional Networks (NFN) with permutation equivariance outperform parameter-matched MLPs on weight-space accuracy prediction at low sample sizes (N=1K). Success demonstrates equivariance provides sample efficiency benefit.

---

## Problem Statement

Standard MLPs treat neural network weights as flat vectors, ignoring neuron permutation symmetry. NFNs exploit this symmetry via equivariant layers. At limited training data (N=1K models), does built-in equivariance provide measurable advantage over learned representations?

---

## Functional Requirements

### FR-1: Data Pipeline
- **FR-1.1:** Download Model Zoo CIFAR-10 CNN subset (Zenodo/GitHub)
- **FR-1.2:** Filter for single-architecture family with homogeneous layer shapes
- **FR-1.3:** Extract N=1K models with accuracy labels spanning 10-90% range
- **FR-1.4:** Split 80% train / 20% test (fixed seed)
- **FR-1.5:** Normalize weights per-layer (zero mean, unit variance)

### FR-2: NFN Model (Proposed)
- **FR-2.1:** Implement NFNRegressor using `nfn` package (pip install nfn)
- **FR-2.2:** Architecture: NPLinear → ReLU → NPLinear → ReLU → HNPPool → Linear(1)
- **FR-2.3:** Channels: 32 (nfn_channels parameter)
- **FR-2.4:** Input: WeightSpaceFeatures from state_dict_to_tensors

### FR-3: MLP-Matched Baseline
- **FR-3.1:** Implement MLPMatched with parameter count ≈ NFN
- **FR-3.2:** Architecture: 3-layer MLP with ReLU, hidden_dim=256
- **FR-3.3:** Input: Flattened concatenated weights

### FR-4: Training Protocol
- **FR-4.1:** Optimizer: AdamW (lr=1e-3, weight_decay=1e-4)
- **FR-4.2:** Scheduler: Cosine annealing (T_max=50, eta_min=1e-6)
- **FR-4.3:** Loss: MSE
- **FR-4.4:** Epochs: 50
- **FR-4.5:** Batch size: 32
- **FR-4.6:** Single seed for PoC

### FR-5: Evaluation
- **FR-5.1:** Compute R² on test set for both models
- **FR-5.2:** Calculate difference: nfn_r2 - mlp_r2
- **FR-5.3:** Generate comparison bar chart with 0.05 threshold line
- **FR-5.4:** Generate scatter plots (predicted vs actual) for both models

### FR-6: Outputs
- **FR-6.1:** Save trained models to `h-e1/checkpoints/`
- **FR-6.2:** Save figures to `h-e1/figures/`
- **FR-6.3:** Generate results JSON with R² values and hypothesis verdict

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds for all stochastic operations
- Version-pinned dependencies (nfn, torch, numpy)

### NFR-2: Performance
- Training completes within 30 minutes on single GPU
- Memory usage < 16GB VRAM

### NFR-3: Code Quality
- Type hints for all functions
- Docstrings for public APIs
- Pytest-compatible test structure

---

## Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| **Primary** | nfn_r2 - mlp_r2 > 0.05 | R² difference |
| **Secondary** | Code runs without error | Execution success |
| **Tertiary** | Figures generated | File existence |

---

## Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| nfn | pip install nfn | NFN layers and utilities |
| torch | pip install torch | Deep learning framework |
| Model Zoo | github.com/ModelZoos/ModelZooDataset | Training data |
| sklearn | pip install scikit-learn | R² metric |

---

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Insufficient models in zoo | HIGH | Verify subset sizes before training |
| NFN package bugs | MEDIUM | Use official implementation, pin version |
| Layer shape heterogeneity | MEDIUM | Strict filtering for homogeneous architectures |

---

## Out of Scope

- Multi-seed statistical significance (deferred to full study)
- Additional baselines beyond MLP-Matched
- Scale experiments beyond N=1K
- Hyperparameter tuning

---

*Generated from Phase 2C Experiment Brief*
*Next: Architecture Design (Step 3)*
