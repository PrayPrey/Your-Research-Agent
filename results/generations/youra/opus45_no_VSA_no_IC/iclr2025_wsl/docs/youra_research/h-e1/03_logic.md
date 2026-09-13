# Logic: H-E1 (EXISTENCE) — Statistics Baseline

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze, designing new APIs
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: Feature Extraction [Complexity: 12, Budget: 2 subtasks]

**Applied**: 7-stat weight tensor summary (Unterthiner et al. 2020 predict-accuracy-from-weights pattern)

### API Signatures

```python
import numpy as np
import torch
from torch import Tensor

def layer_statistics(w: Tensor) -> np.ndarray:
    """7 stats for one weight tensor. w: any shape -> [7]"""
    ...

def extract_weight_statistics(state_dict: dict) -> np.ndarray:
    """Concat layer_statistics over all weight tensors. -> [~147]"""
    ...

def build_feature_matrix(
    items: list[tuple[dict, float]]
) -> tuple[np.ndarray, np.ndarray]:
    """items: [(state_dict, accuracy), ...] -> X:[M,147], y:[M]"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| w | arbitrary (e.g. [Cout,Cin,K,K] or [Cout,Cin]) | one layer's weight tensor |
| w_flat | [Cout, -1] | reshaped 2D for spectral norm (SVD) |
| layer_statistics(w) | [7] | mean, std, min, max, L2, Fro, spectral, sparsity — 8 listed in PRD but header says 7; see note |
| extract_weight_statistics(state_dict) | [~147] | 7 stats × ~21 weight layers (skip biases/BN scalars) |
| X | [M, 147] | M = number of models |
| y | [M] | accuracy labels, 0.70-0.95 |

Note: PRD FR-2 lists 8 items (mean/std/min/max/L2/Fro/spectral/sparsity) but says "7 features". Implement all 8 in `layer_statistics`; if final width must hit ~147, drop L2 norm (redundant with Fro norm for a flattened tensor) to land at 7×21=147. Document choice in code comment.

### Pseudo-code

```
layer_statistics(w):
    v = w.flatten()
    mean, std, min, max = v.mean(), v.std(), v.min(), v.max()
    fro = torch.norm(w)                          # Frobenius norm
    spectral = svdvals(w.reshape(w.shape[0], -1)).max()  # top singular value
    sparsity = (v.abs() < 1e-6).float().mean()
    return np.array([mean, std, min, max, fro, spectral, sparsity])

extract_weight_statistics(state_dict):
    feats = [layer_statistics(w) for name, w in state_dict.items()
             if "weight" in name and w.dim() >= 2]   # skip 1D BN/bias params
    return np.concatenate(feats)   # [~147]

build_feature_matrix(items):
    X = np.stack([extract_weight_statistics(sd) for sd, _ in items])
    y = np.array([acc for _, acc in items])
    return X, y
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | `layer_statistics` | Per-tensor 7/8-stat vector via numpy/torch (mean/std/min/max/Fro/spectral SVD/sparsity) |
| L-A2-2 | `extract_weight_statistics` + `build_feature_matrix` | Filter weight-only 2D+ tensors, concat per layer, stack into (X, y) arrays |

---

## Non-A-2 Modules (signatures only, no budget consumed here — see architecture.md for owning tasks)

```python
# data.py (A-1)
def download_model_zoo(dest_dir: str) -> str: ...
def load_checkpoints(zoo_dir: str) -> list[tuple[dict, float]]: ...
def split_test_set(items: list, test_size: int, seed: int) -> tuple[list, list]: ...

# model.py (A-4)
from sklearn.linear_model import RidgeCV
def fit_ridge(X_train: np.ndarray, y_train: np.ndarray, alphas: list[float]) -> RidgeCV: ...
def evaluate(model: RidgeCV, X_test: np.ndarray, y_test: np.ndarray) -> float: ...  # R^2

# train.py (A-5, A-6)
def sample_models(pool: list, n: int, seed: int) -> tuple[np.ndarray, np.ndarray]: ...
def run_sweep(N_values: list[int], n_seeds: int) -> "pd.DataFrame": ...
def main() -> None: ...
```
