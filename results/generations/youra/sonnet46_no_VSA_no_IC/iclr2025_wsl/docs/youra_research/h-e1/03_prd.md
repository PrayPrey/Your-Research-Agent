# Product Requirements Document: H-E1
# Equivariant Weight-Space Encoders — Sample Efficiency PoC

---
stepsCompleted: [prd-step-01, prd-step-02, prd-step-03, prd-step-04, prd-step-05]
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
date: 2026-08-21
author: yoon303@etri.re.kr

---

## 1. Executive Summary

This PoC experiment validates whether equivariant weight-space encoders (DWSNets, GNN-NFN) achieve higher R² on accuracy prediction than a plain Flat-MLP at training sizes ≤500 on the ModelZooDataset MNIST and CIFAR-10 model zoos. The central claim is that permutation-equivariant inductive bias provides measurable sample efficiency at small dataset regimes. A single training seed (42) is used; bootstrap 95% CI is applied to test-set predictions for statistical validation.

---

## 2. Problem Statement

Neural network weight-space learning (predicting properties of trained models from their weights) requires encoding structured weight matrices. Flat-MLP approaches discard the permutation symmetry of neurons, potentially requiring more training data. Equivariant encoders exploit this symmetry as an inductive bias, hypothetically requiring fewer examples to achieve equivalent or better predictive accuracy. This experiment empirically tests whether that sample-efficiency advantage exists on a standardized shared benchmark (ModelZooDataset).

**Success gate**: Equivariant encoder R² > Flat-MLP R² with non-overlapping bootstrap 95% CIs at training size ≤500 on at least one zoo.

---

## 3. Scope

### In Scope
- 4 encoder conditions: Flat-MLP, Flat-MLP+PermAug, DWSNets (or NFN), GNN-NFN
- 2 model zoos: ModelZooDataset MNIST (hyp_rand) and CIFAR-10 (hyp_rand)
- 5 training size conditions: {100, 250, 500, 1000, full}
- 3 parameter budget tiers per encoder: small (~50K), medium (~200K), large (~500K params)
- Evaluation metric: R² on fixed held-out test set
- Bootstrap 95% CI (B=1000) for statistical comparison

### Out of Scope
- Multi-seed training runs (single seed PoC only)
- New equivariant architectures beyond the listed repos
- Datasets outside ModelZooDataset MNIST and CIFAR-10 zoos

---

## 4. Data Specification

### 4.1 Primary Datasets

**Dataset 1: ModelZooDataset MNIST (hyp_rand)**
- Source: Schürholt et al. NeurIPS 2022
- Repository: https://github.com/ModelZoos/ModelZooDataset
- Download: Zenodo https://zenodo.org/records/6632087
- File: `dataset_mnist_hyp_rand.pt`
- Size: ~4,860 models; small CNN (3 conv + 2 FC layers) trained on MNIST
- Splits: Pre-computed train/val/test from ModelZooDataset (use as-is)
- Ground truth: `zoo.metrics['test_accuracy']` per model
- **Download required**: YES (manual download from Zenodo)

**Dataset 2: ModelZooDataset CIFAR-10 (hyp_rand)**
- Source: Schürholt et al. NeurIPS 2022
- Download: Zenodo https://zenodo.org/records/6620869
- File: `dataset_cifar10_hyp_rand.pt`
- Size: ~9,000 models; same CNN structure trained on CIFAR-10
- **Download required**: YES (manual download from Zenodo)

### 4.2 Data Preprocessing

**For Flat-MLP conditions:**
- Flatten all zoo model weights+biases into 1D vector per model
- Standardize input (zero mean, unit variance, fit on training split)

**For DWSNets/NFN/GNN-NFN conditions:**
- Keep weights as structured matrices via `state_dict_to_tensors()`
- No flattening — preserve matrix/tensor structure per layer

### 4.3 Training Size Ablation

Subsample from training split only using fixed random seed 42:
- Sizes: {100, 250, 500, 1000, full}
- Test set: full held-out test (never subsampled)

### 4.4 Pre-experiment Diversity Check (Mandatory)

Compute test-accuracy variance in each zoo before training. If variance < 5%, flag as potentially degenerate and report. Continue with harder DV (generalization gap) if needed.

---

## 5. Functional Requirements

### FR-1: Dataset Download and Loading
- Download both Zenodo `.pt` files
- Load using `torch.load()` and ModelZooDataset dataset class
- Verify splits exist and diversity check passes
- Support subsampling to specified training sizes with seed=42

### FR-2: Flat-MLP Encoder (Condition 1)
- 3-hidden-layer MLP on flattened weight vector
- hidden_dim parameter-budget-matched to equivariant encoder
- Regression head (scalar output = predicted accuracy)
- Training: Adam lr=1e-3, MSE loss, 200 epochs, CosineAnnealingLR

### FR-3: Flat-MLP + PermAug Encoder (Condition 2)
- Same as FR-2 plus random neuron permutation augmentation during training
- Permutation probability p=0.5 per training sample
- Consistent permutation across weight matrix rows and subsequent bias

### FR-4: DWSNets / NFN Encoder (Condition 3)
- Use `AvivNavon/DWSNets` (MLPModelForRegression) if zoo models are MLP-compatible
- If CNN zoo: use `AllanYangZhou/nfn` (NPLinear + HNPPool layers)
- Architecture compatibility check on first run (detect conv layers in zoo)
- Structured weight input (list of matrices, not flattened)
- Same training protocol as FR-2

### FR-5: GNN-NFN Encoder (Condition 4)
- Use `mkofinas/neural-graphs` (GNNForRegression, PNA-based)
- Neural graph representation of zoo model weights (edge=weights, node=biases)
- PyG graph batching for efficient training
- Same training protocol as FR-2

### FR-6: Parameter Budget Matching
- Run each encoder at 3 budget tiers: small (~50K), medium (~200K), large (~500K params)
- Report results at matched budget tier for fair comparison
- Grid search hidden_dim to hit each target budget within ±20%

### FR-7: Evaluation and Metrics
- Compute R² (sklearn.metrics.r2_score) on full fixed test set
- Bootstrap 95% CI (B=1000 resamples) on test-set predictions
- Report: R² ± CI for each condition × training size × zoo

### FR-8: Mechanism Verification
- Log encoder type and weight_shapes at model init
- Permutation equivariance test: verify `|output(perm_weights) - output(orig_weights)| < 1e-4`
- Log mechanism activation status per encoder

### FR-9: Visualization
- Figure 1 (mandatory): R² bar chart with 95% CI at training size=500, all 4 conditions, per zoo
- Figure 2: Learning curves — R² vs training size for all 4 conditions, both zoos
- Figure 3: Bootstrap CI overlap plot at each training size (equivariant vs Flat-MLP)
- Figure 4: Zoo diversity histogram (test accuracy distribution)
- Save all figures to `docs/youra_research/h-e1/figures/`

### FR-10: CNN Architecture Fallback
- Detect conv layers in zoo model architecture at runtime
- If CNN: automatically switch from DWSNets to NFN library (AllanYangZhou/nfn)
- Log which path was taken; fail fast if neither path works

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- All random seeds fixed at 42 (data subsampling, model init, augmentation)
- Results must be fully reproducible from same seed + dataset files

### NFR-2: Runtime Budget
- EXISTENCE PoC — minimize redundant computation
- Single seed per condition (no multi-seed averaging)
- GPU recommended (CUDA); CPU fallback acceptable for debugging

### NFR-3: Code Organization
- Self-contained experiment script(s)
- Minimal dependencies beyond PyTorch, PyG (for GNN-NFN), sklearn, scipy

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.12.1
torchvision>=0.13.1
torch-geometric>=2.3.0  # for GNN-NFN only
einops
hydra-core              # for neural-graphs config
scikit-learn
scipy
numpy
matplotlib
```

### 7.2 External Repositories (clone)
- `AvivNavon/DWSNets` — equivariant encoder (Condition 3, MLP zoo)
- `mkofinas/neural-graphs` — GNN-NFN encoder (Condition 4)
- `AllanYangZhou/nfn` — NFN library (fallback for CNN zoo with DWSNets)
- `ModelZoos/ModelZooDataset` — dataset loading utilities

### 7.3 Data Files (Manual Download)
- `dataset_mnist_hyp_rand.pt` from Zenodo DOI 10.5281/zenodo.6632087
- `dataset_cifar10_hyp_rand.pt` from Zenodo DOI 10.5281/zenodo.6620869

---

## 8. Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| Code runs without error on both zoos | Required |
| Diversity check passes (variance ≥ 5%) | Required |
| Permutation equivariance test passes | Required for equivariant encoders |
| R²_equivariant > R²_flat_mlp | With non-overlapping bootstrap 95% CI at ≥1 training size ≤500, on ≥1 zoo |
| All 4 figures generated | Required |

**Gate condition**: MUST_WORK — if gate fails, entire hypothesis chain is blocked.

---

## 9. Ablation Variants

### A1: Zoo Diversity Ablation
- If diversity check fails (variance < 5%): switch DV to generalization gap (val_acc - train_acc)
- Re-run all 4 encoder conditions with new DV

### A2: Parameter Budget Ablation (Built into FR-6)
- 3 budget tiers × 4 encoders × 5 training sizes × 2 zoos = 120 conditions total (reduced to matched-budget comparison in reporting)

### A3: Architecture Compatibility Fallback
- If DWSNets incompatible (CNN zoo): use AllanYangZhou/nfn (NPLinear + HNPPool)
- Document which code path was taken

---

## 10. Phase 4 Guidance

Phase 4 Coder reads `03_tasks.yaml` for task-by-task implementation. Key implementation decisions:
1. Check zoo architecture first (FR-10) before building any encoder
2. DWSNets path: use `MLPModelForRegression` from `nn/dws/models.py`
3. GNN-NFN path: use `GNNForRegression` from `nn/gnn.py` in neural-graphs
4. NFN fallback: use `nfn.layers.NPLinear + HNPPool` for CNN zoo compatibility
5. Parameter budget matching via grid search on `hidden_dim`
