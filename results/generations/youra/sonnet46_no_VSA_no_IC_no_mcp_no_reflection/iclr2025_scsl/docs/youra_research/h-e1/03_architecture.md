---
hypothesis_id: h-e1
phase: 3
document_type: architecture
generated: 2026-08-31
---

# Architecture: H-E1
## Gradient Alignment Signal Existence Verification

Applied: per-sample-gradient-vmap-pattern (torch.func.vmap + grad for last-layer per-sample gradients)
Applied: erm-checkpoint-probe-pattern (inject diagnostic probe at fixed epochs without altering training loop)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. All primitives (torch.func, sklearn, group_DRO dataset loaders) are external well-documented libraries.

---

## System Overview

Single experiment script verifying whether per-sample last-layer gradient alignment ROC-AUC exceeds per-sample loss ROC-AUC as a predictor of spurious-minority group membership. Standard ERM training on ResNet-50 with probe injected at checkpoint epochs {1, 5, 10, 25, 50}.

**File structure** (LIGHT tier — minimal):
- `h-e1/experiment.py` — main entry point, all training + probing + evaluation logic
- `h-e1/data/dataset.py` — dataset loading wrappers around group_DRO ConfounderDataset
- `h-e1/config.py` — fixed configs for Waterbirds and CelebA
- `h-e1/results/` — JSON output
- `h-e1/figures/` — PNG outputs

---

## Modules

### Config (`h-e1/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass
from typing import List

@dataclass
class DatasetConfig:
    name: str                    # "waterbirds" | "celeba"
    root_dir: str
    target_name: str
    confounder_names: List[str]
    n_classes: int
    lr: float
    n_epochs: int
    batch_size: int = 32
    seed: int = 42
    checkpoint_epochs: List[int] = (1, 5, 10, 25, 50)

WATERBIRDS_CONFIG: DatasetConfig
CELEBA_CONFIG: DatasetConfig
```

---

### Dataset (`h-e1/data/dataset.py`)

**Dependencies**: group_DRO ConfounderDataset (external), DatasetConfig

```python
from torch.utils.data import DataLoader

def get_loaders(cfg: DatasetConfig) -> tuple[DataLoader, DataLoader, DataLoader]:
    """Returns (train_loader, val_loader, test_loader).
    train_loader yields (x, y, group_id) per batch.
    Preprocessing: Resize(256) -> CenterCrop(224) -> ToTensor -> ImageNet normalize.
    Train augmentation: RandomHorizontalFlip.
    """
    ...
```

---

### Experiment (`h-e1/experiment.py`)

**Dependencies**: Config, Dataset, torch.func, sklearn, matplotlib

```python
def set_seed(seed: int) -> None: ...

def build_model(n_classes: int, device: torch.device) -> nn.Module:
    """ResNet-50 ImageNet pretrained, last layer replaced to Linear(2048, n_classes)."""
    ...

def train_epoch(model: nn.Module, loader: DataLoader,
                optimizer: Optimizer, device: torch.device) -> float:
    """One ERM epoch. Returns mean cross-entropy loss."""
    ...

def compute_probe(model: nn.Module, loader: DataLoader,
                  device: torch.device) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """At checkpoint epoch: computes over FULL train set.
    Uses vmap(grad(loss_fn)) scoped to model.fc parameters only.
    Returns (alignment_scores, loss_scores, group_ids) each shape (N,).
    alignment_scores = negative cosine similarity (low alignment -> high predictor score).
    """
    ...

def evaluate_roc_auc(scores: np.ndarray, group_ids: np.ndarray,
                     minority_group_ids: set) -> float:
    """Binary label: 1 if group_id in minority_group_ids else 0.
    Returns sklearn roc_auc_score.
    """
    ...

def run_dataset(cfg: DatasetConfig, device: torch.device) -> list[dict]:
    """Full training loop for one dataset config.
    Injects probe at checkpoint_epochs. Returns list of result dicts."""
    ...

def save_results(results: list[dict], path: str) -> None:
    """Appends to h-e1/results/results.json."""
    ...

def plot_roc_auc_vs_epoch(results: list[dict]) -> None:
    """2x1 subplot: alignment_roc_auc and loss_roc_auc vs epoch.
    Saves to h-e1/figures/roc_auc_vs_epoch.png."""
    ...

def plot_score_distribution(probe_data: dict) -> None:
    """Violin plot at epoch 5: alignment scores by group.
    Saves to h-e1/figures/score_distribution_epoch5.png."""
    ...

def plot_roc_curves(probe_data: dict) -> None:
    """ROC curves at best alignment epoch per dataset.
    Saves to h-e1/figures/roc_curves_best_epoch.png."""
    ...

if __name__ == "__main__":
    main()
```

---

## File Dependency Graph

```
config.py
    └── data/dataset.py
            └── experiment.py (imports both; all logic here)
```

External: `group_dro/` (cloned separately), `torch.func`, `sklearn`, `matplotlib`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown | Type |
|----|------|-------------|------------|-----------|------|
| E1 | Project setup & data loading | Config dataclasses, get_loaders() wrapping group_DRO ConfounderDataset, verify group_id extraction for both datasets | 8 | 2+2+2+2 | data-pipeline |
| E2 | ERM trainer | build_model(), train_epoch(), checkpoint loop with seed, SGD optimizer per dataset config | 7 | 2+1+2+2 | training |
| E3 | Per-sample gradient probe | compute_probe() using vmap(grad()) scoped to model.fc; flatten weight+bias to (N,4098); cosine similarity with batch mean; memory-safe batched pass | 14 | 3+3+4+4 | model |
| E4 | ROC-AUC evaluation & results | evaluate_roc_auc(), spurious-minority binary labels per dataset, save_results() to JSON | 6 | 1+2+2+1 | evaluation |
| E5 | Visualization | Three plots: roc_auc_vs_epoch (mandatory), score_distribution_epoch5, roc_curves_best_epoch | 7 | 2+1+2+2 | evaluation |
| E6 | Integration & end-to-end run | Wire run_dataset() for both configs, seed consistency, results aggregation, smoke test on small subset | 8 | 2+2+2+2 | training |

**Distribution**: High(14-17): [E3], Medium(9-13): [], Low(4-8): [E1, E2, E4, E5, E6]

---

## Notes

- E3 is the only non-trivial task. The vmap scope must be restricted to `model.fc` params only — passing all ResNet-50 params to vmap will OOM. Pattern: extract `{k:v for k,v in model.named_parameters() if 'fc' in k}`, freeze backbone before probe pass.
- Waterbirds minority group IDs: {1, 2} (waterbird_on_land=1, landbird_on_water=2 per group_DRO metadata). CelebA minority: blond_male group = group_id 1 (blond=1, male=0 → group=(1,0) → index per group_DRO encoding).
- batch-mean gradient is computed per DataLoader batch (not global mean across all N) due to memory — this is a known approximation. # ponytail: per-batch mean gradient approximates global mean; upgrade to two-pass (store all gradients then mean) if alignment signal is noisy.
