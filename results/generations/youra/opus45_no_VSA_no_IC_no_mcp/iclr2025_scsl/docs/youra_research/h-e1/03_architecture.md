# Architecture: H-E1 (EXISTENCE / PoC)

**Hypothesis:** Spurious features dominate earlier than core features (GradCAM ratio > 1 before epoch 10)

Applied: GradCAM epoch-wise attribution tracking pattern (pytorch-grad-cam standard usage)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis or existing codebase.

---

## File Structure

- `h-e1/code/data.py` - Waterbirds dataset + mask loading
- `h-e1/code/model.py` - ResNet-50 baseline + GradCAM attribution tracker
- `h-e1/code/train.py` - training loop with per-epoch attribution logging
- `h-e1/code/config.py` - fixed hyperparameters
- `h-e1/code/evaluate.py` - dominance epoch computation + gate check
- `h-e1/code/visualize.py` - figures (ratio-over-epochs, gate bar chart, CAM overlays)
- `h-e1/figures/` - output plots
- `h-e1/results/` - metrics CSV/JSON, checkpoints

---

## Modules

### WaterbirdsDataset (`data.py`)

**Dependencies**: torchvision, PIL, numpy

```python
class WaterbirdsDataset(Dataset):
    def __init__(self, root_dir: str, split: str, transform=None): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> tuple[Tensor, int, Tensor, Tensor]: ...
    # returns: image, label, spurious_mask (H,W), core_mask (H,W)

def get_dataloaders(root_dir: str, batch_size: int) -> dict[str, DataLoader]: ...
def download_waterbirds(root_dir: str) -> None: ...
```

### Model (`model.py`)

**Dependencies**: torchvision.models, pytorch-grad-cam

```python
def build_resnet50(num_classes: int = 2) -> nn.Module: ...

class AttributionTracker:
    def __init__(self, model: nn.Module, target_layer): ...
    def compute_attribution_ratio(self, dataloader, device) -> float: ...
    def log_epoch(self, epoch: int, dataloader, device) -> float: ...
    epoch_ratios: list[tuple[int, float]]
```

### Trainer (`train.py`)

**Dependencies**: model.py, data.py, config.py

```python
def train_one_epoch(model, loader, optimizer, criterion, device) -> float: ...
def run_training(config: Config) -> AttributionTracker: ...
def main() -> None: ...
```

### Config (`config.py`)

```python
@dataclass
class Config:
    seed: int = 42
    batch_size: int = 128
    lr: float = 0.01
    momentum: float = 0.9
    weight_decay: float = 1e-4
    step_size: int = 20
    gamma: float = 0.1
    epochs: int = 50
    attribution_subset_size: int = 500
    data_root: str = "./data/waterbirds_v1.0"
    output_dir: str = "./h-e1/results"
```

### Evaluate (`evaluate.py`)

**Dependencies**: model.AttributionTracker output

```python
def dominance_epoch(epoch_ratios: list[tuple[int, float]]) -> int | None: ...
def check_gate(epoch_ratios: list[tuple[int, float]]) -> dict:
    # returns {"pass": bool, "dominance_epoch": int, "ratio_at_dominance": float}
def save_metrics(epoch_ratios, output_dir: str) -> None: ...
```

### Visualize (`visualize.py`)

**Dependencies**: matplotlib, evaluate.py output

```python
def plot_ratio_over_epochs(epoch_ratios, save_path: str) -> None: ...
def plot_gate_comparison(gate_result: dict, save_path: str) -> None: ...
def plot_cam_overlays(model, samples, epochs: list[int], save_path: str) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Dataset setup | Download Waterbirds, implement WaterbirdsDataset with masks | 10 | 3+2+3+2 |
| A-2 | Baseline model | ResNet-50 pretrained + fc replacement | 4 | 1+1+1+1 |
| A-3 | GradCAM tracker | AttributionTracker with ratio computation | 9 | 2+3+3+1 |
| A-4 | Training loop | Full training + per-epoch attribution logging | 8 | 2+2+2+2 |
| A-5 | Evaluation | Dominance epoch + gate check + metrics saving | 5 | 1+1+2+1 |
| A-6 | Visualization | Ratio plot, gate bar chart, CAM overlays | 6 | 2+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-3], Low(4-8): [A-2, A-4, A-5, A-6]
