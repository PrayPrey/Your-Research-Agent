# Architecture: H-M2
# Causal Propagation — CISE OrbitVar → LightGBM Prediction Variance

**Hypothesis ID:** H-M2
**Type:** MECHANISM (Causal Step 2)
**Date:** 2026-08-03
**Prerequisite:** H-M1 (VALIDATED)

Applied: orbit-variance-propagation pattern (MSE decomposition via permutation orbits)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**: H-M1 has flat code structure (no subdirs). Key functions: `load_dataset` returns `(models, accs)`, `sample_functional_permutations` returns list of per-layer index tensors, `CISEEncoder.forward(state_dict)` returns `(embed_dim,)` tensor, `compute_orbit_var_all_models` returns `(per_model_vars, mean_orbitvar, max_orbitvar)`. Results saved to `results/orbit_var_results.json` relative to run location.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_dataset | `sys.path.insert + from data_loader import load_dataset` | `h-m1/code/data_loader.py` |
| sample_functional_permutations | `from permutation import sample_functional_permutations` | `h-m1/code/permutation.py` |
| apply_permutation | `from permutation import apply_permutation` | `h-m1/code/permutation.py` |
| audit_functional_equivalence | `from permutation import audit_functional_equivalence` | `h-m1/code/permutation.py` |
| CISEEncoder | `from encoder_c1 import CISEEncoder, build_c1_encoder` | `h-m1/code/encoder_c1.py` |
| CHANNELS_PER_LAYER | `from data_loader import CHANNELS_PER_LAYER` | `h-m1/code/data_loader.py` |

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation)

**Import bootstrap** (H-M1 has no package `__init__`; use sys.path):
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'h-m1', 'code'))
```

---

## File Structure

```
h-m2/code/
├── run_experiment.py       # single entry point
├── embeddings.py           # load/recompute C1 embeddings + permuted embeddings
├── lgbm_trainer.py         # 5-fold CV + full-data model + MSE_perm decomposition
├── evaluate.py             # gate check, metrics, C0 baseline, results saving
└── visualize.py            # 5 figures
```

```
h-m2/results/              # auto-created
h-m2/figures/              # auto-created
```

---

## Module Definitions

### embeddings (`h-m2/code/embeddings.py`)

**Dependencies**: H-M1 data_loader, H-M1 encoder_c1, H-M1 permutation, torch, numpy

```python
H1_RESULTS_PATH: str  # default: h-m1/results/orbit_var_results.json
ORBIT_VAR_EXPECTED: float = 0.010333
ORBIT_VAR_TOL: float = 0.20  # 20% tolerance

def load_or_compute_embeddings(
    pt_path: str,
    h1_results_path: str = H1_RESULTS_PATH,
    n_models: int = 100,
    K: int = 50,
    embed_dim: int = 64,
    seed: int = 1,
) -> tuple:
    """
    Returns (X_cise, permuted_X, y_acc, perm_specs, orbit_var_h1).
    X_cise: (N, embed_dim) ndarray float32
    permuted_X: (N, K, embed_dim) ndarray float32
    y_acc: (N,) ndarray float64
    perm_specs: list[list[Tensor]] — K permutation specs (reuse or regenerate)
    orbit_var_h1: float — H-M1 OrbitVar for verification
    Loads from h1_results if cached; recomputes via CISEEncoder if not.
    """
    ...

def verify_orbit_var(orbit_var: float) -> None:
    """Assert orbit_var within 20% of ORBIT_VAR_EXPECTED. Raises RuntimeError if not."""
    ...
```

---

### lgbm_trainer (`h-m2/code/lgbm_trainer.py`)

**Dependencies**: lightgbm, sklearn, numpy

```python
LGBM_PARAMS: dict = {
    "n_estimators": 500,
    "learning_rate": 0.05,
    "num_leaves": 31,
    "reg_alpha": 0.0,
    "reg_lambda": 0.1,
    "random_state": 42,
}

def run_cv_lgbm(
    X: np.ndarray,       # (N, embed_dim)
    y: np.ndarray,       # (N,)
    n_splits: int = 5,
    random_state: int = 42,
    params: dict = LGBM_PARAMS,
) -> tuple:
    """
    Returns (fold_preds, full_model).
    fold_preds: (N,) OOF predictions on original X
    full_model: LGBMRegressor trained on all N samples
    """
    ...

def compute_orbit_preds(
    full_model,           # fitted LGBMRegressor
    permuted_X: np.ndarray,  # (N, K, embed_dim)
) -> np.ndarray:
    """
    Returns orbit_preds: (N, K) float64.
    orbit_preds[:, k] = full_model.predict(permuted_X[:, k, :])
    """
    ...

def decompose_mse(
    y: np.ndarray,          # (N,)
    fold_preds: np.ndarray, # (N,) OOF
    orbit_preds: np.ndarray, # (N, K)
) -> dict:
    """
    Returns {mse_total, mse_perm, mse_res, ratio, r2_c1, tau_c1,
             y_avg_pred, r2_c1_avg, tau_c1_avg, per_model_orbit_var}.
    mse_perm = mean(var(orbit_preds, axis=1))
    ratio = mse_perm / mse_total  [gate: >= 0.10]
    y_avg_pred = orbit_preds.mean(axis=1)
    per_model_orbit_var: (N,) — Var_k(ŷ) per model
    """
    ...
```

---

### evaluate (`h-m2/code/evaluate.py`)

**Dependencies**: lgbm_trainer, embeddings, H-M1 permutation, numpy, scipy, json, csv, sys

```python
C0_R2: float = 0.984
C0_TAU: float = 0.915
GATE_RATIO: float = 0.10
RESULTS_DIR: str = "results"

def run_permutation_validator(
    dataset: list,
    perm_specs: list,
) -> dict:
    """
    Wraps audit_functional_equivalence from H-M1.
    Returns {"pass": bool, "max_diff": float}.
    Aborts (sys.exit(2)) if validator fails.
    """
    ...

def compute_c0_features(state_dicts: list) -> np.ndarray:
    """
    Returns X_c0: (N, n_features) — per-layer [mean, var, p0, p25, p50, p75, p100].
    Reference only; C0 R²/τ are fixed constants — no LightGBM retraining.
    """
    ...

def verify_mechanism(orbit_preds: np.ndarray, mse_total: float, mse_perm: float, ratio: float) -> dict:
    """
    Returns indicators dict with gate_result.
    Asserts orbit_preds.shape==(100,50), var>1e-10, mse_perm>0, 0<=ratio<=1.
    """
    ...

def gate_check(results: dict) -> bool:
    """Prints PASS/FAIL lines. Returns True if primary gate passes."""
    ...

def save_results(results: dict, summary: dict) -> None:
    """Saves results/mse_decomposition.json and results/h_m2_summary.csv."""
    ...
```

---

### visualize (`h-m2/code/visualize.py`)

**Dependencies**: matplotlib, numpy

```python
FIGURES_DIR: str = "figures"

def plot_mse_decomposition(mse_total: float, mse_perm: float, mse_res: float, ratio: float) -> None:
    """Figure 1 (MANDATORY): bar chart MSE_perm / MSE_res / MSE_total + 10% threshold line."""
    ...

def plot_orbit_var_histogram(per_model_orbit_var: np.ndarray) -> None:
    """Figure 2: histogram of Var_k(ŷ(π_k·W_v)) across 100 models."""
    ...

def plot_r2_comparison(r2_c1: float, r2_c1_avg: float, r2_c0: float = C0_R2) -> None:
    """Figure 3: bar chart R²(C0), R²(C1), R²(C1_avg)."""
    ...

def plot_orbitvar_vs_pred_var(embed_orbit_vars: list, pred_orbit_vars: np.ndarray) -> None:
    """Figure 4: scatter OrbitVar(embed) vs Var_k(ŷ) per model."""
    ...

def plot_orbit_fan(orbit_preds: np.ndarray, model_indices: list = None) -> None:
    """Figure 5: violin plot of K=50 orbit predictions for 5 representative models."""
    ...
```

---

### run_experiment (`h-m2/code/run_experiment.py`)

**Dependencies**: embeddings, lgbm_trainer, evaluate, visualize

```python
DATA_PATH: str  # ../../data/dataset_cifar_small_hyp_rand.pt
H1_CODE_DIR: str  # ../../h-m1/code  (sys.path target)
H1_RESULTS_PATH: str  # ../../h-m1/results/orbit_var_results.json

def main() -> int:
    """
    Entry: python run_experiment.py
    1. sys.path bootstrap for H-M1 imports
    2. load_or_compute_embeddings → (X_cise, permuted_X, y_acc, perm_specs, orbit_var)
    3. verify_orbit_var(orbit_var)
    4. run_permutation_validator(dataset, perm_specs) — abort if FAIL
    5. run_cv_lgbm(X_cise, y_acc) → (fold_preds, full_model)
    6. compute_orbit_preds(full_model, permuted_X) → orbit_preds
    7. decompose_mse(y_acc, fold_preds, orbit_preds) → results
    8. verify_mechanism(orbit_preds, ...) — asserts
    9. gate_check(results) → pass/fail
    10. save_results(results, summary)
    11. all 5 plots
    Returns 0 on gate PASS, 1 on gate FAIL.
    """
    ...

if __name__ == "__main__":
    sys.exit(main())
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | H-M1 import bootstrap + embedding loader | sys.path setup, load_or_compute_embeddings, verify_orbit_var; handle cached vs recompute branch | 9 | 2+2+3+2 |
| A-2 | Permutation validator integration | Wrap audit_functional_equivalence; abort-on-fail logic; PASS/FAIL report | 6 | 1+2+2+1 |
| A-3 | 5-fold CV LightGBM trainer | run_cv_lgbm with OOF collection; full-data model; LGBM_PARAMS | 8 | 2+2+2+2 |
| A-4 | MSE_perm orbit loop | compute_orbit_preds (N×K inference); decompose_mse with all metrics (MSE_total, MSE_perm, MSE_res, ratio, R², τ, orbit-averaged control) | 11 | 3+2+4+2 |
| A-5 | Mechanism verifier + gate check | verify_mechanism asserts; gate_check PASS/FAIL output; save_results (JSON + CSV) | 7 | 2+1+2+2 |
| A-6 | C0 baseline feature extractor | compute_c0_features (per-layer stats); reference-only (no retraining) | 5 | 1+1+2+1 |
| A-7 | Visualization (5 figures) | All 5 plots: MSE bar, orbit var histogram, R² bar, scatter, violin fan | 10 | 3+1+3+3 |
| A-8 | run_experiment.py orchestration + integration test | main() wiring, exit codes, end-to-end smoke test | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-7], Low(4-8): [A-1, A-2, A-3, A-5, A-6, A-8]

---

## Data Flow

- `dataset_cifar_small_hyp_rand.pt` → `load_dataset` → `(models, y_acc)`
- `h-m1/results/orbit_var_results.json` → `load_or_compute_embeddings` → `X_cise (100, 64)`, `permuted_X (100, 50, 64)`
- `X_cise` + `y_acc` → `run_cv_lgbm` → `fold_preds (100,)`, `full_model`
- `full_model` + `permuted_X` → `compute_orbit_preds` → `orbit_preds (100, 50)`
- `y_acc` + `fold_preds` + `orbit_preds` → `decompose_mse` → results dict
- results → `gate_check` → exit 0/1; `save_results`; 5 plots

## Notes

- All MSE computations in float64 (`orbit_preds` cast before `np.var`)
- `per_model_orbit_var` (shape 100,) stored in results for Figure 4 scatter against H-M1 `per_model_vars`
- H-M1 `per_model_vars` loaded from `orbit_var_results.json` for scatter; no re-encoding needed
- C0 R²/τ are constants — `compute_c0_features` only used for documentation; no LightGBM refit on C0
