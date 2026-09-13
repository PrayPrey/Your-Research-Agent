# Config: H-E1 Crystallization Zone Detection (EXISTENCE/PoC)

Applied: EXISTENCE PoC pattern - single fixed dataclass config, no HP search, 1 seed
Applied: WILDS-loader dataset naming convention (waterbirds/celebA)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (no base_hypothesis, no existing code)
**Config Files Found**: None
**Pattern Used**: dataclass (Python)

---

## A-5: Crystallization Detector [Complexity: 9, Budget: 9]

**Applied**: EXISTENCE PoC - single fixed config, ablation values are function args, not separate configs.

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    # Training (FR-2)
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    batch_size: int = 128
    epochs_waterbirds: int = 100
    epochs_celeba: int = 50
    seed: int = 42

    # Detector (FR-4) - primary run values
    smoothing_window: int = 5
    detection_threshold: float = -0.01
    search_fraction: float = 0.5  # search first 50% of wga_history

    # Ablation (FR-6) - passed as args to detect_crystallization_peak(),
    # NOT separate config instances (EXISTENCE = no config grid)
    ablation_smoothing_windows: list = field(default_factory=lambda: [3, 5, 7])
    ablation_thresholds: list = field(default_factory=lambda: [-0.005, -0.01, -0.02])

    # Experiment / paths
    datasets: list = field(default_factory=lambda: ["waterbirds", "celebA"])
    data_root: str = "./data"
    output_dir: str = "./results"
    checkpoint_dir: str = "./checkpoints"
    checkpoint_every: int = 1  # epoch

CONFIG = Config()
```

### YAML Schema (equivalent, optional load path)

```yaml
lr: 0.001
momentum: 0.9
weight_decay: 0.0001
batch_size: 128
epochs_waterbirds: 100
epochs_celeba: 50
seed: 42

smoothing_window: 5
detection_threshold: -0.01
search_fraction: 0.5

ablation_smoothing_windows: [3, 5, 7]
ablation_thresholds: [-0.005, -0.01, -0.02]

datasets: ["waterbirds", "celebA"]
data_root: "./data"
output_dir: "./results"
checkpoint_dir: "./checkpoints"
checkpoint_every: 1
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Detector config fields | `smoothing_window`, `detection_threshold`, `search_fraction` in `Config` dataclass; wire into `CrystallizationDetector.__init__` and `detect_crystallization_peak` |
| C-5-2 | Ablation value lists | `ablation_smoothing_windows`, `ablation_thresholds` fields; consumed as loop args by `run.py`/`visualize.py`, no separate Config instances created |

---

## Notes

- Single `Config` dataclass covers training + detector + experiment settings (matches architecture's `config.py`).
- Ablations (FR-6) are **not** separate config objects — `run.py` loops over `ablation_smoothing_windows`/`ablation_thresholds` and calls `CrystallizationDetector(smoothing_window=w)` / `detect_crystallization_peak(threshold=t)` per value. Keeps EXISTENCE PoC to one config, no grid.
- No LR schedule, no multi-seed, no dropout/regularization sweep — out of scope per PRD Section 9.
