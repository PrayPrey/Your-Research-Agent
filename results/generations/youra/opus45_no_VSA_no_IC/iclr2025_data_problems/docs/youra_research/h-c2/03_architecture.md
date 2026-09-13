# Architecture: h-c2

**Type:** CONDITION | **Epic Range:** 6-12

Applied: No closely-matching KB pattern found (best matches unrelated diffusers pipeline docs, similarity <0.47) — architecture follows h-m1's validated CIFAR-10/TRAK/Kronfluence pattern, extended to multi-model (ResNet-18/ViT-Small/ConvNeXt-Tiny).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1) referenced, but no actual code exists yet
**Status**: h-m1/code/ does not exist on disk (glob returned no files) — h-m1 has spec (03_architecture.md) only, no implementation to inspect via Serena. Treated as green-field; following h-m1's spec as design pattern since it's the only available reference.
**Analyzed Path**: h-m1/code/ (checked, empty), h-c2/code/ (checked, empty)
**Findings**: New implementation from scratch, reusing h-m1's probe-pair/attribution methodology conceptually. No import-path reuse possible since h-m1/code/ has no files — h-c2 must reimplement probe construction (with identical seed/logic) rather than import.

---

## File Organization

```
h-c2/code/
  config.py                  # Central hyperparameters/config
  data.py                     # CIFAR-10 loading + probe pair construction (reuses h-m1 seed/logic)
  models.py                    # ResNet-18, ViT-Small, ConvNeXt-Tiny builders
  train.py                      # Per-model fine-tuning loop with checkpointing
  attribution_trak.py            # TRAK method wrapper (cross-architecture)
  attribution_kronfluence.py      # Kronfluence verification wrapper
  cross_model_eval.py              # Profile computation + pairwise Pearson r + bootstrap CI
  visualize.py                      # Heatmap, correlation bar chart, radar charts
  run_experiment.py                  # Orchestrator (main entrypoint)
h-c2/figures/                # Output figures
h-c2/checkpoints/            # Saved checkpoints (every 10 epochs, per model)
```

## Modules

### Config (`config.py`)

```python
@dataclass
class ExperimentConfig:
    seed: int = 42
    batch_size: int = 128
    checkpoint_every: int = 10
    proj_dim: int = 2048
    probes_per_mode: int = 1000
    r_threshold: float = 0.7
    bonferroni_alpha: float = 0.05 / 3
    data_root: str = "./data"
    ckpt_dir: str = "./h-c2/checkpoints"
    fig_dir: str = "./h-c2/figures"

@dataclass
class ModelTrainConfig:
    name: str          # 'resnet18' | 'vit_small' | 'convnext_tiny'
    epochs: int
    lr: float
    optimizer: str      # 'sgd' | 'adamw'
```

### Data (`data.py`)

**Dependencies**: config.py

```python
def get_datasets(cfg: ExperimentConfig) -> tuple[Dataset, Dataset]: ...
def get_loaders(train_ds, test_ds, cfg) -> tuple[DataLoader, DataLoader]: ...

def build_probe_pairs(train_ds, test_ds, seed: int) -> dict[str, list[tuple[int, int]]]:
    """Same construction logic/seed as h-m1: {'memorization': [...], 'feature_transfer': [...], 'spurious': [...]}
    Identical probe indices reused across all 3 models (FR-2)."""

def probe_subset(probes: dict, fraction: float, seed: int) -> dict:
    """ABL-2: random subset of probe pairs per mode, for stability check."""
```

### Models (`models.py`)

**Dependencies**: config.py, torchvision, timm

```python
def build_resnet18(num_classes: int = 10) -> nn.Module: ...
def build_vit_small(num_classes: int = 10) -> nn.Module: ...
def build_convnext_tiny(num_classes: int = 10) -> nn.Module: ...

def build_model(name: str, num_classes: int = 10) -> nn.Module:
    """Dispatch by name: 'resnet18' | 'vit_small' | 'convnext_tiny'."""
```

### Train (`train.py`)

**Dependencies**: models.py, data.py, config.py

```python
def train_model(model: nn.Module, train_loader, test_loader,
                 mcfg: ModelTrainConfig, cfg: ExperimentConfig) -> tuple[list[str], float]:
    """Fine-tunes model, saves checkpoint every checkpoint_every epochs.
    Returns (checkpoint_paths, final_test_accuracy). Asserts test_accuracy > 0.85 (FR-1)."""

def train_all_models(models: dict[str, nn.Module], train_loader, test_loader,
                      cfg: ExperimentConfig) -> dict[str, tuple[list[str], float]]: ...
```

### Attribution: TRAK (`attribution_trak.py`)

**Dependencies**: models.py, data.py, trak (external)

```python
def compute_trak_scores(model, train_loader, test_loader,
                         probes: dict, cfg: ExperimentConfig) -> dict[str, np.ndarray]:
    """Returns {'memorization': scores, 'feature_transfer': scores, 'spurious': scores}."""
```

### Attribution: Kronfluence (`attribution_kronfluence.py`)

**Dependencies**: models.py, data.py, kronfluence (external)

```python
def compute_kronfluence_scores(model, train_loader, test_loader,
                                probes: dict, cfg: ExperimentConfig) -> dict[str, np.ndarray]:
    """Verification method (FR-3, ABL-1). Same return shape as TRAK."""
```

### Cross-Model Evaluation (`cross_model_eval.py`)

**Dependencies**: numpy, scipy.stats

```python
def compute_mode_profile(scores: dict[str, np.ndarray]) -> dict[str, float]:
    """Mean per mode -> profile vector {'memorization': x, 'feature_transfer': y, 'spurious': z}"""

def pairwise_correlations(profiles: dict[str, dict[str, float]]) -> dict[tuple[str, str], dict]:
    """Pearson r + p-value per model pair. Applies Bonferroni correction (FR-5)."""

def bootstrap_ci(v1: np.ndarray, v2: np.ndarray, n_boot: int = 1000) -> tuple[float, float]:
    """95% CI for Pearson r via bootstrap (FR-4)."""

def check_transfer_success(correlations: dict) -> dict:
    """PASS: all r>0.7. PARTIAL: mean r>0.7 some below. FAIL: mean r<0.7 (per success criteria table)."""
```

### Visualize (`visualize.py`)

**Dependencies**: matplotlib, seaborn, cross_model_eval.py

```python
def plot_profile_heatmap(profiles: dict[str, dict[str, float]], out_path: str): ...
def plot_correlation_bars(correlations: dict, threshold: float, out_path: str): ...
def plot_profile_radar(profiles: dict[str, dict[str, float]], out_path: str): ...
def plot_bootstrap_ci(correlations: dict, out_path: str): ...
```

### Orchestrator (`run_experiment.py`)

**Dependencies**: all modules above

```python
def main(): ...
    # 1. load config, set seeds
    # 2. data.get_datasets/get_loaders, build_probe_pairs (identical across models)
    # 3. models.build_model x3 -> train.train_all_models -> checkpoints + accuracies
    # 4. compute_trak_scores per model -> profiles (primary)
    # 5. compute_kronfluence_scores per model -> profiles (verification, ABL-1)
    # 6. cross_model_eval.pairwise_correlations, bootstrap_ci, check_transfer_success
    # 7. ABL-2: probe_subset -> recompute correlations -> stability check
    # 8. visualize.* -> save to fig_dir
    # 9. log PASS/PARTIAL/FAIL per success criteria
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & seeding | ExperimentConfig, ModelTrainConfig, seed all RNGs | 4 | 1+1+1+1 |
| A-2 | Data pipeline | CIFAR-10 loaders + probe pair construction (3 modes, h-m1-consistent) | 9 | 3+2+2+2 |
| A-3 | Model builders | ResNet-18, ViT-Small, ConvNeXt-Tiny via torchvision/timm | 6 | 2+2+1+1 |
| A-4 | Multi-model training | Per-model fine-tune loop, checkpoint every 10 epochs, accuracy gate | 11 | 3+3+2+3 |
| A-5 | TRAK integration | Cross-architecture featurize/finalize per model/probe/mode | 13 | 3+4+3+3 |
| A-6 | Kronfluence integration | EK-FAC factor fit + pairwise scores per model (verification) | 14 | 4+4+4+2 |
| A-7 | Cross-model correlation | Profile vectors, pairwise Pearson r, Bonferroni, bootstrap CI | 10 | 2+3+3+2 |
| A-8 | Ablations | ABL-1 (TRAK vs Kronfluence corr), ABL-2 (probe subset stability) | 8 | 2+3+2+1 |
| A-9 | Visualization | Heatmap + correlation bars (required) + radar/CI plots (optional) | 7 | 2+2+1+2 |
| A-10 | Orchestration & gate | run_experiment.py wiring, PASS/PARTIAL/FAIL logging | 8 | 2+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-6], Medium(9-13): [A-2, A-4, A-5, A-7, A-10], Low(4-8): [A-1, A-3, A-8, A-9]

---

## External Dependencies (Base Hypothesis — Conceptual Only)

No importable code exists in `h-m1/code/` (directory absent). h-c2 reimplements probe-pair construction using the same seed/logic described in `h-m1/03_architecture.md` rather than importing, to guarantee identical probe indices (FR-2). If h-m1/code/ is populated before Phase 4, prefer importing `data.build_probe_pairs` directly instead of reimplementing.

## External Dependencies (Third-Party)

| Library | Install | Used In |
|---------|---------|---------|
| trak | `pip install traker[fast]` | attribution_trak.py |
| kronfluence | `pip install kronfluence` | attribution_kronfluence.py |
| torchvision | standard | data.py, models.py |
| timm | `pip install timm` | models.py (ViT-Small, ConvNeXt-Tiny) |
| scipy, numpy | standard | cross_model_eval.py |
| matplotlib, seaborn | standard | visualize.py |
