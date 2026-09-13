# Config: H-M2 (MECHANISM)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-M1, which extends H-E1)
**Status**: H-M1 config verified from `03_config.md` spec (H-M1 `code/` not on disk yet); field names/defaults confirmed from that spec, which itself was verified against actual `h-e1/code/config.py`.
**Config Files Found**: `docs/youra_research/h-m1/03_config.md` (dataclass `Config`); `docs/youra_research/h-e1/code/config.py` referenced transitively
**Pattern Used**: dataclass (matches H-M1/H-E1 convention)

**Applied**: Archon KB search ("DL experiment configuration hyperparameters") returned no directly relevant results (consistency-model/SDXL configs only) — used standard PyTorch/sklearn defaults per PRD, consistent with H-M1 pattern.

---

## Inherited Configuration (Base Hypothesis)

```python
# From: docs/youra_research/h-m1/03_config.md (verified from h-e1/code/config.py)
@dataclass
class Config:
    seed: int = 42
    data_root: str = "../h-e1/code/data/waterbirds"
    img_size: int = 224
    norm_mean: tuple = (0.485, 0.456, 0.406)
    norm_std: tuple = (0.229, 0.224, 0.225)
    num_workers: int = 4
    num_classes: int = 2
    pretrained: bool = True
    device: str = "cuda"
    momentum: float = 0.9
    weight_decay: float = 1e-4
    feature_dim: int = 512
```

H-M2 reuses `data_root`, `img_size`, `norm_mean/std`, `num_workers`, `num_classes`,
`pretrained`, `device`, `momentum`, `weight_decay`, `feature_dim` verbatim via
`get_dataloaders`/`build_resnet18`. `batch_size` changes to 128 (PRD FR-2, vs H-M1's 64).
`n_epochs`=100 (full curve, vs H-M1's 50 with sparse checkpoints). Probe swapped from
torch `nn.Linear` (H-M1) to sklearn `LogisticRegression` (PRD FR-4).

---

## M2-1 to M2-10: H-M2 Config [Complexity: 3+8+7+9+6+6+4+4+5+5=57, Budget: full allocation]

**Applied**: Single fixed dataclass, no hyperparameter search (mechanism verification, not tuning)

### Configuration (Python Dataclass)

```python
"""Configuration for H-M2 MECHANISM experiment."""
from dataclasses import dataclass

@dataclass
class Config:
    seed: int = 42
    data_root: str = "../h-e1/code/data/waterbirds"  # reuse H-E1 downloaded data
    img_size: int = 224
    norm_mean: tuple = (0.485, 0.456, 0.406)
    norm_std: tuple = (0.229, 0.224, 0.225)
    batch_size: int = 128
    num_workers: int = 4
    num_classes: int = 2
    pretrained: bool = True
    device: str = "cuda"

    # Full checkpointed training (ERM)
    n_epochs: int = 100
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4

    # Feature extraction
    feature_dim: int = 512

    # sklearn LogisticRegression probes
    probe_C: float = 1.0
    probe_max_iter: int = 1000
    probe_solver: str = "lbfgs"

    # Peak detection
    peak_window: int = 5
    auc_range: tuple = (1, 20)

    # Paths
    ckpt_dir: str = "./checkpoints"
    cache_dir: str = "./feature_cache"
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    metrics_path: str = "./outputs/metrics.json"
```

### YAML Schema

```yaml
seed: 42
data_root: "../h-e1/code/data/waterbirds"
img_size: 224
norm_mean: [0.485, 0.456, 0.406]
norm_std: [0.229, 0.224, 0.225]
batch_size: 128
num_workers: 4
num_classes: 2
pretrained: true
device: "cuda"

n_epochs: 100
lr: 0.001
momentum: 0.9
weight_decay: 0.0001

feature_dim: 512

probe_C: 1.0
probe_max_iter: 1000
probe_solver: "lbfgs"

peak_window: 5
auc_range: [1, 20]

ckpt_dir: "./checkpoints"
cache_dir: "./feature_cache"
output_dir: "./outputs"
figures_dir: "./figures"
metrics_path: "./outputs/metrics.json"
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-M2-1 | Full checkpointed training | `train_with_full_checkpoints` using `n_epochs=100`, `lr`, `momentum`, `weight_decay`, save every epoch to `ckpt_dir` |
| C-M2-2 | Feature cache + epoch-wise probes | `extract_epoch_features`(`feature_dim`) → cache to `cache_dir`; `train_epoch_probes` with `probe_C`, `probe_max_iter`, `probe_solver` for all 100 epochs |
| C-M2-3 | Peak detection + evaluation | `find_peak_epoch`(`peak_window`), `compute_auc`(`auc_range`), `wilcoxon_test`, `verify_mechanism`, plot to `figures_dir`, write `metrics_path` |
