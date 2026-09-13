# Architecture: H-M1 (MECHANISM)

**Hypothesis:** Spurious features produce stronger gradient signal than core features (gradient norm ratio > 1.5 in early epochs)

Applied: gradient-hook regional norm tracking pattern (pytorch-grad-cam forward/backward hooks + Waterbirds masks)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - H-E1 code (`h-e1/code/`) does not exist on disk (H-E1 was spec-only through 04_validation.md); no existing implementation to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. H-E1's `03_architecture.md` used only as a design reference (dataset/model patterns), not as verified code.

---

## File Structure

- `h-m1/code/data.py` - Waterbirds dataset + mask loading (reused pattern from H-E1)
- `h-m1/code/model.py` - ResNet-50 baseline + GradientNormTracker
- `h-m1/code/train.py` - training loop with per-epoch gradient norm logging
- `h-m1/code/config.py` - fixed hyperparameters
- `h-m1/code/evaluate.py` - ratio aggregation + gate check
- `h-m1/code/visualize.py` - figures (gate bar chart, ratio trajectory, heatmaps)
- `h-m1/figures/` - output plots
- `h-m1/results/` - metrics CSV/JSON, checkpoints

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

**Dependencies**: torchvision.models

```python
def build_resnet50(num_classes: int = 2) -> nn.Module: ...

class GradientNormTracker:
    def __init__(self, model: nn.Module, target_layer): ...
    def _save_activation(self, module, input, output) -> None: ...
    def _save_gradient(self, module, grad_input, grad_output) -> None: ...
    def compute_regional_gradient_norms(
        self, bird_mask: Tensor, background_mask: Tensor
    ) -> tuple[float, float]: ...
    # returns: (core_norm, spurious_norm), masks resized to activation H',W'
    def remove_hooks(self) -> None: ...
```

### Trainer (`train.py`)

**Dependencies**: model.py, data.py, config.py

```python
def train_one_epoch(
    model, tracker: GradientNormTracker, loader, optimizer, criterion, device
) -> tuple[float, float, float]: ...
# returns: (avg_loss, mean_core_norm, mean_spurious_norm) for the epoch

def run_training(config: Config, seed: int) -> list[dict]: ...
# returns: per-epoch records {epoch, core_norm, spurious_norm, ratio}

def main() -> None: ...
```

### Config (`config.py`)

```python
@dataclass
class Config:
    seeds: tuple[int, ...] = (42, 123, 456)
    batch_size: int = 128
    lr: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 1e-4
    step_sizes: tuple[int, ...] = (60, 120)
    gamma: float = 0.1
    epochs: int = 50
    data_root: str = "./data/waterbirds_v1.0"
    output_dir: str = "./h-m1/results"
```

### Evaluate (`evaluate.py`)

**Dependencies**: train.py output (per-seed epoch records)

```python
def aggregate_ratios(records: list[dict]) -> dict:
    # per-epoch mean ratio across batches within one seed run
def early_epoch_ratio(records: list[dict], early_range: tuple[int, int] = (1, 10)) -> float: ...
def ratio_trend_decreasing(records: list[dict]) -> bool: ...
def check_gate(all_seed_records: dict[int, list[dict]]) -> dict:
    # returns {"pass": bool, "early_ratio": float, "decreasing": bool, "per_seed": dict}
def save_metrics(all_seed_records: dict[int, list[dict]], output_dir: str) -> None: ...
```

### Visualize (`visualize.py`)

**Dependencies**: matplotlib, evaluate.py output

```python
def plot_gate_bar_chart(gate_result: dict, save_path: str) -> None: ...
def plot_ratio_trajectory(all_seed_records: dict[int, list[dict]], save_path: str) -> None: ...
def plot_norm_comparison(records: list[dict], save_path: str) -> None: ...
def plot_gradient_heatmaps(model, tracker, samples, epochs: list[int], save_path: str) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Dataset setup | Download Waterbirds, implement WaterbirdsDataset with bird/background masks | 10 | 3+2+3+2 |
| A-2 | Baseline model | ResNet-50 pretrained + fc replacement | 4 | 1+1+1+1 |
| A-3 | GradientNormTracker | Forward/backward hooks on layer4, regional norm computation | 12 | 3+3+4+2 |
| A-4 | Training loop | Per-batch gradient norm capture integrated into training | 10 | 2+3+3+2 |
| A-5 | Multi-seed runner | Run training across 3 seeds, collect per-epoch records | 6 | 1+2+1+2 |
| A-6 | Evaluation | Ratio aggregation, early-epoch check, trend check, gate | 8 | 2+2+3+1 |
| A-7 | Visualization | Gate bar chart, ratio trajectory, norm comparison, heatmaps | 8 | 3+1+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-4, A-6, A-7], Low(4-8): [A-2, A-5], A-3: 12 (Medium)
