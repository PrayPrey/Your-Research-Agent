# Architecture: H-M2 Post-Crystallization Feature Commitment (MECHANISM/FULL)

Applied: Forward-hook feature extraction on avgpool layer (PyTorch `register_forward_hook`)
Applied: Linear probe training pattern from Kirichenko et al. (2023)

## Codebase Analysis (Serena)

**Project Type**: incremental_hypothesis (base: h-m1)
**Status**: patterns found from base code (h-m1)
**Analyzed Path**: `h-m1/code/`
**Findings**: Flat module layout continuing from h-e1. Copies model.py, data.py, evaluate.py, detector.py from h-e1. New: gradient_tracker.py, inflection.py. H-M2 reuses checkpoint loading, adds feature extraction and probe analysis. Key: checkpoints stored at `h-m1/code/checkpoints/epoch_{n}.pt`.

---

## File Structure

```
h-m2/code/
  model.py          # copied from h-m1: build_resnet50 (unchanged)
  data.py           # copied from h-m1: get_loaders (unchanged)
  config.py         # EXTENDED: h-m1 Config + probe training params
  feature_extractor.py  # NEW: forward hook on avgpool, batch feature extraction
  probe.py          # NEW: LinearProbe class, train/evaluate functions
  analyzer.py       # NEW: FeatureProbeAnalyzer orchestration
  commitment.py     # NEW: commitment detection logic
  visualize.py      # EXTENDED: h-m1 plots + probe accuracy figures
  run.py            # NEW: orchestration for H-M2
```

---

## Modules

### feature_extractor.py (NEW)

**Dependencies**: torch

```python
class FeatureExtractor:
    def __init__(self, model: nn.Module, layer_name: str = "avgpool"):
        """Registers forward hook on specified layer."""
    def _feature_hook(self, module, input, output) -> None: ...
    def extract_batch(self, x: Tensor) -> Tensor:
        """Returns features [B, 2048] for input batch."""
    def extract_dataset(self, model: nn.Module, dataloader: DataLoader, device: str) -> tuple:
        """Returns (features [N, 2048], core_labels [N], spurious_labels [N])."""
    def remove(self) -> None:
        """Detach hook."""
```

### probe.py (NEW)

**Dependencies**: torch

```python
class LinearProbe(nn.Module):
    def __init__(self, input_dim: int = 2048, num_classes: int = 2):
        """Linear layer for probing."""
    def forward(self, x: Tensor) -> Tensor: ...

def train_probe(probe: LinearProbe, features: Tensor, labels: Tensor, 
                lr: float = 0.01, iterations: int = 100) -> LinearProbe:
    """Train probe from scratch using SGD. Returns trained probe."""

def evaluate_probe(probe: LinearProbe, features: Tensor, labels: Tensor) -> float:
    """Returns accuracy (0-1)."""
```

### analyzer.py (NEW)

**Dependencies**: feature_extractor.py, probe.py, commitment.py

```python
class FeatureProbeAnalyzer:
    def __init__(self, model_builder: Callable, checkpoint_dir: str, 
                 crystallization_epoch: int, final_epoch: int, hidden_dim: int = 2048):
        """Setup for temporal probe analysis."""
    def analyze_checkpoint(self, epoch: int, dataloader: DataLoader, device: str) -> dict:
        """Load checkpoint, extract features, train probes, return accuracies."""
    def analyze_all(self, dataloader: DataLoader, device: str) -> dict:
        """Iterate checkpoints crystallization_epoch to final_epoch, return history."""
    def get_commitment_result(self) -> dict:
        """Evaluate commitment criteria from accumulated history."""
```

### commitment.py (NEW)

**Dependencies**: numpy

```python
def check_commitment(spurious_acc_history: list[float], core_acc_history: list[float],
                     noise_margin: float = 0.02, core_threshold: float = 0.85) -> dict:
    """Returns {'committed': bool, 'core_suppressed': bool, 
                'spurious_trend': str, 'core_final': float}."""

def compute_trend(history: list[float]) -> str:
    """Returns 'increasing', 'stable', or 'decreasing'."""
```

### visualize.py (EXTENDED)

**Dependencies**: matplotlib

```python
def plot_probe_accuracy_timeline(spurious_history: list[float], core_history: list[float],
                                  crystallization_epoch: int, save_path: str) -> None:
    """Dual-line plot: spurious vs core probe accuracy over epochs."""

def plot_gate_metrics_comparison(commitment_result: dict, save_path: str) -> None:
    """REQUIRED gate figure: commitment status visualization."""

def plot_commitment_summary(spurious_history: list[float], core_history: list[float],
                            commitment_result: dict, save_path: str) -> None:
    """Summary figure with trend annotations."""
```

### config.py (EXTENDED)

```python
@dataclass
class Config:
    # Inherited from h-m1
    lr: float = 1e-3
    batch_size: int = 128
    seed: int = 42
    epochs_waterbirds: int = 100
    data_root: str = "./data"
    checkpoint_dir: str = "./checkpoints"
    
    # H-M2 specific
    probe_lr: float = 0.01
    probe_iterations: int = 100
    noise_margin: float = 0.02
    core_suppression_threshold: float = 0.85
    crystallization_epoch: int = -1  # Auto-detect from h-m1/h-e1
    feature_dim: int = 2048
    
    # Paths
    h_m1_checkpoint_dir: str = "../h-m1/code/checkpoints"
    output_dir: str = "./outputs"
    figures_dir: str = "../figures"
```

### run.py (NEW)

**Dependencies**: all above

```python
def main() -> None:
    """
    1. Load crystallization_epoch from h-m1 outputs
    2. Initialize FeatureProbeAnalyzer
    3. Load Waterbirds val/test data
    4. Iterate checkpoints: crystallization_epoch to final
    5. For each: extract features, train probes, record accuracies
    6. Check commitment criteria
    7. Generate figures
    8. Print gate result: PASS if committed and core_suppressed
    """
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| build_resnet50 | `from model import build_resnet50` | `h-m2/code/model.py` (copied from h-m1) |
| get_loaders | `from data import get_loaders` | `h-m2/code/data.py` (copied from h-m1) |
| Config | `from config import Config, CONFIG` | `h-m2/code/config.py` (extended from h-m1) |

**Verified from**: `h-m1/code/` (actual implementation)

---

## Epic Tasks

| ID | Task | Description | Complexity | Subtask Count |
|----|------|-------------|------------|---------------|
| M2-1 | Port h-m1 base modules | Copy model.py, data.py; extend config.py | 3 | 2 |
| M2-2 | Feature extractor | Forward hook on avgpool, batch/dataset extraction | 8 | 3 |
| M2-3 | Linear probe module | LinearProbe class, train/evaluate functions | 6 | 3 |
| M2-4 | Probe analyzer | FeatureProbeAnalyzer: checkpoint iteration, temporal tracking | 10 | 4 |
| M2-5 | Commitment detection | check_commitment logic, trend analysis | 5 | 2 |
| M2-6 | Visualization suite | 3 figures: timeline, gate comparison, summary | 6 | 3 |
| M2-7 | Run orchestration | run.py: load crystallization epoch, analyze, gate report | 6 | 3 |
| M2-8 | Integration | End-to-end test, checkpoint validation | 4 | 2 |

**Total Epic Tasks:** 8
**Total Subtasks:** 22
**Distribution**: Medium(9-13): [M2-4], Low(4-8): [M2-1, M2-2, M2-3, M2-5, M2-6, M2-7, M2-8]

---

## Notes

- No new model training — analysis only on H-M1 checkpoints
- Forward hooks for feature extraction (avgpool layer before fc)
- Linear probes trained fresh per checkpoint (no transfer)
- Single seed (42), single dataset (Waterbirds) per experiment brief
- h-m1 modules copied (model.py, data.py); analyzer/probe are new
