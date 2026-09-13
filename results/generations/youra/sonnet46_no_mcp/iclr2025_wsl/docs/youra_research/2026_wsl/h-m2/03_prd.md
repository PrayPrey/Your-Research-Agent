# Product Requirements Document: H-M2
# NFN Equivariant Encoder Permutation Sensitivity Probing

**stepsCompleted:** [executive-summary, problem-statement, functional-requirements, nfrs, success-criteria, data-specification, dependencies]

**Hypothesis ID:** h-m2
**Hypothesis Type:** MECHANISM (INCREMENTAL — builds on h-m1)
**Gate Type:** SHOULD_WORK
**Date:** 2026-05-05
**Author:** Anonymous
**Source:** h-m2/02c_experiment_brief.md

---

## 1. Executive Summary

This experiment trains a Navon et al. permutation-equivariant NFN encoder (~500K parameters, matched to h-m1) on weight-space accuracy prediction using the Schurholt MNIST-CNN model zoo, then probes whether its learned embeddings exhibit near-zero permutation sensitivity. The key mechanism under test: NFN encoders are equivariant by construction and map all permutation-equivalent weight vectors to identical embeddings before the final prediction head. We measure this via the same permutation sensitivity score used in h-m1: mean L2 distance between embeddings of permutation-equivalent pairs divided by mean L2 distance of random non-equivalent pairs. A score < 0.1 AND < 0.3245 (50% of flat MLP score) confirms the mechanism and gates downstream H-M3.

**Hypothesis Statement:** Under conditions of matched encoder capacity (~500K parameters ±5%) on the Schurholt MNIST-CNN zoo, if we train a Navon et al. permutation-equivariant NFN encoder on accuracy prediction, then its learned embeddings will exhibit near-zero permutation sensitivity (similar embeddings for permutation-equivalent weight configurations), because NFN encoders are equivariant by construction and map all permutation-equivalent weight vectors to identical embeddings before the final prediction head.

---

## 2. Problem Statement

### 2.1 Background

H-E1 confirmed orbit_proportion=1.000 (100% of MNIST-CNN pairs are permutation-distinct for flat MLP). H-M1 confirmed flat MLP permutation sensitivity_score=0.6490 > 0.3, establishing the mechanistic baseline. H-M2 now tests the complementary causal claim: does the NFN equivariant encoder, by architectural construction, map permutation-equivalent weight configurations to near-identical embeddings (sensitivity_score < 0.1)?

The Navon et al. (2023) NFN encoder uses NPLinear layers — permutation-equivariant linear layers that operate on per-layer weight tensors. By mathematical guarantee, all permutation-equivalent weight configurations map to identical intermediate representations at every NPLinear layer.

### 2.2 Motivation

This experiment is required before H-M3 (Δρ comparison), as it confirms the structural equivariance property of the NFN encoder under matched capacity constraints. Without confirming NFN near-zero permutation sensitivity, the claimed capacity reallocation advantage cannot be attributed to the permutation-equivariance mechanism.

### 2.3 Scope

- **In scope:** Train NFN encoder with matched ~500K params via channel_dim grid search; probe permutation sensitivity using same 500 pairs from h-e1/h-m1; report Spearman ρ as quality check
- **Out of scope:** Re-training flat MLP (h-m1 result used directly); CIFAR-10 experiments (H-M3); Δρ comparative analysis (H-M3)

---

## 3. Functional Requirements

### FR-1: Dataset Loading and Preprocessing

- **FR-1.1:** Load `dataset_mnist_hyp_rand.pt` from cache at `docs/youra_research/20260505_wsl/.data_cache/datasets/mnist_hyp_rand/dataset_mnist_hyp_rand.pt` (REUSE from h-m1 — already verified 2,249 checkpoints)
- **FR-1.2:** Extract final-epoch checkpoints (`training_iteration=50`) with `test_accuracy` labels — same as h-m1
- **FR-1.3:** For NFN input: extract per-layer weight tensors as structured list (NOT flattened): `[conv1.weight, conv1.bias, conv2.weight, conv2.bias, fc1.weight, fc1.bias, fc2.weight, fc2.bias]`
- **FR-1.4:** For sensitivity probing: also flatten weights (reuse `flatten_weights()` from h-e1 for permutation generation compatibility)
- **FR-1.5:** Use Schurholt standard train/val/test splits (train=1589, val=322, test=338) — same as h-m1
- **FR-1.6:** Dataset must yield ≥100 test samples for Spearman ρ computation
- **FR-1.7:** MNIST-CNN weight shapes: `[(32,1,3,3), (32,), (64,32,3,3), (64,), (128,1024), (128,), (10,128), (10,)]` (8 tensors)

### FR-2: NFN Equivariant Encoder Architecture

- **FR-2.1:** Implement `NPLinear(in_ch, out_ch, weight_shapes)` — permutation-equivariant linear layer (Navon et al. 2023) operating on list of per-layer weight tensors
- **FR-2.2:** Implement `NFNEncoder(weight_shapes, channel_dim, embed_dim=128, n_layers)` using stacked NPLinear layers with global mean pooling readout
- **FR-2.3:** Run width grid search over `channel_dim ∈ {24, 32, 40, 48, 56}` × `n_layers ∈ {2, 3, 4}` to hit total params in [475K, 525K]
- **FR-2.4:** Attach prediction head `Linear(128, 1)` for accuracy regression during training
- **FR-2.5:** Verify parameter count via `sum(p.numel() for p in model.parameters())`
- **FR-2.6:** Input: list of 8 per-layer tensors → Output embedding: `(B, 128)`
- **FR-2.7:** MUST preserve equivariant NPLinear layer structure (no arbitrary `nn.Linear` substitutions inside encoder)

### FR-3: Training Protocol (REUSE from h-m1 — controlled experiment)

- **FR-3.1:** Optimizer: Adam, lr=1e-3, weight_decay=1e-4, betas=(0.9, 0.999)
- **FR-3.2:** LR Schedule: CosineAnnealingLR, T_max=150, eta_min=1e-6
- **FR-3.3:** Batch size: 32
- **FR-3.4:** Epochs: 150
- **FR-3.5:** Loss: MSE on accuracy regression (`F.mse_loss(pred, true_accuracy)`)
- **FR-3.6:** Fixed random seed: 42
- **FR-3.7:** Log train/val loss and Spearman ρ every epoch

### FR-4: Permutation Sensitivity Probing

- **FR-4.1:** Load 500 permutation-equivalent weight pairs (SAME pairs as h-m1/h-e1: `stratified_pair_sample`, seed=42, 50 pairs per accuracy decile)
- **FR-4.2:** Generate permuted weight variants via `generate_permuted_weights()` (REUSE from h-m1/code/probe.py) — preserve functional equivalence
- **FR-4.3:** Compute `sensitivity_score = mean(L2(enc(w), enc(perm(w)))) / mean(L2(enc(w_i), enc(w_j)))` for 500 pairs
- **FR-4.4:** Use trained NFN encoder in eval mode with `torch.no_grad()`
- **FR-4.5:** Report: nfn_sensitivity_score, mean_equiv_L2, mean_random_L2, n_pairs used
- **FR-4.6:** Run per-decile sensitivity breakdown (10 accuracy deciles, 50 pairs each)

### FR-5: Evaluation and Metrics

- **FR-5.1 [GATE METRIC PRIMARY]:** NFN sensitivity_score < 0.1 → absolute gate PASS
- **FR-5.2 [GATE METRIC SECONDARY]:** NFN sensitivity_score < flat_MLP_score × 0.5 = 0.3245 → relative gate PASS
- **FR-5.3 [GATE CONDITION]:** BOTH FR-5.1 AND FR-5.2 must pass → H-M2 PASS
- **FR-5.4 [QUALITY CHECK]:** Spearman ρ(NFN) on test set > Spearman ρ(flat MLP) = 0.1041 (informational, not blocking)
- **FR-5.5:** Compute Spearman ρ using `scipy.stats.spearmanr`
- **FR-5.6:** If sensitivity_score ≥ 0.1 → EXPLORE: investigate equivariant layer structure integrity

### FR-6: Ablation Variants

- **FR-6.1 [Channel Dim Grid]:** channel_dim ∈ {24, 32, 40, 48, 56} — parameter matching grid search (select one that hits 475K–525K)
- **FR-6.2 [N Layers Grid]:** n_layers ∈ {2, 3, 4} — combined with channel_dim grid search
- **FR-6.3 [Baseline Reference]:** Flat MLP sensitivity_score=0.6490 from h-m1 (NOT re-trained, used as reference only)

### FR-7: Visualizations

- **FR-7.1 [MANDATORY]:** Gate Metrics Comparison bar chart: NFN sensitivity_score vs 0.1 threshold vs 0.3245 threshold vs h-m1 flat MLP 0.6490
- **FR-7.2:** L2 Distance Distribution: side-by-side histograms of equiv-pair L2 and random-pair L2 for NFN vs flat MLP
- **FR-7.3:** Embedding Scatter (PCA): 2D projection of NFN embeddings colored by accuracy; permutation-equivalent pairs connected
- **FR-7.4:** Training Curve: loss and Spearman ρ on train/val over 150 epochs for NFN
- **FR-7.5:** Sensitivity Score by Accuracy Decile: bar chart for NFN per decile (compare to h-m1)
- **FR-7.6:** NFN vs Flat MLP Sensitivity Comparison: grouped bar per decile

Output location: `h-m2/figures/`

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | Schurholt ModelZooDataset MNIST-CNN (hyp_rand) |
| Source | Zenodo record 6632087 (Schurholt et al. 2022) |
| Cache | `docs/youra_research/20260505_wsl/.data_cache/datasets/mnist_hyp_rand/dataset_mnist_hyp_rand.pt` |
| Size | 2,249 checkpoints |
| Splits | train=1,589 / val=322 / test=338 (Schurholt standard) |
| Accuracy Range | [0.85, 0.99] |
| Architecture | Conv(32)-Conv(64)-FC(128)-FC(10), BN-free plain CNN |
| Loading | `torch.load(cache_path, weights_only=False)` |

**Status:** REUSE from h-m1 — already cached and verified. No manual download required.

### 4.2 NFN Input Format

Weight tensors extracted per-layer (structured list, NOT flattened):

| Layer Index | Tensor Name | Shape |
|-------------|-------------|-------|
| 0 | conv1.weight | (32, 1, 3, 3) |
| 1 | conv1.bias | (32,) |
| 2 | conv2.weight | (64, 32, 3, 3) |
| 3 | conv2.bias | (64,) |
| 4 | fc1.weight | (128, 1024) |
| 5 | fc1.bias | (128,) |
| 6 | fc2.weight | (10, 128) |
| 7 | fc2.bias | (10,) |

**Note:** fc1.weight is (128, 1024) after 64×4×4 spatial flatten at conv→fc boundary.

### 4.3 Permutation Pairs

- Count: 500 pairs (SAME as h-m1/h-e1)
- Sampling: stratified by accuracy decile (50 per decile)
- Seed: 42
- Source: `stratified_pair_sample` from h-e1/code/weight_analysis.py

---

## 5. Non-Functional Requirements

- **NFR-1 Performance:** Full experiment (training + probing) completes in ≤ 60 minutes on single GPU
- **NFR-2 Reproducibility:** Fixed seed=42 throughout; `torch.manual_seed(42)`, `np.random.seed(42)`
- **NFR-3 Capacity Matching:** NFN total params strictly in [475K, 525K] — verified before training
- **NFR-4 Equivariance Integrity:** No arbitrary `nn.Linear` layers inside NFN encoder body (only NPLinear)
- **NFR-5 Reuse:** Maximize code reuse from h-m1/code/ (data_loader, probe, evaluate, train)
- **NFR-6 Single GPU:** `CUDA_VISIBLE_DEVICES=<empty_gpu>` set before experiment run

---

## 6. Success Criteria

| Criterion | Threshold | Status |
|-----------|-----------|--------|
| NFN sensitivity_score (absolute) | < 0.1 | Gate Primary |
| NFN sensitivity_score (relative) | < 0.3245 (= 0.6490 × 0.5) | Gate Secondary |
| Both gate conditions | BOTH must pass | H-M2 PASS |
| NFN param count | 475K–525K | Required |
| Spearman ρ(NFN) > ρ(flat MLP) | > 0.1041 | Quality check (informational) |

**Gate Type:** SHOULD_WORK — if fails: EXPLORE (investigate equivariant layer structure integrity)

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=1.12.0
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.5.0
pyyaml>=6.0
```

### 7.2 Internal Dependencies (REUSE from h-m1)

| Module | Source File | Reuse Notes |
|--------|-------------|-------------|
| `WeightDataset` | `h-m1/code/data_loader.py` | Extend to return structured weight list for NFN |
| `load_and_split_dataset` | `h-m1/code/data_loader.py` | Unchanged — same zoo, same splits |
| `train_encoder` | `h-m1/code/train.py` | Same optimizer; adapt for NFN forward |
| `compute_spearman` | `h-m1/code/evaluate.py` | Unchanged |
| `get_mnist_cnn_layer_order` | `h-m1/code/probe.py` | Unchanged — Conv(32)-Conv(64)-FC(128)-FC(10) |
| `generate_permuted_weights` | `h-m1/code/probe.py` | Unchanged — same permutation generation |
| `compute_permutation_sensitivity` | `h-m1/code/probe.py` | Unchanged — only encoder changes |
| `run_gate_check` | `h-m1/code/evaluate.py` | Adapt thresholds to 0.1 (absolute) + 0.3245 (relative) |

### 7.3 External References

| Reference | URL | Usage |
|-----------|-----|-------|
| AvivNavon/equivariant-weight-space-networks | https://github.com/AvivNavon/equivariant-weight-space-networks | NFN encoder architecture reference |
| ModelZoos/ModelZooDataset | https://github.com/ModelZoos/ModelZooDataset | Dataset loading reference |

---

## 8. Implementation Constraints

- **CRITICAL:** NFN input is list of per-layer weight tensors, NOT concatenated flat vector
- **CRITICAL:** NPLinear layers must preserve equivariant structure — no arbitrary `nn.Linear` inside encoder
- **CONTROLLED EXPERIMENT:** Only encoder type changes from h-m1 (flat MLP → NFN); all other components identical
- **CAPACITY MATCHING:** Grid search required to match ~500K params before training
- **SAME PAIRS:** Must use identical 500 permutation-equivalent pairs from h-e1/h-m1 (seed=42, stratified)
