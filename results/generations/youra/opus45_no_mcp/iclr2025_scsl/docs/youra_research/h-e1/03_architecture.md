# Architecture: H-E1 Crystallization Zone Detection (EXISTENCE/PoC)

Applied: WILDS-loader pattern (group-annotated dataset subset loading via `get_dataset`/`get_subset`)
Applied: Rolling-window numerical differentiation for training-dynamics peak detection

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No `src/`, `code/`, or base_hypothesis folder present in repo.

---

## File Structure (EXISTENCE minimal)

```
h-e1/code/
  model.py       # ResNet-50 wrapper (baseline only, no proposed model variant)
  data.py        # WILDS Waterbirds + CelebA loaders
  train.py       # ERM training loop with per-epoch WGA logging
  detector.py    # CrystallizationDetector (2nd-derivative analysis)
  evaluate.py    # WGA computation, success-criteria check
  visualize.py   # WGA curve, d2WGA/dt2 plot, multi-benchmark + ablation figures
  config.py      # Fixed hyperparameter config (single dict/dataclass)
  run.py         # Entry point: train -> detect -> evaluate -> visualize
```

---

## Modules

### data.py

**Dependencies**: wilds, torchvision.transforms

```python
def get_transforms(eval_mode: bool) -> Compose: ...
def load_dataset(name: str, root_dir: str = "./data") -> WILDSDataset: ...
def get_loaders(name: str, batch_size: int = 128) -> dict[str, DataLoader]:
    """Returns {'train','val','test'} DataLoaders. Each batch yields
    (x, y, metadata) where metadata[:,0] gives group id."""
```

### model.py

**Dependencies**: torchvision.models

```python
def build_resnet50(num_classes: int = 2, pretrained: bool = True) -> nn.Module: ...
```

### train.py

**Dependencies**: model.py, data.py, config.py

```python
def train_one_epoch(model, loader, optimizer, criterion, device) -> float: ...
def train(dataset_name: str, cfg: Config) -> dict:
    """Runs full training, checkpoint every epoch.
    Returns {'wga_history': list[float], 'group_acc_history': list[dict]}."""
```

### evaluate.py

**Dependencies**: data.py

```python
def compute_wga(predictions: Tensor, labels: Tensor, groups: Tensor) -> float: ...
def compute_group_accuracies(predictions, labels, groups) -> dict[int, float]: ...
def evaluate_epoch(model, loader, device) -> tuple[float, dict[int, float]]: ...
```

### detector.py

**Dependencies**: numpy, scipy.ndimage

```python
class CrystallizationDetector:
    def __init__(self, smoothing_window: int = 5): ...
    def log_epoch(self, wga: float) -> None: ...
    def compute_second_derivative(self) -> np.ndarray: ...
    def detect_crystallization_peak(self, threshold: float = -0.01) -> tuple[int, float, bool]:
        """Returns (peak_epoch, peak_magnitude, is_significant).
        Searches first 50% of wga_history only."""
```

### visualize.py

**Dependencies**: matplotlib, detector.py

```python
def plot_wga_curve(wga_history: list[float], peak_epoch: int, save_path: str) -> None: ...
def plot_second_derivative(d2: np.ndarray, peak_epoch: int, save_path: str) -> None: ...
def plot_multi_benchmark(histories: dict[str, list[float]], save_path: str) -> None: ...
def plot_smoothing_sensitivity(wga_history: list[float], windows: list[int], save_path: str) -> None: ...
def plot_group_divergence(group_acc_history: list[dict[int, float]], save_path: str) -> None: ...
```

### config.py

```python
@dataclass
class Config:
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    batch_size: int = 128
    epochs_waterbirds: int = 100
    epochs_celeba: int = 50
    smoothing_window: int = 5
    detection_threshold: float = -0.01
    seed: int = 42
```

### run.py

**Dependencies**: all above

```python
def main(datasets: list[str] = ["waterbirds", "celebA"]) -> None:
    """For each dataset: train() -> log to detector -> detect_crystallization_peak()
    -> evaluate_epoch() -> save figures -> print success-criteria summary
    (2/3 benchmark rule N/A here since only 2 datasets; report both)."""
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | WILDS Waterbirds+CelebA loaders, group metadata, transforms | 10 | 3+3+2+2 |
| A-2 | Model setup | ResNet-50 pretrained, FC head swap | 4 | 1+1+1+1 |
| A-3 | Training loop | ERM loop, SGD, checkpointing, per-epoch WGA eval hook | 11 | 3+3+3+2 |
| A-4 | WGA/group accuracy computation | compute_wga, per-group breakdown | 6 | 2+1+2+1 |
| A-5 | Crystallization detector | Smoothing, 1st/2nd derivative, peak detection in first 50% | 9 | 2+2+3+2 |
| A-6 | Visualization suite | WGA curve, d2 plot, multi-benchmark, smoothing ablation, group divergence | 8 | 3+1+2+2 |
| A-7 | Run orchestration + success check | run.py wiring, threshold ablation (3 thresholds), 2/3 benchmark rule | 7 | 2+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-3, A-5], Low(4-8): [A-2, A-4, A-6, A-7]

---

## Notes

- No "proposed model" module — EXISTENCE hypothesis tests detection of a phenomenon in standard ERM, not a new architecture.
- Ablations (FR-6: smoothing window 3/5/7, threshold -0.005/-0.01/-0.02) are handled as parameterized calls into `detector.py` from `visualize.py`/`run.py`, not separate modules.
- Single seed (42), no multi-seed statistical infra per PRD Section 9 (out of scope).
