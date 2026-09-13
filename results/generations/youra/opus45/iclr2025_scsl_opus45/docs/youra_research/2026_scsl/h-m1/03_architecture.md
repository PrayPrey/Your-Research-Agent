# Architecture Design: H-M1

**Hypothesis:** Minority samples exhibit delayed curvature stabilization (sign-flip epoch ≥3 epochs later than majority in ≥70% of seeds)
**Type:** MECHANISM
**Date:** 2026-04-14
**Prerequisite:** H-E1 (PASSED - AUROC = 0.9452)

Applied: per-sample loss tracking extension pattern
Applied: multi-seed statistical evaluation pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Direct file reads used (Serena project activation failed)
**Analyzed Path**: `docs/youra_research/20260414_scsl/h-e1/code/`
**Findings**: H-E1 flat module layout (no package). `LossTrajectoryTracker` in `train.py`. Config dataclass in `config.py` with `trajectory_epochs=5`, `epochs=20`. All imports are flat: `from config import Config`, `from train import train`. Dataset returns `(image, label, group_id, sample_idx)`.

---

## File Organization

H-M1 code lives in: `docs/youra_research/20260414_scsl/h-m1/code/`

- `config.py` - Extended config (20 epochs, 5 seeds, curvature params)
- `data.py` - Copied from H-E1 (no modification)
- `model.py` - Copied from H-E1 (no modification)
- `train.py` - Extended LossTrajectoryTracker + training loop (20 epochs, all trajectory epochs)
- `curvature.py` - CurvatureTimingAnalyzer (new module)
- `evaluate.py` - Gate evaluation + visualization
- `run.py` - Multi-seed orchestration

---

## Module Definitions

### Config (`config.py`)

**Dependencies**: none

```python
@dataclass
class Config:
    # Dataset (unchanged from H-E1)
    data_root: str = "./data/waterbirds"
    dataset: str = "waterbirds"
    num_workers: int = 4
    pin_memory: bool = True

    # Preprocessing (unchanged)
    train_crop_size: int = 224
    eval_resize: int = 256
    eval_crop_size: int = 224
    img_mean: Tuple[float, float, float] = (0.485, 0.456, 0.406)
    img_std: Tuple[float, float, float] = (0.229, 0.224, 0.225)

    # Model (unchanged)
    model_name: str = "resnet50"
    num_classes: int = 2

    # Training (extended)
    epochs: int = 20
    trajectory_epochs: int = 20      # Changed: track ALL 20 epochs
    batch_size: int = 128
    lr: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 0.0001

    # Multi-seed
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456, 789, 1011])

    # Curvature parameters
    smoothing_sigma: float = 1.0
    curvature_threshold: float = -0.002
    consecutive_epochs: int = 2

    # Gate
    timing_gap_threshold: float = 3.0
    pass_rate_threshold: float = 0.70

    # Output
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    fig_dpi: int = 300

def get_config() -> Config: ...
```

---

### LossTrajectoryTracker + train (`train.py`)

**Dependencies**: Config, ResNet50Classifier (from model.py)

```python
class LossTrajectoryTracker:
    """Extended from H-E1: supports up to 20 trajectory epochs."""
    def __init__(self, num_samples: int, num_epochs: int = 20): ...
    def log_epoch_losses(
        self,
        sample_indices: np.ndarray,
        losses: np.ndarray,
        epoch_idx: int,
    ) -> None: ...
    def get_loss_matrix(self) -> np.ndarray: ...
    # Returns shape (num_samples, num_epochs) = (4795, 20)


def run_epoch_eval_pass(
    model: ResNet50Classifier,
    eval_loader: DataLoader,
    device: torch.device,
    tracker: LossTrajectoryTracker,
    epoch_idx: int,
) -> None: ...

def train(
    config: Config,
    model: ResNet50Classifier,
    train_loader: DataLoader,
    eval_loader: DataLoader,
    device: torch.device,
    seed: int,
) -> Tuple[ResNet50Classifier, LossTrajectoryTracker]: ...
# Runs ALL 20 epochs with eval pass after each epoch
```

---

### CurvatureTimingAnalyzer (`curvature.py`)

**Dependencies**: numpy, scipy.ndimage

```python
class CurvatureTimingAnalyzer:
    def __init__(
        self,
        loss_history: np.ndarray,          # (N, 20)
        kappa_threshold: float = -0.002,
        consecutive_epochs: int = 2,
    ): ...

    def compute_normalized_loss(self) -> np.ndarray: ...
    # Returns (N, 20), L_norm[t] = L[t] / (L[0] + 1e-8)

    def compute_curvature(self, sigma: float = 1.0) -> np.ndarray: ...
    # Returns (N, 18): central differences after Gaussian smoothing

    def detect_sign_flip_epoch(self, curvature: np.ndarray) -> np.ndarray: ...
    # Returns (N,): first epoch index where curvature > threshold for consecutive epochs
    # Default if never stabilized: max_epoch + 2

    def compute_timing_gap(
        self, group_labels: np.ndarray
    ) -> Dict[str, Any]: ...
    # Returns: timing_gap, minority_median_epoch, majority_median_epoch,
    #          minority_sign_flips, majority_sign_flips
    # minority_mask = (group_labels == 1) | (group_labels == 3)
```

---

### evaluate (`evaluate.py`)

**Dependencies**: CurvatureTimingAnalyzer, Config, numpy, matplotlib

```python
def evaluate_timing_gap(
    results_per_seed: List[Dict[str, Any]]
) -> Dict[str, Any]: ...
# Returns: pass_rate, gaps, mean_gap, std_gap, passes, gate_passed

def evaluate_gate(
    pass_rate: float,
    threshold: float = 0.70
) -> bool: ...

def plot_gate_metrics(
    results: Dict[str, Any],
    save_path: str,
    config: Config,
) -> None: ...
# Bar chart: timing gap vs 3-epoch threshold per seed + pass rate vs 70%

def plot_curvature_trajectories(
    curvature_per_seed: List[np.ndarray],
    group_labels: np.ndarray,
    save_path: str,
    config: Config,
) -> None: ...
# Mean ± std curvature over epochs for minority vs majority

def plot_sign_flip_distribution(
    sign_flip_epochs_per_seed: List[np.ndarray],
    group_labels: np.ndarray,
    save_path: str,
    config: Config,
) -> None: ...
# Violin/histogram: minority vs majority sign-flip epoch distribution

def plot_per_seed_timing_gap(
    gaps: List[float],
    save_path: str,
    config: Config,
) -> None: ...
# Bar chart of gap per seed with 3-epoch threshold line
```

---

### run (`run.py`)

**Dependencies**: Config, data.py, model.py, train.py, curvature.py, evaluate.py

```python
def set_seed(seed: int) -> None: ...

def run_single_seed(
    config: Config,
    seed: int,
    device: torch.device,
) -> Dict[str, Any]: ...
# Returns CurvatureTimingAnalyzer results for one seed

def main(config: Config) -> Dict[str, Any]: ...
# Multi-seed loop: for seed in config.seeds → run_single_seed
# Aggregates results → evaluate_gate → save results.json → visualize

if __name__ == "__main__": ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual H-E1 Code)

| Module | Import in H-M1 | Source File |
|--------|----------------|-------------|
| WaterbirdsDataset | `from data import WaterbirdsDataset` | `h-e1/code/data.py` (copy) |
| get_dataloaders | `from data import get_dataloaders, get_eval_dataloader, get_minority_labels` | `h-e1/code/data.py` (copy) |
| ResNet50Classifier | `from model import ResNet50Classifier` | `h-e1/code/model.py` (copy) |
| build_model | `from model import build_model` | `h-e1/code/model.py` (copy) |
| LossTrajectoryTracker | Extended in `train.py` | `h-e1/code/train.py` (extend) |

**Strategy**: Copy `data.py` and `model.py` unchanged. Extend `train.py` (change `num_epochs` default to 20, log all epochs). New `curvature.py` module.

**Verified from**: `docs/youra_research/20260414_scsl/h-e1/code/` (actual implementation)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create h-m1/code/ directory, copy data.py + model.py from H-E1, set up output dirs | 5 | 1+1+1+2 |
| A-2 | Extend Config | Add multi-seed list, curvature params (sigma, threshold, consecutive), update trajectory_epochs=20 | 6 | 1+2+1+2 |
| A-3 | Extend LossTrajectoryTracker | Update default num_epochs=20, ensure all 20 epochs are logged in training loop | 7 | 2+2+1+2 |
| A-4 | Implement CurvatureTimingAnalyzer | normalize_loss, compute_curvature (Gaussian + central diff), detect_sign_flip_epoch, compute_timing_gap | 14 | 4+3+4+3 |
| A-5 | Implement Multi-Seed Training | run_single_seed(), multi-seed loop in run.py, per-seed result collection | 11 | 3+3+3+2 |
| A-6 | Gate Evaluation Logic | evaluate_timing_gap(), pass_rate computation, gate_passed boolean | 8 | 2+2+2+2 |
| A-7 | Visualization | plot_gate_metrics, plot_curvature_trajectories, plot_sign_flip_distribution, plot_per_seed_timing_gap | 12 | 3+2+4+3 |
| A-8 | Results Logging | Save results.json with all metrics, save npy arrays, update verification_state.yaml | 8 | 2+2+2+2 |
| A-9 | Integration & Run Orchestration | Wire run.py: setup → data → model → multi-seed train → curvature → evaluate → visualize → save | 13 | 3+3+4+3 |
| A-10 | Ablation Parameter Support | Configurable sigma (0.5,1.0,1.5,2.0), threshold, consecutive epochs via CLI or config variants | 9 | 2+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-5, A-7, A-9, A-10], Low(4-8): [A-1, A-2, A-3, A-6, A-8]
