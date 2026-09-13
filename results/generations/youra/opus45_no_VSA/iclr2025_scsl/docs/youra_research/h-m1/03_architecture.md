# Architecture: H-M1

**Applied**: PyTorch per-sample gradient (torch.func.vmap+grad) + scipy lagged cross-correlation pattern

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base_hypothesis code reuse required (H-E1 is a separate init-only check, no shared training code).

---

## File Organization

```
h-m1/code/
├── config.py
├── data.py
├── model.py
├── gradient_ratio.py
├── sharpness_ratio.py
├── cross_correlation.py
├── train.py
├── evaluate.py
└── visualize.py
```

---

## Module Interfaces

### config.py

```python
@dataclass
class Config:
    seed: int
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    batch_size: int = 128
    epochs: int = 50
    step_size: int = 10
    gamma: float = 0.1
    max_lag: int = 5
    device: str = "cuda"
```

### data.py (`data.py`)

**Dependencies**: None

```python
def load_waterbirds(split: str) -> torch.utils.data.Dataset: ...
def get_dataloader(dataset, batch_size: int, shuffle: bool) -> DataLoader: ...
# Dataset __getitem__ returns (image, label, group_id)
```

### model.py

**Dependencies**: None

```python
def build_resnet50(num_classes: int = 2) -> nn.Module: ...
```

### gradient_ratio.py

**Dependencies**: model.py

```python
def compute_per_sample_grad_norms(model: nn.Module, data: Tensor, targets: Tensor,
                                   loss_fn: Callable) -> Tensor: ...  # (batch,)
def compute_gradient_ratio(grad_norms: Tensor, group_labels: Tensor,
                            majority_groups=(0, 3)) -> float: ...
```

### sharpness_ratio.py

**Dependencies**: model.py

```python
def hvp_top_eigenvalue(model: nn.Module, data_loader: DataLoader,
                        loss_fn: Callable, num_iters: int = 20) -> float: ...
    # power iteration via torch.autograd.functional.vhp
def compute_sharpness_ratio(model: nn.Module, minority_loader: DataLoader,
                             majority_loader: DataLoader, loss_fn: Callable) -> float: ...
```

### cross_correlation.py

**Dependencies**: None

```python
def compute_lagged_cross_correlation(r_series: np.ndarray, sr_series: np.ndarray,
                                      max_lag: int = 5) -> tuple[int, np.ndarray, np.ndarray]:
    ...  # returns (tau, corr_values, lags)
def bootstrap_ci_tau(tau_per_seed: list[int], confidence: float = 0.95) -> tuple[float, float, float]:
    ...  # returns (mean, ci_low, ci_high)
```

### train.py

**Dependencies**: config, data, model, gradient_ratio, sharpness_ratio

```python
def train_one_seed(cfg: Config) -> dict:
    ...  # returns {"r_series": np.ndarray, "sr_series": np.ndarray}
def main(): ...  # loops over 5 seeds, saves per-seed series to disk
```

### evaluate.py

**Dependencies**: cross_correlation, train outputs

```python
def evaluate_all_seeds(results_dir: str, max_lag: int = 5) -> dict:
    ...  # returns {"tau_per_seed": list, "tau_mean": float, "tau_ci": tuple, "pass": bool}
```

### visualize.py

**Dependencies**: matplotlib, evaluate outputs

```python
def plot_gate_metrics(lags: np.ndarray, corr_per_seed: list[np.ndarray], save_path: str): ...
def plot_time_series(r_series: np.ndarray, sr_series: np.ndarray, save_path: str): ...
def plot_tau_per_seed(tau_per_seed: list[int], save_path: str): ...
```

---

## External Dependencies (Base Hypothesis)

Not applicable — H-E1 validated SR≈1 at init as a standalone check; no shared code artifacts to import.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Load Waterbirds, 4-group labels, transforms | 8 | 2+2+2+2 |
| A-2 | Model setup | ResNet-50 + fc replacement | 4 | 1+1+1+1 |
| A-3 | Per-sample gradients | vmap+grad norms, majority/minority ratio | 15 | 4+3+5+3 |
| A-4 | Sharpness ratio (Hessian) | Power iteration HVP top eigenvalue, per-group | 17 | 4+3+5+5 |
| A-5 | Training loop | SGD/StepLR, per-epoch r_t/SR_t logging, 5 seeds | 13 | 3+4+3+3 |
| A-6 | Cross-correlation analysis | scipy lag correlation, τ extraction, bootstrap CI | 10 | 2+2+4+2 |
| A-7 | Evaluation aggregation | Aggregate seeds, gate pass/fail check | 6 | 2+1+2+1 |
| A-8 | Visualization | Gate plot, dual-axis time series, per-seed τ plot | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3, A-4], Medium(9-13): [A-1, A-5, A-6], Low(4-8): [A-2, A-7, A-8]
