# PRD: H-M3 — DeepSets Mechanism Closure Validation

**Version:** 1.0
**Date:** 2026-08-03
**Hypothesis:** H-M3 (MECHANISM, INCREMENTAL — extends H-M2)
**Author:** YouRA Pipeline

---

## stepsCompleted
- [x] Executive Summary
- [x] Problem Statement
- [x] Functional Requirements
- [x] Non-Functional Requirements
- [x] Data Specification
- [x] Success Criteria
- [x] Dependencies

---

## 1. Executive Summary

H-M3 tests whether DeepSets (C2), by eliminating permutation sensitivity (MSE_perm), achieves mechanism closure: R²(C2) ≥ R²(C0)=0.984 and ΔMSE(C1→C2) ≈ MSE_perm^C1 = 0.006137. This is an INCREMENTAL experiment extending H-M2 — only the encoder changes (C1 CISE → C2 DeepSets → C3 NFN), all LightGBM hyperparameters and CV splits are reused verbatim.

**Predicted outcome:** If the bias-variance decomposition E[(y-ŷ)²] = MSE_res + MSE_perm holds causally, eliminating MSE_perm via invariant encoding closes the C1→C0 performance gap by exactly MSE_perm^C1.

---

## 2. Problem Statement

H-M2 confirmed CISE (C1) has OrbitVar=0.010333 that propagates to prediction space: MSE_perm^C1 = 0.006137 >> 0.10 × MSE_total. H-M3 tests whether DeepSets (C2), which achieves OrbitVar<1e-6 (validated H-E1), eliminates MSE_perm and thereby recovers the R²(C0)=0.984 baseline through this single mechanistic change.

**Null hypothesis (H0):** Eliminating MSE_perm does NOT close the performance gap to R²(C0)=0.984 — other factors (representation expressivity, capacity) dominate.

---

## 3. Functional Requirements

### FR-1: Dataset Loading
- Load `data/dataset_cifar_small_hyp_rand.pt` (already downloaded from Zenodo in H-M2)
- Extract weights and test accuracy labels for N=100 CIFAR-10 CNN models (3 conv layers, C=16 channels)
- Reuse identical train/val/test assignments via 5-fold CV (seed=42, stratified by accuracy quartile)

### FR-2: C0 Baseline (Ŵ_L per-layer statistics)
- Compute per-layer quantile statistics (5-quantile per layer, flattened) — no neural encoder
- Reuse `compute_layer_stats(weights)` from H-M2 code
- Fit LightGBM regressor on C0 features with H-M2 hyperparameters
- Record R²(C0), τ(C0)

### FR-3: C1 Baseline (CISE — Reference Load)
- Load saved H-M2 results from `h-m2/experiment_results.json` — NO RETRAINING
- Extract: MSE_total(C1)=0.001834, MSE_perm^C1=0.006137, R²(C1)=0.851, τ(C1)=0.721

### FR-4: C2 Encoder (DeepSets — Primary Proposed)
- Load `DeepSetsEncoder` from `h-e1/code/encoders.py` (H-E1 validated, OrbitVar<1e-6)
- Extract per-model embeddings: φ per channel → sum pool over C_out → ρ → concat layers
- Fit LightGBM (same hyperparameters as H-M2) on C2 embeddings
- Compute MSE_perm(C2) via K=50 orbit permutations (seed=1)
- Record R²(C2), τ(C2), MSE_total(C2), MSE_perm(C2)

### FR-5: C3 Encoder (NFN — Secondary Proposed)
- Install: `pip install git+https://github.com/AllanYangZhou/nfn.git`
- Build NFN encoder: NPLinear(network_spec, 1, 32, io_embed=True) → ReLU → NPLinear → ReLU → HNPPool → Flatten
- Check architecture compatibility: `state_dict_to_tensors(network_spec)` — verify spatial folding if needed
- Extract per-model NFN embeddings; fit LightGBM and RidgeCV linear heads
- Record R²(C3-LightGBM), R²(C3-Ridge)

### FR-6: Linear Head Ablation
- Fit RidgeCV(alphas=[0.01, 0.1, 1.0, 10.0], cv=5) on frozen C2 embeddings
- Fit RidgeCV on frozen C3 embeddings
- Record R²(C2-Ridge), R²(C3-Ridge)
- Compute expressivity gap: R²(C3-Ridge) − R²(C2-Ridge)

### FR-7: Mechanism Closure Computation
- ΔMSE = MSE_total(C1) − MSE_total(C2)
- closure = |ΔMSE − MSE_perm^C1| / MSE_perm^C1
- MSE_perm^C1 reference: 0.006137 (from H-M2)

### FR-8: Gate Evaluation
- Primary gate (SHOULD_WORK PASS): R²(C2) ≥ 0.984 AND closure ≤ 0.10
- EXPLORE branch: R²(C2) ∈ (0.851, 0.984) → report τ as primary
- PIVOT branch: closure > 2.0 → representation geometry dominates

### FR-9: Mechanism Verification
- Execute `verify_mechanism_activated(results)` — 3/4 indicators required
- Log OrbitVar(C2), MSE_perm(C2), ΔMSE, closure

### FR-10: Visualization
- **Mandatory:** Bar chart R²(C0, C1, C2, C3) with 0.984 threshold line
- **Optional (LLM autonomous):** MSE decomposition stacked bar, closure scatter, OrbitVar scatter, linear head ablation bar, τ comparison

### FR-11: Results Persistence
- Save all metrics to `h-m3/experiment_results.json`
- Save figures to `docs/youra_research/h-m3/figures/`
- Save experiment log to `h-m3/experiment.log`

---

## 4. Data Specification

### Primary Dataset

| Field | Value |
|-------|-------|
| Name | ModelZooDataset CIFAR10-GS (Hyp-rand split) |
| Source | Zenodo DOI 10.5281/zenodo.6620868 |
| File | `data/dataset_cifar_small_hyp_rand.pt` |
| Status | Already downloaded (H-M2 reuse) — NO DOWNLOAD TASK |
| N models | 100 CNNs (3 conv layers, C=16 channels) |
| Labels | Test accuracy on CIFAR-10 ∈ [0, 1] |
| Split | 5-fold CV (seed=42, stratified by accuracy quartile) |

**Note:** Auto-load via `torch.load("data/dataset_cifar_small_hyp_rand.pt")` — no manual download task needed.

### Reference Results

| Source | File | Fields Used |
|--------|------|-------------|
| H-M2 | `h-m2/experiment_results.json` | MSE_total, MSE_perm, R², τ for C1 |
| H-E1 | `h-e1/code/encoders.py` | DeepSetsEncoder class |

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- All CV splits identical to H-M2 (seed=42)
- Permutation sampling identical (seed=1, K=50)
- LightGBM: n_estimators=500, learning_rate=0.05

### NFR-2: Controlled Comparison
- Only encoder changes between C1/C2/C3 — ALL other variables fixed
- Do NOT retrain C1; load H-M2 results directly

### NFR-3: Correctness Checks
- Assert OrbitVar(C2) < 1e-4 before proceeding
- Assert MSE_perm(C2) < MSE_perm(C1) (permutation sensitivity reduced)
- If C3 NFN spatial folding fails: fall back to custom DeepSets variant for C3

### NFR-4: Performance
- Full experiment (C0 + C2 + C3 + all ablations + permutations) should complete < 30 min on CPU

---

## 6. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| R²(C2) vs C0 | ≥ 0.984 | OOF LightGBM R² on C2 embeddings |
| Mechanism closure | ≤ 0.10 | \|ΔMSE − 0.006137\| / 0.006137 |
| Mechanism activated | TRUE | OrbitVar(C2) < 1e-4, MSE_perm(C2) ≈ 0 |
| Code runs error-free | No exceptions | All encoders (C0, C2, C3) succeed |

---

## 7. Dependencies

### 7.1 Python Packages (Environment Setup Required)

```
lightgbm>=3.3.0
torch>=1.12.0
scikit-learn>=1.0.0
scipy>=1.7.0
numpy>=1.21.0
matplotlib>=3.5.0
git+https://github.com/AllanYangZhou/nfn.git   # C3 NFN encoder
```

### 7.2 Internal Code Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| `DeepSetsEncoder` | `h-e1/code/encoders.py` | C2 encoder (validated) |
| `compute_layer_stats()` | `h-m2/code/*.py` | C0 features |
| `experiment_results.json` | `h-m2/` | C1 baseline metrics |
| `dataset_cifar_small_hyp_rand.pt` | `data/` | Dataset |

### 7.3 External Repositories

- AllanYangZhou/nfn: Official NFN library (pip install)
- ModelZoos/ModelZooDataset: Dataset reference (already downloaded)
