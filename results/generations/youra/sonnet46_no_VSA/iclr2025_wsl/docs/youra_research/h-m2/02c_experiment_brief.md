# Experiment Design: h-m2

**Date:** 2026-08-03
**Author:** Anonymous
**Hypothesis Statement:** Under 5-fold CV LightGBM on CISE (C1) embeddings from ModelZooDataset CIFAR10-GS, CISE OrbitVar=0.010333 propagates to prediction space as MSE_perm^C1 ≥ 10% of MSE_total^C1, because permutation-sensitive encoder representations create within-orbit prediction variance that LightGBM cannot fully cancel.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates causal propagation of encoder symmetry noise to prediction-level variance.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 VALIDATED (OrbitVar(C1)=0.010333 vs C2=1.002e-14, 12.0 OOM; Wilcoxon p=1.95e-18)
**Gate Status:** MUST_WORK — MSE_perm^C1 / MSE_total^C1 ≥ 0.10

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM (Causal Step 2)
- **Prerequisites:** H-M1 (VALIDATED)

### Gate Condition
MUST_WORK: MSE_perm^C1 / MSE_total^C1 ≥ 0.10 (≥10% of total prediction error attributable to within-orbit prediction variance)

Secondary: R²(C1) < R²(C0)=0.984 (CISE underperforms the Ŵ_L per-layer statistics baseline)

Fail Action: EXPLORE — if MSE_perm < 1% of MSE_total, LightGBM cancels permutation variance; H0 holds; redirect to Kendall's τ as primary metric; still report MSE decomposition.

---

## Continuation Context

H-M1 established Causal Step 1: encoder architectural design causally determines OrbitVar (CISE=0.010333 vs DeepSets C2<1e-14, NFN C3<1e-7, both ≥4 OOM). H-M2 tests Causal Step 2: does encoder-level symmetry violation propagate to predictor-level noise?

The theoretical basis is the bias-variance decomposition applied over permutation orbits:
```
E[(y - ŷ)²] = MSE_res + MSE_perm
```
where MSE_perm = E_v[Var_π(ŷ(π·W))] captures the prediction variance induced by permutation sensitivity of CISE embeddings.

### Previous Hypothesis Results (H-M1)
- OrbitVar(C1/CISE) = 0.010333 (established; reuse for C1 baseline comparison)
- OrbitVar(C2/DeepSets) = 1.002e-14 (12.0 OOM below C1)
- OrbitVar(C3/NFN) = 8.905e-08 (5.1 OOM below C1)
- Anti-confound gate PASSED: 100% model coverage (100/100)

**Reuse from H-M1:**
- Same 100 models from ModelZooDataset CIFAR10-GS
- Same functional S_16³ permutation code (K=50 permutations per model, validated)
- CISE (C1) embeddings already computed — reuse directly
- No re-implementation of permutation infrastructure needed

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Archon KB result:** No relevant past implementation cases found for this domain. The Archon KB (source id 8b1c7f40739544a6) contains only diffusion model / image generation content (Stable Diffusion, ControlNet, LCM). All 4 queries (LightGBM permutation invariance bias-variance decomposition; MSE decomposition orbit variance weight encoder; ModelZooDataset CIFAR10 weight encoder; LightGBM CV MSE orbit variance PyTorch) returned low-similarity (0.33–0.51) unrelated results.

**Implication:** Experiment design draws entirely from primary literature and official repositories (Exa findings below).

### Archon Code Examples

No relevant code examples found in Archon KB for this domain. See Exa GitHub findings below.

### Exa GitHub Implementations

**Query 1: Unterthiner ModelZooDataset Official Implementation**

**Repository 1: google-research/dnn_predict_accuracy** (Unterthiner et al., 2020)
- **URL:** https://github.com/google-research/google-research/tree/master/dnn_predict_accuracy
- **Relevance:** ⭐⭐⭐ HIGHEST PRIORITY — official implementation of "Predicting Neural Network Accuracy from Weights" (the Ŵ_L baseline, R²=0.984, Kendall's τ=0.915). Establishes the STATNN baseline we compare C1 against.
- **Dataset:** Small CNN Zoo dataset (same architecture: 3 conv layers, 16 hidden units, global avg pool, 10-class dense, 4970 parameters total). Cifar10 subset: 270,000 samples (30k models × 9 checkpoints).
- **Architecture:** STATNN = per-layer mean/variance/quantiles → MLP predictor. This is C0 (Ŵ_L baseline).
- **Key insight:** They use flat weight vectors from 9 training checkpoints; we use end-of-training weights only (like ModelZooDataset CIFAR10-GS).
- **Loading:** `metrics.csv.gz` contains test_accuracy labels; `layout.csv` maps weight columns to layers.
- **Used For:** Establishes C0 R²=0.984 reference performance we measure C1 against.

**Repository 2: ModelZoos/ModelZooDataset** (Schürholt et al., NeurIPS 2022)
- **URL:** https://github.com/ModelZoos/ModelZooDataset (⭐ 60)
- **Relevance:** ⭐⭐⭐ HIGHEST PRIORITY — official dataset repository. Contains the exact CIFAR10-GS `.pt` file at Zenodo DOI 10.5281/zenodo.6620868.
- **Loading code:** `code/checkpoints_to_datasets/dataset_base.py` — custom PyTorch Dataset class that loads `.pt` files, vectorizes weights, filters faulty models.
- **Key architecture info:** CNN-small: 3 conv layers × 16 channels + 1 dense, 4970 parameters total. This defines the S_16³ permutation group.
- **Train/val/test splits:** [70, 15, 15] as per SANE paper; standard practice for this zoo.
- **Used For:** Loading the 100 CIFAR10-GS models; getting test_accuracy labels for LightGBM target.

**Query 2: LightGBM Cross-Validation MSE**

**Repository 3: lightgbm-org/LightGBM** (Microsoft, ⭐ 18K)
- **URL:** https://github.com/lightgbm-org/LightGBM
- **Relevance:** ⭐⭐ MEDIUM — official LightGBM sklearn API
- **Key API:** `lightgbm.cv(params, train_set, nfold=5, seed=0, return_cvbooster=True)` — note: uses Dataset.subset() internally for consistent bin boundaries across folds.
- **Key code pattern for 5-fold CV + MSE:**
  ```python
  from sklearn.model_selection import KFold
  from sklearn.metrics import mean_squared_error, r2_score
  import lightgbm as lgb
  
  kf = KFold(n_splits=5, shuffle=True, random_state=42)
  fold_mses = []
  for train_idx, val_idx in kf.split(X):
      X_tr, X_val = X[train_idx], X[val_idx]
      y_tr, y_val = y[train_idx], y[val_idx]
      model = lgb.LGBMRegressor(n_estimators=500, learning_rate=0.05, num_leaves=31)
      model.fit(X_tr, y_tr)
      preds = model.predict(X_val)
      fold_mses.append(mean_squared_error(y_val, preds))
  mse_total = np.mean(fold_mses)
  ```
- **Used For:** 5-fold CV training protocol; MSE_total^C1 measurement.

**Query 3: Bias-Variance Decomposition (mlxtend)**

**Repository 4: rasbt/mlxtend** (bias_variance_decomp.py)
- **URL:** https://github.com/rasbt/mlxtend/blob/master/mlxtend/evaluate/bias_variance_decomp.py
- **Relevance:** ⭐ Reference — standard bias-variance decomposition using bootstrap rounds. However, our MSE_perm is NOT the standard bias-variance decomposition; it is the within-orbit prediction variance: `MSE_perm = E_v[Var_π(ŷ(π_k·W_v))]`. This is a novel measurement not in existing libraries.
- **Pattern derived:** `all_pred[i] = model.predict(X_permuted)` across K orbits → compute variance per model → average.
- **Used For:** Structural pattern for per-model orbit variance computation.

**Query 4: NFN / DWSNet / Permutation Equivariant Neural Functionals**

**Repository 5: AllanYangZhou/nfn** (Zhou et al., NeurIPS 2023)
- **URL:** https://proceedings.neurips.cc/paper_files/paper/2023/file/4e9d8aeeab6120c3c83ccf95d4c211d3-Paper-Conference.pdf
- **Relevance:** ⭐⭐ Reference — establishes that permutation equivariant NFN achieves Kendall's τ=0.934 on CIFAR10-GS. Used as secondary metric anchor if R² ceiling is reached.
- **Used For:** Expected Kendall's τ reference for secondary success criterion.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

No paper specifically implements MSE_perm orbit decomposition — this is a NOVEL measurement. Implementation must be built from scratch combining:
1. Existing CISE embedding computation (from H-M1 code)
2. Existing functional permutation application (from H-M1 code, validated)
3. Standard LightGBM 5-fold CV (lgb.LGBMRegressor + sklearn KFold)
4. Novel per-model orbit prediction loop for MSE_perm

**Recommended Implementation Path:**
- Primary: Reuse H-M1 codebase (CISE embeddings + permutation infrastructure) + add LightGBM CV + MSE_perm orbit loop
- Fallback: If H-M1 code unavailable, implement CISE encoder from scratch using sinusoidal PE on flattened per-channel weight vectors
- Justification: H-M1 validated permutation correctness (functional validator passed). Zero reason to reimplement validated infrastructure.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results and H-M1 codebase is sufficiently clear. No complex >100-line unfamiliar architecture patterns requiring Serena semantic analysis. The novel MSE_perm loop is a straightforward extension of H-M1's OrbitVar loop.

---

## Experiment Specification

### Dataset

**Name:** ModelZooDataset CIFAR10-GS (Schürholt et al., NeurIPS 2022)
**Type:** standard (real dataset, pre-existing)
**Source:** Zenodo DOI 10.5281/zenodo.6620868
**File:** `dataset_cifar_small_hyp_rand.pt` (preprocessed PyTorch format)

**Statistics:**
- Total models: ~100 (CIFAR10 small CNN zoo, same 100 used in H-M1)
- Architecture: 3 conv layers (C=16 channels each) + global avg pool + dense (10 classes)
- Total parameters per model: 4,970
- Labels: test_accuracy (float, range ~0.3–0.7 for this zoo)
- No train/test split needed for model samples — use all 100 for 5-fold CV on LightGBM

**Split for LightGBM training:**
- 5-fold CV: 80 models train / 20 models validation per fold
- Random seed: 42 (fixed)
- No held-out test set (100 models is small; CV MSE is the primary metric)

**Preprocessing (model weights → CISE embeddings):**
- Reuse precomputed C1 (CISE) embeddings from H-M1 (shape: [100, embedding_dim])
- CISE: sinusoidal positional encoding applied per channel position in each conv layer
- If H-M1 embeddings not cached: recompute using same CISE encoder with same config

**Loading Information** (for Phase 4 download):
- Method: custom (ModelZooDataset PyTorch Dataset class)
- Identifier: `zenodo:10.5281/zenodo.6620868` → `dataset_cifar_small_hyp_rand.pt`
- Code:
  ```python
  import torch
  zoo = torch.load("data/dataset_cifar_small_hyp_rand.pt")
  # zoo contains: weights (list of state_dicts or vectorized), test_accuracy labels
  # Use code/checkpoints_to_datasets/dataset_base.py from ModelZoos/ModelZooDataset
  ```

**Synthetic data policy:** REAL dataset (standard). No synthetic data used.

### Models

#### Baseline Model

**Architecture:** C0 — Ŵ_L per-layer statistics (STATNN, Unterthiner et al., 2020)

**Description:**
- Compute per-layer statistics (mean, variance, 0/25/50/75/100 percentiles) for each weight tensor
- Concatenate all statistics into a flat feature vector
- Feed into LightGBM regressor
- R²(C0) = 0.984, Kendall's τ(C0) = 0.915 (established; use as reference, not re-trained)

**Note:** C0 result from 02b_verification_plan.md Section 1.4 is treated as a fixed reference baseline. We train LightGBM on C1 (CISE) embeddings and compare R²(C1) against R²(C0)=0.984.

**Loading Information** (for Phase 4):
- Method: custom (implement per-layer statistics function)
- Identifier: n/a (no pretrained model; feature extractor only)
- Code:
  ```python
  def compute_wl_features(state_dict):
      """Ŵ_L: per-layer mean, var, 0/25/50/75/100 percentiles → flat vector"""
      features = []
      for name, param in state_dict.items():
          w = param.cpu().numpy().flatten()
          features.extend([np.mean(w), np.var(w)] + list(np.percentile(w, [0,25,50,75,100])))
      return np.array(features)
  ```

#### Proposed Model

**Architecture:** C1 — CISE encoder (non-invariant; sinusoidal PE) → LightGBM regressor

**Description:**
CISE encodes each conv layer's weight tensor by applying sinusoidal positional encoding to each channel position, making the embedding sensitive to channel order. The resulting embeddings (OrbitVar=0.010333 from H-M1) are fed to a 5-fold CV LightGBM regressor.

**The experiment measures whether this OrbitVar propagates to prediction variance (MSE_perm).**

**Core Mechanism Implementation:**

```python
# Core Mechanism: MSE Permutation Decomposition for CISE (C1) Embeddings
# Based on: H-M1 validated permutation infrastructure + LightGBM CV
# Novel measurement: within-orbit prediction variance propagation

import numpy as np
import lightgbm as lgb
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error, r2_score

def compute_mse_perm_decomposition(
    X_cise,        # (N_models, embed_dim) CISE embeddings
    y_acc,         # (N_models,) test accuracies
    permuted_X,    # (N_models, K, embed_dim) K=50 orbit embeddings per model
    n_splits=5,
    random_state=42,
    n_estimators=500,
    learning_rate=0.05,
    num_leaves=31
):
    """
    Args:
        X_cise: (100, embed_dim) baseline CISE embeddings
        y_acc: (100,) test accuracy labels
        permuted_X: (100, 50, embed_dim) CISE embeddings under K=50 permutations
    Returns:
        mse_total, mse_perm, mse_res, ratio, r2_c1
    """
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    
    fold_preds = np.zeros(len(y_acc))  # out-of-fold predictions on original X
    
    for train_idx, val_idx in kf.split(X_cise):
        model = lgb.LGBMRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            num_leaves=num_leaves,
            random_state=random_state
        )
        model.fit(X_cise[train_idx], y_acc[train_idx])
        fold_preds[val_idx] = model.predict(X_cise[val_idx])
    
    # MSE_total: average squared error on original embeddings
    mse_total = mean_squared_error(y_acc, fold_preds)
    r2_c1 = r2_score(y_acc, fold_preds)
    
    # MSE_perm: train on original, predict on K=50 orbit permutations per model
    # Retrain single model on full data for orbit variance measurement
    full_model = lgb.LGBMRegressor(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        num_leaves=num_leaves,
        random_state=random_state
    )
    full_model.fit(X_cise, y_acc)
    
    # For each model v, compute variance over K orbit predictions
    orbit_preds = np.zeros((len(y_acc), permuted_X.shape[1]))  # (100, 50)
    for k in range(permuted_X.shape[1]):
        orbit_preds[:, k] = full_model.predict(permuted_X[:, k, :])
    
    # MSE_perm = E_v[Var_k(ŷ(π_k · W_v))]
    mse_perm = np.mean(np.var(orbit_preds, axis=1))
    
    # MSE_res = MSE_total - MSE_perm
    mse_res = mse_total - mse_perm
    ratio = mse_perm / mse_total  # PRIMARY GATE: must be >= 0.10
    
    return {
        "mse_total": mse_total,
        "mse_perm": mse_perm,
        "mse_res": mse_res,
        "ratio": ratio,        # Gate: >= 0.10
        "r2_c1": r2_c1         # Secondary: < 0.984
    }

# Orbit-averaged implicit invariance control:
def compute_orbit_avg_baseline(full_model, permuted_X, y_acc):
    """ŷ_avg(W) = (1/K) Σ ŷ(π_k·W) — implicit invariance by averaging"""
    orbit_preds = np.array([
        full_model.predict(permuted_X[:, k, :])
        for k in range(permuted_X.shape[1])
    ])  # (K, N)
    y_avg_pred = orbit_preds.mean(axis=0)
    return r2_score(y_acc, y_avg_pred)
```

### Training Protocol

**Reuse from H-M1 validation:** No hyperparameter search needed. Use standard LightGBM defaults matching Unterthiner et al. (2020) STATNN setup.

**Optimizer (LightGBM):**
- Algorithm: Gradient Boosting Decision Tree (`boosting_type='gbdt'`)
- n_estimators: 500 (enough for small dataset; early stopping via CV)
- learning_rate: 0.05
  - **Source:** Standard for small tabular datasets (LightGBM docs; Unterthiner et al. use similar)
- num_leaves: 31 (default; appropriate for N=80 training samples)
- reg_alpha: 0.0, reg_lambda: 0.1 (light L2 regularization)
- **Source:** LightGBM official docs + Unterthiner et al. 2020 (they use GBM with default settings)

**Cross-Validation:**
- 5-fold CV, KFold with shuffle=True, random_state=42
- Metric: MSE (regression), R² computed post-hoc
- **Source:** Phase 2B H-M2 protocol (5-fold CV, identical HP search space and seeds)

**Seeds:** 1 fixed seed (42). Per EXISTENCE/MECHANISM PoC spec — no multi-seed required.

**MSE Decomposition Protocol:**
- K=50 orbit samples per model (same as H-M1 OrbitVar measurement)
- Use full-data trained LightGBM model (no fold split) for orbit variance measurement
  - Rationale: orbit variance is a property of the trained model, not generalization; full-data model gives stable variance estimate
- **Source:** Phase 2B H-M2 verification protocol (K=50, same permutation code)

**Orbit-averaged control:**
- Compute ŷ_avg(W) = (1/K) Σ ŷ(π_k·W) as implicit-invariance control R²
- **Source:** Phase 2B Section 4.2 Risk R2 mitigation

### Evaluation

**Primary Metric:**
- MSE_perm^C1 / MSE_total^C1 — ratio of within-orbit prediction variance to total prediction error
- **Gate:** ≥ 0.10 (10%)
- **Expected range:** 5–30% based on OrbitVar=0.010333 and typical LightGBM sensitivity

**Secondary Metrics:**
- R²(C1) vs R²(C0)=0.984 — CISE underperforms per-layer statistics baseline
- Kendall's τ(C1) vs τ(C0)=0.915 — rank correlation (backup if R² ceiling effect)
- R²(C1_avg) — orbit-averaged implicit invariance control (test H0 mitigation)

**Success Criteria:**
- Primary: MSE_perm^C1 / MSE_total^C1 ≥ 0.10
- Secondary: R²(C1) < R²(C0)=0.984 (CISE underperforms Ŵ_L)
- Exploratory: R²(C1_avg) > R²(C1) (orbit averaging recovers some performance)

**Expected Baseline Performance (from research):**
- R²(C0/Ŵ_L) = 0.984, Kendall's τ(C0) = 0.915 (Unterthiner et al., 2020)
- NFN R²/τ: τ=0.934 (Zhou et al., 2023)
- R²(C1/CISE) expected: < 0.984 (hypothesis predicts underperformance)
- MSE_total^C1 expected: > MSE_total^C0 if hypothesis holds

**Metrics Loading Information:**
- Task Type: regression (predict CNN test accuracy from weights)
- Library: sklearn.metrics
- Code:
  ```python
  from sklearn.metrics import mean_squared_error, r2_score
  from scipy.stats import kendalltau
  mse = mean_squared_error(y_true, y_pred)
  r2 = r2_score(y_true, y_pred)
  tau, p = kendalltau(y_true, y_pred)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart with 4 bars: MSE_perm, MSE_res, MSE_total for C1; plus ratio line at 10% threshold. Title: "MSE Decomposition: Permutation Variance vs Residual Variance (CISE C1)"

#### Additional Figures (LLM Autonomous)
Based on the MECHANISM hypothesis type and MSE decomposition measurements:

1. **Per-model orbit variance distribution:** Histogram of Var_k(ŷ(π_k·W_v)) across 100 models — shows distribution of permutation sensitivity across the zoo
2. **R² comparison bar chart:** C0 (Ŵ_L), C1 (CISE), C1_avg (orbit-averaged) — shows performance gap
3. **Scatter plot:** OrbitVar(model_v) vs Var_k(ŷ(π_k·W_v)) per model — visual test of propagation
4. **Orbit prediction fan plot:** For 5 representative models, show K=50 orbit predictions as violin plot — illustrates within-orbit prediction spread

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | CISE OrbitVar=0.010333 > 0 (confirmed by H-M1); non-zero within-orbit embedding variance exists | TRUE (H-M1 VALIDATED) |
| Mechanism Isolatable | Can run LightGBM on original C1 embeddings vs K=50 permuted C1 embeddings independently | TRUE |
| Baseline Measurable | C0 R²=0.984 established; C1 5-fold CV MSE measurable independently | TRUE |

### Architecture Compatibility Check

**Required Components:**
- CISE encoder (C1): must produce embeddings with OrbitVar > 0 under S_16³ permutations (verified in H-M1)
- Functional permutation implementation: must satisfy ||f_v(x) - f_{g·v}(x)||_∞ ≤ 1e-6 (validated in H-E1)
- LightGBM regressor: version ≥ 3.0, scikit-learn API
- 100 models from ModelZooDataset CIFAR10-GS

**Incompatible scenarios:**
- C2/C3 (invariant encoders) cannot be used as C1 substitute — they have OrbitVar ≈ 0 by design
- Independent (non-coupled) permutations would invalidate the functional S_16³ group structure

> ⚠️ If permutation validator fails, Phase 4 MUST abort with: "ERROR: Permutation not functional — H-M1 result invalid"

---

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"MSE_perm/MSE_total = {ratio:.4f} (gate: >= 0.10)"` | evaluate.py:main() |
| Tensor Shape | `orbit_preds.shape == (100, 50)` — 100 models × 50 orbit predictions | compute_mse_perm:line ~50 |
| Metric Delta | `var(orbit_preds, axis=1).mean() > 0` — non-zero per-model orbit variance | compute_mse_perm:return |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mse_perm_mechanism(orbit_preds, mse_total, mse_perm, ratio):
    """Verify MSE_perm measurement is valid and mechanism is active."""
    indicators = {
        "orbit_preds_shape_valid": orbit_preds.shape == (100, 50),
        "nonzero_orbit_variance": np.mean(np.var(orbit_preds, axis=1)) > 1e-10,
        "mse_perm_positive": mse_perm > 0,
        "ratio_computed": 0.0 <= ratio <= 1.0,
        "gate_result": ratio >= 0.10
    }
    all_valid = all(v for k, v in indicators.items() if k != "gate_result")
    return all_valid, indicators
```

---

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Zero orbit variance | `np.var(orbit_preds, axis=1).mean() < 1e-10` | FAIL: LightGBM invariant to CISE channel order; debug embedding |
| MSE_perm/MSE_total < 0.01 | ratio < 0.01 | EXPLORE: H0 supported; LightGBM cancels noise; switch to Kendall's τ |
| MSE_perm/MSE_total ∈ [0.01, 0.10) | ratio between 0.01 and 0.10 | PARTIAL: some propagation but below gate; report finding |
| Permutation validator fail | `||f_v(x) - f_{g·v}(x)||_∞ > 1e-6` | ABORT: functional permutation requirement violated |

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | Orbit variance > 0 | `np.var(orbit_preds, axis=1).mean() > 1e-10` |
| Effect Measurable | MSE_perm > 0 | Direct computation |
| Hypothesis Supported | MSE_perm / MSE_total ≥ 0.10 | `ratio >= 0.10` |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `MSE_perm^C1 / MSE_total^C1 ≥ 0.10`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant sources found. Archon KB contains only diffusion model content unrelated to this domain.

---

### B. GitHub Implementations (Exa)

**Repository 1: google-research/dnn_predict_accuracy** (Unterthiner et al., 2020)
- **URL:** https://github.com/google-research/google-research/tree/master/dnn_predict_accuracy
- **Query Used:** "Unterthiner ModelZooDataset CIFAR10 LightGBM weight encoder prediction model zoo GitHub"
- **Relevance:** Official implementation of STATNN (C0 Ŵ_L baseline). Establishes R²=0.984, τ=0.915 reference.
- **Key insight:** CNN architecture: 3 conv layers, 16 units, global avg pool, 10-class dense, 4970 params. Flat weight vector features per checkpoint.
- **Used For:** C0 baseline reference performance; understanding feature extraction pipeline

**Repository 2: ModelZoos/ModelZooDataset** (Schürholt et al., NeurIPS 2022)
- **URL:** https://github.com/ModelZoos/ModelZooDataset
- **Query Used:** "ModelZooDataset zenodo 6620869 dataset_cifar_small_hyp_rand.pt loading PyTorch CIFAR10-GS small CNN zoo"
- **Relevance:** Official dataset repository. CIFAR10-GS zoo at DOI 10.5281/zenodo.6620868.
- **Key code:** `code/checkpoints_to_datasets/dataset_base.py` — PyTorch Dataset for .pt zoo files
- **Used For:** Dataset loading specification; model architecture confirmation (CNN-small, 4970 params)

**Repository 3: lightgbm-org/LightGBM** (Microsoft)
- **URL:** https://github.com/lightgbm-org/LightGBM
- **Query Used:** "LightGBM cross-validation MSE orbit variance prediction PyTorch"
- **Key code extracted:**
  ```python
  # 5-fold CV using sklearn API (consistent with Dataset.subset() bin boundaries)
  from sklearn.model_selection import KFold
  kf = KFold(n_splits=5, shuffle=True, random_state=42)
  for train_idx, val_idx in kf.split(X):
      model = lgb.LGBMRegressor(n_estimators=500, learning_rate=0.05)
      model.fit(X[train_idx], y[train_idx])
      preds = model.predict(X[val_idx])
  ```
- **Used For:** 5-fold CV training protocol; LGBMRegressor hyperparameter defaults

**Repository 4: rasbt/mlxtend** (bias_variance_decomp.py)
- **URL:** https://github.com/rasbt/mlxtend/blob/master/mlxtend/evaluate/bias_variance_decomp.py
- **Relevance:** Standard bias-variance decomposition pattern (bootstrap). Our MSE_perm is NOT bootstrap-based — it uses functional permutation orbits instead.
- **Key pattern adapted:**
  ```python
  # mlxtend pattern: collect predictions across perturbations
  all_pred[i] = estimator.predict(X_perturbed)
  # Our adaptation: perturbations = functional orbit permutations
  orbit_preds[:, k] = full_model.predict(permuted_X[:, k, :])
  ```
- **Used For:** Structural pattern for per-model variance computation in MSE_perm loop

**Repository 5: AllanYangZhou/nfn** (Zhou et al., NeurIPS 2023)
- **URL:** https://proceedings.neurips.cc/paper_files/paper/2023/file/4e9d8aeeab6120c3c83ccf95d4c211d3-Paper-Conference.pdf
- **Relevance:** NFN achieves Kendall's τ=0.934 on same CIFAR10-GS zoo. Provides secondary metric anchor.
- **Used For:** Expected Kendall's τ reference for secondary performance comparison

---

### C. Code Analysis (Serena)

Serena analysis not performed — code from search results and H-M1 validated infrastructure is sufficiently clear. The novel MSE_perm computation is a direct extension of the OrbitVar loop from H-M1 with LightGBM predictions substituted for encoder outputs.

---

### D. Previous Hypothesis Context

**Source:** H-M1 Phase 4 Validation Report (in progress)
- **Reused Components:**
  - CISE (C1) embeddings for all 100 models — precomputed, reuse directly
  - Functional S_16³ permutation implementation — validated (||f_v(x) - f_{g·v}(x)||_∞ ≤ 1e-6 confirmed)
  - 50 permutations per model — same K value used for OrbitVar; reuse same permutation matrices
- **Why Reused:** Enables causal chain continuity — same 100 models, same permutations, same CISE embeddings as H-M1. Only new component is LightGBM training + MSE_perm decomposition.

---

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: ModelZooDataset CIFAR10-GS | GitHub (official) | Repo B.2 (ModelZoos/ModelZooDataset) |
| Dataset DOI and file path | GitHub/Zenodo | Repo B.2 + DOI 10.5281/zenodo.6620868 |
| C0 baseline R²=0.984 | GitHub (official) | Repo B.1 (google-research/dnn_predict_accuracy) |
| C0 baseline τ=0.915 | Paper | Unterthiner et al., 2020 (arXiv:2002.11448) |
| NFN τ=0.934 | Paper | Zhou et al., 2023 (NeurIPS 2023) |
| CISE (C1) OrbitVar=0.010333 | Previous validation | H-M1 Phase 4 Validation Report |
| Functional permutation validator | Previous validation | H-E1 + H-M1 infrastructure |
| MSE decomposition formula | Phase 2B | 02b_verification_plan.md §2.2 H-M2 |
| LightGBM 5-fold CV protocol | GitHub (official) | Repo B.3 (lightgbm-org/LightGBM) |
| MSE_perm orbit loop pattern | GitHub | Repo B.4 (rasbt/mlxtend, adapted) |
| K=50 orbit samples | Phase 2B | 02b_verification_plan.md §2.2 H-M2 |
| LightGBM hyperparameters | Official docs + paper | LightGBM docs; Unterthiner et al. 2020 |
| Success threshold ≥10% | Phase 2B | 02b_verification_plan.md §2.2 H-M2 |
| Kendall's τ backup metric | Phase 2B | 02b_verification_plan.md §3.2 Gate Summary |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-03

### Workflow History for This Hypothesis
- 2026-08-03T00:00:00Z: Phase 2C experiment design IN_PROGRESS
- 2026-08-03: All 8 steps completed (UNATTENDED mode)

---

*MCP Tools Used: Archon (4 KB queries + 1 code query — no relevant results), Exa (5 GitHub/web queries — 5 repositories found)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
