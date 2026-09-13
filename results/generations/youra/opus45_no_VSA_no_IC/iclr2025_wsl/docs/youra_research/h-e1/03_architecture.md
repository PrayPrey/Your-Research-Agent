# Architecture: H-E1 (EXISTENCE)

Applied: sklearn RidgeCV baseline pattern (feature-extraction -> tabular -> linear model)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Organization

```
h-e1/code/
  data.py         # download/load Model Zoo checkpoints, accuracy labels
  features.py      # weight statistics extraction
  model.py         # RidgeCV training + eval
  train.py         # main experiment loop (N x seed sweep)
  config.py        # fixed constants (N list, seeds, alphas, paths)
```

No `evaluate.py` split — R² scoring folded into `train.py` per EXISTENCE minimalism.

---

## Modules

### data.py

**Dependencies**: none (torch, requests/zenodo)

```python
def download_model_zoo(dest_dir: str) -> str: ...  # returns extracted path
def load_checkpoints(zoo_dir: str) -> list[tuple[dict, float]]: ...  # (state_dict, accuracy)
def split_test_set(items: list, test_size: int, seed: int) -> tuple[list, list]: ...  # (train_pool, test)
```

### features.py

**Dependencies**: numpy, torch

```python
def extract_weight_statistics(state_dict: dict) -> np.ndarray: ...  # ~147-dim vector
def build_feature_matrix(items: list[tuple[dict, float]]) -> tuple[np.ndarray, np.ndarray]: ...  # (X, y)
```

### model.py

**Dependencies**: sklearn

```python
def fit_ridge(X_train: np.ndarray, y_train: np.ndarray, alphas: list[float]) -> RidgeCV: ...
def evaluate(model: RidgeCV, X_test: np.ndarray, y_test: np.ndarray) -> float: ...  # R^2
```

### train.py

**Dependencies**: data, features, model, config

```python
def sample_models(pool: list, n: int, seed: int) -> tuple[np.ndarray, np.ndarray]: ...
def run_sweep(N_values: list[int], n_seeds: int) -> pd.DataFrame: ...  # results table
def main() -> None: ...  # orchestrates full pipeline, saves outputs
```

### config.py

```python
N_VALUES = [100, 250, 500, 1000, 2500, 5000]
N_SEEDS = 10
TEST_SIZE = 500
ALPHAS = [0.01, 0.1, 1, 10, 100]
ZOO_DIR = "data/model_zoo"
FEATURES_PATH = "statistics_features.npy"
RESULTS_PATH = "statistics_baseline_results.csv"
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data acquisition | Download/extract Model Zoo, parse state_dicts + accuracy labels | 10 | 3+3+2+2 |
| A-2 | Feature extraction | Implement per-layer stats (mean/std/min/max/L2/Fro/spectral/sparsity) | 12 | 3+2+4+3 |
| A-3 | Feature matrix + caching | Build X,y arrays, save statistics_features.npy | 6 | 2+2+1+1 |
| A-4 | Ridge baseline model | RidgeCV fit/eval wrapper with 5-fold CV | 5 | 2+1+1+1 |
| A-5 | Data efficiency sweep | N x seed loop, sample_models, fixed test set | 9 | 2+3+2+2 |
| A-6 | Results logging | Save results CSV, R² vs N learning curve plot | 6 | 2+1+1+2 |
| A-7 | Unit tests | Feature extraction correctness + spot checks | 6 | 2+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-2, A-5], Low(4-8): [A-3, A-4, A-6, A-7]
