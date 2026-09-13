---
hypothesis_id: h-e1
phase: 3
document_type: config
generated: 2026-08-31
---

# Config: H-E1
## Gradient Alignment Signal Existence Verification

Applied: standard-dataclass-config-pattern (frozen dataclass with typed fields and dataset-specific instances)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — new config design, no existing codebase to analyze
**Config Files Found**: None — new config
**Pattern Used**: dataclass

---

## C-E1-1: DatasetConfig Dataclass [Complexity: 2, Budget: 2]

Applied: standard-dataclass-config-pattern

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-E1-1-1 | DatasetConfig class | Dataclass with all fields and defaults |
| C-E1-1-2 | Dataset instances | WATERBIRDS_CONFIG and CELEBA_CONFIG with exact values |

### Configuration

```python
# h-e1/config.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

import torch


def _check_torch_version() -> None:
    major, minor = (int(x) for x in torch.__version__.split(".")[:2])
    assert (major, minor) >= (2, 0), (
        f"torch>=2.0.0 required for torch.func.vmap; got {torch.__version__}"
    )


@dataclass
class DatasetConfig:
    name: str                                  # "waterbirds" | "celeba"
    root_dir: str
    target_name: str
    confounder_names: List[str]
    n_classes: int
    lr: float
    n_epochs: int
    batch_size: int = 32
    seed: int = 42
    checkpoint_epochs: tuple = (1, 5, 10, 25, 50)
    # minority_group_ids: group_ids where correct label requires ignoring spurious feature
    # Waterbirds: {1, 2} = waterbird_on_land, landbird_on_water
    # CelebA: {1} = blond_male (blond=1, male=0 → group index 1 per group_DRO encoding)
    minority_group_ids: frozenset = field(default_factory=frozenset)


WATERBIRDS_CONFIG = DatasetConfig(
    name="waterbirds",
    root_dir="./data/waterbirds",
    target_name="y",
    confounder_names=["place"],
    n_classes=2,
    lr=0.001,
    n_epochs=300,
    batch_size=32,
    seed=42,
    checkpoint_epochs=(1, 5, 10, 25, 50),
    minority_group_ids=frozenset({1, 2}),
)

CELEBA_CONFIG = DatasetConfig(
    name="celeba",
    root_dir="./data/celeba",
    target_name="Blond_Hair",
    confounder_names=["Male"],
    n_classes=2,
    lr=0.0001,
    n_epochs=50,
    batch_size=32,
    seed=42,
    checkpoint_epochs=(1, 5, 10, 25, 50),
    minority_group_ids=frozenset({1}),
)


_check_torch_version()
```

---

## C-E1-2: YAML Experiment Config [Complexity: 1, Budget: 1]

Applied: standard-dataclass-config-pattern

### YAML Schema

```yaml
# h-e1/config.yaml
# Equivalent representation of DatasetConfig instances for CLI override / logging.
# Source of truth is config.py; this file is for logging and override reference only.

waterbirds:
  name: waterbirds
  root_dir: ./data/waterbirds
  target_name: "y"
  confounder_names: ["place"]
  n_classes: 2
  lr: 0.001
  n_epochs: 300
  batch_size: 32
  seed: 42
  checkpoint_epochs: [1, 5, 10, 25, 50]
  minority_group_ids: [1, 2]

celeba:
  name: celeba
  root_dir: ./data/celeba
  target_name: Blond_Hair
  confounder_names: ["Male"]
  n_classes: 2
  lr: 0.0001
  n_epochs: 50
  batch_size: 32
  seed: 42
  checkpoint_epochs: [1, 5, 10, 25, 50]
  minority_group_ids: [1]
```

### Config Loading Snippet

```python
import yaml
from config import DatasetConfig, WATERBIRDS_CONFIG, CELEBA_CONFIG

CONFIGS = {"waterbirds": WATERBIRDS_CONFIG, "celeba": CELEBA_CONFIG}

def load_config_with_overrides(dataset: str, yaml_path: str = "h-e1/config.yaml") -> DatasetConfig:
    """Load base dataclass config, optionally override fields from YAML."""
    base = CONFIGS[dataset]
    with open(yaml_path) as f:
        overrides = yaml.safe_load(f).get(dataset, {})
    if not overrides:
        return base
    import dataclasses
    fields = {k: v for k, v in overrides.items() if hasattr(base, k)}
    if "minority_group_ids" in fields:
        fields["minority_group_ids"] = frozenset(fields["minority_group_ids"])
    if "checkpoint_epochs" in fields:
        fields["checkpoint_epochs"] = tuple(fields["checkpoint_epochs"])
    return dataclasses.replace(base, **fields)
```

---

## Validation Notes

- `torch>=2.0.0` required for `torch.func.vmap` — enforced by `_check_torch_version()` at import time.
- `minority_group_ids` uses `frozenset` to prevent accidental mutation; YAML loading converts list → frozenset.
- `checkpoint_epochs` stored as `tuple` (immutable); YAML override converts list → tuple.
- Optimizer params (momentum=0.9, weight_decay=1e-4) are NOT in DatasetConfig — they are hardcoded in `experiment.py` as they never vary between runs in this PoC.
