# Architecture: H-M3 — DeepSets Mechanism Closure Validation

**Date:** 2026-08-03
**Type:** MECHANISM (INCREMENTAL — extends H-M2)
**Applied:** incremental-experiment-flat-module-pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (incremental from H-M2)
**Status:** Patterns found from base code
**Analyzed Path:** `docs/youra_research/h-m2/code/` + `docs/youra_research/h-e1/code/`
**Findings:** H-M2 uses flat module layout: `data_loader.py`, `encoder_c1/c2/c3.py`, `lgbm_trainer.py`, `permutation.py`, `evaluate.py`, `visualize.py`, `run_experiment.py`. H-E1 has `encoder_c2.py` with `DeepSetsChannelEncoder` (doubly-invariant, sums over C_out × C_in kernels). H-M2 `evaluate.py` has `compute_c0_features`. H-M2 `lgbm_trainer.py` has `run_cv_lgbm`, `decompose_mse`, `compute_orbit_preds`.

---

## External Dependencies (Base Hypothesis)

### Module Paths (Verified from Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| DeepSetsChannelEncoder | `sys.path.insert` + `from encoder_c2 import DeepSetsChannelEncoder, build_c2_encoder` | `h-e1/code/encoder_c2.py` (L6–73) |
| build_c2_encoder | same file | kernel_dims=[25,25,4], hidden_dim=64, embed_dim=128 |
| load_dataset | `from data_loader import load_dataset` | `h-m2/code/data_loader.py` |
| run_cv_lgbm | `from lgbm_trainer import run_cv_lgbm, LGBM_PARAMS` | `h-m2/code/lgbm_trainer.py` |
| decompose_mse | `from lgbm_trainer import decompose_mse` | `h-m2/code/lgbm_trainer.py` |
| compute_orbit_preds | `from lgbm_trainer import compute_orbit_preds` | `h-m2/code/lgbm_trainer.py` |
| compute_c0_features | `from evaluate import compute_c0_features` | `h-m2/code/evaluate.py` |
| sample_functional_permutations | `from permutation import sample_functional_permutations` | `h-m2/code/permutation.py` |
| NFN layers | `from nfn import layers` + `from nfn.common import network_spec_from_wsfeat, state_dict_to_tensors` | pip install git+https://github.com/AllanYangZhou/nfn.git |

**H-M2 `LGBM_PARAMS`:** n_estimators=500, learning_rate=0.05 (verified from `lgbm_trainer.py`)
**H-E1 encoder forward signature:** `forward(self, state_dict: dict) -> torch.Tensor` → returns `(embed_dim,)` tensor

---

## File Organization

```
docs/youra_research/h-m3/code/
  data_loader.py        # load .pt, extract weights/labels (thin wrapper over h-m2)
  encoder_c2.py         # import DeepSetsChannelEncoder from h-e1; extract embeddings
  encoder_c3.py         # NFN encoder: NPLinear → HNPPool pipeline + fallback
  encoder_c0.py         # per-layer quantile stats (reuse compute_c0_features from h-m2)
  linear_head.py        # RidgeCV ablation for C2 and C3
  permutation_test.py   # K=50 orbit permutations; MSE_perm(C2)
  closure.py            # ΔMSE, closure metric, verify_mechanism_activated
  evaluate.py           # R², τ, gate evaluation
  visualize.py          # bar chart + optional figures
  results.py            # JSON save + logging
  run_experiment.py     # orchestration entry point
  requirements.txt
```

---

## Module Definitions

### DataLoader (`data_loader.py`)

**Dependencies:** torch, h-m2 data_loader (path-injected)

```python
def load_zoo(data_path: str = "data/dataset_cifar_small_hyp_rand.pt") -> tuple:
    # Returns (state_dicts: list[dict], labels: np.ndarray)
    ...
```

---

### C0Encoder (`encoder_c0.py`)

**Dependencies:** numpy, h-m2 evaluate.compute_c0_features

```python
def extract_c0_features(state_dicts: list) -> np.ndarray:
    # Returns X_c0: (N, 7*n_conv_layers) — per-layer [mean,var,p0,p25,p50,p75,p100]
    # Reuses compute_c0_features from h-m2/code/evaluate.py verbatim
    ...
```

---

### C2Encoder (`encoder_c2.py`)

**Dependencies:** torch, h-e1 encoder_c2 (path-injected)

```python
def extract_c2_embeddings(
    state_dicts: list,
    embed_dim: int = 128,
    hidden_dim: int = 64,
) -> np.ndarray:
    # Returns X_c2: (N, embed_dim)
    # Loads DeepSetsChannelEncoder via build_c2_encoder() from h-e1
    # Asserts orbitvar < 1e-4 before returning
    ...

def compute_c2_orbitvar(
    encoder: "DeepSetsChannelEncoder",
    state_dicts: list,
    perm_fn,
    K: int = 50,
    seed: int = 1,
) -> float:
    # Returns orbitvar_c2: mean orbit variance of C2 embeddings
    ...
```

---

### C3Encoder (`encoder_c3.py`)

**Dependencies:** torch, nfn (pip), numpy

```python
def build_nfn_encoder(
    network_spec,
    nfn_channels: int = 32,
) -> "nn.Sequential":
    # NPLinear(network_spec, 1, nfn_channels, io_embed=True) → ReLU →
    # NPLinear(network_spec, nfn_channels, nfn_channels, io_embed=True) → ReLU →
    # HNPPool(network_spec) → Flatten
    ...

def extract_c3_embeddings(
    state_dicts: list,
    nfn_channels: int = 32,
) -> np.ndarray:
    # Returns X_c3: (N, embed_dim_c3)
    # Handles spatial-folding fallback: if state_dict_to_tensors fails,
    # falls back to DeepSetsChannelEncoder (C2 variant) and logs warning
    ...
```

---

### LinearHead (`linear_head.py`)

**Dependencies:** sklearn.linear_model.RidgeCV, numpy

```python
def fit_ridge(
    X: np.ndarray,
    y: np.ndarray,
    alphas: list = [0.01, 0.1, 1.0, 10.0],
    cv: int = 5,
) -> dict:
    # Returns {"r2": float, "model": RidgeCV}
    # Uses leave-one-out OOF via cross_val_predict for fair comparison
    ...
```

---

### PermutationTest (`permutation_test.py`)

**Dependencies:** numpy, h-m2 permutation.sample_functional_permutations, h-m2 lgbm_trainer.compute_orbit_preds

```python
def compute_mse_perm_c2(
    lgbm_model,
    encoder: "DeepSetsChannelEncoder",
    state_dicts: list,
    y: np.ndarray,
    K: int = 50,
    seed: int = 1,
) -> float:
    # Generates K orbit permutations per model, runs encoder + lgbm_model.predict,
    # returns MSE_perm(C2) = mean orbit prediction variance
    # Reuses sample_functional_permutations from h-m2/code/permutation.py
    ...
```

---

### Closure (`closure.py`)

**Dependencies:** numpy

```python
MSE_PERM_C1 = 0.006137   # from H-M2 validated results

def compute_closure(
    mse_total_c1: float,
    mse_total_c2: float,
    mse_perm_c1: float = MSE_PERM_C1,
) -> dict:
    # Returns {"delta_mse": float, "closure": float}
    ...

def verify_mechanism_activated(results: dict) -> tuple:
    # Returns (passed: bool, indicators: dict)
    # Checks 4 indicators; requires 3/4:
    #   c2_orbitvar_near_zero: orbitvar_c2 < 1e-4
    #   mse_perm_c2_near_zero: mse_perm_c2 < 0.0001
    #   r2_c2_improves_c1:     r2_c2 > r2_c1
    #   closure_within_tolerance: closure <= 0.10
    ...
```

---

### Evaluate (`evaluate.py`)

**Dependencies:** sklearn.metrics, scipy.stats, numpy

```python
def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    # Returns {"r2": float, "mse": float, "tau": float}
    ...

def gate_check(results: dict) -> dict:
    # Returns {"status": str, "primary_gate": bool, "explore": bool, "pivot": bool}
    # PASS: r2_c2 >= 0.984 AND closure <= 0.10
    # EXPLORE: r2_c2 in (0.851, 0.984)
    # PIVOT: closure > 2.0
    ...
```

---

### Visualize (`visualize.py`)

**Dependencies:** matplotlib, numpy

```python
FIGURES_DIR: str  # = "docs/youra_research/h-m3/figures/"

def plot_r2_comparison(results: dict) -> str:
    # MANDATORY: bar chart R²(C0, C1, C2, C3) with 0.984 threshold line
    # Returns saved figure path
    ...

def plot_mse_decomposition(results: dict) -> str:
    # Stacked bar MSE_total, MSE_perm, MSE_res for C1, C2, C3 + closure annotation
    ...

def plot_closure_scatter(results: dict) -> str:
    # Scatter ΔMSE vs MSE_perm per encoder; diagonal = perfect closure
    ...

def plot_linear_head_ablation(results: dict) -> str:
    # Grouped bar: R²(C2-LGB), R²(C2-Ridge), R²(C3-LGB), R²(C3-Ridge)
    ...

def plot_tau_comparison(results: dict) -> str:
    # τ bar chart across C0, C1, C2, C3
    ...
```

---

### Results (`results.py`)

**Dependencies:** json, logging, pathlib

```python
RESULTS_DIR: str  # = "docs/youra_research/h-m3/"

def load_c1_reference(h_m2_results_path: str) -> dict:
    # Loads h-m2/experiment_results.json
    # Returns subset: mse_total, mse_perm, r2, tau for C1
    ...

def save_results(results: dict, path: str = None) -> str:
    # Saves experiment_results.json to RESULTS_DIR
    # Returns saved path
    ...
```

---

### RunExperiment (`run_experiment.py`)

**Dependencies:** all above modules

```python
def main() -> None:
    # 1. load_zoo()
    # 2. load_c1_reference()
    # 3. extract_c0_features() → run_cv_lgbm() → compute_metrics()
    # 4. extract_c2_embeddings() → run_cv_lgbm() → compute_metrics()
    # 5. compute_mse_perm_c2()
    # 6. extract_c3_embeddings() → run_cv_lgbm() + fit_ridge() → compute_metrics()
    # 7. fit_ridge(X_c2), fit_ridge(X_c3)
    # 8. compute_closure()
    # 9. verify_mechanism_activated()
    # 10. gate_check()
    # 11. all plot_*() functions
    # 12. save_results()
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data & Reference Load | load_zoo() + load_c1_reference() from h-m2 JSON; assert labels shape | 6 | 2+1+1+2 |
| A-2 | C0 Baseline | extract_c0_features (reuse h-m2 compute_c0_features) → run_cv_lgbm → metrics | 7 | 2+2+1+2 |
| A-3 | C2 DeepSets Encoder | path-inject h-e1, build_c2_encoder, extract embeddings, assert orbitvar < 1e-4 | 10 | 3+3+2+2 |
| A-4 | C2 LightGBM Training | run_cv_lgbm on C2 embeddings with H-M2 LGBM_PARAMS; OOF predictions | 8 | 2+2+2+2 |
| A-5 | C3 NFN Encoder | build_nfn_encoder via nfn lib, spatial-folding check, fallback to DeepSets if error | 14 | 4+3+4+3 |
| A-6 | Linear Head Ablation | RidgeCV on frozen C2 + C3 embeddings; expressivity gap R²(C3)-R²(C2) | 8 | 2+2+2+2 |
| A-7 | MSE Permutation Test (C2) | K=50 orbit perms via sample_functional_permutations; compute MSE_perm(C2) | 11 | 3+3+3+2 |
| A-8 | Mechanism Closure | compute_closure + verify_mechanism_activated (4-indicator check) | 9 | 2+2+3+2 |
| A-9 | Gate Evaluation | gate_check: PASS/EXPLORE/PIVOT branches; log all indicator values | 7 | 2+1+2+2 |
| A-10 | Visualization | plot_r2_comparison (mandatory) + 4 optional figures | 10 | 3+2+2+3 |
| A-11 | Results Persistence | save_results JSON; experiment.log with all metrics and gate verdict | 6 | 2+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-3, A-7, A-8, A-10], Low(4-8): [A-1, A-2, A-4, A-6, A-9, A-11]
