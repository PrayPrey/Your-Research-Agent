# Configuration: H-M4
# DFR Efficacy Correlation with Backbone Training Depth

Applied: dataclass-config (h-e1 config.py pattern - nested sub-configs + yaml loader)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from actual h-e1 and h-m3 code (Serena MCP unavailable - analyzed directly)
**Config Files Found**: `h-e1/code/config.py`, `h-m3/code/config.py`
**Pattern Used**: dataclass

**Key findings from actual code**:
- h-e1 `TrainConfig` uses `epochs` (not `max_epochs`), `checkpoint_interval` (not `checkpoint_epochs` list), `seeds=[1,2,3,4,5]`
- h-e1 has `ProbeConfig` (not `DFRConfig`) with `C, max_iter, solver, random_state` (not `dfr_seed`, no `class_weight`)
- h-m3 `PathConfig` uses `results_dir`, `figures_dir` (no `checkpoint_dir`)
- H-M4 introduces new field names: `max_epochs`, `checkpoint_epochs`, `DFRConfig.class_weight`, `DFRConfig.dfr_seed`

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE - verified)
@dataclass
class TrainConfig:          # H-E1 original
    dataset: str            # "waterbirds" | "celeba"
    data_root: str
    checkpoint_dir: str
    epochs: int             # ← field name in h-e1 (NOT max_epochs)
    checkpoint_interval: int = 2
    batch_size: int = 128
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    seeds: List[int] = field(default_factory=lambda: [1, 2, 3, 4, 5])
    num_workers: int = 4

@dataclass
class ProbeConfig:          # H-E1 original (NOT DFRConfig)
    C: float = 1.0
    max_iter: int = 1000
    solver: str = "lbfgs"
    random_state: int = 42  # ← field name in h-e1 (NOT dfr_seed)
                            # No class_weight in h-e1

# From: h-m3/code/config.py (ACTUAL CODE - verified)
@dataclass
class PathConfig:           # H-M3 original
    results_dir: str = "./results"
    figures_dir: str = "./figures"
    # No checkpoint_dir in h-m3 PathConfig
```

**H-M4 adaptations from h-e1**:
- `TrainConfig.epochs` → renamed to `max_epochs` (H-M4 specific)
- `TrainConfig.checkpoint_interval` → replaced by `checkpoint_epochs: List[int]` (H-M4 specific)
- `TrainConfig.seeds` → `[1, 2, 3]` (reduced from h-e1's 5 seeds)
- `ProbeConfig` → renamed to `DFRConfig`, added `class_weight='balanced'`, `dfr_seed=42`
- New `AnalysisConfig` and expanded `PathConfig` are H-M4-specific

---

## E-1: Project Setup [Complexity: 5, Budget: 0 subtasks + config schema]

**Applied**: Standard dataclass defaults, yaml-loader pattern from h-e1

### Configuration (`config.py`)

```python
from dataclasses import dataclass, field
from typing import List
import yaml


@dataclass
class TrainConfig:
    data_root: str = ".data_cache/datasets/waterbirds"
    checkpoint_dir: str = "./checkpoints"
    max_epochs: int = 30
    # Non-standard: list of specific epochs replaces checkpoint_interval scalar
    checkpoint_epochs: List[int] = field(default_factory=lambda: [1, 2, 10, 20, 30])
    batch_size: int = 128
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    seeds: List[int] = field(default_factory=lambda: [1, 2, 3])
    num_workers: int = 4


@dataclass
class DFRConfig:
    C: float = 1.0
    max_iter: int = 1000
    class_weight: str = "balanced"
    solver: str = "lbfgs"
    dfr_seed: int = 42


@dataclass
class AnalysisConfig:
    t_star_mean: float = 2.0
    pearson_r_threshold: float = 0.7
    conditions: List[int] = field(default_factory=lambda: [1, 2, 10, 20, 30])


@dataclass
class PathConfig:
    results_dir: str = "./results"
    figures_dir: str = "./figures"
    checkpoint_dir: str = "./checkpoints"


@dataclass
class ExperimentConfig:
    train: TrainConfig
    dfr: DFRConfig
    analysis: AnalysisConfig
    paths: PathConfig


def load_config(config_path: str = "configs/waterbirds.yaml") -> ExperimentConfig:
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    train_cfg = TrainConfig(**raw.get("train", {}))
    dfr_cfg = DFRConfig(**raw.get("dfr", {}))
    analysis_cfg = AnalysisConfig(**raw.get("analysis", {}))
    paths_cfg = PathConfig(**raw.get("paths", {}))

    return ExperimentConfig(
        train=train_cfg,
        dfr=dfr_cfg,
        analysis=analysis_cfg,
        paths=paths_cfg,
    )
```

---

## C-1-1: waterbirds.yaml [Complexity: 2, Budget: 1 subtask]

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | waterbirds YAML | Create `configs/waterbirds.yaml` with all default values |

### Configuration (`configs/waterbirds.yaml`)

```yaml
train:
  data_root: ".data_cache/datasets/waterbirds"
  checkpoint_dir: "./checkpoints"
  max_epochs: 30
  checkpoint_epochs: [1, 2, 10, 20, 30]
  batch_size: 128
  lr: 0.001
  momentum: 0.9
  weight_decay: 0.0001
  seeds: [1, 2, 3]
  num_workers: 4

dfr:
  C: 1.0
  max_iter: 1000
  class_weight: "balanced"
  solver: "lbfgs"
  dfr_seed: 42

analysis:
  t_star_mean: 2.0
  pearson_r_threshold: 0.7
  conditions: [1, 2, 10, 20, 30]

paths:
  results_dir: "./results"
  figures_dir: "./figures"
  checkpoint_dir: "./checkpoints"
```

---

## E-8: Visualizer [Complexity: 10, Budget: 1 subtask]

**Applied**: Standard matplotlib defaults

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Visualizer plot params | Figure size, DPI, font, color palette for 4 plots |

### Configuration (inline constants in `visualizer.py`)

```python
# Plot constants — top of visualizer.py
FIGURE_SIZE = (8, 5)
FIGURE_DPI = 150
BAR_COLOR = "#4C72B0"
SCATTER_COLOR = "#DD8452"
ERM_COLOR = "#4C72B0"
DFR_COLOR = "#DD8452"
CI_ALPHA = 0.2
ERROR_CAPSIZE = 4
FONT_SIZE_TITLE = 13
FONT_SIZE_LABEL = 11
FONT_SIZE_ANNOT = 10
GATE_PASS_COLOR = "green"
GATE_FAIL_COLOR = "red"
```

---

## E-10: Orchestrator [Complexity: 9, Budget: 1 subtask]

**Applied**: Standard argparse defaults

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-10-1 | Orchestrator CLI args | argparse defaults for run_experiment.py |

### Configuration (inline in `run_experiment.py`)

```python
# argparse defaults
DEFAULT_CONFIG = "configs/waterbirds.yaml"
DEFAULT_DEVICE = "cuda"

# Feature cache path template (under paths.results_dir)
FEATURE_CACHE_TEMPLATE = "{results_dir}/features_seed{seed}_epoch{epoch:03d}.npz"
```

---

## E-11: Integration Test [Complexity: 9, Budget: 1 subtask]

**Applied**: Minimal-epoch smoke test pattern

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-11-1 | Integration test config | Reduced config for fast smoke test (1 seed, 2 conditions) |

### Configuration (hardcoded dict in `test_integration.py`)

```python
SMOKE_TEST_CONFIG = {
    "train": {
        "data_root": ".data_cache/datasets/waterbirds",
        "checkpoint_dir": "./checkpoints_test",
        "max_epochs": 2,
        "checkpoint_epochs": [1, 2],
        "batch_size": 128,
        "lr": 1e-3,
        "momentum": 0.9,
        "weight_decay": 1e-4,
        "seeds": [1],
        "num_workers": 2,
    },
    "dfr": {
        "C": 1.0,
        "max_iter": 1000,
        "class_weight": "balanced",
        "solver": "lbfgs",
        "dfr_seed": 42,
    },
    "analysis": {
        "t_star_mean": 2.0,
        "pearson_r_threshold": 0.7,
        "conditions": [1, 2],
    },
    "paths": {
        "results_dir": "./results_test",
        "figures_dir": "./figures_test",
        "checkpoint_dir": "./checkpoints_test",
    },
}

# Assertions
EXPECTED_FEATURE_DIM = 2048
TIMEOUT_SECONDS = 300  # 5 min budget
```

---

*Config for H-M4 — DFR efficacy vs. backbone training depth*
*Generated: 2026-05-04*
