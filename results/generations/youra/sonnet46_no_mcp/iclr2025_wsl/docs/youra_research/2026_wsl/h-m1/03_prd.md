# Product Requirements Document: H-M1
# Flat MLP Encoder Permutation Sensitivity Probing

**stepsCompleted:** [executive-summary, problem-statement, functional-requirements, nfrs, success-criteria, data-specification, dependencies]

**Hypothesis ID:** h-m1
**Hypothesis Type:** MECHANISM (INCREMENTAL — builds on h-e1)
**Gate Type:** MUST_WORK
**Date:** 2026-05-05
**Author:** Anonymous
**Source:** h-m1/02c_experiment_brief.md

---

## 1. Executive Summary

This experiment trains a flat MLP encoder (~500K parameters) on weight-space accuracy prediction using the Schurholt MNIST-CNN model zoo, then probes whether its learned embeddings are permutation-sensitive. The key mechanism under test: flat MLPs receive all permutations of a network's weights as distinct input vectors, and therefore must waste capacity learning redundant mappings across the factorial-sized permutation orbit. We measure this via a permutation sensitivity score: the ratio of mean L2 distance between embeddings of permutation-equivalent weight configurations to mean L2 distance between random non-equivalent pairs. A score >0.3 confirms the mechanism and gates downstream H-M2/H-M3 experiments.

**Hypothesis Statement:** Under conditions of matched encoder capacity (~500K parameters ±5%) on the Schurholt MNIST-CNN zoo, if we train a flat MLP encoder (concatenated weight vector input) on accuracy prediction, then its learned embeddings will exhibit permutation sensitivity (different embeddings for permutation-equivalent weight configurations of similar-accuracy models), because flat MLPs receive all permutations of a network's weights as distinct input vectors and must learn to map all equivalent permutations to the same output — consuming capacity for redundant mappings.

---

## 2. Problem Statement

### 2.1 Background

NFN (Neural Functional Network) encoders claim to outperform flat MLP encoders on weight-space learning tasks because they operate in the permutation-quotient weight space. The mechanistic argument is: flat MLPs waste encoder capacity navigating the factorial-sized permutation orbits (|S_{n_1}| × ... × |S_{n_L}| symmetry-equivalent configurations per function), while NFN encoders are equivariant by construction and map all permutations to identical embeddings.

H-E1 confirmed (orbit_proportion=1.000) that the MNIST-CNN zoo has non-trivial permutation orbit structure. H-M1 now tests the causal mechanistic claim: does the flat MLP actually learn permutation-sensitive embeddings?

### 2.2 Motivation

This experiment is required before H-M2 (NFN near-zero sensitivity) and H-M3 (Δρ comparison), as it establishes the baseline permutation behavior of the flat MLP encoder. Without confirming flat MLP permutation sensitivity, the claimed capacity reallocation advantage of NFN cannot be attributed to the permutation-equivariance mechanism.

### 2.3 Scope

- **In scope:** Train one flat MLP encoder; probe permutation sensitivity; report Spearman ρ as quality check
- **Out of scope:** NFN training (H-M2); comparative Δρ analysis (H-M3); CIFAR-10 experiments

---

## 3. Functional Requirements

### FR-1: Dataset Loading and Preprocessing
- **FR-1.1:** Load `dataset_mnist_hyp_rand.pt` from Zenodo record 6632087 (full hyperparameter-random MNIST-CNN zoo, ~4,100 checkpoints)
- **FR-1.2:** Extract final-epoch checkpoints (`training_iteration=50`) with `test_accuracy` labels
- **FR-1.3:** Flatten all weight/bias tensors into single vector using `flatten_weights()` (reuse from h-e1/code/weight_analysis.py)
- **FR-1.4:** Compute `input_dim` dynamically from first loaded checkpoint (~53,002)
- **FR-1.5:** Apply z-score normalization per feature across training set
- **FR-1.6:** Use Schurholt standard train/val/test splits from dataset metadata
- **FR-1.7:** Dataset must yield ≥100 test samples for Spearman ρ computation

### FR-2: Flat MLP Encoder Architecture
- **FR-2.1:** Implement `FlatMLPEncoder(input_dim, hidden_dims, embed_dim=128)` with ReLU activations and 0.1 dropout
- **FR-2.2:** Run width grid search to achieve total parameter count in [475K, 525K]
- **FR-2.3:** Attach prediction head `Linear(128, 1)` for accuracy regression during training
- **FR-2.4:** Verify parameter count via `sum(p.numel() for p in model.parameters())`
- **FR-2.5:** Input shape: `(B, input_dim)` → Output embedding: `(B, 128)`

### FR-3: Training Protocol
- **FR-3.1:** Optimizer: Adam, lr=1e-3, weight_decay=1e-4, betas=(0.9, 0.999)
- **FR-3.2:** LR Schedule: CosineAnnealingLR, T_max=150, eta_min=1e-6
- **FR-3.3:** Batch size: 32
- **FR-3.4:** Epochs: 150
- **FR-3.5:** Loss: MSE on accuracy regression (`F.mse_loss(pred, true_accuracy)`)
- **FR-3.6:** Fixed random seed: 42
- **FR-3.7:** Log train/val loss and Spearman ρ every epoch

### FR-4: Permutation Sensitivity Probing
- **FR-4.1:** Load ≥50 permutation-equivalent weight pairs (reuse `stratified_pair_sample` output from h-e1)
- **FR-4.2:** Generate permuted weight variants via `generate_permuted_weights(state_dict, layer_order)` — preserve functional equivalence by permuting outgoing weights of layer l AND incoming weights of layer l+1 simultaneously
- **FR-4.3:** Compute `sensitivity_score = mean(L2(enc(w), enc(perm(w)))) / mean(L2(enc(w_i), enc(w_j)))` where w_i, w_j are random non-equivalent pairs
- **FR-4.4:** Use trained encoder in eval mode with `torch.no_grad()`
- **FR-4.5:** Report: sensitivity_score, mean_equiv_L2, mean_random_L2, n_pairs used

### FR-5: Evaluation and Metrics
- **FR-5.1 [GATE METRIC]:** Permutation sensitivity score > 0.3 → H-M1 PASS
- **FR-5.2 [QUALITY CHECK]:** Spearman ρ ≥ 0.5 on full test set (confirms encoder trained successfully)
- **FR-5.3:** If sensitivity_score ≤ 0.3 → EXPLORE mode: document as key finding, re-examine key tension
- **FR-5.4:** Compute Spearman ρ using `scipy.stats.spearmanr`

### FR-6: Reuse from H-E1
- **FR-6.1:** Reuse `flatten_weights` from `h-e1/code/weight_analysis.py` (handles `module_list.*` keys, returns float32 CPU tensor)
- **FR-6.2:** Reuse `stratified_pair_sample` from `h-e1/code/weight_analysis.py` (deterministic seed=42, 500 pairs)
- **FR-6.3:** Reuse `load_zoo_checkpoints` from `h-e1/code/data_loader.py` (dual-path fallback, `weights_only=False`)
- **FR-6.4:** Skip BN-free verification (already confirmed by h-e1)
- **FR-6.5:** Use `dataset_mnist_hyp_rand.pt` (NOT `dataset_mnist_seed.pt` used in h-e1)

### FR-7: Visualization
- **FR-7.1 [MANDATORY]:** Gate Metrics Comparison bar chart (sensitivity_score vs threshold 0.3; Spearman ρ vs target 0.5)
- **FR-7.2:** Embedding L2 Distance Distribution histogram (equiv pairs vs random pairs)
- **FR-7.3:** Training curve (loss + Spearman ρ on train/val over epochs)
- **FR-7.4:** Sensitivity Score per Accuracy Decile bar chart
- **FR-7.5:** t-SNE/PCA scatter of encoder embeddings colored by accuracy (with equiv pairs as connected dots)
- Output: `h-m1/figures/`

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | Schurholt ModelZooDataset MNIST-CNN (hyp_rand) |
| File | `dataset_mnist_hyp_rand.pt` |
| Zenodo | Record 6632087 |
| URL | https://zenodo.org/record/6632087/files/dataset_mnist_hyp_rand.pt |
| Architecture | Conv(32)-Conv(64)-FC(128)-FC(10), BN-free |
| Size | ~4,100 final-epoch checkpoints |
| Input dim | ~53,002 (computed dynamically) |
| Splits | Standard Schurholt train/val/test from metadata |
| Labels | `test_accuracy` (float, range ~[0.85, 0.99]) |
| Download method | `torch.load("data/dataset_mnist_hyp_rand.pt", weights_only=False)` |
| Storage | `docs/youra_research/20260505_wsl/.data_cache/datasets/mnist_hyp_rand/` |

### 4.2 Permutation Pairs (from H-E1)

| Field | Value |
|-------|-------|
| Source | h-e1 `stratified_pair_sample` output |
| Count | 500 pairs (all orbit-qualified, orbit_proportion=1.000) |
| Seed | 42 (deterministic) |
| Minimum required | 50 pairs for sensitivity probing |

---

## 5. Non-Functional Requirements

- **NFR-1 Reproducibility:** Fixed seed=42 throughout; deterministic data loading
- **NFR-2 Performance:** Training must complete in <2 hours on single GPU
- **NFR-3 Memory:** Batch processing of weight vectors; no full-dataset GPU loading
- **NFR-4 Capacity Matching:** Encoder must be within 475K–525K parameters (±5% of 500K)
- **NFR-5 Code Reuse:** Maximize reuse of h-e1 utilities; minimize code duplication
- **NFR-6 Logging:** Structured log messages with `[H-M1]` prefix for traceability

---

## 6. Success Criteria

| Criterion | Threshold | Gate |
|-----------|-----------|------|
| Permutation sensitivity score | > 0.3 | MUST_WORK (primary gate) |
| Spearman ρ on test set | ≥ 0.5 | Quality check (non-blocking) |
| Parameter count | 475K–525K | Pre-condition |
| Permutation pairs used | ≥ 50 | Pre-condition |
| Training convergence | Val loss decreasing | Quality check |

**Gate Decision:**
- sensitivity_score > 0.3 → PASS → proceed to H-M2
- sensitivity_score ≤ 0.3 → EXPLORE (not hard failure; document flat MLP may learn partial invariance from data)

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
torchvision
numpy
scipy
scikit-learn
matplotlib
seaborn
pyyaml
tqdm
```

### 7.2 External Repositories (Reference Only)

| Repository | Purpose |
|-----------|---------|
| AvivNavon/equivariant-weight-space-networks | Official Navon et al. 2023 flat MLP baseline reference |
| ModelZoos/ModelZooDataset | Official dataset loading code reference |

### 7.3 Internal Dependencies

| Component | Source | Purpose |
|-----------|--------|---------|
| `flatten_weights` | h-e1/code/weight_analysis.py | Flatten weight tensors |
| `stratified_pair_sample` | h-e1/code/weight_analysis.py | Get permutation-equiv pairs |
| `load_zoo_checkpoints` | h-e1/code/data_loader.py | Load dataset |
| `dataset_mnist_hyp_rand.pt` | Zenodo 6632087 | Primary dataset |

---

## 8. File Structure

```
h-m1/
├── 02c_experiment_brief.md   # Phase 2C input
├── 03_prd.md                 # This document
├── 03_architecture.md        # Architecture (Step 3)
├── 03_logic.md               # Logic/API design (Step 5)
├── 03_config.md              # Config/hyperparams (Step 5)
├── 03_tasks.yaml             # Implementation tasks (Step 9)
├── code/
│   ├── config.py             # ExperimentConfig dataclass
│   ├── data_loader.py        # Dataset loading (extends h-e1)
│   ├── models.py             # FlatMLPEncoder
│   ├── train.py              # Training loop
│   ├── probe.py              # Permutation sensitivity probing
│   ├── evaluate.py           # Metrics computation
│   └── run_experiment.py     # Main entry point
└── figures/
    ├── gate_metrics.png
    ├── l2_distance_distribution.png
    ├── training_curve.png
    ├── sensitivity_by_decile.png
    └── embedding_scatter.png
```

---

## 9. References

1. Schurholt et al. (2022) "Model Zoos: A Dataset of Diverse Populations of Neural Network Models" — arXiv:2209.12892
2. Unterthiner et al. (2020) "Predicting Neural Network Accuracy from Weights" — arXiv:2002.11448
3. Navon et al. (2023) "Equivariant Architectures for Learning in Deep Weight Spaces" — arXiv:2301.12780
