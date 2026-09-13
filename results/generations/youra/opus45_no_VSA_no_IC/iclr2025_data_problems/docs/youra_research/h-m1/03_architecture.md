# Architecture: h-m1

**Type:** MECHANISM | **Epic Range:** 6-12

Applied: No closely-matching KB pattern found (best matches were unrelated diffusers/transformers training loops, similarity <0.46) — architecture based on PRD/brief official-library APIs (trak, kronfluence, captum-style TracIn) instead.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze (only 02c_experiment_brief.md and 03_prd.md present in h-m1/)
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base_hypothesis_folder referenced.

---

## File Organization

```
h-m1/code/
  data.py            # CIFAR-10 loading + probe pair construction
  model.py            # ResNet-18 baseline builder
  train.py             # Fine-tuning loop with checkpointing
  attribution_trak.py  # TRAK method wrapper
  attribution_tracin.py # TracIn method wrapper
  attribution_kronfluence.py # Kronfluence method wrapper
  evaluate.py           # Mode sensitivity scoring + ranking + gate checks
  visualize.py           # Heatmap + radar + distributions + correlation figures
  run_experiment.py      # Orchestrator (main entrypoint)
  config.py               # Central hyperparameters/config
h-m1/figures/            # Output figures
h-m1/checkpoints/        # Saved checkpoints (every 20 epochs)
```

## Modules

### Config (`config.py`)

```python
@dataclass
class ExperimentConfig:
    seed: int = 42
    epochs: int = 200
    batch_size: int = 128
    lr: float = 0.1
    momentum: float = 0.9
    weight_decay: float = 5e-4
    checkpoint_every: int = 20
    proj_dim: int = 2048
    probes_per_mode: int = 1000
    data_root: str = "./data"
    ckpt_dir: str = "./h-m1/checkpoints"
    fig_dir: str = "./h-m1/figures"
```

### Data (`data.py`)

**Dependencies**: config.py

```python
def get_datasets(cfg: ExperimentConfig) -> tuple[Dataset, Dataset]: ...
def get_loaders(train_ds, test_ds, cfg) -> tuple[DataLoader, DataLoader]: ...

def build_probe_pairs(train_ds, test_ds, seed: int) -> dict[str, list[tuple[int, int]]]:
    """Returns {'mem': [(train_idx, test_idx), ...], 'transfer': [...], 'spurious': [...]}"""
```

### Model (`model.py`)

**Dependencies**: config.py

```python
def build_resnet18_cifar10(pretrained: bool = True) -> nn.Module: ...
```

### Train (`train.py`)

**Dependencies**: model.py, data.py, config.py

```python
def train_model(model: nn.Module, train_loader, cfg: ExperimentConfig) -> list[str]:
    """SGD + cosine annealing, saves checkpoint every checkpoint_every epochs.
    Returns list of checkpoint file paths (10 for 200 epochs)."""
```

### Attribution: TRAK (`attribution_trak.py`)

**Dependencies**: model.py, data.py, trak (external)

```python
def compute_trak_scores(model, train_loader, test_loader,
                         probes: dict, cfg: ExperimentConfig) -> dict[str, np.ndarray]:
    """Returns {'mem': scores, 'transfer': scores, 'spurious': scores}, shape (num_probes,) each."""
```

### Attribution: TracIn (`attribution_tracin.py`)

**Dependencies**: model.py, data.py, checkpoint paths from train.py

```python
def compute_tracin_scores(model, checkpoints: list[str], train_loader,
                           probes: dict, cfg: ExperimentConfig) -> dict[str, np.ndarray]:
    """TracIn(z,z') = sum_k eta_k * grad_l(w_k,z) . grad_l(w_k,z'). Same return shape as TRAK."""
```

### Attribution: Kronfluence (`attribution_kronfluence.py`)

**Dependencies**: model.py, data.py, kronfluence (external)

```python
def compute_kronfluence_scores(model, train_loader, test_loader,
                                probes: dict, cfg: ExperimentConfig) -> dict[str, np.ndarray]:
    """Fits EK-FAC factors then computes pairwise scores. Same return shape as TRAK."""
```

### Evaluate (`evaluate.py`)

**Dependencies**: numpy, scipy.stats

```python
def compute_mode_sensitivity(scores: dict[str, np.ndarray]) -> dict[str, float]:
    """mean per mode: {'mem': x, 'transfer': y, 'spurious': z}"""

def build_interaction_matrix(results: dict[str, dict[str, np.ndarray]]) -> np.ndarray:
    """3x3 matrix, rows=methods (trak,tracin,kronfluence), cols=modes, normalized."""

def rank_modes(mode_scores: dict[str, float]) -> tuple[str, ...]: ...

def verify_mechanism_active(results: dict[str, dict[str, np.ndarray]]) -> bool:
    """Asserts variance>0 per method; returns True if >=2 methods differ in mode ranking."""
```

### Visualize (`visualize.py`)

**Dependencies**: matplotlib, seaborn, evaluate.py

```python
def plot_heatmap(interaction_matrix: np.ndarray, methods: list[str], modes: list[str], out_path: str): ...
def plot_radar(results: dict, out_path: str): ...
def plot_distributions(results: dict, out_path: str): ...
def plot_method_correlation(results: dict, out_path: str): ...
```

### Orchestrator (`run_experiment.py`)

**Dependencies**: all modules above

```python
def main(): ...
    # 1. load config, set seeds
    # 2. data.get_datasets/get_loaders, build_probe_pairs
    # 3. model.build_resnet18_cifar10
    # 4. train.train_model -> checkpoints
    # 5. compute_{trak,tracin,kronfluence}_scores -> results dict
    # 6. evaluate.compute_mode_sensitivity, build_interaction_matrix, verify_mechanism_active
    # 7. visualize.* -> save to fig_dir
    # 8. log gate pass/fail per success criteria
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & seeding | ExperimentConfig, seed all RNGs | 4 | 1+1+1+1 |
| A-2 | Data pipeline | CIFAR-10 loaders + probe pair construction (3 modes) | 10 | 3+2+3+2 |
| A-3 | Model builder | ResNet-18 pretrained, fc replaced | 4 | 1+1+1+1 |
| A-4 | Training loop | SGD+cosine, checkpoint every 20 epochs | 9 | 2+2+2+3 |
| A-5 | TRAK integration | Wrap trak.TRAKer featurize/finalize per probe/mode | 12 | 3+4+3+2 |
| A-6 | TracIn integration | Checkpoint-based gradient dot product across 10 ckpts | 13 | 3+4+4+2 |
| A-7 | Kronfluence integration | EK-FAC factor fit + pairwise scores | 14 | 4+4+4+2 |
| A-8 | Evaluation metrics | Mode sensitivity, interaction matrix, ranking, mechanism verify | 8 | 2+2+2+2 |
| A-9 | Visualization | Heatmap (required) + radar/dist/correlation (optional) | 7 | 2+2+1+2 |
| A-10 | Orchestration & gate | run_experiment.py wiring all stages, success-criteria logging | 8 | 2+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-7], Medium(9-13): [A-2, A-4, A-5, A-6, A-10], Low(4-8): [A-1, A-3, A-8, A-9]

---

## External Dependencies (Third-Party, not base hypothesis)

| Library | Install | Used In |
|---------|---------|---------|
| trak | `pip install traker[fast]` | attribution_trak.py |
| kronfluence | `pip install kronfluence` | attribution_kronfluence.py |
| captum / Empirical-Influence-Function | `pip install captum` (or vendor KuchikiRenji/Empirical-Influence-Function) | attribution_tracin.py |
| torchvision | standard | data.py, model.py |
| scipy, numpy | standard | evaluate.py |
| matplotlib, seaborn | standard | visualize.py |

No base_hypothesis_folder — this is the first hypothesis in the sequence (h-m1), gating h-m2/h-c1/h-c2.
