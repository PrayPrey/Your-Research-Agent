# Configuration: H-M3 — Transition Epoch t* Reproducibility Analysis

Applied: dataclass-config pattern (H-E1 config.py verified)
Applied: flat-module-layout pattern (H-E1 code structure verified)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code (H-E1 03_config.md)
**Config Files Found**: `h-e1/03_config.md` — TrainConfig, ProbeConfig, GateConfig, DatasetPathConfig, ExperimentConfig
**Pattern Used**: dataclass

---

## Inherited Configuration (Base H-E1)

The following values are reused from H-E1 without change:

| Field | H-E1 Source | H-M3 Value | Note |
|-------|-------------|------------|------|
| `seeds` | `TrainConfig.seeds` | `[42, 43, 44]` | Reduced to 3 seeds (min_seeds gate) |
| `checkpoint_interval` | `TrainConfig.checkpoint_interval` | `2` | Same protocol |
| `threshold` / `t_star_delta_threshold` | `GateConfig.t_star_delta_threshold = 0.02` | `0.02` | Same t* detection criterion |
| `n_consecutive` / `t_star_consecutive` | `GateConfig.t_star_consecutive = 3` | `3` | Same consecutive count |
| `waterbirds_root` | `DatasetPathConfig.waterbirds_root` | `.data_cache/datasets/waterbirds` | Path updated for H-M3 layout |

**New in H-M3** (not in H-E1):
- `n_bootstrap`, `bootstrap_seed`, `std_gate_threshold` — bootstrap CI analysis
- `min_checkpoints`, `min_seeds` — array validation guards
- `h_e1_results_dir`, `h_e1_checkpoint_dir`, `h_e1_json_filename` — cross-hypothesis path references
- `hypothesis_id`, `device` — experiment metadata

---

## A-1: AnalysisConfig [Complexity: 1, Budget: 1]

**Applied**: Standard scipy bootstrap + threshold-detection defaults

### Configuration

```python
# config.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class AnalysisConfig:
    threshold: float = 0.02          # t* detection: delta < threshold
    n_consecutive: int = 3           # consecutive checkpoints below threshold
    checkpoint_interval: int = 2     # epochs per checkpoint (matches H-E1 protocol)
    n_bootstrap: int = 10000         # bootstrap CI resamples
    bootstrap_seed: int = 42
    std_gate_threshold: float = 10.0 # MUST_WORK gate: std(t*) < 10 epochs
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    min_checkpoints: int = 15        # validate loaded arrays have enough data
    min_seeds: int = 3               # minimum seeds for statistical validity
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | AnalysisConfig | Dataclass with detection + bootstrap + gate params |

---

## A-2: PathConfig [Complexity: 1, Budget: 1]

**Applied**: Standard relative-path config (H-E1 DatasetPathConfig pattern)

### Configuration

```python
@dataclass
class PathConfig:
    h_e1_results_dir: str = "../../h-e1/results"
    h_e1_checkpoint_dir: str = "../../h-e1/checkpoints"
    h_e1_json_filename: str = "h-e1_results.json"
    waterbirds_root: str = ".data_cache/datasets/waterbirds"
    results_dir: str = "./results"
    figures_dir: str = "./figures"
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | PathConfig | Dataclass with H-E1 and H-M3 paths |

---

## A-3: ExperimentConfig [Complexity: 1, Budget: 1]

**Applied**: Composition pattern from H-E1 ExperimentConfig

### Configuration

```python
@dataclass
class ExperimentConfig:
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    hypothesis_id: str = "H-M3"
    device: str = "cpu"  # pure numpy/scipy — no GPU needed
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | ExperimentConfig | Composed config with metadata |

---

## A-4: load_config() [Complexity: 2, Budget: 1]

**Applied**: Standard YAML-load + env-var-override pattern

### Configuration

```python
import os
import yaml
from dataclasses import fields

def load_config(config_path: str = "configs/waterbirds.yaml") -> ExperimentConfig:
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    analysis_dict = raw.get("analysis", {})
    paths_dict = raw.get("paths", {})
    meta = {k: v for k, v in raw.items() if k not in ("analysis", "paths")}

    # Env var overrides (H_M3_ prefix)
    for fld in fields(AnalysisConfig):
        env_key = f"H_M3_{fld.name.upper()}"
        if env_key in os.environ:
            val = os.environ[env_key]
            analysis_dict[fld.name] = fld.type(val) if fld.type != "List[int]" else list(map(int, val.split(",")))

    for fld in fields(PathConfig):
        env_key = f"H_M3_{fld.name.upper()}"
        if env_key in os.environ:
            paths_dict[fld.name] = os.environ[env_key]

    analysis_cfg = AnalysisConfig(**{k: v for k, v in analysis_dict.items() if k in {f.name for f in fields(AnalysisConfig)}})
    paths_cfg = PathConfig(**{k: v for k, v in paths_dict.items() if k in {f.name for f in fields(PathConfig)}})

    return ExperimentConfig(
        analysis=analysis_cfg,
        paths=paths_cfg,
        **{k: v for k, v in meta.items() if k in {f.name for f in fields(ExperimentConfig)} and k not in ("analysis", "paths")},
    )
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | load_config | YAML load with H_M3_ env var overrides |

---

## A-5: validate_config() [Complexity: 2, Budget: 1]

**Applied**: Standard pre-flight validation pattern

### Configuration

```python
import os

def validate_config(cfg: ExperimentConfig) -> None:
    a = cfg.analysis
    p = cfg.paths

    # Threshold range
    if not (0.0 < a.threshold < 1.0):
        raise ValueError(f"threshold must be in (0, 1), got {a.threshold}")

    # Seeds uniqueness and minimum count
    if len(set(a.seeds)) != len(a.seeds):
        raise ValueError(f"seeds must be unique, got {a.seeds}")
    if len(a.seeds) < a.min_seeds:
        raise ValueError(f"Need at least {a.min_seeds} seeds, got {len(a.seeds)}")

    # Positive integers
    if a.n_bootstrap < 1:
        raise ValueError(f"n_bootstrap must be >= 1, got {a.n_bootstrap}")
    if a.n_consecutive < 1:
        raise ValueError(f"n_consecutive must be >= 1, got {a.n_consecutive}")
    if a.min_checkpoints < 1:
        raise ValueError(f"min_checkpoints must be >= 1, got {a.min_checkpoints}")

    # H-E1 results path must exist
    if not os.path.isdir(p.h_e1_results_dir):
        raise FileNotFoundError(f"h_e1_results_dir not found: {p.h_e1_results_dir}")
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | validate_config | Pre-flight checks: paths, threshold range, seeds uniqueness |

---

## A-6: configs/waterbirds.yaml [Complexity: 1, Budget: 1]

**Applied**: Flat YAML matching dataclass field names

### Configuration

```yaml
# configs/waterbirds.yaml
hypothesis_id: "H-M3"
device: "cpu"

analysis:
  threshold: 0.02
  n_consecutive: 3
  checkpoint_interval: 2
  n_bootstrap: 10000
  bootstrap_seed: 42
  std_gate_threshold: 10.0
  seeds: [42, 43, 44]
  min_checkpoints: 15
  min_seeds: 3

paths:
  h_e1_results_dir: "../../h-e1/results"
  h_e1_checkpoint_dir: "../../h-e1/checkpoints"
  h_e1_json_filename: "h-e1_results.json"
  waterbirds_root: ".data_cache/datasets/waterbirds"
  results_dir: "./results"
  figures_dir: "./figures"
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | waterbirds.yaml | Default YAML config matching all dataclass fields |

---

## Complete config.py (copy-paste ready)

```python
# h-m3/code/config.py
import os
import yaml
from dataclasses import dataclass, field, fields
from typing import List


@dataclass
class AnalysisConfig:
    threshold: float = 0.02
    n_consecutive: int = 3
    checkpoint_interval: int = 2
    n_bootstrap: int = 10000
    bootstrap_seed: int = 42
    std_gate_threshold: float = 10.0
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    min_checkpoints: int = 15
    min_seeds: int = 3


@dataclass
class PathConfig:
    h_e1_results_dir: str = "../../h-e1/results"
    h_e1_checkpoint_dir: str = "../../h-e1/checkpoints"
    h_e1_json_filename: str = "h-e1_results.json"
    waterbirds_root: str = ".data_cache/datasets/waterbirds"
    results_dir: str = "./results"
    figures_dir: str = "./figures"


@dataclass
class ExperimentConfig:
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    hypothesis_id: str = "H-M3"
    device: str = "cpu"


def load_config(config_path: str = "configs/waterbirds.yaml") -> ExperimentConfig:
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    analysis_dict = raw.get("analysis", {})
    paths_dict = raw.get("paths", {})
    meta = {k: v for k, v in raw.items() if k not in ("analysis", "paths")}

    analysis_field_names = {f.name for f in fields(AnalysisConfig)}
    paths_field_names = {f.name for f in fields(PathConfig)}

    # Env var overrides (H_M3_ prefix)
    for fld in fields(AnalysisConfig):
        env_key = f"H_M3_{fld.name.upper()}"
        if env_key in os.environ:
            raw_val = os.environ[env_key]
            if fld.name == "seeds":
                analysis_dict[fld.name] = list(map(int, raw_val.split(",")))
            else:
                analysis_dict[fld.name] = type(getattr(AnalysisConfig(), fld.name))(raw_val)

    for fld in fields(PathConfig):
        env_key = f"H_M3_{fld.name.upper()}"
        if env_key in os.environ:
            paths_dict[fld.name] = os.environ[env_key]

    analysis_cfg = AnalysisConfig(**{k: v for k, v in analysis_dict.items() if k in analysis_field_names})
    paths_cfg = PathConfig(**{k: v for k, v in paths_dict.items() if k in paths_field_names})

    exp_field_names = {f.name for f in fields(ExperimentConfig)} - {"analysis", "paths"}
    return ExperimentConfig(
        analysis=analysis_cfg,
        paths=paths_cfg,
        **{k: v for k, v in meta.items() if k in exp_field_names},
    )


def validate_config(cfg: ExperimentConfig) -> None:
    a = cfg.analysis
    p = cfg.paths

    if not (0.0 < a.threshold < 1.0):
        raise ValueError(f"threshold must be in (0, 1), got {a.threshold}")

    if len(set(a.seeds)) != len(a.seeds):
        raise ValueError(f"seeds must be unique, got {a.seeds}")
    if len(a.seeds) < a.min_seeds:
        raise ValueError(f"Need at least {a.min_seeds} seeds, got {len(a.seeds)}")

    if a.n_bootstrap < 1:
        raise ValueError(f"n_bootstrap must be >= 1, got {a.n_bootstrap}")
    if a.n_consecutive < 1:
        raise ValueError(f"n_consecutive must be >= 1, got {a.n_consecutive}")
    if a.min_checkpoints < 1:
        raise ValueError(f"min_checkpoints must be >= 1, got {a.min_checkpoints}")

    if not os.path.isdir(p.h_e1_results_dir):
        raise FileNotFoundError(f"h_e1_results_dir not found: {p.h_e1_results_dir}")
```
