# Architecture: H-E1 (EXISTENCE / PoC)

**Hypothesis:** NFN R² > MLP-Matched R² + 0.05 at N=1K
**Type:** EXISTENCE — minimal architecture to test "does it work?"

Applied: PyTorch standard training loop pattern (optimizer/scheduler/loss step)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. H-E1 is the foundation hypothesis (no base_hypothesis folder, no prior code).

---

## File Structure

```
h-e1/code/
  data.py         # download, filter, split, normalize Model Zoo subset
  model.py        # NFNRegressor + MLPMatched
  train.py        # training loop for both models
  evaluate.py      # R2 comparison, figures, results JSON
  config.py        # single fixed config (hyperparams, paths, seed)
h-e1/checkpoints/   # saved model weights
h-e1/figures/       # bar chart, scatter, residual, learning curves
h-e1/results.json
```

---

## Modules

### config.py

```python
@dataclass
class Config:
    seed: int = 0
    n_models: int = 1000
    train_frac: float = 0.8
    lr: float = 1e-3
    weight_decay: float = 1e-4
    epochs: int = 50
    batch_size: int = 32
    nfn_channels: int = 32
    mlp_hidden_dim: int = 256
    mlp_num_layers: int = 3
    checkpoint_dir: str = "h-e1/checkpoints"
    figure_dir: str = "h-e1/figures"
```

### data.py (`h-e1/code/data.py`)

**Dependencies**: config.py, nfn.common

```python
def download_model_zoo(dest_dir: str) -> str: ...
def load_models(zoo_dir: str, n: int) -> list[dict]:  # list of state_dicts + labels
def filter_homogeneous(models: list[dict]) -> list[dict]: ...
def normalize_weights(models: list[dict]) -> list[dict]: ...
def split_train_test(models: list[dict], train_frac: float, seed: int) -> tuple[list, list]: ...

class WeightSpaceDataset(torch.utils.data.Dataset):
    def __init__(self, models: list[dict]): ...
    def __getitem__(self, idx: int) -> tuple[dict, float]: ...
    def __len__(self) -> int: ...

def make_collate_fn(network_spec) -> Callable:  # builds WeightSpaceFeatures via state_dict_to_tensors
```

### model.py (`h-e1/code/model.py`)

**Dependencies**: nfn (pip package)

```python
class NFNRegressor(nn.Module):
    def __init__(self, network_spec, nfn_channels: int = 32): ...
    def forward(self, wsfeat: WeightSpaceFeatures) -> Tensor: ...  # (B, 1)

class MLPMatched(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 256, num_layers: int = 3): ...
    def forward(self, x: Tensor) -> Tensor: ...  # (B, 1)

def flatten_weights(wsfeat: WeightSpaceFeatures) -> Tensor:  # concat all weights/biases -> (B, D)
def count_params(model: nn.Module) -> int: ...
def match_mlp_dim(nfn_param_count: int, hidden_dim: int, num_layers: int) -> int:  # search input_dim
```

### train.py (`h-e1/code/train.py`)

**Dependencies**: model.py, data.py, config.py

```python
def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    cfg: Config,
    model_kind: Literal["nfn", "mlp"],
) -> dict:  # {"train_loss": [...], "val_loss": [...]}

def build_optimizer(model: nn.Module, cfg: Config) -> AdamW: ...
def build_scheduler(optimizer, cfg: Config) -> CosineAnnealingLR: ...
def set_seed(seed: int) -> None: ...
```

### evaluate.py (`h-e1/code/evaluate.py`)

**Dependencies**: sklearn.metrics, model.py

```python
def compute_r2(model: nn.Module, loader: DataLoader, model_kind: str) -> tuple[np.ndarray, np.ndarray, float]:
    # returns (preds, targets, r2)

def compare_models(nfn_result: tuple, mlp_result: tuple) -> dict:
    # {"nfn_r2":..., "mlp_r2":..., "difference":..., "hypothesis_supported": bool}

def plot_r2_comparison(nfn_r2: float, mlp_r2: float, threshold: float, out_path: str) -> None: ...
def plot_scatter(preds: np.ndarray, targets: np.ndarray, title: str, out_path: str) -> None: ...
def plot_residuals(preds: np.ndarray, targets: np.ndarray, title: str, out_path: str) -> None: ...
def plot_learning_curves(history: dict, title: str, out_path: str) -> None: ...
def save_results_json(results: dict, out_path: str) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Download Model Zoo subset, filter, normalize, split, Dataset/collate | 12 | 3+3+4+2 |
| A-2 | NFN model | Implement NFNRegressor with nfn package layers | 10 | 3+3+3+1 |
| A-3 | MLP baseline | Implement MLPMatched with param-matched dim search | 6 | 2+1+2+1 |
| A-4 | Training loop | AdamW + cosine scheduler training for both models | 8 | 2+3+2+1 |
| A-5 | Evaluation & R2 | Compute R2, mechanism verification, comparison dict | 6 | 2+2+1+1 |
| A-6 | Visualization | Bar chart, scatter, residual, learning curve figures | 5 | 2+1+1+1 |
| A-7 | Run experiment | Wire pipeline end-to-end, save checkpoints/results JSON | 7 | 2+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-2, A-4], Low(4-8): [A-3, A-5, A-6, A-7]

---

## Notes

- Single fixed seed (PoC scope) — no multi-seed loop.
- No ablation modules — only NFN vs MLP-Matched per EXISTENCE rules.
- `network_spec` derived once from a sample state_dict via `network_spec_from_wsfeat`, shared across NFN construction and collate_fn.
