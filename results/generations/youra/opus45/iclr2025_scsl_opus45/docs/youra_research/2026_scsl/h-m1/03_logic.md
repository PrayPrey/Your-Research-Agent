# Logic Design: H-M1 (Curvature Timing Analysis)

**Hypothesis:** Minority samples show delayed curvature stabilization (sign-flip epoch ≥3 later than majority in ≥70% of seeds).
**Gate:** SHOULD_WORK
**Date:** 2026-04-14

Applied: per-sample loss tracking extension pattern
Applied: central differences curvature computation pattern
Applied: multi-seed statistical evaluation pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Direct file reads used (Serena project not activated for this path)
**Analyzed Path**: `docs/youra_research/20260414_scsl/h-e1/code/`
**Relevant Symbols**:
- `LossTrajectoryTracker.__init__(num_samples, num_epochs=5)` - train.py line 26
- `LossTrajectoryTracker.log_epoch_losses(sample_indices, losses, epoch_idx)` - train.py line 38
- `LossTrajectoryTracker.get_loss_matrix() -> np.ndarray` - train.py line 53
- `train(config, model, train_loader, eval_loader, device)` - train.py line 99 (no `seed` param!)
- `run_epoch_eval_pass(model, eval_loader, device, tracker, epoch_idx)` - train.py line 62
- `Config.trajectory_epochs = 5`, `Config.epochs = 20` - config.py lines 35-36

---

## External Dependencies API (Base Hypothesis)

### API Signatures Verified from Actual H-E1 Code

```python
# From: docs/youra_research/20260414_scsl/h-e1/code/train.py (ACTUAL CODE)

class LossTrajectoryTracker:
    def __init__(self, num_samples: int, num_epochs: int = 5):
        """Pre-allocate (num_samples, num_epochs) matrix."""
        ...

    def log_epoch_losses(
        self,
        sample_indices: np.ndarray,  # shape (N_batch,)
        losses: np.ndarray,          # shape (N_batch,)
        epoch_idx: int,              # 0-based
    ) -> None: ...

    def get_loss_matrix(self) -> np.ndarray:  # returns (num_samples, num_epochs)
        ...

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
    # NOTE: No `seed` parameter in actual H-E1 code!
) -> Tuple[ResNet50Classifier, LossTrajectoryTracker]: ...
```

**Key Note**: H-E1 `train()` has NO `seed` param. H-M1 must call `set_seed()` before calling `train()`.
**Key Change**: H-M1 uses `trajectory_epochs=20` (not 5) and logs ALL 20 epochs.

---

## A-1: Project Setup [Complexity: 5, Budget: 1]

**Applied**: Standard PyTorch flat module layout (matching H-E1)

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Directory + copy | Create h-m1/code/, copy data.py + model.py from H-E1 verbatim |

---

## A-2: Extend Config [Complexity: 6, Budget: 1]

### API Signatures

```python
# config.py
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class Config:
    # Dataset (unchanged)
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

    # Training (extended: trajectory_epochs=20)
    epochs: int = 20
    trajectory_epochs: int = 20   # changed from H-E1's 5
    batch_size: int = 128
    lr: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 0.0001

    # Multi-seed (new)
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456, 789, 1011])

    # Curvature parameters (new)
    smoothing_sigma: float = 1.0
    curvature_threshold: float = -0.002
    consecutive_epochs: int = 2

    # Gate (new)
    timing_gap_threshold: float = 3.0
    pass_rate_threshold: float = 0.70

    # Output
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    fig_dpi: int = 300


def get_config() -> Config:
    """Return default H-M1 configuration."""
    return Config()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Config dataclass | Write config.py with all fields above |

---

## A-3: Extend LossTrajectoryTracker [Complexity: 7, Budget: 1]

### API Signatures

```python
# train.py (extends H-E1 train.py)

class LossTrajectoryTracker:
    def __init__(self, num_samples: int, num_epochs: int = 20):
        """Pre-allocate matrix. Default num_epochs changed to 20."""
        # self.matrix shape: (num_samples, num_epochs) = (4795, 20)
        ...

    def log_epoch_losses(
        self,
        sample_indices: np.ndarray,  # (N_batch,)
        losses: np.ndarray,          # (N_batch,)
        epoch_idx: int,
    ) -> None: ...

    def get_loss_matrix(self) -> np.ndarray:
        """Returns (num_samples, 20)."""
        ...


def run_epoch_eval_pass(
    model: ResNet50Classifier,
    eval_loader: DataLoader,
    device: torch.device,
    tracker: LossTrajectoryTracker,
    epoch_idx: int,
) -> None:
    """Identical to H-E1 version."""
    ...


def train(
    config: Config,
    model: ResNet50Classifier,
    train_loader: DataLoader,
    eval_loader: DataLoader,
    device: torch.device,
) -> Tuple[ResNet50Classifier, LossTrajectoryTracker]:
    """ERM training. Logs eval pass for ALL epochs (epoch <= trajectory_epochs=20)."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Extend train.py | Copy H-E1 train.py, change default num_epochs=20 |

---

## A-4: CurvatureTimingAnalyzer [Complexity: 14, Budget: 4]

### API Signatures

```python
# curvature.py
from typing import Any, Dict
import numpy as np
from scipy.ndimage import gaussian_filter1d

class CurvatureTimingAnalyzer:
    """Compute curvature timing statistics from loss trajectories."""

    def __init__(
        self,
        loss_history: np.ndarray,       # (N, 20)
        kappa_threshold: float = -0.002,
        consecutive_epochs: int = 2,
    ) -> None: ...

    def normalize_loss(self) -> np.ndarray:
        """L_norm[t] = L[t] / (L[0] + 1e-8). Returns (N, 20)."""
        ...

    def compute_curvature(self, sigma: float = 1.0) -> np.ndarray:
        """Gaussian smooth then central differences.
        Returns (N, 18): kappa[t] = L[t+1] - 2*L[t] + L[t-1] for t in 1..18."""
        ...

    def detect_sign_flip_epoch(self, curvature: np.ndarray) -> np.ndarray:
        """First epoch where curvature > threshold for `consecutive_epochs` in a row.
        curvature: (N, 18) -> returns (N,) int array.
        If no flip found: value = 20 (num_epochs) + 2."""
        ...

    def compute_timing_gap(
        self,
        group_labels: np.ndarray,  # (N,) int, groups 0-3
    ) -> Dict[str, Any]:
        """Compute minority vs majority median sign-flip epochs and gap.

        minority_mask = (group_labels == 1) | (group_labels == 3)
        Returns dict with keys:
          timing_gap: float  (median_minority - median_majority)
          minority_median_epoch: float
          majority_median_epoch: float
          minority_sign_flips: np.ndarray  (N_min,)
          majority_sign_flips: np.ndarray  (N_maj,)
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| loss_history | (N, 20) | Raw per-sample losses, N=4795 |
| L_norm | (N, 20) | Normalized: L[t] / (L[0] + 1e-8) |
| L_smooth | (N, 20) | After gaussian_filter1d(sigma) along axis=1 |
| curvature | (N, 18) | Central diff: L[t+1] - 2L[t] + L[t-1], t=1..18 |
| sign_flip_epochs | (N,) | First stabilization epoch per sample |

### Pseudo-code: detect_sign_flip_epoch

```
for each sample i in 0..N-1:
    flip_epoch = num_epochs + 2  # default: never stabilized
    for t in 0 .. len(curvature[i]) - consecutive_epochs:
        window = curvature[i, t : t + consecutive_epochs]
        if all(window > kappa_threshold):
            flip_epoch = t + 1  # 1-based epoch offset from curvature start
            break
    sign_flip_epochs[i] = flip_epoch
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | normalize_loss | Divide by L[0] + 1e-8, shape (N, 20) |
| L-4-2 | compute_curvature | gaussian_filter1d then central diff, shape (N, 18) |
| L-4-3 | detect_sign_flip_epoch | Sliding window search per sample |
| L-4-4 | compute_timing_gap | Minority mask, medians, gap computation |

---

## A-5: Multi-Seed Training [Complexity: 11, Budget: 2]

### API Signatures

```python
# run.py

def set_seed(seed: int) -> None:
    """Set torch, numpy, random seeds for reproducibility."""
    ...

def run_single_seed(
    config: Config,
    seed: int,
    device: torch.device,
) -> Dict[str, Any]:
    """Run full pipeline for one seed.

    Steps: set_seed -> build_model -> get_dataloaders -> train ->
           CurvatureTimingAnalyzer -> compute_timing_gap
    Returns dict with keys:
      seed: int
      loss_matrix: np.ndarray  (N, 20)
      group_labels: np.ndarray  (N,)
      timing_gap: float
      minority_median_epoch: float
      majority_median_epoch: float
      sign_flip_epochs: np.ndarray  (N,)
      curvature: np.ndarray  (N, 18)
      gap_passes: bool  (timing_gap >= config.timing_gap_threshold)
    """
    ...

def main(config: Config) -> Dict[str, Any]:
    """Multi-seed orchestration.

    Loop over config.seeds -> run_single_seed -> collect results ->
    evaluate_timing_gap -> save results.json -> generate figures
    Returns aggregate gate evaluation dict.
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | run_single_seed | Full per-seed pipeline |
| L-5-2 | main + set_seed | Multi-seed loop, aggregation, save |

---

## A-6: Gate Evaluation [Complexity: 8, Budget: 1]

### API Signatures

```python
# evaluate.py

def evaluate_timing_gap(
    results_per_seed: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Compute aggregate gate metrics from per-seed results.

    Returns dict:
      gaps: List[float]             per-seed timing gaps
      passes: List[bool]            per-seed gap >= 3.0
      pass_rate: float              fraction passing
      mean_gap: float
      std_gap: float
      gate_passed: bool             pass_rate >= 0.70
    """
    ...

def evaluate_gate(pass_rate: float, threshold: float = 0.70) -> bool:
    """Return True if pass_rate >= threshold."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Gate functions | evaluate_timing_gap + evaluate_gate |

---

## A-7: Visualization [Complexity: 12, Budget: 2]

### API Signatures

```python
# evaluate.py (continued)

def plot_gate_metrics(
    results: Dict[str, Any],   # from evaluate_timing_gap
    save_path: str,
    config: Config,
) -> None:
    """Bar chart: per-seed timing gap vs 3-epoch threshold + pass rate vs 70%."""
    ...

def plot_curvature_trajectories(
    curvature_per_seed: List[np.ndarray],  # list of (N, 18)
    group_labels: np.ndarray,              # (N,)
    save_path: str,
    config: Config,
) -> None:
    """Mean +/- std curvature over epochs, minority vs majority."""
    ...

def plot_sign_flip_distribution(
    sign_flip_epochs_per_seed: List[np.ndarray],  # list of (N,)
    group_labels: np.ndarray,                      # (N,)
    save_path: str,
    config: Config,
) -> None:
    """Violin/histogram: sign-flip epoch distribution, minority vs majority."""
    ...

def plot_per_seed_timing_gap(
    gaps: List[float],
    save_path: str,
    config: Config,
) -> None:
    """Bar chart: gap per seed with 3-epoch threshold line."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | plot_gate_metrics + plot_per_seed_timing_gap | Mandatory gate figures |
| L-7-2 | plot_curvature_trajectories + plot_sign_flip_distribution | Recommended figures |

---

## A-8: Results Logging [Complexity: 8, Budget: 1]

### API Signatures

```python
# evaluate.py (continued)

def save_results(
    gate_results: Dict[str, Any],
    results_per_seed: List[Dict[str, Any]],
    output_dir: str,
) -> None:
    """Save results.json and per-seed npy arrays to output_dir."""
    ...

def update_verification_state(
    gate_passed: bool,
    pass_rate: float,
    yaml_path: str = "../../verification_state.yaml",
) -> None:
    """Update verification_state.yaml: status=COMPLETED, gate result."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | save_results + update_verification_state | JSON + yaml update |

---

## A-9: Integration & Run Orchestration [Complexity: 13, Budget: 1]

### Pseudo-code: main()

```
1. config = get_config()
2. device = select_device()
3. results_per_seed = []
4. for seed in config.seeds:
5.     result = run_single_seed(config, seed, device)
6.     results_per_seed.append(result)
7. gate_results = evaluate_timing_gap(results_per_seed)
8. save_results(gate_results, results_per_seed, config.output_dir)
9. plot_gate_metrics(gate_results, figures_dir/gate_metrics.png, config)
10. plot_per_seed_timing_gap(gate_results.gaps, figures_dir/per_seed_gap.png, config)
11. plot_curvature_trajectories(...)
12. plot_sign_flip_distribution(...)
13. update_verification_state(gate_results.gate_passed, gate_results.pass_rate)
14. print summary
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | Wire run.py main | Connect all modules per pseudo-code above |

---

## Subtask Budget Summary

| Task | Budget | Used |
|------|--------|------|
| A-1 | 1 | 1 |
| A-2 | 1 | 1 |
| A-3 | 1 | 1 |
| A-4 | 4 | 4 |
| A-5 | 2 | 2 |
| A-6 | 1 | 1 |
| A-7 | 2 | 2 |
| A-8 | 1 | 1 |
| A-9 | 1 | 1 |
| **Total** | **14** | **14** |
