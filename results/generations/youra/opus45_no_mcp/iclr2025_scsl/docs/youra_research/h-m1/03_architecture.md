# Architecture: H-M1 Gradient Starvation Mechanism (MECHANISM/FULL)

Applied: Backward-hook gradient magnitude capture on classifier layer (PyTorch `register_full_backward_hook`)
Applied: Rolling-window numerical differentiation for inflection-point detection (reuse H-E1 pattern)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (h-e1)
**Analyzed Path**: `h-e1/code/`
**Findings**: Flat module layout, no package prefix — files import each other directly (e.g. `from model import build_resnet50`), run from within `code/` dir. `data.get_loaders` returns dict of WILDS DataLoaders yielding `(x, y, metadata)` with `metadata[:,0]` = group id. `evaluate.evaluate_epoch(model, loader, device)` returns `(wga, group_acc_dict)`. `detector.CrystallizationDetector` logs per-epoch WGA and exposes `detect_crystallization_peak(threshold) -> (peak_idx, peak_value, is_significant)` searching first 50% of history. `train.train(dataset_name, cfg)` returns `{'wga_history','group_acc_history','detector'}`. H-M1 will copy these files (not import cross-hypothesis) since h-e1 has no installable package — training loop is extended in place with hook wiring.

---

## File Structure

```
h-m1/code/
  model.py        # copied from h-e1: build_resnet50 (unchanged)
  data.py          # copied from h-e1: get_loaders (unchanged)
  detector.py       # copied from h-e1: CrystallizationDetector (unchanged)
  evaluate.py       # copied from h-e1: compute_wga, evaluate_epoch (unchanged)
  gradient_tracker.py  # NEW: GradientTracker (per-group gradient hook)
  inflection.py     # NEW: gradient ratio inflection detection + Pearson correlation
  train.py          # EXTENDED: h-e1 train.py + GradientTracker wiring
  visualize.py       # EXTENDED: h-e1 plots + gradient/correlation figures
  config.py         # EXTENDED: h-e1 Config + gradient/correlation params
  run.py            # NEW: orchestration for H-M1 (single dataset: waterbirds)
```

---

## Modules

### gradient_tracker.py (NEW)

**Dependencies**: torch

```python
class GradientTracker:
    def __init__(self, model: nn.Module, majority_group: int = 0, minority_group: int = 3):
        """Registers full backward hook on model.fc."""
    def _gradient_hook(self, module, grad_input, grad_output) -> None: ...
    def compute_group_gradient_ratio(self, batch_groups: Tensor) -> float | None:
        """minority_norm / (majority_norm + eps) for current batch. None if either group absent."""
    def log_epoch_gradients(self, epoch: int, ratios: list[float]) -> None:
        """Appends {'epoch','gradient_ratio': mean(ratios), 'group_norms': dict} to self.gradient_history."""
    def get_history(self) -> list[dict]: ...
```

### inflection.py (NEW)

**Dependencies**: numpy, scipy.stats, scipy.ndimage

```python
def compute_inflection_epoch(gradient_ratio_history: list[float], smoothing_window: int = 5) -> tuple[int, np.ndarray]:
    """Smooths ratio series, computes d(ratio)/dt, returns (inflection_epoch, first_derivative).
    Inflection = epoch of max |d/dt| acceleration within first 50% of training."""

def correlate_with_wga(inflection_epoch: int, wga_peak_epoch: int, gradient_history: list[float], wga_history: list[float]) -> dict:
    """Pearson r between gradient_ratio series and WGA series (aligned by epoch).
    Returns {'r': float, 'p_value': float, 'inflection_epoch', 'wga_peak_epoch',
    'temporal_precedence': bool  # True if inflection_epoch <= wga_peak_epoch
    'gate_pass': bool  # r > 0.7 and inflection_epoch < 0.5*n_epochs}."""
```

### train.py (EXTENDED)

**Dependencies**: model.py, data.py, evaluate.py, detector.py, gradient_tracker.py, config.py

```python
def train_one_epoch(model, loader, optimizer, criterion, device, tracker: GradientTracker) -> tuple[float, list[float]]:
    """Same as h-e1 but after each loss.backward(), before optimizer.step(),
    calls tracker.compute_group_gradient_ratio(metadata[:,0]); collects per-batch ratios.
    Returns (avg_loss, batch_ratios)."""

def train(dataset_name: str, cfg: Config) -> dict:
    """h-e1 train() + GradientTracker(model) instantiation; after each epoch calls
    tracker.log_epoch_gradients(epoch, batch_ratios).
    Returns {'wga_history','group_acc_history','detector','gradient_history'}."""
```

### visualize.py (EXTENDED)

**Dependencies**: matplotlib, inflection.py

```python
def plot_wga_curve(wga_history, peak_epoch, save_path) -> None: ...          # reused from h-e1
def plot_second_derivative(d2, peak_epoch, save_path) -> None: ...           # reused from h-e1
def plot_gradient_ratio_timeline(gradient_history: list[dict], inflection_epoch: int, save_path: str) -> None: ...
def plot_wga_gradient_overlay(wga_history: list[float], gradient_history: list[dict], save_path: str) -> None:
    """Dual-axis: WGA (left) vs gradient ratio (right) over epochs."""
def plot_per_group_gradient_norms(gradient_history: list[dict], save_path: str) -> None: ...
def plot_gate_metrics_comparison(correlation_result: dict, save_path: str) -> None:
    """REQUIRED gate figure: inflection epoch vs WGA peak epoch, r/p annotated."""
```

### config.py (EXTENDED)

```python
@dataclass
class Config:
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    batch_size: int = 128
    epochs_waterbirds: int = 100
    smoothing_window: int = 5
    detection_threshold: float = -0.01
    seed: int = 42
    majority_group: int = 0
    minority_group: int = 3
    checkpoint_dir: str = "./checkpoints"
    checkpoint_every: int = 1
    data_root: str = "./data"
```

### run.py (NEW)

**Dependencies**: all above

```python
def main() -> None:
    """train(waterbirds, cfg) -> detector.detect_crystallization_peak()
    -> inflection.compute_inflection_epoch(gradient_history)
    -> inflection.correlate_with_wga(...)
    -> save all figures to h-m1/figures/
    -> print gate result: PASS if r>0.7 and inflection_epoch<50."""
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| build_resnet50 | `from model import build_resnet50` | `h-m1/code/model.py` (copied verbatim from `h-e1/code/model.py`) |
| get_loaders | `from data import get_loaders` | `h-m1/code/data.py` (copied verbatim from `h-e1/code/data.py`) |
| evaluate_epoch, compute_wga | `from evaluate import evaluate_epoch, compute_wga` | `h-m1/code/evaluate.py` (copied verbatim from `h-e1/code/evaluate.py`) |
| CrystallizationDetector | `from detector import CrystallizationDetector` | `h-m1/code/detector.py` (copied verbatim from `h-e1/code/detector.py`) |

**Verified from**: `h-e1/code/` (actual implementation — flat, no package prefix; files copied not cross-imported since h-e1 has no installable package)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Port h-e1 base modules | Copy model.py, data.py, evaluate.py, detector.py unchanged; extend config.py | 4 | 1+1+1+1 |
| M-2 | GradientTracker implementation | Backward hook on model.fc, per-group norm ratio, epoch aggregation | 9 | 2+2+3+2 |
| M-3 | Training loop integration | Wire GradientTracker into train_one_epoch/train, collect per-batch ratios | 8 | 2+2+2+2 |
| M-4 | Inflection detection | compute_inflection_epoch: smoothing + derivative + first-50% search | 7 | 2+1+3+1 |
| M-5 | Correlation analysis | Pearson r/p between gradient ratio and WGA series, temporal precedence check | 8 | 2+2+2+2 |
| M-6 | Gate evaluation | Combine inflection + crystallization peak, apply gate thresholds (r>0.7, epoch<50) | 6 | 1+1+2+2 |
| M-7 | Visualization suite | 4 required figures incl. mandatory gate metrics comparison | 9 | 3+2+2+2 |
| M-8 | Run orchestration | run.py: train -> detect -> correlate -> visualize -> gate report | 6 | 1+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-2, M-7], Low(4-8): [M-1, M-3, M-4, M-5, M-6, M-8]

---

## Notes

- No new model architecture — GradientTracker observes gradients via hooks, does not modify forward/backward computation (per PRD Section 9: "no model intervention").
- Single seed (42), single dataset (Waterbirds only) per experiment brief.
- h-e1 modules copied rather than package-imported since h-e1/code has no `__init__.py`/setup.py; avoids fragile relative-path cross-hypothesis imports.
