# Architecture: H-M2 (Update-Norm Parity Intervention)

**Type:** MECHANISM | **Applied:** standard SGD training-loop-intervention pattern (KB: no group-robustness-specific match; used PyTorch grad-utils pattern from experiment brief)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-E1)
**Status:** Patterns found from base code — reused verbatim where compatible
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Findings:**
- `model.py::create_random_model(seed)` returns `resnet50` + `Linear(2048,2)`, cast `.double()` — reusable as-is, but H-M2 needs **trained** (not random-init) models with real forward/backward, so add `pretrained=True` variant.
- `data.py::WaterbirdDataset` already implements 4-group loading (`group = 2*y + place`), ImageNet transforms, matches FR-1 exactly — reuse directly.
- `sharpness.py::compute_sharpness_ratio(model, dataset)` computes power-iteration Hessian trace ratio minority/majority — reuse directly for FR-5.1.
- H-E1 has no training loop (init-only SR study) — H-M2 must add training infrastructure net new.

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| WaterbirdDataset, get_group_loader | `from data import WaterbirdDataset, get_group_loader` | `h-e1/code/data.py` |
| compute_sharpness_ratio | `from sharpness import compute_sharpness_ratio` | `h-e1/code/sharpness.py` |
| create_random_model (reference only, adapt for pretrained) | `from model import create_random_model` | `h-e1/code/model.py` |

**Verified from**: `h-m2/code` will copy/adapt `data.py` and `sharpness.py` unmodified; `model.py` extended with pretrained loader.

---

## File Structure

- `h-m2/code/config.py` — hyperparams, group defs, ablation variant enum
- `h-m2/code/data.py` — copied from H-E1 (WaterbirdDataset, get_group_loader) + train DataLoader w/ group-aware batching
- `h-m2/code/model.py` — pretrained ResNet-50 builder
- `h-m2/code/parity.py` — UpdateNormParityTrainer (core mechanism)
- `h-m2/code/sharpness.py` — copied from H-E1 (compute_sharpness_ratio, unchanged)
- `h-m2/code/train.py` — training loop (ERM / Full Parity / Partial Parity variants)
- `h-m2/code/metrics.py` — WGA, per-group accuracy
- `h-m2/code/stats.py` — cross-seed aggregation + significance test
- `h-m2/code/visualize.py` — 4 required figures
- `h-m2/code/main.py` — orchestrates: train all variants x 5 seeds -> eval -> stats -> figures

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
@dataclass
class Config:
    data_root: str = "./data/waterbird_complete95_forest2water2"
    img_size: int = 224
    batch_size: int = 128
    lr: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 0.0001
    epochs: int = 100
    minority_groups: tuple = (1, 2)
    majority_groups: tuple = (0, 3)
    num_classes: int = 2
    num_power_iter: int = 20
    seeds: tuple = (0, 1, 2, 3, 4)
    variants: tuple = ("baseline", "full_parity", "partial_parity")
    partial_scale: float = 0.5
    sr_eval_epoch: int = 50
    early_stop_patience: int = 10
```

### Model (`model.py`)

**Dependencies**: config

```python
def create_pretrained_model(seed: int) -> nn.Module: ...
```

### Data (`data.py`)

**Dependencies**: config
Reused from H-E1: `WaterbirdDataset(root, split)`, `get_group_loader(dataset, group_id, batch_size)`.
Add:
```python
def get_train_loader(dataset: WaterbirdDataset, batch_size: int) -> DataLoader: ...
```

### Parity Intervention (`parity.py`)

**Dependencies**: torch

```python
class UpdateNormParityTrainer:
    def __init__(self, model: nn.Module, num_groups: int = 4, scale: float = 1.0): ...
    def compute_group_grad_norms(self, group_labels: Tensor) -> dict: ...
    def apply_parity_scaling(self, group_labels: Tensor) -> dict: ...  # returns norms logged
```
`scale=1.0` -> Full Parity, `scale=0.5` -> Partial Parity, `scale=0.0`/trainer unused -> Baseline.

### Sharpness (`sharpness.py`)

**Dependencies**: data, config (unchanged from H-E1)

```python
def compute_sharpness_ratio(model: nn.Module, dataset: WaterbirdDataset) -> float: ...
```

### Metrics (`metrics.py`)

**Dependencies**: sklearn.metrics

```python
def per_group_accuracy(y_true, y_pred, groups) -> dict: ...
def worst_group_accuracy(y_true, y_pred, groups) -> float: ...
```

### Train (`train.py`)

**Dependencies**: model, data, parity, sharpness, metrics, config

```python
def train_one_variant(variant: str, seed: int, cfg: Config) -> dict: ...
    # variant in {"baseline","full_parity","partial_parity"}
    # returns {"sr_by_epoch": [...], "wga": float, "per_group_acc": dict, "update_norms": list}
def evaluate(model, loader) -> tuple:  # (y_true, y_pred, groups)
```

### Stats (`stats.py`)

**Dependencies**: scipy.stats, numpy

```python
def aggregate_across_seeds(results: list[dict]) -> dict: ...
def sr_significance_test(baseline_srs: list, parity_srs: list) -> dict:  # p-value
```

### Visualize (`visualize.py`)

**Dependencies**: matplotlib

```python
def plot_sr_trajectory(results_by_variant: dict, out_path: str): ...
def plot_group_accuracy_trajectories(results_by_variant: dict, out_path: str): ...
def plot_update_norm_boxplot(results_by_variant: dict, out_path: str): ...
def plot_wga_comparison(results_by_variant: dict, out_path: str): ...
```

### Main (`main.py`)

**Dependencies**: all modules above

```python
def main(): ...  # loop variants x seeds -> train_one_variant -> aggregate -> stats -> figures -> save results/summary.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Adapt WaterbirdDataset + group-aware train loader | 8 | 2+2+2+2 |
| A-2 | Pretrained model builder | ResNet-50 pretrained + FC(2048,2) | 4 | 1+1+1+1 |
| A-3 | Parity intervention module | UpdateNormParityTrainer (grad norm compute + scale) | 14 | 4+2+5+3 |
| A-4 | Training loop (ERM baseline) | SGD, CE loss, early stop on WGA | 10 | 3+2+3+2 |
| A-5 | Training loop integration (parity variants) | Insert parity hook, log activation | 12 | 3+3+3+3 |
| A-6 | SR + metrics wiring | Reuse H-E1 sharpness.py, per-epoch SR eval, WGA/per-group acc | 9 | 2+3+2+2 |
| A-7 | Ablation orchestration | Run 3 variants x 5 seeds, save per-run results | 10 | 3+3+2+2 |
| A-8 | Statistical validation | Mean±std, significance test SR baseline vs parity | 7 | 2+2+2+1 |
| A-9 | Visualization suite | 4 required figures | 8 | 2+2+2+2 |
| A-10 | End-to-end orchestration + success criteria check | main.py, gate check (SR<=1.1 vs >1.2, WGA no regression) | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-1, A-4, A-5, A-6, A-7], Low(4-8): [A-2, A-8, A-9, A-10]
