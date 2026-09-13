# Architecture: H-M2 (Spurious-Specificity Mechanism Test)

Applied: modular-training-regime-separation

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from actual h-e1 code (filesystem read; Serena project activation unavailable)
**Analyzed Path**: `docs/youra_research/20260414_scsl/h-e1/code/`
**Findings**: H-E1 uses flat imports (`from config import Config`). Core reusable components: `LossTrajectoryTracker`, `run_epoch_eval_pass` from `train.py`; `extract_trajectory_features`, `compute_auroc_cv` from `evaluate.py`; `WaterbirdsDataset`, `get_dataloaders`, `get_eval_dataloader` from `data.py`.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| WaterbirdsDataset | `from data import WaterbirdsDataset` | `h-e1/code/data.py` |
| get_dataloaders | `from data import get_dataloaders` | `h-e1/code/data.py` |
| get_eval_dataloader | `from data import get_eval_dataloader` | `h-e1/code/data.py` |
| get_minority_labels | `from data import get_minority_labels` | `h-e1/code/data.py` |
| ResNet50Classifier | `from model import ResNet50Classifier` | `h-e1/code/model.py` |
| build_model | `from model import build_model` | `h-e1/code/model.py` |
| LossTrajectoryTracker | `from train import LossTrajectoryTracker` | `h-e1/code/train.py` |
| run_epoch_eval_pass | `from train import run_epoch_eval_pass` | `h-e1/code/train.py` |
| extract_trajectory_features | `from evaluate import extract_trajectory_features` | `h-e1/code/evaluate.py` |
| compute_auroc_cv | `from evaluate import compute_auroc_cv` | `h-e1/code/evaluate.py` |

**Verified from**: `docs/youra_research/20260414_scsl/h-e1/code/` (actual implementation)

**Strategy**: H-M2 code lives in its own directory. H-E1 files are copied into `h-m2/code/` and extended (flat import style preserved).

---

## File Organization

```
h-m2/code/
  config.py       - Extended Config with GroupDRO + regime params
  data.py         - Copy from H-E1, add get_group_counts()
  model.py        - Copy from H-E1 (unchanged)
  trainers.py     - Three training regime implementations
  evaluate.py     - Extended: per-regime AUROC + delta + gate + visualize
  run.py          - Orchestrator: 3 regimes sequentially → compare → gate
  figures/        - Output figures directory
  outputs/        - JSON results, .npy arrays
```

---

## Module Definitions

### Config (`config.py`)

**Dependencies**: none

```python
@dataclass
class Config:
    # Inherited from H-E1
    data_root: str = "../../.data_cache/datasets/waterbirds/waterbird_complete95_forest2water2"
    num_workers: int = 4
    pin_memory: bool = True
    train_crop_size: int = 224
    eval_resize: int = 256
    eval_crop_size: int = 224
    img_mean: Tuple[float, float, float] = (0.485, 0.456, 0.406)
    img_std: Tuple[float, float, float] = (0.229, 0.224, 0.225)
    model_name: str = "resnet50"
    num_classes: int = 2
    epochs: int = 20
    trajectory_epochs: int = 5
    batch_size: int = 128
    lr: float = 0.001
    momentum: float = 0.9
    n_folds: int = 5
    lr_clf_max_iter: int = 1000
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    fig_dpi: int = 300
    fig_format: str = "png"
    # H-M2 additions
    base_seed: int = 42          # seed for regime i = base_seed + i
    num_seeds: int = 3
    num_groups: int = 4
    # ERM
    weight_decay_erm: float = 0.0001
    # GroupDRO
    weight_decay_gdro: float = 1.0
    groupdro_gamma: float = 0.1
    # Gate thresholds
    delta_gdro_threshold: float = 0.10
    delta_random_threshold: float = 0.05
    # Figure filenames
    fig_gate_filename: str = "gate_metrics.png"
    fig_auroc_comparison_filename: str = "auroc_comparison.png"
    fig_group_weights_filename: str = "group_weights_evolution.png"
    fig_grad_variance_filename: str = "gradient_variance.png"
    fig_trajectory_panels_filename: str = "loss_trajectory_panels.png"

def get_config() -> Config: ...
```

---

### DataModule (`data.py`)

**Dependencies**: Config

```python
class WaterbirdsDataset(Dataset):
    def __init__(self, root: str, split: str, transform=None): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> Tuple[Tensor, int, int, int]: ...
    # Returns: (image, label, group_id, sample_idx)

def get_train_transforms(config: Config) -> transforms.Compose: ...
def get_eval_transforms(config: Config) -> transforms.Compose: ...
def get_dataloaders(config: Config) -> Tuple[DataLoader, DataLoader, DataLoader]: ...
def get_eval_dataloader(config: Config) -> DataLoader: ...
def get_minority_labels(dataset: WaterbirdsDataset) -> np.ndarray: ...

# NEW for H-M2
def get_group_counts(dataset: WaterbirdsDataset) -> np.ndarray:
    """Return count per group, shape (4,), for GroupDRO weight init and variance matching."""
    ...
```

---

### ModelModule (`model.py`)

**Dependencies**: Config

```python
class ResNet50Classifier(nn.Module):
    def __init__(self, num_classes: int = 2, pretrained: bool = True): ...
    def forward(self, x: Tensor) -> Tensor: ...
    # x: (B, 3, 224, 224) -> logits: (B, num_classes)

def build_model(config: Config) -> ResNet50Classifier: ...
```

---

### Trainers (`trainers.py`)

**Dependencies**: Config, ResNet50Classifier, LossTrajectoryTracker, run_epoch_eval_pass (from train.py base)

```python
class LossTrajectoryTracker:
    """Copied from H-E1 train.py - unchanged."""
    def __init__(self, num_samples: int, num_epochs: int = 5): ...
    def log_epoch_losses(self, sample_indices: np.ndarray, losses: np.ndarray, epoch_idx: int) -> None: ...
    def get_loss_matrix(self) -> np.ndarray: ...

def run_epoch_eval_pass(
    model: ResNet50Classifier,
    eval_loader: DataLoader,
    device: torch.device,
    tracker: LossTrajectoryTracker,
    epoch_idx: int,
) -> None: ...

def train_erm(
    config: Config,
    model: ResNet50Classifier,
    train_loader: DataLoader,
    eval_loader: DataLoader,
    device: torch.device,
) -> Tuple[ResNet50Classifier, LossTrajectoryTracker]:
    """Standard ERM: uniform cross-entropy loss."""
    ...

def train_groupdro(
    config: Config,
    model: ResNet50Classifier,
    train_loader: DataLoader,
    eval_loader: DataLoader,
    device: torch.device,
    group_counts: np.ndarray,
) -> Tuple[ResNet50Classifier, LossTrajectoryTracker, np.ndarray]:
    """GroupDRO: exponentiated gradient on group losses.
    
    Returns: (model, tracker, group_weights_history)  shape of history: (epochs, 4)
    """
    ...

def compute_variance_matched_weights(
    group_counts: np.ndarray,
    num_samples: int,
    groupdro_gamma: float,
    seed: int,
) -> np.ndarray:
    """Sample per-sample weights matching GroupDRO gradient variance.
    
    Returns: weights shape (num_samples,)
    """
    ...

def train_random_reweight(
    config: Config,
    model: ResNet50Classifier,
    train_loader: DataLoader,
    eval_loader: DataLoader,
    device: torch.device,
    random_weights: np.ndarray,
) -> Tuple[ResNet50Classifier, LossTrajectoryTracker]:
    """Random reweighting: variance-matched sample weights."""
    ...
```

---

### Evaluator (`evaluate.py`)

**Dependencies**: Config, LossTrajectoryTracker

```python
# Copied from H-E1 (unchanged)
def extract_trajectory_features(loss_matrix: np.ndarray) -> np.ndarray: ...
def compute_auroc_cv(features: np.ndarray, minority_labels: np.ndarray, n_splits: int, seed: int) -> Tuple[float, float]: ...

# NEW for H-M2
def evaluate_all_regimes(
    regime_features: Dict[str, np.ndarray],
    minority_labels: np.ndarray,
    config: Config,
) -> Dict[str, Tuple[float, float]]:
    """Compute AUROC CV for each regime.
    
    Args:
        regime_features: {'erm': (N,4), 'groupdro': (N,4), 'random': (N,4)}
    Returns:
        {'erm': (mean, std), 'groupdro': (mean, std), 'random': (mean, std)}
    """
    ...

def compute_delta_auroc(
    auroc_erm: float,
    auroc_gdro: float,
    auroc_random: float,
) -> Tuple[float, float]:
    """Returns (delta_gdro, delta_random)."""
    ...

def evaluate_gate(
    delta_gdro: float,
    delta_random: float,
    config: Config,
) -> Tuple[bool, str]:
    """Gate: delta_gdro > 0.10 AND delta_random < 0.05.
    
    Returns: (passed, result_str)
    """
    ...

def verify_mechanism_activation(
    group_weights_history: np.ndarray,
    groupdro_grad_var: float,
    random_grad_var: float,
) -> Dict[str, bool]:
    """Verify GroupDRO weights diverge; variance within 20% tolerance."""
    ...

# Visualization
def plot_gate_metrics(delta_gdro: float, delta_random: float, config: Config, save_path: str) -> None: ...
def plot_auroc_comparison(auroc_results: Dict[str, Tuple[float, float]], config: Config, save_path: str) -> None: ...
def plot_group_weights_evolution(group_weights_history: np.ndarray, config: Config, save_path: str) -> None: ...
def plot_gradient_variance_comparison(gdro_var: float, random_var: float, config: Config, save_path: str) -> None: ...
def plot_loss_trajectory_panels(
    loss_matrices: Dict[str, np.ndarray],
    minority_labels: np.ndarray,
    config: Config,
    save_path: str,
) -> None: ...
```

---

### Orchestrator (`run.py`)

**Dependencies**: all modules

```python
def set_seed(seed: int) -> None: ...

def run_regime(
    regime_name: str,
    config: Config,
    seed: int,
    device: torch.device,
    group_counts: np.ndarray,
    random_weights: np.ndarray,
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Run one training regime, return (loss_matrix, group_weights_history or None)."""
    ...

def main(config: Config) -> Dict: ...

if __name__ == "__main__":
    config = get_config()
    results = main(config)
    sys.exit(0 if results["gate"]["passed"] else 1)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Extend H-E1 config with GroupDRO/regime params, copy model.py and data.py, add get_group_counts() | 7 | 2+1+2+2 |
| A-2 | ERM Trainer | Copy H-E1 train.py as trainers.py foundation, implement train_erm() wrapping existing LossTrajectoryTracker | 8 | 2+2+2+2 |
| A-3 | GroupDRO Trainer | Implement train_groupdro() with exponentiated gradient weight updates, group loss computation, weight history logging | 14 | 3+3+4+4 |
| A-4 | Random Reweighting | Implement compute_variance_matched_weights() and train_random_reweight() with verified variance matching | 13 | 3+3+4+3 |
| A-5 | Multi-Regime Evaluator | Implement evaluate_all_regimes(), compute_delta_auroc(), evaluate_gate(), verify_mechanism_activation() | 11 | 3+2+3+3 |
| A-6 | Visualization | Implement all 5 plot functions (gate metrics, AUROC comparison, group weights, grad variance, trajectory panels) | 10 | 2+2+3+3 |
| A-7 | Orchestrator | Implement run.py with sequential 3-regime execution, seed management, results aggregation and JSON output | 12 | 3+3+3+3 |
| A-8 | Integration & Gate | End-to-end run, verify mechanism activation, gate evaluation output, verification_state.yaml update | 9 | 2+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-4, A-5, A-7, A-8], Low(4-8): [A-1, A-2, A-6]

---

## Data Flow

- `run.py` loads data once (shared `WaterbirdsDataset`, `eval_loader`, `minority_labels`, `group_counts`)
- For each of 3 seeds: run ERM → GroupDRO → Random Reweighting sequentially
- Each regime returns `loss_matrix (N, 5)` → `extract_trajectory_features` → `(N, 4)`
- `evaluate_all_regimes` computes AUROC CV per regime
- `compute_delta_auroc` → `evaluate_gate` → PASS/FAIL
- All results saved to `outputs/results.json`; figures to `figures/`
