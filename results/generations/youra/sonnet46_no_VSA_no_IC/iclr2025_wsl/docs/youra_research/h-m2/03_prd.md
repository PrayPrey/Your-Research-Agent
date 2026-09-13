---
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - data_specification
  - evaluation_criteria
  - dependencies
  - success_criteria
hypothesis_id: h-m2
hypothesis_type: MECHANISM
tier: FULL
generated_at: "2026-08-21T15:00:00+00:00"
---

# PRD: H-M2 — Sample Efficiency Advantage via Permutation Equivariance

## 1. Executive Summary

This experiment quantifies the sample efficiency advantage of permutation-equivariant encoders (DWSNets, GNN-NFN) over a plain Flat-MLP baseline in weight-space property prediction. Using R² learning curves across training sizes {100, 250, 500, 1000, full} on both MNIST and CIFAR-10 ModelZooDataset CNN zoos, the experiment computes the efficiency ratio (N_plain(90% peak R²) / N_equiv(90% peak R²)). The hypothesis is supported if this ratio ≥ 2.0 for at least one equivariant encoder on both zoos.

**Prerequisite:** H-M1 VALIDATED — structural permutation equivariance confirmed in DWSNets (max_diff=7.45e-09) and GNN-NFN (max_diff=1.80e-06).

**Continuation:** H-M2 re-uses H-E1 training runs if R² results are stored at each training size. Phase 4 primarily loads H-E1 results and computes efficiency ratios. If H-E1 results are missing, re-runs training with the same protocol.

---

## 2. Problem Statement

H-E1 established that equivariant encoders achieve higher R² at small training sizes. H-M1 confirmed the structural permutation-equivariance mechanism. H-M2 asks: **how large is the sample efficiency advantage, and is it at least 2× in terms of training data required?**

The efficiency ratio test provides a causal attribution: if equivariant encoders require ≤50% of the training data to reach 90% of their peak R², while plain Flat-MLP requires 100%, the VC dimension reduction hypothesis is supported.

A FlatMLP+permutation-augmentation ablation isolates structural equivariance from data-level symmetry exploitation.

---

## 3. Functional Requirements

### FR-1: H-E1 Result Loading (Primary Path)
- Check for H-E1 R² results at: `docs/youra_research/h-e1/results/learning_curve_results.json` (or equivalent)
- If found: load `{encoder: {zoo: {size: r2}}}` dictionary directly — no training needed
- If not found: proceed to FR-2 (training re-run)

### FR-2: Dataset Loading (if H-E1 results missing)
- Load ModelZooDataset MNIST CNN zoo from Zenodo: `data/modelzoo/dataset_mnist_hyp_fix.pt`
- Load ModelZooDataset CIFAR-10 CNN zoo from Zenodo: `data/modelzoo/dataset_cifar10_hyp_fix.pt`
- Fixed 70%/15%/15% train/val/test splits (from dataset)
- Subsampling: from training split, draw N models with `torch.manual_seed(42)` for N in {100, 250, 500, 1000, full}
- Same subsets used across all encoder conditions

### FR-3: FlatMLP Encoder
- 3-layer MLP: `input_dim → hidden_dim → hidden_dim → 1`
- Parameter budget: matched to equivariant encoders (Small: hidden=128 ~50K, Medium: hidden=512 ~200K, Large: hidden=1024 ~1M)
- Input: flattened weight vector of zoo model

### FR-4: FlatMLP + Permutation Augmentation
- Same architecture as FR-3
- During training: apply random neuron permutations to input weight vector (via `permute_weights()` from H-M1)
- Augmentation applied at batch level during training; test set evaluated without augmentation
- Purpose: isolate structural vs. data-level equivariance

### FR-5: DWSNets Encoder
- Source: `AvivNavon/DWSNets` (MIT, ICML 2023)
- Input: structured weight+bias representation (layer/neuron structure preserved)
- Configuration: `network_spec` derived from zoo model CNN architecture
- Caveat: DWSNets designed for MLP weight spaces; CNN zoo has limited FC layers. If CNN-s zoo incompatible (only 2 FC layers, DWSNets requires >2), fall back to synthetic 4-layer MLP zoo and document limitation
- Output: scalar accuracy prediction (invariant head)

### FR-6: GNN-NFN Encoder
- Source: `mkofinas/neural-graphs` (ICLR 2024 Oral)
- Input: neural graph (biases=node features, weights=edge features)
- Architecture: PNA GNN + FiLM modulation; `hidden_dim=64, num_layers=4` (matching H-E1/H-M1 checkpoints)
- Load from H-E1/H-M1 checkpoint if available; else random init + re-train
- Handles CNN architectures natively — primary encoder for CNN zoo experiments

### FR-7: Training Protocol (if re-running)
- Optimizer: Adam, lr=1e-3, weight_decay=1e-4, betas=(0.9, 0.999)
- Schedule: CosineAnnealingLR, T_max=epochs, eta_min=1e-5
- Batch size: 32 (16 for N≤250 to avoid batch > dataset)
- Epochs: 100 (fixed across all conditions and sizes)
- Loss: MSE
- Seeds: 5 seeds per (encoder, size, zoo) cell → seeds [0,1,2,3,4]
- Total runs if from scratch: 4 conditions × 5 sizes × 5 seeds × 2 zoos = 200

### FR-8: Learning Curve Computation
- For each (encoder, zoo, size, seed): compute R² on fixed test set via `r2_score(targets, preds)`
- Aggregate: mean R² and 95% CI (bootstrap, 1000 resamples over 5 seeds) per (encoder, zoo, size) cell

### FR-9: Efficiency Ratio Computation
- For each (encoder, zoo) pair:
  - `plain_peak = max(R²_flatmlp)`, `equiv_peak = max(R²_encoder)`
  - `N_plain_90 = min N s.t. R²_flatmlp[N] >= 0.90 * plain_peak`
  - `N_equiv_90 = min N s.t. R²_encoder[N] >= 0.90 * equiv_peak`
  - `efficiency_ratio = N_plain_90 / N_equiv_90`
- Gate: ≥ 2.0 for at least one equivariant encoder on BOTH MNIST and CIFAR-10

### FR-10: Mechanism Activation Verification (inherited from H-M1)
- For each equivariant encoder: sanity check equivariance on small test batch (max_diff < 1e-4)
- Log: "Equivariant encoder: permutation-invariant forward pass verified"

### FR-11: Visualization (Mandatory)
- **Learning Curve Plot**: R² vs. training size for all 4 conditions, both zoos. Line plots with 95% CI bands. Color-coded by encoder.
- **Efficiency Ratio Bar Chart**: Efficiency ratio per (encoder, zoo), with 90%-peak threshold markers and ≥2.0 threshold line.
- **Per-seed traces**: Individual seed curves (lighter lines) overlaid on mean (optional, autonomous)
- Save to: `docs/youra_research/h-m2/figures/`

### FR-12: Results Report
- Print table: encoder | zoo | N_90 | efficiency_ratio | gate
- Save JSON: `docs/youra_research/h-m2/results/learning_curve_results.json`
  - Schema: `{encoder: {zoo: {size: {mean_r2, ci_lo, ci_hi, seed_r2s: [...]}}}, efficiency_ratios: {encoder: {zoo: float}}}`
- DWSNets caveat must be documented if CNN zoo fallback triggered

---

## 4. Non-Functional Requirements

### NFR-1: Reproducibility
- All random operations seeded (seed 42 for data splits, seeds 0-4 for training)
- Results JSON saved for Phase 4.5 synthesis

### NFR-2: Parameter Budget Matching
- All encoders evaluated at same parameter tier for fair comparison
- Primary: Medium tier (~200K params)
- Ablation: Small and Large tiers (secondary)

### NFR-3: DWSNets Compatibility Fallback
- If DWSNets incompatible with CNN-s zoo (FC layer count), document explicitly in results JSON
- Use GNN-NFN as primary equivariant encoder for CNN zoo; DWSNets on synthetic MLP zoo
- Pipeline should NOT fail on DWSNets incompatibility — log and continue

### NFR-4: Continuation from H-E1
- Check for H-E1 learning curve results before re-running any training
- If H-E1 results exist at expected path, skip training entirely

---

## 5. Data Specification

### Dataset 1: ModelZooDataset MNIST CNN Zoo
- Source: Schürholt et al. NeurIPS 2022 [arXiv:2209.14764]
- Size: ~4,860 models (CNN-s architecture)
- Splits: 70%/15%/15% train/val/test (fixed)
  - Train: ~3,402; Val: ~729; Test: ~729
- Target: test accuracy (float, ground truth in dataset)
- Download: Zenodo (see ModelZoos/ModelZooDataset README for DOI)
- File: `data/modelzoo/dataset_mnist_hyp_fix.pt`
- Loading: `torch.load(path)` → `{"trainset": [...], "valset": [...], "testset": [...]}`
- No additional normalization required

### Dataset 2: ModelZooDataset CIFAR-10 CNN Zoo
- Size: ~9,000 models (CNN-s architecture)
- Splits: 70%/15%/15%
  - Train: ~6,300; Val: ~1,350; Test: ~1,350
- File: `data/modelzoo/dataset_cifar10_hyp_fix.pt`
- Same structure as MNIST zoo

### Subsampling Protocol
- From training split indices, generate permuted index list: `torch.randperm(len(train_indices), generator=torch.Generator().manual_seed(42))`
- Fixed subsets: `{100: perm[:100], 250: perm[:250], 500: perm[:500], 1000: perm[:1000], 'full': perm}`
- Val and test sets fixed across all sizes

---

## 6. Evaluation Criteria

### Primary: Efficiency Ratio
- Target: ≥ 2.0 for at least one equivariant encoder on BOTH MNIST and CIFAR-10
- Partial support: 1.5–2.0 (document as trend)

### Secondary: Visual Learning Curve Distinguishability
- Equivariant learning curves must be visually steeper in 100–500 range

### Bootstrap CI
- 95% CI must not overlap between equivariant and flat-MLP at N=250 (on at least one zoo)

### Expected Baselines (from literature)
- Flat-MLP at full data: R² ≈ 0.60–0.75
- GNN-NFN at full data: R² ≈ 0.83–0.89
- Linear baseline (weight statistics): R² ≈ 0.83 (MNIST, from Schürholt 2022 Table 3)

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.13
torch_geometric
scikit-learn
numpy
matplotlib
scipy
```

### 7.2 External Repositories
- `AvivNavon/DWSNets` (MIT) — DWSNets encoder
- `mkofinas/neural-graphs` (ICLR 2024) — GNN-NFN encoder
- `ModelZoos/ModelZooDataset` — dataset loading utilities

### 7.3 Base Hypothesis Dependencies
- H-E1 code: `docs/youra_research/h-e1/code/` — `ZooDataset`, `GNNNFNEncoder`, `FlatMLP`, `state_dict_to_graph`
- H-M1 code: `docs/youra_research/h-m1/code/` — `permute_weights()` (for FlatMLP+Aug ablation)
- H-E1 results (optional): `docs/youra_research/h-e1/results/` — learning curve R² results if available
- ModelZooDataset code: `data/ModelZooDataset/code/` (for preprocessing utilities)

---

## 8. Success Criteria

| Criterion | Threshold | Status |
|-----------|-----------|--------|
| H-E1 or training results available | All 4 × 5 × 2 cells populated | Required |
| Efficiency ratio (primary) | ≥ 2.0 for ≥1 encoder on both MNIST + CIFAR-10 | SHOULD_WORK gate |
| Partial support threshold | Ratio 1.5–2.0 | Document as trend |
| Equivariance sanity check | max_diff < 1e-4 per batch | Required |
| Results JSON saved | learning_curve_results.json exists | Required |
| Figures generated | Learning curve + efficiency ratio bar chart | Required |
