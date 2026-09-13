# Architecture: H-M1 (Layer-wise Structure Advantage)

**Applied**: Encoder-Regressor pattern with paired-method comparison harness (StatNN baseline vs Hyper-Representations layer-wise encoding)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field - no existing code to analyze (first implementation in causal chain; H-E1 only validated dataset, produced no reusable code module)
**Analyzed Path**: N/A
**Findings**: New implementation from scratch, following interfaces specified in `02c_experiment_brief.md`

---

## Module Structure

```
h-m1/code/
├── data.py
├── models.py
├── train.py
├── evaluate.py
├── run_experiment.py
└── config.py
```

### data.py

**Dependencies**: None (torch, zenodo_get)

```python
def download_model_zoo(data_dir: str = "data/") -> None: ...
def load_model_zoo(data_path: str = "data/dataset_cifar_small_hyp_fix.pt") -> tuple[list, list, list]: ...
def extract_weights_and_accuracy(sample: dict) -> tuple[dict, float]: ...

class ModelZooDataset(torch.utils.data.Dataset):
    def __init__(self, samples: list): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> tuple[dict, float]: ...

def collate_weights(batch: list[tuple[dict, float]]) -> tuple[list[dict], torch.Tensor]: ...
def make_dataloaders(train, val, test, batch_size: int = 256) -> tuple[DataLoader, DataLoader, DataLoader]: ...
```

### models.py

**Dependencies**: None (torch, torch.nn)

```python
def flatten_weights(weights_dict: dict) -> torch.Tensor: ...
def layer_wise_stats(weights_dict: dict) -> torch.Tensor: ...  # mean,std,min,max per layer, sorted keys

class FlattenMLPEncoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 256, embed_dim: int = 128): ...
    def forward(self, weights_flat: torch.Tensor) -> torch.Tensor: ...

class LayerWiseEncoder(nn.Module):
    def __init__(self, num_layers: int, stats_per_layer: int = 4, hidden_dim: int = 256, embed_dim: int = 128): ...
    def forward(self, weights_dict: dict) -> torch.Tensor: ...

class AccuracyPredictor(nn.Module):
    def __init__(self, embed_dim: int = 128, hidden_dim: int = 64): ...
    def forward(self, embedding: torch.Tensor) -> torch.Tensor: ...

class FullModel(nn.Module):
    """Wraps encoder + AccuracyPredictor, dispatches encoder type."""
    def __init__(self, encoder: nn.Module, predictor: AccuracyPredictor): ...
    def forward(self, weights_input) -> torch.Tensor: ...
```

### train.py

**Dependencies**: models.py, data.py

```python
def set_seed(seed: int) -> None: ...

def train_one_epoch(model: nn.Module, loader: DataLoader, optimizer, device) -> float: ...
def validate(model: nn.Module, loader: DataLoader, device) -> float: ...

def train_model(
    model: nn.Module, train_loader: DataLoader, val_loader: DataLoader,
    lr: float = 1e-3, weight_decay: float = 1e-4, max_epochs: int = 50,
    early_stop_patience: int = 10, device: str = "cuda"
) -> tuple[nn.Module, dict]:  # returns best model + loss history
    ...

def save_checkpoint(model: nn.Module, path: str) -> None: ...
```

### evaluate.py

**Dependencies**: models.py (types only)

```python
def predict(model: nn.Module, loader: DataLoader, device) -> tuple[np.ndarray, np.ndarray]: ...  # preds, targets
def compute_pearson(preds: np.ndarray, targets: np.ndarray) -> dict: ...  # {'pearson_r', 'p_value'}
def compare_methods(flatten_results: list[float], layerwise_results: list[float]) -> dict: ...  # {'delta_r','t_stat','p_value'}

def plot_gate_metrics(flatten_r: list[float], layerwise_r: list[float], save_path: str) -> None: ...
def plot_scatter(preds: np.ndarray, targets: np.ndarray, method_name: str, save_path: str) -> None: ...
def plot_per_seed(flatten_r: list[float], layerwise_r: list[float], save_path: str) -> None: ...
def plot_loss_curves(history: dict, method_name: str, save_path: str) -> None: ...
```

### run_experiment.py

**Dependencies**: data.py, models.py, train.py, evaluate.py, config.py

```python
def run_seed(method: str, seed: int, train_loader, val_loader, test_loader, cfg) -> dict: ...  # {'pearson_r','history'}
def main() -> None:  # orchestrates 5 seeds x 2 methods, gate check, figure generation, results.json
    ...
```

### config.py

**Dependencies**: None

```python
@dataclass
class Config:
    data_path: str = "data/dataset_cifar_small_hyp_fix.pt"
    batch_size: int = 256
    lr: float = 1e-3
    weight_decay: float = 1e-4
    max_epochs: int = 50
    early_stop_patience: int = 10
    seeds: list = field(default_factory=lambda: [0, 1, 2, 3, 4])
    hidden_dim: int = 256
    embed_dim: int = 128
    predictor_hidden: int = 64
    device: str = "cuda"
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data download + loading | Zenodo download, load .pt, train/val/test split extraction | 8 | 2+2+2+2 |
| A-2 | Dataset/DataLoader + collate | Custom Dataset, variable-shape weight collate_fn, batch_size=256 | 9 | 2+2+3+2 |
| A-3 | Flatten+MLP encoder | flatten_weights fn + FlattenMLPEncoder module | 6 | 2+1+2+1 |
| A-4 | Layer-wise encoder | layer_wise_stats fn + LayerWiseEncoder module (per-layer mean/std/min/max) | 10 | 3+1+4+2 |
| A-5 | Regressor head + FullModel wrapper | AccuracyPredictor + dispatch wrapper for both encoders | 5 | 2+2+1+0 |
| A-6 | Training loop | train/val loop, AdamW, ReduceLROnPlateau, early stopping, checkpointing | 11 | 3+2+3+3 |
| A-7 | Evaluation metrics | Pearson r, paired t-test, delta_r comparison | 6 | 2+1+2+1 |
| A-8 | Visualization suite | gate bar chart, scatter, per-seed line plot, loss curves | 9 | 3+1+2+3 |
| A-9 | Multi-seed orchestration | run_experiment.py: 5 seeds x 2 methods, results aggregation, gate decision | 12 | 3+4+2+3 |
| A-10 | Config + reproducibility | Config dataclass, seed setting, deterministic ops | 4 | 1+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4, A-6, A-8, A-9], Low(4-8): [A-1, A-3, A-5, A-7, A-10]

---

## Notes

- No External Dependencies section: green-field, no base hypothesis code to reuse.
- Weight tensors vary in shape per model → collate_fn must return list[dict] (no stacking), batching handled per-sample inside encoders.
- Both encoders share identical `AccuracyPredictor` and training loop for fair comparison.
