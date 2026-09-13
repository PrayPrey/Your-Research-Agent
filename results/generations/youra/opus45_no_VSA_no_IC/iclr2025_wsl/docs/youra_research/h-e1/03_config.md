# Config: H-E1 (EXISTENCE — Statistics Baseline)

Applied: hardcoded-constants pattern (EXISTENCE PoC, no dataclass needed)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: hardcoded dict/constants (module-level, matches architecture's `config.py`)

---

## Config (`code/config.py`)

Single fixed config per EXISTENCE rules — no hyperparameter grid, no ablations.

```python
# config.py — fixed constants, no tuning

N_VALUES = [100, 250, 500, 1000, 2500, 5000]
N_SEEDS = 10
TEST_SIZE = 500
ALPHAS = [0.01, 0.1, 1, 10, 100]
CV_FOLDS = 5

ZOO_URL = "https://zenodo.org/records/6974029"
ZOO_DIR = "data/model_zoo"
FEATURES_PATH = "statistics_features.npy"
RESULTS_PATH = "statistics_baseline_results.csv"
PLOT_PATH = "r2_vs_n.png"

SPLIT_SEED = 42  # fixed test-set split, separate from sweep seeds
```

No dataclass — architecture spec already defines `config.py` as flat constants; matching it avoids a redundant wrapper.

---

## A-1: Data Acquisition [Complexity: 10, Budget: 10]

**Applied**: Standard download/split constants above (`ZOO_URL`, `ZOO_DIR`, `SPLIT_SEED`, `TEST_SIZE`)

No task-specific config beyond global constants.

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Download | Fetch Model Zoo archive from `ZOO_URL` to `ZOO_DIR` |
| C-1-2 | Extract | Unpack checkpoints, parse state_dicts |
| C-1-3 | Labels | Parse accuracy labels from metadata |
| C-1-4 | Split | Fixed train_pool/test split using `SPLIT_SEED`, `TEST_SIZE` |

---

## A-2: Feature Extraction [Complexity: 12, Budget: 12]

**Applied**: Standard PyTorch tensor stats (no config needed — stats list is fixed by PRD FR-2)

```python
STAT_FUNCS = ["mean", "std", "min", "max", "l2_norm", "fro_norm", "spectral_norm", "sparsity"]
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Per-tensor stats | Mean/std/min/max/L2/Fro/sparsity per weight tensor |
| C-2-2 | Spectral norm | SVD-based largest singular value per tensor |
| C-2-3 | Layer aggregation | Concatenate stats across ~21 layers -> ~147-dim vector |
| C-2-4 | Validation | Assert output shape/dtype matches expected |

---

## A-3: Feature Matrix + Caching [Complexity: 6, Budget: 6]

**Applied**: `FEATURES_PATH` constant above; numpy `.npy` save/load

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Build X,y | Stack per-model features and accuracy labels |
| C-3-2 | Cache | Save/load `statistics_features.npy` to skip re-extraction |

---

## A-4: Ridge Baseline Model [Complexity: 5, Budget: 5]

**Applied**: sklearn `RidgeCV` defaults (`ALPHAS`, `CV_FOLDS` above)

```python
from sklearn.linear_model import RidgeCV

def fit_ridge(X_train, y_train):
    return RidgeCV(alphas=ALPHAS, cv=CV_FOLDS).fit(X_train, y_train)
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Fit | `RidgeCV` with `ALPHAS`, `cv=CV_FOLDS` |
| C-4-2 | Eval | R² on held-out test set (`model.score`) |

---

## A-5: Data Efficiency Sweep [Complexity: 9, Budget: 9]

**Applied**: `N_VALUES` x `N_SEEDS` nested loop (KB: no direct match, standard sweep pattern used)

```python
def run_sweep(N_values=N_VALUES, n_seeds=N_SEEDS):
    for n in N_values:
        for seed in range(n_seeds):
            ...  # sample_models(pool, n, seed) -> fit_ridge -> evaluate
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Sampling | `sample_models(pool, n, seed)` draws n models per seed, seed = loop index |
| C-5-2 | Sweep loop | Nested `N_VALUES` x `range(N_SEEDS)`, collect (n, seed, r2) rows |

---

## A-6: Results Logging [Complexity: 6, Budget: 6]

**Applied**: `RESULTS_PATH`, `PLOT_PATH` constants above; pandas CSV + matplotlib

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | CSV | Save sweep results (`n`, `seed`, `r2`) to `RESULTS_PATH` |
| C-6-2 | Plot | R² vs N learning curve (mean ± std across seeds) to `PLOT_PATH` |

---

## A-7: Unit Tests [Complexity: 6, Budget: 6]

**Applied**: pytest, synthetic small tensors for correctness checks

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Stats correctness | Known-input tensor -> verify mean/std/norm values |
| C-7-2 | Spot check | Feature vector shape (~147-dim) and dtype on real checkpoint |
