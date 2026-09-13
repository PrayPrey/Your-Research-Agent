# Config: H-M1 (MECHANISM)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1)
**Status**: config classes verified from base code (`h-e1/code/config.py` read directly)
**Config Files Found**: `docs/youra_research/h-e1/code/config.py` (dataclass `Config`)
**Pattern Used**: dataclass (matches H-E1 convention)

---

## Inherited Configuration (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    seed: int = 42
    data_url: str = "https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz"
    data_root: str = "./data/waterbirds"
    img_size: int = 224
    norm_mean: tuple = (0.485, 0.456, 0.406)
    norm_std: tuple = (0.229, 0.224, 0.225)
    batch_size: int = 64
    num_workers: int = 4
    num_classes: int = 2
    pretrained: bool = True
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    device: str = "cuda"
```

H-M1 reuses `data_root`, `img_size`, `norm_mean/std`, `batch_size`, `num_workers`,
`num_classes`, `pretrained`, `lr`, `momentum`, `weight_decay`, `device` verbatim
(via `get_dataloaders`/`build_resnet18` imports). `n_epochs` differs (50 vs H-E1's 100)
per PRD NFR-2.

---

## M-1 to M-8: H-M1 Config [Complexity: 3+7+5+8+6+4+4+5=42, Budget: full allocation]

**Applied**: Single fixed dataclass, no hyperparameter search (mechanism verification, not tuning)

### Configuration (Python Dataclass)

```python
"""Configuration for H-M1 MECHANISM experiment."""
from dataclasses import dataclass

@dataclass
class Config:
    seed: int = 42
    data_root: str = "../h-e1/code/data/waterbirds"  # reuse H-E1 downloaded data
    img_size: int = 224
    norm_mean: tuple = (0.485, 0.456, 0.406)
    norm_std: tuple = (0.229, 0.224, 0.225)
    batch_size: int = 64
    num_workers: int = 4
    num_classes: int = 2
    pretrained: bool = True
    device: str = "cuda"

    # Base model training (ERM, same as H-E1)
    n_epochs: int = 50
    checkpoint_epochs: tuple = (5, 20, 50)
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4

    # Linear probes
    feature_dim: int = 512
    probe_lr: float = 0.01
    probe_epochs: int = 10

    # Paths
    ckpt_dir: str = "./checkpoints"
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    metrics_path: str = "./outputs/metrics.json"
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-M-1 | Data/model wiring | Import `get_dataloaders`, `build_resnet18` from H-E1 with `Config` fields |
| C-M-2 | Checkpointed training | `train_with_checkpoints` using `n_epochs`, `checkpoint_epochs`, `lr`, `momentum`, `weight_decay`, save to `ckpt_dir` |
| C-M-3 | Probe backbone | `load_frozen_backbone`/`LinearProbeAnalysis` using `feature_dim`, `num_classes` |
| C-M-4 | Probe train/eval | `train_probe`/`eval_probe` using `probe_lr`, `probe_epochs`, label_idx 1 (core) / 2 (spurious) |
| C-M-5 | Checkpoint loop | Iterate `checkpoint_epochs`, run both probes per checkpoint |
| C-M-6 | Mechanism verification | `verify_mechanism` on results dict keyed `epoch_5`/`epoch_20`/`epoch_50` |
| C-M-7 | Visualization | `plot_probe_accuracy_curve` to `figures_dir` |
| C-M-8 | Orchestration | `run_experiment.py` wiring all above, write `metrics_path` |
