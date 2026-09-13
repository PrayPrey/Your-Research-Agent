# Architecture: H-E1 — Sharpness Anisotropy in SSL Loss Landscapes

**Hypothesis:** H-E1 (EXISTENCE / PoC)
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Applied:** Standard DL Experiment Pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. All SSL implementations (SimCLR, MoCo-v2, DINO) adapted from reference repos (izmailovpavel/spurious_feature_learning, facebookresearch/moco, facebookresearch/dino). SAM perturbation from davda54/sam.

---

## Overview

Single-package PoC that:
1. SSL-pretrains ResNet-50 (SimCLR / MoCo-v2 / DINO) on 3 datasets with SGD; saves 4 checkpoints each
2. Trains a frozen linear probe per checkpoint; computes per-sample losses
3. Applies SAM perturbation post-hoc along spurious direction vs. 100 random directions; computes anisotropy ratio
4. Evaluates worst-group accuracy (WGA) via group labels (eval only)
5. Computes Pearson r between anisotropy ratio and WGA across 4 checkpoints
6. Saves figures and a YAML results file

Total experiments: 9 SSL training runs × 4 checkpoints = 36 (model, dataset, epoch) triples.

---

## File Structure

```
src/h_e1/
    __init__.py
    config.py          # single frozen config dataclass
    data.py            # Waterbirds / CelebA / CMNIST loaders
    ssl_trainer.py     # SimCLR / MoCo-v2 / DINO training loops + checkpointing
    probe.py           # linear probe trainer + per-sample loss + WGA eval
    anisotropy.py      # SAM perturbation measurement (spurious + random)
    stats.py           # Pearson r + summary table
    visualize.py       # bar chart / scatter / line plot / heatmap
    run.py             # CLI entry point — orchestrates all 9 runs

data/
    waterbirds/        # manual download
    celeba/            # WILDS auto-download
    cmnist/            # torchvision auto-download

checkpoints/h_e1/
    {method}_{dataset}_ep{epoch}.pt   # 9 × 4 = 36 files

results/h_e1/
    results.yaml       # all anisotropy ratios, WGA, Pearson r

docs/youra_research/h-e1/figures/
    anisotropy_bar.png
    anisotropy_scatter.png
    anisotropy_line.png
    anisotropy_heatmap.png
```

---

## Module Interfaces

### Config (`src/h_e1/config.py`)

**Dependencies:** dataclasses, pathlib

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

@dataclass
class Cfg:
    # paths
    data_root: Path = Path("data")
    ckpt_dir: Path = Path("checkpoints/h_e1")
    results_path: Path = Path("results/h_e1/results.yaml")
    figures_dir: Path = Path("docs/youra_research/h-e1/figures")

    # grid
    ssl_methods: List[str] = field(default_factory=lambda: ["simclr", "mocov2", "dino"])
    datasets: List[str] = field(default_factory=lambda: ["waterbirds", "celeba", "cmnist"])
    checkpoint_epochs: List[int] = field(default_factory=lambda: [50, 100, 150, 200])

    # SSL training
    seed: int = 1
    batch_size: int = 256
    total_epochs: int = 200
    ssl_lr: float = 0.03
    ssl_momentum: float = 0.9
    ssl_weight_decay: float = 1e-4
    simclr_tau: float = 0.5
    moco_tau: float = 0.2
    moco_queue: int = 65536
    moco_momentum: float = 0.999

    # linear probe
    probe_lr: float = 0.01
    probe_epochs: int = 100

    # SAM measurement
    sam_rho: float = 0.05
    n_random_dirs: int = 100
    spurious_quantile: float = 0.75   # top-25% high-loss

def get_cfg() -> Cfg: ...
```

---

### Data (`src/h_e1/data.py`)

**Dependencies:** torch, torchvision, wilds, Pillow

```python
from torch.utils.data import DataLoader, Dataset
from typing import Tuple

def get_ssl_loader(dataset: str, data_root: str, batch_size: int,
                   augment: bool = True) -> DataLoader:
    """Returns DataLoader with SSL augmentation (two-view for SimCLR/MoCo, single for DINO)."""
    ...

def get_eval_loader(dataset: str, data_root: str, batch_size: int,
                    split: str = "train") -> DataLoader:
    """Returns DataLoader with standard eval transforms; yields (img, label, group_id)."""
    ...

def get_cmnist(root: str, train: bool, correlation: float = 0.99) -> Dataset:
    """MNIST + color augmentation wrapper exposing (img, label, group_id)."""
    ...
```

---

### SSL Trainer (`src/h_e1/ssl_trainer.py`)

**Dependencies:** torch, torchvision, config.Cfg

```python
import torch.nn as nn
from torch import Tensor
from pathlib import Path

class SimCLR(nn.Module):
    def __init__(self, base_encoder: nn.Module, proj_dim: int = 128): ...
    def forward(self, x1: Tensor, x2: Tensor) -> Tuple[Tensor, Tensor]: ...
    def nt_xent_loss(self, z1: Tensor, z2: Tensor, tau: float) -> Tensor: ...

class MoCoV2(nn.Module):
    def __init__(self, base_encoder: nn.Module, K: int = 65536,
                 m: float = 0.999, tau: float = 0.2, proj_dim: int = 128): ...
    def forward(self, im_q: Tensor, im_k: Tensor) -> Tensor: ...

class DINO(nn.Module):
    def __init__(self, student: nn.Module, teacher: nn.Module,
                 out_dim: int = 65536): ...
    def forward(self, views: list[Tensor]) -> Tensor: ...
    def update_teacher(self, momentum: float) -> None: ...

def train_ssl(method: str, dataset: str, cfg, device: str) -> None:
    """Full SSL training loop; saves checkpoints at cfg.checkpoint_epochs."""
    ...

def load_backbone(ckpt_path: Path, device: str) -> nn.Module:
    """Returns frozen ResNet-50 backbone (projection head stripped)."""
    ...
```

---

### Linear Probe (`src/h_e1/probe.py`)

**Dependencies:** torch, ssl_trainer.load_backbone, data.get_eval_loader

```python
import torch.nn as nn
from torch import Tensor
from typing import Dict

class LinearProbe(nn.Module):
    def __init__(self, feat_dim: int = 2048, n_classes: int = 2): ...
    def forward(self, x: Tensor) -> Tensor: ...

def train_probe(backbone: nn.Module, dataset: str, cfg,
                device: str) -> LinearProbe:
    """Train frozen-backbone linear classifier; returns trained probe."""
    ...

def compute_per_sample_losses(backbone: nn.Module, probe: LinearProbe,
                               loader, device: str) -> Tensor:
    """Returns 1-D tensor of cross-entropy loss per training sample."""
    ...

def eval_wga(backbone: nn.Module, probe: LinearProbe,
             loader, device: str) -> float:
    """Worst-group accuracy: min(avg_acc_per_group) across 4 groups."""
    ...
```

---

### Anisotropy Measurement (`src/h_e1/anisotropy.py`)

**Dependencies:** torch, probe module, config.Cfg

```python
from torch import Tensor
import torch.nn as nn

def apply_sam_perturbation(model: nn.Module, loader,
                            rho: float, device: str) -> nn.Module:
    """One-step SAM first_step perturbation; returns perturbed copy (no grad update)."""
    ...

def measure_anisotropy(backbone: nn.Module, probe_losses: Tensor,
                        dataset_obj, cfg, device: str) -> Dict[str, float]:
    """
    Returns:
        {
          'spurious_increase': float,
          'random_mean_increase': float,
          'anisotropy_ratio': float,
        }
    """
    ...
```

---

### Statistics (`src/h_e1/stats.py`)

**Dependencies:** scipy, numpy, yaml

```python
from typing import List, Dict

def pearson_r(anisotropy_ratios: List[float],
              wga_values: List[float]) -> Dict[str, float]:
    """Returns {'r': float, 'p': float}."""
    ...

def summarize_results(results: dict) -> dict:
    """
    Aggregates per-(method, dataset) Pearson r and per-combination
    anisotropy ratio; computes pass/fail (ratio > 1.2, |r| > 0.5).
    Returns summary dict written to YAML.
    """
    ...

def save_yaml(data: dict, path: str) -> None: ...
```

---

### Visualization (`src/h_e1/visualize.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
from pathlib import Path

def plot_anisotropy_bar(results: dict, figures_dir: Path) -> None:
    """Bar chart: anisotropy ratio per (method, dataset); horizontal line at 1.2."""
    ...

def plot_scatter(results: dict, figures_dir: Path) -> None:
    """Scatter: anisotropy ratio vs. WGA per checkpoint; Pearson r annotated."""
    ...

def plot_epoch_lines(results: dict, figures_dir: Path) -> None:
    """Line plot: anisotropy ratio over epochs 50/100/150/200 per (method, dataset)."""
    ...

def plot_heatmap(results: dict, figures_dir: Path) -> None:
    """3×3 heatmap: SSL methods × datasets; color-coded by pass (>1.2) / fail."""
    ...
```

---

### Orchestrator / CLI (`src/h_e1/run.py`)

**Dependencies:** all above modules, argparse

```python
def run_ssl_pretraining(cfg, device: str) -> None:
    """Runs 9 SSL training jobs; skips if checkpoint already exists."""
    ...

def run_measurements(cfg, device: str) -> dict:
    """
    For each (method, dataset, epoch):
      - loads backbone checkpoint
      - trains linear probe
      - computes per-sample losses
      - measures anisotropy
      - evaluates WGA
    Returns nested results dict.
    """
    ...

def run_analysis(results: dict, cfg) -> None:
    """Pearson r per (method, dataset), save YAML, save all figures."""
    ...

def main() -> None:
    """
    CLI: python -m h_e1.run [--skip-training] [--device cuda] [--method all|simclr|mocov2|dino]
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Proposed Epic Tasks

| ID | Task | Modules | Module_Size | Dependencies | Algorithm | Integration | Total |
|----|------|---------|-------------|--------------|-----------|-------------|-------|
| A-1 | Data loaders (Waterbirds, CelebA, CMNIST with group metadata) | data.py | 2 | 2 | 2 | 1 | **7** |
| A-2 | SSL pre-training runners (SimCLR, MoCo-v2, DINO + checkpointing) | ssl_trainer.py | 4 | 3 | 4 | 3 | **14** |
| A-3 | Linear probe trainer + per-sample loss + WGA eval | probe.py | 3 | 3 | 2 | 3 | **11** |
| A-4 | SAM perturbation anisotropy measurement (spurious + 100 random) | anisotropy.py | 3 | 3 | 4 | 3 | **13** |
| A-5 | Statistical analysis (Pearson r, YAML output) | stats.py | 1 | 1 | 1 | 2 | **5** |
| A-6 | Visualization (bar, scatter, line, heatmap) | visualize.py | 2 | 1 | 1 | 2 | **6** |
| A-7 | CLI orchestration (9 runs, skip-if-exists, aggregate) | run.py | 2 | 4 | 1 | 4 | **11** |

**Distribution:** High(14-17): [A-2], Medium(9-13): [A-3, A-4, A-7], Low(4-8): [A-1, A-5, A-6]

---

## Implementation Notes

- `run.py` checks checkpoint existence before launching SSL training — safe to re-run.
- MoCo-v2 queue (~1 GB) and DINO teacher copy both fit in 16 GB GPU RAM alongside ResNet-50.
- SAM `apply_sam_perturbation` clones the model before perturbing; original weights are never modified.
- All 9 SSL runs share one augmentation pipeline; CMNIST uses `Resize(224)` + color jitter.
- `ponytail:` DINO implementation is non-trivial (multi-crop, teacher EMA schedule). Use facebookresearch/dino's `main_dino.py` as a copy-in starting point, not a re-implementation from scratch.
- Results YAML schema:

```yaml
# results/h_e1/results.yaml
simclr:
  waterbirds:
    ep50:  {anisotropy_ratio: 1.35, wga: 0.41}
    ep100: {anisotropy_ratio: 1.48, wga: 0.39}
    ep150: {anisotropy_ratio: 1.61, wga: 0.37}
    ep200: {anisotropy_ratio: 1.72, wga: 0.44}
    pearson_r: -0.72
    pearson_p: 0.028
  ...
summary:
  pass_count: 8   # out of 9
  gate: PASS
```
