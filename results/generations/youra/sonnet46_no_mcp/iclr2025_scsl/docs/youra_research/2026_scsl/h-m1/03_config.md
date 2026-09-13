# Config: H-M1
# SGD Gradient Structure Analysis — Gradient Dominance Ratio (GDR)

Applied: dataclass composition pattern with YAML loading

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code (H-E1)
**Config Files Found**: `h-e1/code/config.py`
**Pattern Used**: dataclass

**Verified field names from `h-e1/code/config.py`**:
- `TrainConfig`: `dataset`, `data_root`, `checkpoint_dir`, `epochs`, `checkpoint_interval`, `batch_size`, `lr`, `momentum`, `weight_decay`, `seeds`, `num_workers`
- H-E1 defaults differ: `batch_size=128`, `seeds=[1,2,3,4,5]` — H-M1 YAML overrides to `batch_size=64`, `seeds=[1,2,3]`

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-e1/code/config.py (ACTUAL CODE — verified)
@dataclass
class TrainConfig:
    dataset: str
    data_root: str
    checkpoint_dir: str
    epochs: int
    checkpoint_interval: int = 2
    batch_size: int = 128        # ← H-M1 YAML overrides to 64
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    seeds: List[int] = field(default_factory=lambda: [1, 2, 3, 4, 5])  # ← H-M1 YAML overrides to [1,2,3]
    num_workers: int = 4
```

---

## A-6: Pearson Temporal Alignment Config [Complexity: 9, Budget: 2 subtasks]

Applied: dataclass with Optional field pattern

### Configuration

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class GDRConfig:
    early_window_epochs: List[int] = field(default_factory=lambda: [2, 4, 6])
    p_threshold: float = 0.05
    min_seeds_pass: int = 2
    he1_delta_path: Optional[str] = None  # path to H-E1 delta(t) JSON; None skips Pearson correlation
```

### YAML Schema (configs/waterbirds.yaml — gdr section)

```yaml
gdr:
  early_window_epochs: [2, 4, 6]
  p_threshold: 0.05
  min_seeds_pass: 2
  he1_delta_path: null
```

### Validation Rules

- `early_window_epochs`: all values must be <= `train.epochs` and multiples of `train.checkpoint_interval`
- `p_threshold`: 0 < p_threshold <= 1.0
- `min_seeds_pass`: 1 <= min_seeds_pass <= len(train.seeds)
- `he1_delta_path`: if not None, file must exist and be valid JSON

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | GDRConfig dataclass | Define GDRConfig with all fields and types as above |
| C-6-2 | YAML schema + validation | Define gdr section in waterbirds.yaml; add field validation in load_config |

---

## A-8: Experiment Runner Config [Complexity: 9, Budget: 2 subtasks]

Applied: dataclass composition with YAML parsing

### Configuration

```python
from dataclasses import dataclass, field
from typing import List, Optional
import yaml
import os


@dataclass
class TrainConfig:
    dataset: str
    data_root: str
    checkpoint_dir: str
    epochs: int
    checkpoint_interval: int = 2
    batch_size: int = 64
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    seeds: List[int] = field(default_factory=lambda: [1, 2, 3])
    num_workers: int = 4


@dataclass
class GDRConfig:
    early_window_epochs: List[int] = field(default_factory=lambda: [2, 4, 6])
    p_threshold: float = 0.05
    min_seeds_pass: int = 2
    he1_delta_path: Optional[str] = None


@dataclass
class ExperimentConfig:
    train: TrainConfig
    gdr: GDRConfig
    results_dir: str = "./results/h-m1"
    figures_dir: str = "./figures"


def load_config(config_path: str) -> ExperimentConfig:
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    train_cfg = TrainConfig(**raw["train"])
    gdr_cfg = GDRConfig(**raw.get("gdr", {}))

    return ExperimentConfig(
        train=train_cfg,
        gdr=gdr_cfg,
        results_dir=raw.get("results_dir", "./results/h-m1"),
        figures_dir=raw.get("figures_dir", "./figures"),
    )
```

### Full configs/waterbirds.yaml

```yaml
train:
  dataset: waterbirds
  data_root: ./data/waterbirds
  checkpoint_dir: ./checkpoints/h-m1
  epochs: 30
  checkpoint_interval: 2
  batch_size: 64
  lr: 0.001
  momentum: 0.9
  weight_decay: 0.0001
  seeds: [1, 2, 3]
  num_workers: 4

gdr:
  early_window_epochs: [2, 4, 6]
  p_threshold: 0.05
  min_seeds_pass: 2
  he1_delta_path: null

results_dir: ./results/h-m1
figures_dir: ./figures
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | ExperimentConfig dataclass | Define ExperimentConfig composing TrainConfig + GDRConfig with results_dir and figures_dir |
| C-8-2 | load_config() + waterbirds.yaml | Implement YAML parsing into dataclasses; write full configs/waterbirds.yaml |
