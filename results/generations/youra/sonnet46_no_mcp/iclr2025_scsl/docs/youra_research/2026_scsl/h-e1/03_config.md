# Configuration: H-E1 — Checkpoint Linear Probe Battery (EXISTENCE)

Applied: Standard PyTorch ERM + sklearn LogisticRegression probe config pattern (green-field)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Config Files Found**: None - new config design
**Pattern Used**: dataclass

---

## Python Dataclass Definitions (`code/config.py`)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class TrainConfig:
    dataset: str                    # "waterbirds" | "celeba"
    data_root: str                  # path to dataset root
    checkpoint_dir: str             # path for checkpoint output
    epochs: int                     # 300 (waterbirds) | 50 (celeba)
    checkpoint_interval: int = 2    # save every 2 epochs (H-E1 protocol, Phase 2B A5)
    batch_size: int = 128           # GroupDRO paper (Sagawa et al. 2020)
    lr: float = 1e-3                # GroupDRO paper
    momentum: float = 0.9           # GroupDRO paper
    weight_decay: float = 1e-4      # GroupDRO paper
    seeds: List[int] = field(default_factory=lambda: [1, 2, 3, 4, 5])
    num_workers: int = 4

@dataclass
class ProbeConfig:
    C: float = 1.0                  # DFR paper (Kirichenko et al. 2022)
    max_iter: int = 1000            # convergence for Waterbirds val N=1,199
    solver: str = "lbfgs"           # DFR paper
    random_state: int = 42

@dataclass
class GateConfig:
    min_window_fraction: float = 0.10   # ≥10% epochs for gate (Phase 2B gate criterion)
    p_threshold: float = 0.05           # standard alpha for paired t-test
    min_seeds: int = 3                  # minimum seeds for statistical validity
    t_star_delta_threshold: float = 0.02  # delta < 0.02 defines t* transition
    t_star_consecutive: int = 3         # 3 consecutive checkpoints below threshold

@dataclass
class DatasetPathConfig:
    waterbirds_root: str = "./data/waterbirds"
    celeba_root: str = "./data"
    waterbirds_metadata_csv: str = "metadata.csv"
    waterbirds_spurious_col: str = "place"   # 0=land, 1=water
    waterbirds_core_col: str = "y"           # 0=landbird, 1=waterbird
    celeba_spurious_attr: str = "Blond_Hair"
    celeba_core_attr: str = "Male"
    waterbirds_splits: dict = None
    celeba_splits: dict = None

    def __post_init__(self):
        if self.waterbirds_splits is None:
            self.waterbirds_splits = {"train": "train", "val": "val", "test": "test"}
        if self.celeba_splits is None:
            self.celeba_splits = {"train": "train", "val": "valid", "test": "test"}

@dataclass
class ExperimentConfig:
    train: TrainConfig
    probe: ProbeConfig
    gate: GateConfig
    paths: DatasetPathConfig
    results_dir: str = "./results/h-e1"
```

---

## YAML Configurations

### `configs/waterbirds.yaml`

```yaml
train:
  dataset: "waterbirds"
  data_root: "./data/waterbirds"
  checkpoint_dir: "./checkpoints/waterbirds"
  epochs: 300
  checkpoint_interval: 2
  batch_size: 128
  lr: 0.001
  momentum: 0.9
  weight_decay: 0.0001
  seeds: [1, 2, 3, 4, 5]
  num_workers: 4

probe:
  C: 1.0
  max_iter: 1000
  solver: "lbfgs"
  random_state: 42

gate:
  min_window_fraction: 0.10
  p_threshold: 0.05
  min_seeds: 3
  t_star_delta_threshold: 0.02
  t_star_consecutive: 3

paths:
  waterbirds_root: "./data/waterbirds"
  waterbirds_metadata_csv: "metadata.csv"
  waterbirds_spurious_col: "place"
  waterbirds_core_col: "y"
  waterbirds_splits:
    train: "train"
    val: "val"
    test: "test"

results_dir: "./results/h-e1"
```

### `configs/celeba.yaml`

```yaml
train:
  dataset: "celeba"
  data_root: "./data"
  checkpoint_dir: "./checkpoints/celeba"
  epochs: 50
  checkpoint_interval: 2
  batch_size: 128
  lr: 0.001
  momentum: 0.9
  weight_decay: 0.0001
  seeds: [1, 2, 3, 4, 5]
  num_workers: 4

probe:
  C: 1.0
  max_iter: 1000
  solver: "lbfgs"
  random_state: 42

gate:
  min_window_fraction: 0.10
  p_threshold: 0.05
  min_seeds: 3
  t_star_delta_threshold: 0.02
  t_star_consecutive: 3

paths:
  celeba_root: "./data"
  celeba_spurious_attr: "Blond_Hair"
  celeba_core_attr: "Male"
  celeba_splits:
    train: "train"
    val: "valid"
    test: "test"

results_dir: "./results/h-e1"
```

---

## Hyperparameter Justification

| Parameter | Value | Source |
|-----------|-------|--------|
| `lr` | 1e-3 | GroupDRO paper (Sagawa et al. 2020), ERM baseline |
| `momentum` | 0.9 | GroupDRO paper, standard SGD setting |
| `weight_decay` | 1e-4 | GroupDRO paper, ERM baseline |
| `batch_size` | 128 | GroupDRO codebase default |
| `epochs` (Waterbirds) | 300 | GroupDRO standard training length for Waterbirds |
| `epochs` (CelebA) | 50 | GroupDRO standard training length for CelebA |
| `checkpoint_interval` | 2 | H-E1 protocol Phase 2B assumption A5; tradeoff between temporal resolution and disk usage |
| `C` (probe) | 1.0 | DFR paper (Kirichenko et al. 2022), L2 logistic regression default |
| `max_iter` (probe) | 1000 | Convergence requirement for lbfgs on Waterbirds val N=1,199 |
| `solver` (probe) | lbfgs | DFR paper; efficient for small N with L2 penalty |
| `min_window_fraction` | 0.10 | Phase 2B gate criterion: ≥10% of epochs must show delta > 0 |
| `p_threshold` | 0.05 | Standard alpha level for hypothesis testing |
| `min_seeds` | 3 | Minimum for paired t-test validity; 5 recommended |
| `t_star_delta_threshold` | 0.02 | Near-zero delta threshold; 2% tolerance for numerical stability |
| `t_star_consecutive` | 3 | 3 consecutive checkpoints = 6 epochs; avoids transient dips |

---

## A-4: Statistical Analysis [Complexity: 11 Medium, Budget: 2 subtasks]

Applied: Standard PyTorch ERM + sklearn probe config pattern

### C-4-1: Gate Evaluation Config

```python
@dataclass
class GateConfig:
    min_window_fraction: float = 0.10   # Phase 2B gate: ≥10% epochs contiguous delta>0
    p_threshold: float = 0.05           # standard alpha; paired t-test across seeds
    min_seeds: int = 3                  # minimum valid sample size for t-test
    t_star_delta_threshold: float = 0.02  # delta<0.02 for 3 epochs defines t* (near-zero)
    t_star_consecutive: int = 3         # avoids transient signal loss triggering t*
```

### C-4-2: Results Schema (`h-e1_results.json`)

```python
# JSON output schema for h-e1_results.json
RESULTS_SCHEMA = {
    "hypothesis_id": "h-e1",
    "dataset": str,               # "waterbirds" | "celeba"
    "gate_pass": bool,
    "window_fraction": float,     # max contiguous delta>0 window / total epochs
    "p_value": float,             # paired t-test p-value across seeds
    "gap_area": {
        "mean": float,            # mean Σmax(delta(t),0) across seeds
        "ci_95_low": float,
        "ci_95_high": float
    },
    "t_star_mean": float,         # mean transition epoch across seeds
    "t_star_std": float,          # std of t* across seeds (target < 10)
    "per_seed": [
        {
            "seed": int,
            "window_fraction": float,
            "gap_area": float,
            "t_star": int,
            "delta_curve": [float],     # list of delta(t) values per checkpoint
            "spurious_curve": [float],
            "core_curve": [float],
            "epochs": [int]
        }
    ],
    "celeba_replication": {
        "window_fraction": float,
        "gate_pass": bool         # directional replication: delta>0 window exists
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Gate Evaluation Config | GateConfig dataclass with all threshold values |
| C-4-2 | Results Schema | JSON output schema for h-e1_results.json |

---

## A-1: Data Loaders [Complexity: 10 Medium, Budget: 1 subtask]

Applied: Standard PyTorch ERM + sklearn probe config pattern

### C-1-1: Dataset Path Configuration

```python
@dataclass
class DatasetPathConfig:
    # Waterbirds
    waterbirds_root: str = "./data/waterbirds"
    waterbirds_metadata_csv: str = "metadata.csv"
    waterbirds_spurious_col: str = "place"    # 0=land, 1=water
    waterbirds_core_col: str = "y"            # 0=landbird, 1=waterbird
    waterbirds_splits: dict = None            # {"train":"train","val":"val","test":"test"}

    # CelebA
    celeba_root: str = "./data"
    celeba_spurious_attr: str = "Blond_Hair"
    celeba_core_attr: str = "Male"
    celeba_splits: dict = None                # {"train":"train","val":"valid","test":"test"}

# Preprocessing transforms (eval/val):
# transforms.Compose([
#     transforms.Resize(256),
#     transforms.CenterCrop(224),
#     transforms.ToTensor(),
#     transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
# ])

# Training augmentation:
# transforms.Compose([
#     transforms.RandomResizedCrop(224),
#     transforms.RandomHorizontalFlip(),
#     transforms.ToTensor(),
#     transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
# ])
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Dataset Path Config | DatasetPathConfig with Waterbirds/CelebA paths, split identifiers, label column mappings, and transform spec |
