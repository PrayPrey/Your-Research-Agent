# Logic: H-M2
# Causal Propagation — CISE OrbitVar → LightGBM Prediction Variance

**Hypothesis ID:** H-M2
**Type:** MECHANISM (Causal Step 2)
**Date:** 2026-08-03

Applied: orbit-variance-propagation pattern (MSE decomposition via permutation orbit predictions)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-m1 code
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Relevant Symbols**:
- `load_dataset(pt_path, split="testset", n_models=100) -> tuple[list[OrderedDict], list[float]]`
- `sample_functional_permutations(channels_per_layer, K, seed=1) -> list[list[LongTensor]]`
- `apply_permutation(state_dict, perm_spec, conv_weight_keys=None, bias_keys=None) -> dict`
- `audit_functional_equivalence(state_dict, perm_specs, tol=1e-6, n_checks=5, n_perms=3) -> float`
- `CISEEncoder.forward(state_dict: dict) -> torch.Tensor`  # (embed_dim,) float32
- `build_c1_encoder(embed_dim=64, max_channels=16) -> CISEEncoder`
- `compute_orbit_var_all_models(dataset, encoder_fn, perm_specs, log_every=10) -> tuple[list, float, float]`
- `CHANNELS_PER_LAYER` — constant list from `data_loader.py`

---

## External Dependencies API

### From `h-m1/code/` — verified from actual implementation

```python
# data_loader.py
def load_dataset(pt_path: str, split: str = "testset", n_models: int = 100) -> tuple:
    # Returns: (list[OrderedDict], list[float])  — (state_dicts, accs)

# permutation.py
def sample_functional_permutations(
    channels_per_layer: list,  # e.g. [16, 16, 16]
    K: int,
    seed: int = 1,
) -> list:
    # Returns: list of K specs; each spec = list[LongTensor(C_i,)]

def apply_permutation(
    state_dict: dict,
    perm_spec: list,                    # list[LongTensor]
    conv_weight_keys: list = None,
    bias_keys: list = None,
) -> dict:
    # Returns: deep-copied permuted state_dict

def audit_functional_equivalence(
    state_dict: dict,
    perm_specs: list,
    tol: float = 1e-6,
    n_checks: int = 5,
    n_perms: int = 3,
) -> float:
    # Returns: max_diff. Raises AssertionError if max_diff > tol.

# encoder_c1.py
class CISEEncoder(nn.Module):
    def forward(self, state_dict: dict) -> torch.Tensor:
        # Returns: (embed_dim,) float32

def build_c1_encoder(embed_dim: int = 64, max_channels: int = 16) -> CISEEncoder: ...

# orbit_var.py
def compute_orbit_var_all_models(
    dataset: list,
    encoder_fn: Callable,
    perm_specs: list,
    log_every: int = 10,
) -> tuple:
    # Returns: (per_model_vars: list[float], mean_orbitvar: float, max_orbitvar: float)
```

**Import bootstrap** (h-m1 has no `__init__.py`):
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'h-m1', 'code'))
from data_loader import load_dataset, CHANNELS_PER_LAYER
from permutation import sample_functional_permutations, apply_permutation, audit_functional_equivalence
from encoder_c1 import CISEEncoder, build_c1_encoder
from orbit_var import compute_orbit_var_all_models
```

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation, NOT specs)

---

## Expected JSON Schema: `h-m1/results/orbit_var_results.json`

```json
{
  "mean_orbitvar": 0.010333,
  "max_orbitvar": 0.045,
  "per_model_vars": [0.008, 0.011],
  "embeddings": [[...]],
  "permuted_embeddings": [[[...]]]
}
```

`embeddings` shape: (N, embed_dim) as nested list.
`permuted_embeddings` shape: (N, K, embed_dim) as nested list.
If `embeddings` / `permuted_embeddings` absent from JSON, use cache-miss branch (recompute via CISEEncoder).

---

## L-1: load_or_compute_embeddings [Complexity: 9, Budget: A-1]

Applied: cache-hit/miss fallback pattern

### API Signature

```python
def load_or_compute_embeddings(
    pt_path: str,
    h1_results_path: str,
    n_models: int = 100,
    K: int = 50,
    seed: int = 1,
) -> tuple:
    # Returns:
    #   X_cise:       np.ndarray (N, embed_dim)     float32
    #   permuted_X:   np.ndarray (N, K, embed_dim)  float32
    #   y_acc:        np.ndarray (N,)                float64
    #   perm_specs:   list[list[Tensor]]             length K
    #   orbit_var_h1: float
```

### Pseudocode — cache-hit branch

```
dataset, accs = load_dataset(pt_path, n_models=n_models)
y_acc = np.array(accs, dtype=np.float64)                              # (N,)
perm_specs = sample_functional_permutations(CHANNELS_PER_LAYER, K=K, seed=seed)

with open(h1_results_path) as f: h1 = json.load(f)
orbit_var_h1 = h1["mean_orbitvar"]

if "embeddings" in h1 and "permuted_embeddings" in h1:
    X_cise     = np.array(h1["embeddings"], dtype=np.float32)            # (N, embed_dim)
    permuted_X = np.array(h1["permuted_embeddings"], dtype=np.float32)  # (N, K, embed_dim)
    return X_cise, permuted_X, y_acc, perm_specs, orbit_var_h1
```

### Pseudocode — cache-miss branch

```
encoder = build_c1_encoder()
encoder.eval()
embed_dim = 64
X_cise     = np.zeros((n_models, embed_dim), dtype=np.float32)
permuted_X = np.zeros((n_models, K, embed_dim), dtype=np.float32)

with torch.no_grad():
    for v, sd in enumerate(dataset):
        X_cise[v] = encoder.forward(sd).cpu().numpy()                    # (embed_dim,)
        for k, ps in enumerate(perm_specs):
            perm_sd = apply_permutation(sd, ps)
            permuted_X[v, k] = encoder.forward(perm_sd).cpu().numpy()   # (embed_dim,)

# orbit_var_h1: from JSON header if file present, else recompute
if os.path.exists(h1_results_path):
    orbit_var_h1 = h1["mean_orbitvar"]
else:
    _, orbit_var_h1, _ = compute_orbit_var_all_models(dataset, encoder.forward, perm_specs)

return X_cise, permuted_X, y_acc, perm_specs, orbit_var_h1
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | cache_hit | JSON load, np.array conversion, orbit_var extraction |
| L-1-2 | cache_miss | CISEEncoder loop, apply_permutation, build (N, K, embed_dim) array |

---

## L-2: compute_mse_perm_decomposition [Complexity: 11, Budget: A-3 + A-4]

Applied: orbit-variance-propagation pattern (MSE decomposition via permutation orbit predictions)

### API Signature

```python
def compute_mse_perm_decomposition(
    X_cise: np.ndarray,       # (N, embed_dim)     e.g. (100, 64)
    y_acc: np.ndarray,        # (N,)                e.g. (100,)
    permuted_X: np.ndarray,   # (N, K, embed_dim)  e.g. (100, 50, 64)
    n_splits: int = 5,
    random_state: int = 42,
    n_estimators: int = 500,
    learning_rate: float = 0.05,
    num_leaves: int = 31,
) -> dict:
    # Returns dict keys:
    #   mse_total:           float
    #   mse_perm:            float
    #   mse_res:             float
    #   ratio:               float   [gate: >= 0.10]
    #   r2_c1:               float
    #   tau_c1:              float
    #   y_avg_pred:          np.ndarray (N,)
    #   r2_c1_avg:           float
    #   tau_c1_avg:          float
    #   per_model_orbit_var: np.ndarray (N,)
    #   orbit_preds:         np.ndarray (N, K)
```

### Step-by-step Pseudocode

```
params = dict(n_estimators=n_estimators, learning_rate=learning_rate,
              num_leaves=num_leaves, reg_alpha=0.0, reg_lambda=0.1,
              random_state=random_state)
N = len(y_acc)
K = permuted_X.shape[1]  # 50

# Step 1: folds
kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)

# Step 2: init OOF buffer
fold_preds = np.zeros(N, dtype=np.float64)                        # (N,)

# Step 3: CV loop
for train_idx, val_idx in kf.split(X_cise):
    model = LGBMRegressor(**params)
    model.fit(X_cise[train_idx], y_acc[train_idx])
    fold_preds[val_idx] = model.predict(X_cise[val_idx])          # (|val|,)

# Steps 4-6: OOF metrics
mse_total = mean_squared_error(y_acc, fold_preds)                  # scalar
r2_c1 = r2_score(y_acc, fold_preds)
tau_c1 = kendalltau(y_acc, fold_preds).statistic

# Step 7: full-data model
full_model = LGBMRegressor(**params)
full_model.fit(X_cise, y_acc)

# Step 8: init orbit buffer
orbit_preds = np.zeros((N, K), dtype=np.float64)                  # (100, 50)

# Step 9: orbit inference loop
for k in range(K):
    orbit_preds[:, k] = full_model.predict(permuted_X[:, k, :])  # (N,)

# Step 10: per-model orbit variance
per_model_orbit_var = np.var(orbit_preds, axis=1, ddof=0)         # (N,)

# Step 11: mse_perm = E_v[Var_k(ŷ)]
mse_perm = float(np.mean(per_model_orbit_var))

# Step 12: residual
mse_res = mse_total - mse_perm

# Step 13: ratio — primary gate
ratio = mse_perm / mse_total                                       # gate: >= 0.10

# Step 14: orbit-averaged predictions
y_avg_pred = orbit_preds.mean(axis=1)                             # (N,)

# Steps 15-16: orbit-averaged metrics
r2_c1_avg = r2_score(y_acc, y_avg_pred)
tau_c1_avg = kendalltau(y_acc, y_avg_pred).statistic

return {
    "mse_total": mse_total, "mse_perm": mse_perm,
    "mse_res": mse_res, "ratio": ratio,
    "r2_c1": r2_c1, "tau_c1": tau_c1,
    "y_avg_pred": y_avg_pred,
    "r2_c1_avg": r2_c1_avg, "tau_c1_avg": tau_c1_avg,
    "per_model_orbit_var": per_model_orbit_var,
    "orbit_preds": orbit_preds,
}
```

### Tensor Shapes

| Variable | Shape | dtype | Note |
|----------|-------|-------|------|
| X_cise | (100, 64) | float32 | CISE embeddings |
| fold_preds | (100,) | float64 | OOF CV predictions |
| orbit_preds | (100, 50) | float64 | K orbit predictions per model |
| per_model_orbit_var | (100,) | float64 | Var_k(ŷ) per model, ddof=0 |
| y_avg_pred | (100,) | float64 | Orbit-averaged control |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | cv_loop | KFold OOF → fold_preds (N,), mse_total, r2_c1, tau_c1 |
| L-2-2 | orbit_loop | full_model.fit + K-iter predict → orbit_preds (N, K) |
| L-2-3 | decompose | per_model_orbit_var, mse_perm, mse_res, ratio, y_avg_pred, tau_c1_avg |

---

## L-3: verify_mse_perm_mechanism [Complexity: 7, Budget: A-5]

Applied: Standard Python assertions with dict reporting

### API Signature

```python
def verify_mse_perm_mechanism(
    orbit_preds: np.ndarray,  # (100, 50)
    mse_total: float,
    mse_perm: float,
    ratio: float,
) -> tuple:
    # Returns: (all_valid: bool, indicators: dict)
    # indicators keys:
    #   "orbit_preds_shape_valid": bool
    #   "nonzero_orbit_variance":  bool
    #   "mse_perm_positive":       bool
    #   "ratio_computed":          bool
    #   "gate_result":             bool
```

### Pseudocode

```
indicators = {}

indicators["orbit_preds_shape_valid"] = (orbit_preds.shape == (100, 50))
assert indicators["orbit_preds_shape_valid"], f"Expected (100,50), got {orbit_preds.shape}"

indicators["nonzero_orbit_variance"] = (np.mean(np.var(orbit_preds, axis=1)) > 1e-10)
assert indicators["nonzero_orbit_variance"], "orbit variance is effectively zero"

indicators["mse_perm_positive"] = (mse_perm > 0)
assert indicators["mse_perm_positive"], f"mse_perm={mse_perm} <= 0"

indicators["ratio_computed"] = (0.0 <= ratio <= 1.0)
assert indicators["ratio_computed"], f"ratio={ratio:.4f} out of [0, 1]"

# Gate: report only, no assert
indicators["gate_result"] = (ratio >= 0.10)
print(f"MSE_perm/MSE_total = {ratio:.4f} (gate: >= 0.10)")

all_valid = all(indicators.values())
return all_valid, indicators
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | assertions | Shape/value checks, gate eval, print log, return (bool, dict) |

---

## Notes for Phase 4 Coder

- `np.var(..., ddof=0)` — matches H-M1 `torch.var(..., unbiased=False)` convention
- `kendalltau(a, b).statistic` — scipy >= 1.7.0 attribute name (not `.correlation`)
- `orbit_preds` must be kept in results dict for Figure 4/5; do not discard after decompose
- Figure 4 x-axis (`embed_orbit_vars`): load from `h1["per_model_vars"]` (list[float] len 100)
- C0 R²=0.984, τ=0.915 are constants — no LightGBM refit on C0 features needed
- `embed_dim=64` default from `build_c1_encoder`; verify if changed in h-m1 run config
