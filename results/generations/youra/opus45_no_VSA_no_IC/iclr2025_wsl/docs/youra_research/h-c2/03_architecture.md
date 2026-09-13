# Architecture: H-C2 — NFN vs Statistics Crossing Point

**Applied:** Weight-space regression pattern (Unterthiner et al. StatNN features + NFN permutation-equivariant layers), no reusable KB code example found.

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze (only unrelated archived SANE_repo cache found, not a base hypothesis for H-C2)
**Analyzed Path:** N/A
**Findings:** New implementation from scratch, built on external `nfn` pip library.

---

## Data Flow

```
Zenodo (5645138) --> data/download.py --> data/cifar10_zoo/*.pt (raw state_dicts + acc)
                                                |
                                                v
                                    data/loader.py: load_cifar10_zoo()
                                                |
                       +------------------------+------------------------+
                       v                                                 v
          features/statistics.py                              features/nfn_input.py
          extract_statistics(sd) -> Tensor[F]                  to_wsfeat(sd) -> WeightSpaceFeatures
                       |                                                 |
                       v                                                 v
              models/stats_model.py                            models/nfn_model.py
              StatsRegressor                                    NFNAccuracyPredictor
                       |                                                 |
                       +------------------------+------------------------+
                                                v
                                        train/loop.py: train_one_run(method, N, seed)
                                                |
                                                v
                                        eval/metrics.py: evaluate(model, test_set)
                                                |
                                                v
                                results/store.py -> results/raw_results.csv
                                                |
                                                v
                                analysis/crossing_point.py -> N*, CI
                                                |
                                                v
                                        viz/plots.py -> figures/*.png
```

---

## Module Structure

### `data/download.py`

**Dependencies:** none (requests, zipfile stdlib)

```python
def download_zenodo_zoo(dest_dir: str, url: str = ZENODO_ZOO_URL) -> str: ...
def ensure_zoo_downloaded(dest_dir: str) -> str:  # idempotent, skip if exists
```

### `data/loader.py`

**Dependencies:** data/download.py

```python
@dataclass
class ModelRecord:
    state_dict: dict[str, torch.Tensor]
    test_accuracy: float

def load_cifar10_zoo(zoo_dir: str) -> list[ModelRecord]: ...
def split_train_test(
    records: list[ModelRecord], test_size: int = 500, seed: int = 0
) -> tuple[list[ModelRecord], list[ModelRecord]]:  # fixed test set across all N/seed
def subsample_train(
    train_pool: list[ModelRecord], n: int, seed: int
) -> list[ModelRecord]: ...
```

### `features/statistics.py`

**Dependencies:** none

```python
def extract_statistics(state_dict: dict[str, torch.Tensor]) -> torch.Tensor: ...  # [F]
def build_stats_matrix(records: list[ModelRecord]) -> tuple[np.ndarray, np.ndarray]:  # X, y
```

### `features/nfn_input.py`

**Dependencies:** nfn (external)

```python
def get_network_spec(sample_state_dict: dict) -> "NetworkSpec": ...  # nfn.common
def to_wsfeat_batch(records: list[ModelRecord]) -> tuple["WeightSpaceFeatures", torch.Tensor]: ...
```

### `models/stats_model.py`

**Dependencies:** features/statistics.py

```python
class StatsRegressor:
    def __init__(self, alpha: float = 1.0): ...  # sklearn Ridge wrapper
    def fit(self, X: np.ndarray, y: np.ndarray) -> "StatsRegressor": ...
    def predict(self, X: np.ndarray) -> np.ndarray: ...
```

### `models/nfn_model.py`

**Dependencies:** nfn (external), features/nfn_input.py

```python
class NFNAccuracyPredictor(nn.Module):
    def __init__(self, network_spec, hidden_channels: int = 64): ...
    def forward(self, wsfeat: "WeightSpaceFeatures") -> torch.Tensor: ...  # [B, 1]
```

### `train/loop.py`

**Dependencies:** models/stats_model.py, models/nfn_model.py, features/*

```python
@dataclass
class RunConfig:
    method: str          # "nfn" | "stats"
    n: int
    seed: int
    lr: float = 1e-3
    weight_decay: float = 1e-4
    batch_size: int = 32
    max_epochs: int = 100
    patience: int = 10

@dataclass
class RunResult:
    method: str; n: int; seed: int
    r2: float; kendall_tau: float; mse: float
    y_true: np.ndarray; y_pred: np.ndarray

def train_one_run(cfg: RunConfig, train_pool, test_set) -> RunResult: ...
def train_nfn(cfg: RunConfig, train_records, val_records) -> nn.Module: ...  # internal, early stop on val loss
def run_all(configs: list[RunConfig], train_pool, test_set) -> list[RunResult]: ...
```

### `eval/metrics.py`

**Dependencies:** sklearn, scipy

```python
def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:  # {r2, kendall_tau, mse}
```

### `results/store.py`

**Dependencies:** train/loop.py (RunResult)

```python
def save_results(results: list[RunResult], path: str) -> None: ...  # CSV: method,n,seed,r2,tau,mse
def load_results(path: str) -> pd.DataFrame: ...
```

### `analysis/crossing_point.py`

**Dependencies:** pandas, scipy.stats (CI)

```python
def aggregate_by_n(df: pd.DataFrame) -> pd.DataFrame:  # mean, 95% CI per (method, n)
def find_crossing_point(agg: pd.DataFrame, threshold: float = 0.03) -> int | None: ...
def crossing_point_report(agg: pd.DataFrame, n_star: int | None) -> dict: ...
```

### `viz/plots.py`

**Dependencies:** matplotlib, analysis/crossing_point.py

```python
def plot_crossing_point(agg: pd.DataFrame, n_star: int | None, out_path: str) -> None: ...
def plot_learning_curves(agg: pd.DataFrame, out_path: str) -> None: ...
def plot_scatter_at_n(result: RunResult, out_path: str) -> None: ...
def plot_r2_bars(agg: pd.DataFrame, out_path: str) -> None: ...
```

### `main.py`

**Dependencies:** all above

```python
def main() -> None:
    # 1. ensure_zoo_downloaded -> load_cifar10_zoo -> split_train_test
    # 2. build RunConfig grid: N x method x seed (5x2x10=100)
    # 3. run_all -> save_results
    # 4. aggregate_by_n -> find_crossing_point -> crossing_point_report
    # 5. generate all figures to h-c2/figures/
```

---

## Interface Contracts

- `ModelRecord.state_dict` keys/shapes constant across zoo (fixed CNN arch, 2864 params) — `get_network_spec` computed once from any record.
- Test set (500 models) is split once with `seed=0` and reused unchanged across all N/method/seed runs.
- `train_pool` for a given N is subsampled from the remaining ~500 models using the run's own seed — 10 seeds per N give 10 distinct train subsets.
- `RunResult.y_true`/`y_pred` always in accuracy units (not normalized) so R²/MSE comparable across methods.
- `find_crossing_point` scans N ascending, returns first N with `|delta| < threshold`; `None` if not found (feeds SHOULD_WORK graceful failure path).

## Error Handling Strategy

- **Download failure** (`data/download.py`): retry 3x with backoff; on persistent failure, raise `RuntimeError` with Zenodo URL — no silent fallback (data integrity required).
- **NFN incompatible architecture**: `get_network_spec` raising an exception from `nfn.common` propagates immediately — halts run rather than falling back to a wrong spec.
- **Training divergence** (loss NaN/inf): `train_nfn` checks loss each epoch; on NaN, abort that (method,N,seed) run, record `RunResult` with `r2=nan` and log a warning, continue with remaining configs (one bad seed shouldn't kill the 100-run sweep).
- **R² outside [0,1] or huge negative** (e.g., H-M2's MLP -1.50 pattern): not an error, logged as-is; `crossing_point_report` flags any method with median R² < 0 as "mechanism failure" per brief's failure-detection criterion.
- **No crossing point found** (N* not < 2500 or None): `main.py` logs limitation and writes report noting SHOULD_WORK gate failed gracefully; does not raise, does not block pipeline completion.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Zenodo download + zoo loader + fixed test split | 10 | 3+2+3+2 |
| A-2 | Statistics features | Per-layer mean/std/L2/spectral norm extraction | 6 | 2+1+2+1 |
| A-3 | NFN input adapter | state_dict -> WeightSpaceFeatures, network_spec | 8 | 2+3+2+1 |
| A-4 | Statistics model | Ridge regressor wrapper, fit/predict | 4 | 1+1+1+1 |
| A-5 | NFN model | NFNAccuracyPredictor per brief's architecture | 9 | 3+3+2+1 |
| A-6 | Training loop | Early stopping, batching, per-method dispatch | 12 | 3+3+3+3 |
| A-7 | Evaluation metrics | R², Kendall's tau, MSE on fixed test set | 4 | 1+1+1+1 |
| A-8 | Run orchestration | 100-run grid (5N x 2method x 10seed), result storage | 9 | 2+3+2+2 |
| A-9 | Crossing point analysis | Aggregation, CI, threshold-based N* detection | 8 | 2+2+3+1 |
| A-10 | Visualization | 4 required figures (crossing plot, curves, scatter, bars) | 7 | 2+2+2+1 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-3, A-5, A-6, A-8, A-9], Low(4-8): [A-2, A-4, A-7, A-10]
