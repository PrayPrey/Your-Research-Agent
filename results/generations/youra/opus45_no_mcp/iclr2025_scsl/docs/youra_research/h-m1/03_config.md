# Configuration: H-M1 Gradient Starvation Mechanism

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: config class verified from actual code (`h-e1/code/config.py`, read directly)
**Config Files Found**: `h-e1/code/config.py` — single `@dataclass Config`
**Pattern Used**: dataclass

**Field name note**: h-e1 uses `epochs_waterbirds` / `epochs_celeba` (not a single `epochs` field), and `detection_threshold` / `smoothing_window` (not `inflection_detection_window`). Extended config below reuses these exact names.

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    batch_size: int = 128
    epochs_waterbirds: int = 100
    epochs_celeba: int = 50
    seed: int = 42

    smoothing_window: int = 5
    detection_threshold: float = -0.01
    search_fraction: float = 0.5

    ablation_smoothing_windows: list = field(default_factory=lambda: [3, 5, 7])
    ablation_thresholds: list = field(default_factory=lambda: [-0.005, -0.01, -0.02])

    datasets: list = field(default_factory=lambda: ["waterbirds", "celebA"])
    data_root: str = "./data"
    output_dir: str = "./outputs"
    checkpoint_dir: str = "./checkpoints"
    checkpoint_every: int = 1
```

---

## M-1: Gradient Starvation Config [Complexity: FULL, Budget: ≤30 tasks]

**Applied**: Standard PyTorch backward-hook + dataclass extension pattern (no KB search available this session; per-group gradient tracking follows WILDS/Group-DRO convention).

### Configuration (Python Dataclass — extends h-e1 Config)

```python
from dataclasses import dataclass, field
from h_e1.code.config import Config as BaseConfig  # reuse h-e1 fields

@dataclass
class GradientStarvationConfig(BaseConfig):
    # Inherited: lr, momentum, weight_decay, batch_size, epochs_waterbirds,
    # epochs_celeba, seed, smoothing_window, detection_threshold,
    # search_fraction, data_root, output_dir, checkpoint_dir, checkpoint_every

    # --- LR schedule (new) ---
    lr_milestones: list = field(default_factory=lambda: [30, 60])
    lr_gamma: float = 0.1

    # --- Gradient tracking (new) ---
    track_gradients: bool = True
    minority_group_id: int = 3
    majority_group_id: int = 0
    gradient_aggregation: str = "epoch_mean"  # options: "epoch_mean", "epoch_median"

    # --- Correlation analysis (new) ---
    correlation_threshold: float = 0.7
    # Non-standard: reuses h-e1's smoothing_window (5) for inflection detection
    # instead of a separate field, per PRD FR-5 (avoid duplicate params)
    inflection_detection_window: int = 5

    # --- Single-dataset override (MECHANISM PoC: Waterbirds only) ---
    datasets: list = field(default_factory=lambda: ["waterbirds"])

CONFIG = GradientStarvationConfig()
```

### Subtasks [4/30 used — remainder allocated to Logic Agent implementation tasks]

| ID | Subtask | Description |
|----|---------|--------------|
| C-M1-1 | Config dataclass | Extend `h_e1.Config` with gradient/correlation/LR-schedule fields above |
| C-M1-2 | Group ID mapping | Hardcode Waterbirds group table (0=landbird/land, 3=waterbird/water) as module-level constant, referenced by `minority_group_id`/`majority_group_id` |
| C-M1-3 | StepLR wiring | Config values (`lr_milestones`, `lr_gamma`) feed directly into `torch.optim.lr_scheduler.MultiStepLR` |
| C-M1-4 | Validation defaults | Confirm `epochs_waterbirds=100` (not new `epochs` field) is what training loop consumes — no override needed |
