# Architecture: H-E1 (EXISTENCE PoC)

**Date:** 2026-08-29
**Hypothesis:** H-E1 — Gradient subspace S aligns with spurious features (>70%) more than core features (<30%) at epoch 10.

Applied: gradient-accumulation-incremental-SVD pattern (from 02c experiment brief; Archon/Serena MCP unavailable in this session, same as Phase 2C).

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze (Serena MCP unavailable this session; no `src/` or base_hypothesis folder present)
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Structure (EXISTENCE minimal)

```
h-e1/code/
├── config.py
├── data.py
├── model.py
├── subspace.py
├── train.py
└── evaluate.py
```

---

## Modules

### config.py

**Dependencies**: None

```python
SEED = 42
BATCH_SIZE = 128
LR = 1e-3
MOMENTUM = 0.9
WEIGHT_DECAY = 1e-4
STEP_MILESTONES = [60, 75]
GAMMA = 0.1
NUM_EPOCHS = 90
ACCUMULATION_EPOCHS = 10
SUBSPACE_RANK = 50
LOG_EPOCHS = [5, 10, 45]
DATA_ROOT = "./data/waterbirds"
FIGURES_DIR = "./figures"
```

### data.py (`code/data.py`)

**Dependencies**: config, torchvision, wilds (or manual Waterbirds CSV)

```python
class WaterbirdsDataset(torch.utils.data.Dataset):
    def __init__(self, root: str, split: str, transform=None): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> tuple[Tensor, int, int]: ...  # (img, label, group)

def get_transforms(train: bool) -> Callable: ...
def get_dataloaders(root: str, batch_size: int) -> tuple[DataLoader, DataLoader, DataLoader]: ...
def get_direction_pairs(dataset) -> tuple[list[tuple], list[tuple]]:
    """Returns (spurious_pairs, core_pairs) index pairs for direction computation."""
```

### model.py (`code/model.py`)

**Dependencies**: torchvision

```python
def build_resnet50(num_classes: int = 2) -> nn.Module:
    """torchvision resnet50(pretrained=True), fc replaced with Linear(2048, num_classes)."""

def get_flat_grad(model: nn.Module) -> Tensor:
    """Concat all param.grad.view(-1) into single vector."""
```

### subspace.py (`code/subspace.py`)

**Dependencies**: torch

```python
class GradientSubspaceAccumulator:
    def __init__(self, rank_k: int, accumulation_epochs: int): ...
    def accumulate(self, model: nn.Module, epoch: int) -> None: ...
    def compute_subspace(self) -> Tensor:  # (num_params, rank_k)
    def measure_alignment(self, direction_vec: Tensor) -> float: ...

def compute_direction(model: nn.Module, dataloader, pairs: list[tuple]) -> Tensor:
    """Average gradient vector over given (img_a, img_b, label) pairs."""
```

### train.py (`code/train.py`)

**Dependencies**: config, data, model, subspace

```python
def train_loop() -> dict:
    """
    Full training loop, epochs 1-90.
    Accumulates gradients epochs 1..ACCUMULATION_EPOCHS.
    Computes subspace S at epoch 10.
    Logs spurious/core alignment at LOG_EPOCHS to CSV + console.
    Saves checkpoint at epoch 10.
    Returns dict of {epoch: {spurious_alignment, core_alignment}}.
    """

def save_checkpoint(model: nn.Module, path: str) -> None: ...
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: config, matplotlib

```python
def check_gate(results: dict) -> bool:
    """spurious_alignment[10] > 0.70 and core_alignment[10] < 0.30."""

def plot_bar_comparison(results: dict, epochs: list[int], out_path: str) -> None: ...
def plot_alignment_evolution(results: dict, out_path: str) -> None: ...
def plot_svd_variance(S: Tensor, singular_values: Tensor, out_path: str) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup + data loading | Waterbirds dataset, transforms, dataloaders, group labels | 10 | 3+3+2+2 |
| A-2 | Baseline model | ResNet-50 + FC replacement, flat-grad utility | 6 | 2+2+1+1 |
| A-3 | Gradient subspace accumulator | Incremental grad buffer + SVD subspace computation | 12 | 3+2+5+2 |
| A-4 | Direction computation | Spurious/core direction from group-paired gradients | 10 | 3+2+3+2 |
| A-5 | Training loop integration | Wire accumulator + direction calc into 90-epoch train loop | 13 | 3+4+3+3 |
| A-6 | Alignment logging + gate check | Cosine similarity logging at epochs 5/10/45, CSV, PoC gate | 8 | 2+2+2+2 |
| A-7 | Visualization | Bar chart, line plot, SVD variance/heatmap figures | 7 | 2+1+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-3, A-4, A-5], Low(4-8): [A-2, A-6, A-7]

---

## External Dependencies

None — green-field, no base hypothesis. All modules implemented from scratch using torchvision/wilds/torch stdlib.
