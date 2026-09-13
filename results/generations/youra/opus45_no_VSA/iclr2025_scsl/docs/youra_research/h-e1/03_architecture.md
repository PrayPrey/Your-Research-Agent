# Architecture: H-E1 (EXISTENCE / PoC)

**Hypothesis:** SR₀ ≈ 1.0 at initialization (no intrinsic curvature asymmetry)
**Type:** EXISTENCE — measurement-only, no training
**Applied:** No matching KB pattern found (generic PyTorch/diffusion results only) — implementation follows brief's power-iteration + group_DRO approach.

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch; no base hypothesis, no prior codebase.

---

## File Structure

```
h-e1/code/
  data.py        # Waterbirds dataset + group-wise loaders
  sharpness.py    # HVP + power iteration + SR computation
  model.py         # ResNet-50 factory (random-init variant)
  main.py          # orchestration: seeds -> SR -> stats -> figure
  config.py        # constants (paths, seeds, iterations)
results/sr_values.json
figures/sr_comparison.png
```

---

## Modules

### config.py

```python
DATA_ROOT: str = "./data/waterbird_complete95_forest2water2"
SEEDS: list[int] = [0, 1, 2, 3, 4]
NUM_POWER_ITER: int = 20
MINORITY_GROUPS: list[int] = [1, 2]
MAJORITY_GROUPS: list[int] = [0, 3]
BATCH_SIZE: int = 32
IMG_SIZE: int = 224
```

### data.py (`h-e1/code/data.py`)

**Dependencies**: config, torchvision, PIL

```python
class WaterbirdDataset(torch.utils.data.Dataset):
    def __init__(self, root: str, split: str = "train"): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> tuple[Tensor, int, int]: ...  # (img, label, group)

def get_group_loader(dataset: WaterbirdDataset, group_id: int, batch_size: int) -> DataLoader: ...
```

### model.py (`h-e1/code/model.py`)

**Dependencies**: torchvision

```python
def create_random_model(seed: int) -> torch.nn.Module:
    """ResNet-50, random init (pretrained=False), fc replaced with Linear(2048, 2)."""
```

### sharpness.py (`h-e1/code/sharpness.py`)

**Dependencies**: model, data, config

```python
def compute_loss(model: nn.Module, loader: DataLoader) -> Tensor: ...

def hessian_vector_product(model: nn.Module, loader: DataLoader, v: Tensor) -> Tensor: ...

def compute_group_sharpness(model: nn.Module, loader: DataLoader, num_iterations: int = 20) -> float:
    """Power iteration for top Hessian eigenvalue (lambda_max)."""

def compute_sharpness_ratio(model: nn.Module, dataset: WaterbirdDataset) -> float:
    """SR = mean(sharpness[minority]) / mean(sharpness[majority])."""
```

### main.py (`h-e1/code/main.py`)

**Dependencies**: config, model, data, sharpness, numpy, scipy, matplotlib

```python
def run_seed(seed: int, dataset: WaterbirdDataset) -> float: ...

def main() -> None:
    """
    For each seed: create_random_model -> compute_sharpness_ratio -> collect.
    Compute mean + 95% CI (scipy.stats.t.interval).
    Write results/sr_values.json, figures/sr_comparison.png.
    Assert gate: 0.9 <= mean_sr <= 1.1 and CI includes 1.0 (report only, non-fatal).
    """
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Dataset setup | WaterbirdDataset + group loaders (data.py) | 8 | 2+2+2+2 |
| A-2 | Model factory | create_random_model with seeding (model.py) | 4 | 1+1+1+1 |
| A-3 | HVP + power iteration | compute_group_sharpness via autograd (sharpness.py) | 12 | 3+2+4+3 |
| A-4 | SR computation | compute_sharpness_ratio, group aggregation | 6 | 2+2+1+1 |
| A-5 | Multi-seed orchestration | main.py loop over 5 seeds, error handling | 6 | 2+2+1+1 |
| A-6 | Stats + gate check | mean/95% CI via scipy, gate assertion, JSON output | 5 | 1+1+2+1 |
| A-7 | Visualization | sr_comparison.png with error bars + SR=1.0 line | 4 | 1+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3], Low(4-8): [A-1, A-2, A-4, A-5, A-6, A-7]

---

## Notes

- No "proposed model" — measurement-only at random init (per brief).
- No training loop needed (0 epochs).
- Double precision recommended for HVP numerical stability (NFR risk mitigation).
