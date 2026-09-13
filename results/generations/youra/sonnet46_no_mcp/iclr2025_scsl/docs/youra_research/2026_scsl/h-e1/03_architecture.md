# Architecture: H-E1 — Checkpoint Linear Probe Battery (EXISTENCE)

**Applied**: checkpoint-linear-probe-erm pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No prior hypothesis code to reuse.

---

## File Organization

```
h-e1/code/
├── config.py          # Experiment configuration (dataclass)
├── data/
│   ├── __init__.py
│   ├── waterbirds.py  # Waterbirds dataset loader
│   └── celeba.py      # CelebA dataset loader
├── train.py           # ERM training loop + checkpoint saving
├── probe.py           # Feature extraction + linear probe battery
├── analyze.py         # Statistical analysis (delta, window, t-test)
├── visualize.py       # Figure generation
└── run_experiment.py  # Top-level orchestration script
```

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: None

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class TrainConfig:
    dataset: str                    # "waterbirds" | "celeba"
    data_root: str
    checkpoint_dir: str
    epochs: int                     # 300 (waterbirds) | 50 (celeba)
    checkpoint_interval: int = 2
    batch_size: int = 128
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    seeds: List[int] = field(default_factory=lambda: [1, 2, 3, 4, 5])
    num_workers: int = 4

@dataclass
class ProbeConfig:
    C: float = 1.0
    max_iter: int = 1000
    solver: str = "lbfgs"
    random_state: int = 42

@dataclass
class ExperimentConfig:
    train: TrainConfig
    probe: ProbeConfig
    results_dir: str
    min_window_fraction: float = 0.10   # ≥10% epochs for gate
    p_threshold: float = 0.05
```

---

### Waterbirds Loader (`code/data/waterbirds.py`)

**Dependencies**: torch, torchvision, pandas

```python
class WaterbirdsDataset(Dataset):
    def __init__(self, root: str, split: str, transform=None): ...
    # split: "train" | "val" | "test"
    # labels: y (core: bird species), place (spurious: background)
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict:
        # returns {"image": Tensor, "core_label": int, "spurious_label": int}
        ...

def get_waterbirds_loader(root: str, split: str, batch_size: int,
                          num_workers: int, augment: bool = False) -> DataLoader: ...
```

---

### CelebA Loader (`code/data/celeba.py`)

**Dependencies**: torch, torchvision

```python
class CelebADataset(Dataset):
    def __init__(self, root: str, split: str, transform=None): ...
    # spurious: Blond_Hair, core: Male
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict:
        # returns {"image": Tensor, "core_label": int, "spurious_label": int}
        ...

def get_celeba_loader(root: str, split: str, batch_size: int,
                      num_workers: int, augment: bool = False) -> DataLoader: ...
```

---

### Training (`code/train.py`)

**Dependencies**: config.py, data/waterbirds.py, data/celeba.py

```python
def build_model() -> nn.Module:
    # ResNet-50 ImageNet pretrained, standard FC head for 2-class
    ...

def train_one_seed(cfg: TrainConfig, seed: int) -> None:
    # Sets random seed, trains ERM for cfg.epochs
    # Saves checkpoint every cfg.checkpoint_interval epochs
    # Path: {cfg.checkpoint_dir}/seed_{seed}/epoch_{t:03d}.pt
    ...

def get_transforms(augment: bool) -> transforms.Compose:
    # augment=True: RandomResizedCrop(224) + RandomHorizontalFlip
    # augment=False: Resize(256) + CenterCrop(224) + ImageNet normalize
    ...

def main(cfg: TrainConfig) -> None:
    # Iterates over cfg.seeds, calls train_one_seed per seed
    ...
```

---

### Probe Battery (`code/probe.py`)

**Dependencies**: config.py, data/

```python
def extract_features(model: nn.Module, loader: DataLoader,
                     device: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Returns (features [N,2048], core_labels [N], spurious_labels [N])
    # model.eval() + torch.no_grad(); hooks avgpool output
    ...

def fit_probe(features: np.ndarray, labels: np.ndarray,
              cfg: ProbeConfig) -> float:
    # LogisticRegression(C=cfg.C, max_iter=cfg.max_iter, solver=cfg.solver)
    # Returns accuracy on same split (val set)
    ...

def run_probe_battery(cfg: ExperimentConfig, seed: int,
                      device: str) -> pd.DataFrame:
    # For each checkpoint epoch t:
    #   load state_dict, extract features (val set), fit spurious probe,
    #   fit core probe, record accuracies, discard features
    # Returns DataFrame: columns=[epoch, spurious_acc, core_acc, delta]
    ...

def run_all_seeds(cfg: ExperimentConfig, device: str) -> pd.DataFrame:
    # Calls run_probe_battery per seed, concatenates results
    # Returns DataFrame with seed column added
    ...
```

---

### Statistical Analysis (`code/analyze.py`)

**Dependencies**: numpy, scipy, pandas

```python
def compute_delta_series(df: pd.DataFrame) -> pd.DataFrame:
    # delta(t) = spurious_acc(t) - core_acc(t) per epoch per seed
    ...

def find_contiguous_window(delta_mean: np.ndarray,
                           epochs: np.ndarray) -> Tuple[int, int, float]:
    # Finds longest contiguous window where delta(t) > 0
    # Returns (start_epoch, end_epoch, window_fraction)
    ...

def paired_ttest(delta_by_seed: np.ndarray) -> Tuple[float, float]:
    # Paired t-test: H0: mean(delta) <= 0 over contiguous window
    # Returns (t_stat, p_value)
    ...

def evaluate_gate(window_fraction: float, p_value: float,
                  cfg: ExperimentConfig) -> dict:
    # Returns {"pass": bool, "window_fraction": float, "p_value": float,
    #          "gate": "MUST_WORK", "decision": str}
    ...

def run_analysis(results_df: pd.DataFrame,
                 cfg: ExperimentConfig) -> dict:
    # Orchestrates delta computation, window detection, t-test, gate evaluation
    # Saves analysis results to JSON
    ...
```

---

### Visualization (`code/visualize.py`)

**Dependencies**: matplotlib, pandas, numpy

```python
def plot_delta_curve(results_df: pd.DataFrame, dataset: str,
                     out_path: str) -> None:
    # Mean delta(t) ± std across seeds, shaded positive region
    ...

def plot_seed_overlay(results_df: pd.DataFrame, dataset: str,
                      out_path: str) -> None:
    # Per-seed delta(t) curves overlaid
    ...

def plot_probe_trajectories(results_df: pd.DataFrame, dataset: str,
                            out_path: str) -> None:
    # spurious_acc and core_acc trajectories + delta shaded between
    ...

def generate_all_figures(results_df: pd.DataFrame,
                         cfg: ExperimentConfig) -> None:
    # Calls all plot functions, saves to cfg.results_dir/figures/
    ...
```

---

### Orchestration (`code/run_experiment.py`)

**Dependencies**: All modules

```python
def main(config_path: str, device: str) -> None:
    # 1. Load ExperimentConfig from YAML
    # 2. train.main(cfg.train) — ERM training across all seeds
    # 3. probe.run_all_seeds(cfg, device) — probe battery
    # 4. analyze.run_analysis(results_df, cfg) — statistics + gate
    # 5. visualize.generate_all_figures(results_df, cfg) — figures
    # 6. Print gate decision (PASS/FAIL)
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Loaders | Implement Waterbirds + CelebA dataset classes with spurious/core label extraction | 10 | 3+2+2+3 |
| A-2 | ERM Training | ResNet-50 ERM training loop with checkpoint saving every 2 epochs, ≥3 seeds | 13 | 4+3+3+3 |
| A-3 | Probe Battery | Feature extraction (avgpool hook) + L2 logistic regression per checkpoint per seed | 14 | 4+3+4+3 |
| A-4 | Statistical Analysis | Contiguous window detection, paired t-test, gate evaluation | 11 | 3+2+4+2 |
| A-5 | Visualization | Delta curves, seed overlays, probe trajectory plots | 7 | 2+1+2+2 |
| A-6 | Orchestration + Config | ExperimentConfig dataclass, run_experiment.py pipeline, YAML config | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-1, A-2, A-4], Low(4-8): [A-5, A-6]

---

## Key Interfaces Summary

| Module | Entry Point | Input | Output |
|--------|-------------|-------|--------|
| train.py | `main(cfg)` | TrainConfig | checkpoints on disk |
| probe.py | `run_all_seeds(cfg, device)` | ExperimentConfig | DataFrame |
| analyze.py | `run_analysis(df, cfg)` | DataFrame + config | dict + JSON |
| visualize.py | `generate_all_figures(df, cfg)` | DataFrame + config | figures on disk |

## Gate Criteria

- Window fraction >= 0.10 (contiguous delta(t) > 0 window covering ≥10% of epochs)
- Paired t-test p < 0.05 across ≥3 seeds
- Directional replication on CelebA (delta > 0 observed)
- FAIL → halt H-M1 through H-M4
