# Product Requirements Document: H-M2
# Causal Propagation — CISE OrbitVar Propagates to LightGBM Prediction Variance (MSE_perm ≥ 10%)

**Hypothesis ID:** H-M2
**Type:** MECHANISM (Causal Step 2)
**Date:** 2026-08-03
**Author:** Anonymous
**Source:** 02c_experiment_brief.md
**Prerequisite:** H-M1 (VALIDATED — OrbitVar(C1)=0.010333 vs C2=1.002e-14, C3=8.905e-08, both ≥4 OOM)

---

## 1. Executive Summary

H-M2 establishes the second causal link in the H-InvEnc-v1 chain: CISE encoder symmetry violation (OrbitVar=0.010333 from H-M1) propagates to LightGBM prediction space as measurable within-orbit prediction variance. The gate condition is MSE_perm^C1 / MSE_total^C1 ≥ 0.10 — at least 10% of total prediction error is attributable to within-orbit prediction variance induced by CISE's permutation sensitivity.

The experiment reuses all H-M1 infrastructure: same 100 models, same CISE (C1) embeddings, same K=50 functional S_16³ permutations. New components are (a) 5-fold CV LightGBM training on C1 embeddings, (b) MSE_perm orbit loop (novel measurement: `E_v[Var_π(ŷ(π·W))]`), and (c) MSE decomposition + orbit-averaged control. New code estimated < 120 lines.

---

## 2. Problem Statement

H-M1 demonstrated CISE OrbitVar=0.010333 — encoder-level within-orbit embedding variance exists and is causal. H-M2 asks: does this embedding variance **propagate to predictor-level noise** in a downstream LightGBM regressor? The causal argument requires (a) training LightGBM on original C1 embeddings, (b) measuring prediction variance across K=50 orbit permutations per model, (c) decomposing MSE into permutation variance and residual components, and (d) confirming the ratio ≥ 10%.

**Gate Condition (MUST_WORK):** MSE_perm^C1 / MSE_total^C1 ≥ 0.10

**Secondary Condition:** R²(C1) < R²(C0)=0.984 (CISE underperforms per-layer statistics baseline)

**Fail Action (EXPLORE):** If ratio < 0.01, LightGBM cancels permutation variance; H0 holds; redirect to Kendall's τ as primary metric.

---

## 3. Functional Requirements

### FR-1: Load H-M1 Prerequisite Infrastructure
- Load CISE (C1) embeddings from H-M1 results: `h-m1/results/` or recompute if not cached
  - Shape: `(100, embed_dim)` — precomputed, reuse directly
- Load K=50 permuted CISE embeddings from H-M1: `(100, 50, embed_dim)` — same permutation matrices used for OrbitVar
- Load test_accuracy labels from `data/dataset_cifar_small_hyp_rand.pt`
- Verify: CISE OrbitVar = 0.010333 (within 20% tolerance from cached value)
- **Reuse H-M1 infrastructure:** `data_loader.py`, `permutation.py`, `encoder_c1.py` via import from `../h-m1/code/`

### FR-2: 5-Fold Cross-Validation LightGBM on C1 Embeddings
- Fit LightGBM regressor with 5-fold CV (KFold, shuffle=True, random_state=42)
- Hyperparameters: `n_estimators=500, learning_rate=0.05, num_leaves=31, reg_alpha=0.0, reg_lambda=0.1, random_state=42`
- Collect out-of-fold predictions: `fold_preds` shape `(100,)`
- Compute MSE_total^C1 = `mean_squared_error(y_acc, fold_preds)`
- Compute R²(C1) = `r2_score(y_acc, fold_preds)`
- Compute Kendall's τ(C1) = `kendalltau(y_acc, fold_preds)`

### FR-3: MSE Permutation Decomposition (Novel Measurement)
- Train full-data LightGBM model on all 100 models (same hyperparameters, random_state=42)
- For each of K=50 permutations: `orbit_preds[:, k] = full_model.predict(permuted_X[:, k, :])`
  - `orbit_preds` shape: `(100, 50)` — 100 models × 50 orbit predictions
- Compute MSE_perm = `np.mean(np.var(orbit_preds, axis=1))`  [E_v[Var_k(ŷ(π_k·W_v))]]
- Compute MSE_res = MSE_total - MSE_perm
- Compute ratio = MSE_perm / MSE_total  [PRIMARY GATE: ≥ 0.10]

### FR-4: Permutation Validator Check (Pre-run)
- Run functional validator: `||f_v(x) - f_{g·v}(x)||_∞ ≤ 1e-6` (reuse H-M1/H-E1 validated code)
- If validator fails: ABORT with "ERROR: Permutation not functional — H-M1 result invalid"
- Report: PASS/FAIL with max_diff value

### FR-5: Mechanism Activation Verification
- Assert `orbit_preds.shape == (100, 50)` — shape validation
- Assert `np.mean(np.var(orbit_preds, axis=1)) > 1e-10` — non-zero orbit variance
- Assert `mse_perm > 0` — positive permutation MSE
- Assert `0.0 <= ratio <= 1.0` — valid ratio bounds
- Log: `"MSE_perm/MSE_total = {ratio:.4f} (gate: >= 0.10)"`

### FR-6: Orbit-Averaged Control (H0 Mitigation)
- Compute orbit-averaged predictions: `y_avg_pred = orbit_preds.mean(axis=1)`  [ŷ_avg(W) = (1/K)Σŷ(π_k·W)]
- Compute R²(C1_avg) = `r2_score(y_acc, y_avg_pred)`
- Compute Kendall's τ(C1_avg)
- Report: does orbit averaging recover performance vs C1? R²(C1_avg) vs R²(C1)

### FR-7: Baseline Comparison (C0 Reference)
- Compute C0 Ŵ_L features: per-layer (mean, var, 0/25/50/75/100 percentiles) → flat vector
  ```python
  def compute_wl_features(state_dict):
      features = []
      for name, param in state_dict.items():
          w = param.cpu().numpy().flatten()
          features.extend([np.mean(w), np.var(w)] + list(np.percentile(w, [0,25,50,75,100])))
      return np.array(features)
  ```
- C0 reference values (established, no retraining needed): R²(C0)=0.984, τ(C0)=0.915
- Report: R²(C1) vs R²(C0), τ(C1) vs τ(C0) — secondary success criterion

### FR-8: Gate Check Output and Results
- Print: `Gate MUST_WORK: MSE_perm/MSE_total >= 0.10: PASS/FAIL ({ratio:.4f})`
- Print: `Secondary: R²(C1)={r2_c1:.4f} < R²(C0)=0.984: PASS/FAIL`
- Print: MSE decomposition table: MSE_total, MSE_perm, MSE_res, ratio
- Print: Performance table: C0 (R², τ), C1 (R², τ), C1_avg (R², τ)
- Save results to `h-m2/results/mse_decomposition.json`
- Save summary to `h-m2/results/h_m2_summary.csv`
- Exit code 0 on PASS, 1 on FAIL

### FR-9: Visualization
- **Figure 1 (MANDATORY):** Bar chart — MSE_perm, MSE_res, MSE_total for C1; ratio line at 10% threshold
  - Title: "MSE Decomposition: Permutation Variance vs Residual Variance (CISE C1)"
- **Figure 2:** Per-model orbit variance histogram — `Var_k(ŷ(π_k·W_v))` across 100 models
- **Figure 3:** R² comparison bar chart — C0 (Ŵ_L), C1 (CISE), C1_avg (orbit-averaged)
- **Figure 4:** Scatter plot — OrbitVar(model_v) vs `Var_k(ŷ(π_k·W_v))` per model
- **Figure 5:** Orbit prediction fan plot — violin plot for 5 representative models (K=50 orbit predictions)
- Save all to `h-m2/figures/`

---

## 4. Data Specification

### Primary Dataset
| Field | Value |
|-------|-------|
| Name | ModelZooDataset CIFAR10-GS |
| Source | Zenodo DOI 10.5281/zenodo.6620868 |
| File | `dataset_cifar_small_hyp_rand.pt` |
| Size | 100 CNN models with CIFAR-10 test accuracy labels |
| Architecture | 3-conv (C=16 channels each), global avg pool, 1-dense (10 classes), 4,970 parameters |
| Access | **Reuse from H-M1** — already downloaded to `data/dataset_cifar_small_hyp_rand.pt` |
| Download | NOT required — reuse H-M1 data |

### Labels
| Field | Value |
|-------|-------|
| Target | test_accuracy (float, range ~0.3–0.7) |
| Task | Regression (predict CNN test accuracy from weights) |
| Split | 5-fold CV on all 100 models (80 train / 20 val per fold) |
| Random seed | 42 (KFold shuffle) |

### H-M1 Prerequisite Files (Load Directly)
| File | Source | Purpose |
|------|--------|---------|
| `h-m1/results/orbit_var_ratios.json` | H-M1 output | C1 embeddings (100, embed_dim) + permuted embeddings (100, 50, embed_dim) |
| `data/dataset_cifar_small_hyp_rand.pt` | H-M1 download | 100 CNN models, test_accuracy labels |

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed = 42 for KFold and all LightGBM models
- Deterministic encoder forward passes (reuse H-M1 permutation matrices)

### NFR-2: Numerical Precision
- MSE computations in float64
- Orbit variance: `np.var(..., axis=1)` applied per-model over K=50 permutations

### NFR-3: Performance
- Full experiment (5-fold CV + orbit loop): ~5-15 min CPU (100 models × 50 perms × LightGBM inference)
- Memory: < 2 GB (embeddings + orbit predictions fit easily)

### NFR-4: Code Quality
- Single entry point: `python run_experiment.py`
- Imports from H-M1 code directory (`../h-m1/code/`) — no code duplication
- All 100 models must complete before gate check

### NFR-5: Permutation Validity
- Functional permutation validator MUST pass before any MSE measurement
- Abort immediately if validator fails (do not report partial results)

---

## 6. Success Criteria

| Criterion | Target | Gate |
|-----------|--------|------|
| MSE_perm / MSE_total ≥ 0.10 | ≥ 10% of prediction error is permutation variance | MUST_WORK |
| R²(C1) < R²(C0)=0.984 | CISE underperforms Ŵ_L baseline | Secondary |
| Permutation validator PASS | Max diff ≤ 1e-6 | Pre-condition |
| orbit_preds shape | (100, 50) | Mechanism check |
| Non-zero orbit variance | mean(var) > 1e-10 | Mechanism check |
| R²(C1_avg) > R²(C1) | Orbit averaging recovers performance | Exploratory |

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.12.0        # already installed (H-M1)
numpy>=1.21.0        # already installed (H-M1)
scipy>=1.7.0         # already installed (H-M1) — kendalltau
matplotlib>=3.5.0    # already installed (H-M1)
lightgbm>=3.0.0      # NEW — LightGBM regressor
scikit-learn>=1.0.0  # NEW — KFold, mean_squared_error, r2_score
```

### 7.2 H-M1 Code Reuse (INCREMENTAL)
| Module | Import Path | What's Reused |
|--------|-------------|---------------|
| data_loader | `../h-m1/code/data_loader` | load_dataset, reconstruct_state_dict |
| permutation | `../h-m1/code/permutation` | sample_functional_permutations, apply_permutation |
| encoder_c1 | `../h-m1/code/encoder_c1` | CISEEncoder (if re-encoding needed) |

### 7.3 Pre-established Baselines (BUILD_ON)
- CISE (C1) embeddings: (100, embed_dim) — precomputed in H-M1, reuse directly
- K=50 permuted C1 embeddings: (100, 50, embed_dim) — same permutation matrices as H-M1 OrbitVar
- C0 reference: R²(C0)=0.984, τ(C0)=0.915 (Unterthiner et al., 2020; no retraining needed)

### 7.4 External Reference Repositories
| Repository | Purpose |
|-----------|---------|
| google-research/dnn_predict_accuracy | C0 STATNN baseline architecture reference |
| ModelZoos/ModelZooDataset | Dataset loading code (dataset_base.py) |
| lightgbm-org/LightGBM | 5-fold CV API reference |

---

## 8. Out of Scope

- Re-implementing H-M1 encoders (C2, C3) or OrbitVar measurement
- Hyperparameter search for LightGBM (use fixed defaults from Unterthiner et al.)
- Re-downloading ModelZooDataset (already available from H-M1)
- GPU optimization
- New encoder architectures beyond C1/C0
- Bootstrap bias-variance decomposition (MSE_perm uses orbit permutations, not bootstrap)

---

## 9. Assumptions and Risks

| Assumption | Risk | Mitigation |
|------------|------|------------|
| H-M1 C1 embeddings + permuted embeddings cached | Low | H-M1 VALIDATED; if not cached, recompute with same config |
| Functional permutation validator passes | Very Low | Validated in H-E1 + H-M1; abort if fails |
| LightGBM available (version ≥ 3.0) | Low | Install via pip; sklearn API stable |
| MSE_perm/MSE_total ≥ 0.10 | Medium | OrbitVar=0.010333 gives theoretical expectation 5-30%; fail action defined |
| N=100 sufficient for 5-fold CV | Accepted | Standard for model zoo prediction tasks (Unterthiner et al. use similar scale) |

---

*stepsCompleted: [executive_summary, problem_statement, functional_requirements, data_specification, nfr, success_criteria, dependencies]*
