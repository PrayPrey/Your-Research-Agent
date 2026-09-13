# Configuration: H-M1 (NFN Equivariant Feature Extraction)

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (H-E1 prerequisite code present, not a formal base_hypothesis reuse)
**Status**: H-E1 `code/config.py` reviewed for style consistency; H-M1 uses richer spec (data/model/training/eval/logging), so dataclasses chosen over H-E1's flat constants module. An archived earlier h-m1 config (dict-based, different hyperparams: batch=64, epochs=10) exists but does not match current PRD/brief — **not reused**.
**Config Files Found**: `docs/youra_research/h-e1/code/config.py` (flat constants), archived `h-m1/code/config.py` (superseded)
**Pattern Used**: Python dataclasses (one format only)

**Applied**: Standard PyTorch/sklearn experiment config conventions (no NFN-specific pattern in KB).

---

## Format: Python Dataclasses

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class DataConfig:
    zenodo_record: str = "6620869"
    zoo_dir: str = "data/model_zoo"
    n_train: int = 5000
    n_test: int = 500
    split_seed: int = 42          # fixed hold-out, matches H-E1
    stats_features_path: str = "outputs/statistics_features.npz"  # reuse H-E1 baseline features

@dataclass
class ModelConfig:
    hidden_dim: int = 128
    num_layers: int = 3
    invariant_output: bool = True
    network_spec: str = "resnet20"  # NFNBuilder network_spec identifier

@dataclass
class TrainConfig:
    optimizer: str = "adam"
    lr: float = 1e-3
    weight_decay: float = 1e-4
    batch_size: int = 32
    epochs: int = 100
    early_stop_patience: int = 20
    lr_schedule: str = "reduce_on_plateau"
    lr_factor: float = 0.5
    lr_patience: int = 10
    loss: str = "mse"
    seeds: List[int] = field(default_factory=lambda: [42, 123, 7])  # 3 seeds per PRD NFR1

@dataclass
class BaselineConfig:
    alphas: List[float] = field(default_factory=lambda: [0.01, 0.1, 1.0, 10.0])  # RidgeCV, matches H-E1

@dataclass
class EvalConfig:
    metrics: List[str] = field(default_factory=lambda: ["r2", "mae"])
    equivariance_tol: float = 1e-5
    n_permutation_trials: int = 500  # one permutation test per test model, per brief FR6.2
    r2_target: float = 0.85
    equivariance_pass_target: float = 1.0

@dataclass
class LoggingConfig:
    results_path: str = "outputs/nfn_results.csv"
    figures_dir: str = "figures"
    log_level: str = "INFO"

@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    baseline: BaselineConfig = field(default_factory=BaselineConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

CONFIG = ExperimentConfig()
```

## YAML Equivalent

```yaml
data:
  zenodo_record: "6620869"
  zoo_dir: "data/model_zoo"
  n_train: 5000
  n_test: 500
  split_seed: 42
  stats_features_path: "outputs/statistics_features.npz"

model:
  hidden_dim: 128
  num_layers: 3
  invariant_output: true
  network_spec: "resnet20"

train:
  optimizer: adam
  lr: 0.001
  weight_decay: 0.0001
  batch_size: 32
  epochs: 100
  early_stop_patience: 20
  lr_schedule: reduce_on_plateau
  lr_factor: 0.5
  lr_patience: 10
  loss: mse
  seeds: [42, 123, 7]

baseline:
  alphas: [0.01, 0.1, 1.0, 10.0]

eval:
  metrics: [r2, mae]
  equivariance_tol: 1.0e-5
  n_permutation_trials: 500
  r2_target: 0.85
  equivariance_pass_target: 1.0

logging:
  results_path: "outputs/nfn_results.csv"
  figures_dir: "figures"
  log_level: INFO
```

## Validation Rules

- `train.batch_size` > 0 and ≤ `data.n_train`
- `data.n_train + data.n_test` ≤ 5500 (Model Zoo total pool)
- `eval.equivariance_tol` > 0 (numerical tolerance, not exact 0)
- `len(train.seeds) == 3` (per NFR1 mechanism validation requirement)
- `model.hidden_dim` > 0, `model.num_layers` ≥ 1
- `eval.r2_target` ∈ (0, 1]
- `train.lr_patience` < `train.early_stop_patience` (scheduler must act before early stop)

## Subtasks

| ID | Subtask | Description |
|----|---------|--------------|
| C-M1-1 | Dataclass module | Implement `config.py` with dataclasses above |
| C-M1-2 | Seed utility | `set_seed(seed)` helper (torch/numpy/random), same pattern as archived h-m1 code |
