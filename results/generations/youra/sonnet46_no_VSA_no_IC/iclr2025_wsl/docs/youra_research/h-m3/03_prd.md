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
hypothesis_id: h-m3
hypothesis_type: MECHANISM
tier: FULL
generated_at: "2026-08-21T17:00:00+00:00"
---

# PRD: H-M3 — Permutation Augmentation as Partial Equivariance Benefit

## 1. Executive Summary

This experiment isolates the contribution of permutation augmentation (PermAug) versus structural equivariance in weight-space property prediction. Flat-MLP + PermAug is trained at {100, 250, 500, 1000} models on the CIFAR-10 ModelZooDataset CNN zoo and its R² is compared to Flat-MLP (no augmentation, from H-E1) and GNN-NFN (equivariant encoder, from H-M2). The hypothesis is supported if a strict ordering `Flat-MLP R² < Flat-MLP+PermAug R² < GNN-NFN R²` holds with non-overlapping bootstrap 95% CIs at BOTH N=100 AND N=250.

**Critical fix from H-E1:** The H-E1 `flat_mlp_perm_aug` condition was broken (identical to `flat_mlp` — same random seeds). H-M3 re-implements PermAug with an explicit mechanism verification check (`aug_diff > 1e-6` and dataset size = 11× base). Only the PermAug condition requires re-training; Flat-MLP and GNN-NFN results are loaded from H-E1/H-M2.

**Secondary criterion:** PermAug closes 50–80% of the Flat-MLP-to-equivariant gap (`perm_aug_fraction = (R²_perm_aug - R²_flat_mlp) / (R²_gnn_nfn - R²_flat_mlp) ∈ [0.50, 0.80]`).

---

## 2. Problem Statement

H-M2 confirmed GNN-NFN achieves 6.8× sample efficiency over Flat-MLP (CIFAR-10). H-M3 asks: **is the advantage structural (equivariance reduces VC dimension) or distributional (data augmentation suffices)?**

If PermAug R² lies strictly between Flat-MLP and GNN-NFN with non-overlapping CIs, the advantage is structural — augmentation provides partial but not full benefit. This rules out the alternative that simply making the data distribution permutation-symmetric is sufficient.

The H-E1 PermAug bug (identical seeds → no actual augmentation) makes this a new experiment, not a re-analysis.

---

## 3. Functional Requirements

### FR-1: Load Baseline Results (Flat-MLP and GNN-NFN)
- Load Flat-MLP R² at N ∈ {100, 250, 500, 1000} from H-E1 results: `docs/youra_research/h-e1/results/`
  - Expected: N=100 → -0.141, N=250 → 0.449, N=500 → 0.687, N=1000 → 0.740
- Load GNN-NFN R² at N ∈ {100, 250, 500, 1000} from H-M2 results: `docs/youra_research/h-m2/results/`
  - Expected: N=100 → -0.016, N=250 → 0.767, N=500 → 0.847, N=1000 → 0.864
- Reuse `results_loader.py` from H-M2 for result loading
- If results not found at expected paths, raise explicit error (do NOT re-train Flat-MLP or GNN-NFN)

### FR-2: Dataset Loading (for PermAug re-training only)
- Load ModelZooDataset CIFAR-10 CNN zoo
- Source: `checkpoints_to_datasets/dataset_base.py` (`WeightDataset`)
- Zoo path: `data/modelzoo/` (same as H-E1/H-M2)
- Fixed 70%/15%/15% train/val/test splits
- Subsampling: from training split, draw N models with `torch.manual_seed(42)` for N in {100, 250, 500, 1000}
- SAME subsets as H-E1/H-M2 (controlled comparison)
- Normalization: per-feature z-score using training set statistics

### FR-3: Flat-MLP Architecture (reused from H-E1)
- 3-layer MLP: `input_dim → 256 → 128 → 1`
- Input: flattened weight vector of zoo model
- Import from: `docs/youra_research/h-e1/code/` (`FlatMLP`)

### FR-4: PermAug Implementation (CRITICAL — new for H-M3)
- `PermAugDataset(base_dataset, layer_sizes, num_permutations=10)` wrapper
- `__len__`: returns `len(base) * (num_permutations + 1)` (10 augmented + 1 original per sample)
- `__getitem__`: for aug_idx > 0, apply `apply_random_permutation(x, layer_sizes)`
- `apply_random_permutation`: permutes hidden-layer neurons following Zhou et al. 2023 (NFN paper Eq. 1)
  - For each hidden layer l: sample `perm = torch.randperm(hidden_size_l)`
  - Apply `W_l[perm, :]` (permute output neurons) and `W_{l+1}[:, perm]` (compensate input)
  - Bias permuted: `b_l[perm]`
  - Flatten back to 1D vector
- Layer sizes derived from `index_dict.json` in ModelZooDataset (CIFAR-10 CNN architecture)

### FR-5: Mechanism Verification (MANDATORY before training)
- `verify_perm_aug_activated(x_batch, layer_sizes)`:
  - Check `aug_diff = (x_aug - x_orig).abs().max() > 1e-6`
  - Assert pass: `[H-M3 MECHANISM CHECK] PermAug diff = X > 1e-6 ✓`
- `verify_perm_aug_mechanism(train_loader_perm, train_loader_plain, layer_sizes)`:
  - Check 1: augmented batch differs from plain batch (`aug_diff > 1e-6`)
  - Check 2: dataset size correct (`len(perm_dataset) == len(plain_dataset) * 11`)
  - Print all indicators; raise `RuntimeError` if any check fails

### FR-6: PermAug Training Protocol
- Model: FlatMLP (same as FR-3)
- Optimizer: Adam, lr=1e-3, weight_decay=1e-4
- Batch size: 64
- Epochs: 100
- Loss: MSE
- Seeds: 1 fixed seed (PoC mode)
- Training sizes: N ∈ {100, 250, 500, 1000} on CIFAR-10
- PermAug applied during training only; test evaluation uses original (non-augmented) weights
- Total training runs: 4 (one per N)

### FR-7: Evaluation
- Primary metric: R² on fixed held-out test set (`r2_score` from sklearn)
- Bootstrap 95% CI: 1000-resample percentile method (reuse `bootstrap_ci()` from H-M2 `analysis.py`)
- Compute for all 3 conditions × 4 sizes: {flat_mlp, flat_mlp_perm_aug, gnn_nfn} × {100, 250, 500, 1000}
- Gate check: `check_gate()` from H-M2 analysis (strict ordering + non-overlapping CIs at N=100, N=250)

### FR-8: Gap Analysis
- `gap_total = R²(gnn_nfn) - R²(flat_mlp)` at each N
- `gap_perm_aug = R²(flat_mlp_perm_aug) - R²(flat_mlp)` at each N
- `perm_aug_fraction = gap_perm_aug / gap_total` at each N
- P2 criterion: `perm_aug_fraction ∈ [0.50, 0.80]` at N=100 and N=250

### FR-9: Visualization (Mandatory)
- **Gate Metrics Comparison**: Bar chart of R² at N=100 and N=250 for all 3 conditions with bootstrap 95% CI error bars. Must visually show whether CIs overlap. Save to `figures/gate_metrics.png`.
- **Ordering Plot**: Line plot of R² vs. training size (N=100, 250, 500, 1000) for all 3 conditions with CI bands. Save to `figures/ordering_plot.png`.
- **Gap Fraction Plot**: Bar chart of `perm_aug_fraction` at N=100 and N=250, with horizontal bands at 50% and 80%. Save to `figures/gap_fraction.png`.
- **PermAug Verification Plot**: Training loss curves for flat_mlp vs flat_mlp_perm_aug to confirm PermAug differs. Save to `figures/training_curves.png`.
- Save all figures to `docs/youra_research/h-m3/figures/`

### FR-10: Results Report
- Save JSON: `docs/youra_research/h-m3/results/results.json`
  - Schema: `{encoder: {size: {r2, ci_lo, ci_hi}}, gap_analysis: {N: {gap_total, gap_perm_aug, perm_aug_fraction}}, gate: {satisfied, result_str}}`
- Print summary table: encoder | N | R² | CI_lo | CI_hi | gate_at_N100_250

---

## 4. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed (42) for all data subsampling
- Fixed seed for PermAug training
- All results saved as JSON for Phase 4.5 synthesis

### NFR-2: Controlled Comparison
- Flat-MLP and GNN-NFN results MUST come from H-E1/H-M2 stored files (not re-trained)
- Only PermAug condition is trained fresh
- This ensures observed differences are due ONLY to augmentation, not random variation

### NFR-3: Mechanism Verification Priority
- Verification (`verify_perm_aug_mechanism`) MUST run BEFORE any training
- If mechanism verification fails, STOP with explicit error (do not proceed to train)

### NFR-4: Compute Budget
- Limit training to CIFAR-10 only (MNIST zoo unavailable locally)
- 4 training runs total (one per N), each ~few minutes
- PoC mode: single seed per condition

---

## 5. Data Specification

### Dataset: ModelZooDataset CIFAR-10 CNN Zoo
- **Source:** Schürholt et al. 2022 [arXiv:2209.14764], https://github.com/ModelZoos/ModelZooDataset
- **Size:** ~9,000 CNN models trained on CIFAR-10
- **Architecture:** CNN-s (convolutional neural network, small variant)
- **Label:** test accuracy (float)
- **Splits:** 70%/15%/15% train/val/test (pre-computed, fixed)
  - Train: ~6,300; Val: ~1,350; Test: ~1,350 models
- **Loading:**
  ```python
  from checkpoints_to_datasets.dataset_base import WeightDataset
  ds = WeightDataset(zoo_path, split='train')
  # Returns (weight_vector, label) per model
  ```
- **Layer sizes:** Extracted from `index_dict.json` in the dataset (needed for PermAug correct row/col permutation)

### Subsampling Protocol
- From training split: `torch.randperm(len(train_split), generator=torch.Generator().manual_seed(42))`
- Fixed subsets: `{100: perm[:100], 250: perm[:250], 500: perm[:500], 1000: perm[:1000]}`
- Same indices as H-E1/H-M2 (controlled comparison)

---

## 6. Evaluation Criteria

### Primary Gate (SHOULD_WORK)
- **Strict ordering** with non-overlapping 95% CIs at BOTH N=100 AND N=250:
  - `R²(flat_mlp) < R²(flat_mlp_perm_aug)` (CI_hi of flat_mlp < CI_lo of perm_aug)
  - `R²(flat_mlp_perm_aug) < R²(gnn_nfn)` (CI_hi of perm_aug < CI_lo of gnn_nfn)
- At least one zoo (CIFAR-10 only available)

### Secondary Criterion (P2)
- `perm_aug_fraction ∈ [0.50, 0.80]` at N=100 and N=250
- If fraction < 0.50: PermAug effect smaller than expected
- If fraction > 0.80: PermAug nearly as good as structural equivariance (interesting finding)

### Failure Modes (Document, Not Ignore)
- If `R²(perm_aug) ≈ R²(gnn_nfn)`: mechanism is distributional, not structural
- If `R²(perm_aug) ≈ R²(flat_mlp)`: augmentation provides no benefit; check mechanism verification

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
- `mkofinas/neural-graphs` — GNN-NFN (results only, no re-training)
- `ModelZoos/ModelZooDataset` — dataset loading utilities (`checkpoints_to_datasets/dataset_base.py`)

### 7.3 Base Hypothesis Dependencies
- H-E1 code: `docs/youra_research/h-e1/code/` — `FlatMLP`, `ZooDataset`, weight vectorization
- H-M2 code: `docs/youra_research/h-m2/code/` — `results_loader.py`, `analysis.py` (`bootstrap_ci`, `check_gate`), `visualize.py`
- H-E1 results: `docs/youra_research/h-e1/results/` — Flat-MLP R² at all training sizes
- H-M2 results: `docs/youra_research/h-m2/results/` — GNN-NFN R² at all training sizes

### 7.4 Reference Implementations
- NFN paper (Zhou et al. 2023 NeurIPS) Eq. 1: PermAug design basis
- Shamsian et al. 2024 (ICML): confirms partial augmentation benefit

---

## 8. Success Criteria

| Criterion | Threshold | Verification |
|-----------|-----------|-------------|
| Mechanism verified pre-training | `aug_diff > 1e-6` AND `len(perm_ds) = 11 × len(base_ds)` | `verify_perm_aug_mechanism()` |
| PermAug ≠ Flat-MLP results | `R²(perm_aug) ≠ 0.449` at N=250 | Post-training comparison |
| Strict ordering at N=100 | `CI_hi(flat_mlp) < CI_lo(perm_aug) < CI_lo(gnn_nfn)` | Bootstrap CI check |
| Strict ordering at N=250 | `CI_hi(flat_mlp) < CI_lo(perm_aug) < CI_lo(gnn_nfn)` | Bootstrap CI check |
| Secondary P2 criterion | `perm_aug_fraction ∈ [0.50, 0.80]` at N=100 AND N=250 | Gap analysis |
| Results JSON saved | `results/results.json` exists with all conditions | File check |
| All 4 figures generated | gate_metrics, ordering_plot, gap_fraction, training_curves | File check |
