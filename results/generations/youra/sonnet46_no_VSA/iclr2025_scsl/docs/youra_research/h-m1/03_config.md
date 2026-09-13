# H-M1 Configuration

Applied: flat-module constants pattern extended to dataclass (H-E3 base verified)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E3)
**Status**: config verified from actual code at `docs/youra_research/h-e3/code/config.py`
**Config Files Found**: `docs/youra_research/h-e3/code/config.py`
**Pattern Used**: flat module-level constants in base; dataclass for H-M1 structured config

---

## Inherited Configuration (Base Hypothesis H-E3)

From `docs/youra_research/h-e3/code/config.py` (verified field names and defaults):

```python
# H-E3 actual constants — verified from implementation
DATA_ROOT         = "/home/PrayPrey/data/waterbirds_v1.0/waterbirds_v1.0/"
CKPT_DIR          = "docs/youra_research/h-e3/results/checkpoints/"
RESULTS_PATH      = "docs/youra_research/h-e3/results/h_e3_results.json"
FIGURES_DIR       = "docs/youra_research/h-e3/figures/"
LR                = 3e-3
MOMENTUM          = 0.9
WEIGHT_DECAY      = 1e-4
BATCH_SIZE        = 32
N_EPOCHS          = 50
CHECKPOINT_EPOCHS = [0, 1, 5, 10, 20, 50]
SEEDS             = [1, 2, 3, 4, 5]
PILOT_SEED        = 1
PILOT_EPOCHS      = 5
K_HUTCHINSON      = 50
MINORITY_GROUPS   = (1, 3)
MAJORITY_GROUPS   = (0, 2)
IMAGENET_MEAN     = [0.485, 0.456, 0.406]
IMAGENET_STD      = [0.229, 0.224, 0.225]
```

**Verified from**: `docs/youra_research/h-e3/code/config.py` (actual implementation)

---

## H-M1 Configuration

```python
from dataclasses import dataclass, field
from typing import Dict, List
import os
import torch

H_E3_CODE = "docs/youra_research/h-e3/code"


@dataclass
class H_M1Config:
    # Paths
    data_root: str = "/home/PrayPrey/data/waterbirds_v1.0/"
    ckpt_dir: str = "docs/youra_research/h-e3/code/outputs/checkpoints"
    results_path: str = "docs/youra_research/h-m1/results/confidence_results.json"
    figures_dir: str = "docs/youra_research/h-m1/figures"

    # Evaluation
    checkpoint_epochs: List[int] = field(default_factory=lambda: [0, 1, 5, 10, 20, 50])
    seeds: List[int] = field(default_factory=lambda: [1, 2, 3, 4, 5])
    tstar_per_seed: Dict[int, int] = field(
        default_factory=lambda: {1: 20, 2: 50, 3: 50, 4: 20, 5: 5}
    )
    batch_size: int = 256  # eval-only; larger than H-E3 training batch (32)
    device: str = "cuda"

    # Gate thresholds
    gate_p_min_low: float = 0.3
    gate_p_min_high: float = 0.7
    gate_p_maj: float = 0.80
    gate_n_seeds: int = 4

    # Visualization
    fig_dpi: int = 150
    fig_format: str = "png"
    fig_width: float = 8.0
    fig_height: float = 5.0
    color_minority: str = "#d62728"
    color_majority: str = "#1f77b4"
    threshold_linestyle: str = "--"
    threshold_linewidth: float = 1.5

    # Inherited from H-E3 (for data loading)
    imagenet_mean: List[float] = field(default_factory=lambda: [0.485, 0.456, 0.406])
    imagenet_std: List[float] = field(default_factory=lambda: [0.229, 0.224, 0.225])
    minority_groups: tuple = (1, 3)  # H-E3 verified field name
    majority_groups: tuple = (0, 2)  # H-E3 verified field name

    def ckpt_path(self, seed: int, epoch: int) -> str:
        return os.path.join(self.ckpt_dir, f"ckpt_seed{seed}_epoch{epoch}.pt")

    def ensure_dirs(self) -> None:
        os.makedirs(self.figures_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.results_path), exist_ok=True)
```

Example instantiation:

```python
cfg = H_M1Config()
# Override device if needed:
cfg = H_M1Config(device="cpu")
```

---

## C-8-1: Visualization Config [Complexity: 1, Budget: 1]

Applied: Standard matplotlib constants pattern

```python
# Extracted from H_M1Config for direct matplotlib use
VIZ = {
    "minority_color":     "#d62728",  # red
    "majority_color":     "#1f77b4",  # blue
    "gate_low_color":     "#888888",  # grey dashed — 0.3 line
    "gate_high_color":    "#888888",  # grey dashed — 0.7 line
    "gate_maj_color":     "#2ca02c",  # green dashed — 0.80 line
    "threshold_linestyle": "--",
    "threshold_linewidth": 1.5,
    "fig_width":  8,
    "fig_height": 5,
    "dpi":    150,
    "format": "png",
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Visualization constants | Color scheme, figure dims, threshold line styles |

---

## C-8-2: Results JSON Schema [Complexity: 1, Budget: 1]

Applied: Standard JSON schema pattern

```yaml
# YAML schema for confidence_results.json
type: object
required: [metadata, seeds, summary]
properties:
  metadata:
    type: object
    properties:
      hypothesis: {type: string, example: "H-M1"}
      date: {type: string, format: date}
      checkpoint_epochs: {type: array, items: {type: integer}}
      seeds: {type: array, items: {type: integer}}
  seeds:
    type: object
    description: "Keyed by seed (as string)"
    additionalProperties:
      type: object
      required: [tstar, trajectory, gate]
      properties:
        tstar:
          type: integer
          description: "Optimal checkpoint epoch for this seed"
        trajectory:
          type: object
          description: "Keyed by epoch (as string)"
          additionalProperties:
            type: object
            properties:
              p_min: {type: number, minimum: 0, maximum: 1}
              p_maj: {type: number, minimum: 0, maximum: 1}
        gate:
          type: object
          properties:
            p_min_at_tstar:    {type: number}
            p_maj_at_tstar:    {type: number}
            minority_boundary: {type: boolean}
            majority_saturated: {type: boolean}
            gap:               {type: number}
            both_pass:         {type: boolean}
  summary:
    type: object
    properties:
      n_seeds_pass:       {type: integer}
      gate_pass:          {type: boolean}
      mean_p_min_at_tstar: {type: number}
      mean_p_maj_at_tstar: {type: number}
```

Example JSON (abbreviated):

```json
{
  "metadata": {
    "hypothesis": "H-M1",
    "date": "2026-08-04",
    "checkpoint_epochs": [0, 1, 5, 10, 20, 50],
    "seeds": [1, 2, 3, 4, 5]
  },
  "seeds": {
    "1": {
      "tstar": 20,
      "trajectory": {
        "0":  {"p_min": 0.52, "p_maj": 0.54},
        "20": {"p_min": 0.31, "p_maj": 0.87}
      },
      "gate": {
        "p_min_at_tstar": 0.31,
        "p_maj_at_tstar": 0.87,
        "minority_boundary": true,
        "majority_saturated": true,
        "gap": 0.56,
        "both_pass": true
      }
    }
  },
  "summary": {
    "n_seeds_pass": 4,
    "gate_pass": true,
    "mean_p_min_at_tstar": 0.33,
    "mean_p_maj_at_tstar": 0.85
  }
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-2 | Results JSON schema | YAML schema + example for confidence_results.json |
