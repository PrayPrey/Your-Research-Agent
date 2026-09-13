# H-M3 Configuration: DeepSets Mechanism Closure

Applied: Standard Python dataclass pattern (Archon KB had no relevant DL config pages)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-m2, h-e1)
**Status**: Config classes verified from actual base code (no Serena MCP needed — files read directly)
**Config Files Found**:
- `/docs/youra_research/h-m2/code/lgbm_trainer.py` — `LGBM_PARAMS` dict
- `/docs/youra_research/h-e1/code/encoder_c2.py` — `DeepSetsChannelEncoder.__init__` defaults
**Pattern Used**: dataclass (sub-configs) + YAML for experiment_config.yaml

---

## Inherited Configuration (Base Hypothesis)

### Verified from h-m2/code/lgbm_trainer.py (ACTUAL CODE)

```python
LGBM_PARAMS = {
    "n_estimators": 500,
    "learning_rate": 0.05,
    "num_leaves": 31,
    "reg_alpha": 0.0,
    "reg_lambda": 0.1,
    "random_state": 42,
    "boosting_type": "gbdt",
    "verbose": -1,
}
```

### Verified from h-e1/code/encoder_c2.py (ACTUAL CODE)

```python
# DeepSetsChannelEncoder defaults:
kernel_dims: list = [25, 25, 4]   # kH*kW per conv layer
hidden_dim: int = 64
embed_dim: int = 128
```

---

## C-8-1: Closure Config [Complexity: 1, Budget: 1]

Applied: Standard dataclass pattern

### Configuration

```python
from dataclasses import dataclass

@dataclass
class ClosureConfig:
    mse_perm_c1_reference: float = 0.006137   # from H-M2 decompose_mse results
    tolerance_fraction: float = 0.10           # ±10% tolerance band
    mechanism_indicators_required: int = 3     # pass if 3/4 indicators satisfied
    r2_c0_threshold: float = 0.984            # gate: C0 must clear this
    r2_c1_reference: float = 0.8511          # from H-M2 baseline
    mse_total_c1_reference: float = 0.001834  # from H-M2 baseline
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Closure evaluation config | Thresholds and reference values for 4-indicator closure check |

---

## C-10-1: Visualization Config [Complexity: 1, Budget: 1]

Applied: Standard dataclass pattern

### Configuration

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class VizConfig:
    figures_dir: str = "figures"
    figure_format: str = "png"
    dpi: int = 150

    # Color scheme for C0/C1/C2/C3 encoder bars
    bar_colors: List[str] = field(default_factory=lambda: [
        "#4C72B0",  # C0 - blue
        "#DD8452",  # C1 - orange
        "#55A868",  # C2 - green (DeepSets)
        "#C44E52",  # C3 - red
    ])

    # Threshold line for r2_c0=0.984 gate
    threshold_color: str = "#333333"
    threshold_linestyle: str = "--"
    threshold_linewidth: float = 1.5

    # Figure sizes (width, height) in inches
    bar_chart_size: tuple = (8, 5)
    stacked_chart_size: tuple = (10, 6)
    scatter_size: tuple = (6, 6)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-10-1 | Visualization config | Figure dirs, DPI, colors, sizes for all plots |

---

## C-ENV-1: Environment / Experiment Config [Complexity: 1, Budget: 1]

Applied: Standard dataclass + YAML pattern

### experiment_config.yaml

```yaml
# H-M3 Experiment Configuration
seed: 42
perm_seed: 1

dataset:
  model_zoo_dir: "data/model_zoo"
  labels_path: "data/labels.csv"

encoder:
  kernel_dims: [25, 25, 4]
  hidden_dim: 64
  embed_dim: 128

nfn:
  nfn_channels: 32

cv:
  n_folds: 5
  K: 50                        # permutation orbit size

ridge:
  alphas: [0.01, 0.1, 1.0, 10.0]

lgbm:
  n_estimators: 500
  learning_rate: 0.05
  num_leaves: 31
  reg_alpha: 0.0
  reg_lambda: 0.1
  random_state: 42
  boosting_type: "gbdt"
  verbose: -1

closure:
  mse_perm_c1_reference: 0.006137
  tolerance_fraction: 0.10
  mechanism_indicators_required: 3
  r2_c0_threshold: 0.984
  r2_c1_reference: 0.8511
  mse_total_c1_reference: 0.001834

viz:
  figures_dir: "figures"
  figure_format: "png"
  dpi: 150
```

### Master ExperimentConfig Dataclass

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class DatasetConfig:
    model_zoo_dir: str = "data/model_zoo"
    labels_path: str = "data/labels.csv"

@dataclass
class EncoderConfig:
    kernel_dims: List[int] = field(default_factory=lambda: [25, 25, 4])
    hidden_dim: int = 64
    embed_dim: int = 128

@dataclass
class NFNConfig:
    nfn_channels: int = 32

@dataclass
class CVConfig:
    n_folds: int = 5
    K: int = 50

@dataclass
class RidgeConfig:
    alphas: List[float] = field(default_factory=lambda: [0.01, 0.1, 1.0, 10.0])

@dataclass
class LGBMConfig:
    n_estimators: int = 500
    learning_rate: float = 0.05
    num_leaves: int = 31
    reg_alpha: float = 0.0
    reg_lambda: float = 0.1
    random_state: int = 42
    boosting_type: str = "gbdt"
    verbose: int = -1

@dataclass
class ExperimentConfig:
    seed: int = 42
    perm_seed: int = 1
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    encoder: EncoderConfig = field(default_factory=EncoderConfig)
    nfn: NFNConfig = field(default_factory=NFNConfig)
    cv: CVConfig = field(default_factory=CVConfig)
    ridge: RidgeConfig = field(default_factory=RidgeConfig)
    lgbm: LGBMConfig = field(default_factory=LGBMConfig)
    closure: ClosureConfig = field(default_factory=ClosureConfig)
    viz: VizConfig = field(default_factory=VizConfig)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-ENV-1 | Experiment config | Master dataclass + YAML covering all hyperparams and paths |
