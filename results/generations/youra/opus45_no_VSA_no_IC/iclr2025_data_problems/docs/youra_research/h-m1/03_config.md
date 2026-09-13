# Config: h-m1

**Applied**: No matching KB pattern (best similarity 0.42) — defaults sourced from PRD/architecture directly.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## Format: Dataclass (Python)

### Configuration (`config.py`)

```python
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    # Reproducibility
    seed: int = 42

    # Training (FR-3.1)
    epochs: int = 200
    batch_size: int = 128
    lr: float = 0.1
    momentum: float = 0.9
    weight_decay: float = 5e-4
    checkpoint_every: int = 20  # -> 10 checkpoints over 200 epochs

    # Paths
    data_root: str = "./data"
    ckpt_dir: str = "./h-m1/checkpoints"
    fig_dir: str = "./h-m1/figures"

    # Probes (FR-2.2)
    probes_per_mode: int = 1000
    modes: tuple = ("mem", "transfer", "spurious")

    # TRAK (FR-1.1)
    trak_proj_dim: int = 2048
    trak_use_half_precision: bool = True

    # TracIn (FR-1.2) - checkpoint list supplied at runtime by train.py
    tracin_num_checkpoints: int = 10

    # Kronfluence (FR-1.3)
    kronfluence_use_amp: bool = True  # NFR-2: AMP where supported
```

### YAML Schema (CLI/file-based loading)

```yaml
# config.yaml
seed: 42
epochs: 200
batch_size: 128
lr: 0.1
momentum: 0.9
weight_decay: 5e-4
checkpoint_every: 20

data_root: "./data"
ckpt_dir: "./h-m1/checkpoints"
fig_dir: "./h-m1/figures"

probes_per_mode: 1000
modes: ["mem", "transfer", "spurious"]

trak:
  proj_dim: 2048
  use_half_precision: true

tracin:
  num_checkpoints: 10

kronfluence:
  use_amp: true
```

Loading: `ExperimentConfig(**yaml.safe_load(open("config.yaml")))` — flat top-level fields map 1:1; nested `trak`/`tracin`/`kronfluence` keys map to prefixed fields (`trak_proj_dim`, etc.) via simple flattening in `run_experiment.py` before constructing `ExperimentConfig`.

---

## Subtasks [1/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1 | ExperimentConfig + YAML loader | Dataclass above + `load_config(path) -> ExperimentConfig` flattening YAML into dataclass fields |

Skipped remaining 2 subtasks: single flat config is sufficient for this MECHANISM experiment (fixed hyperparameters, no sweep/ablation config needed).
