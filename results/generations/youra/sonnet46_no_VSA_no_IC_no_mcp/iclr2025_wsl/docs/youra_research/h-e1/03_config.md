---
title: "Config: H-E1 — Orbit Diameter Characterization"
hypothesis_id: H-E1
date: 2026-08-26
---

Applied: Single flat dataclass pattern (all experiment params in one place, no nesting)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — new config design
**Config Files Found**: None — new config
**Pattern Used**: dataclass

---

## ExperimentConfig

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Data
    hf_dataset_id: str = "ModelZoos/ModelZooDataset"
    hf_config: str = "mnist-mlp"
    hf_split: str = "train"

    # Sampling
    n_models: int = 1000
    K: int = 5  # orbit members per model per symmetry type
    seed: int = 42

    # Architecture constants
    D_in: int = 784
    h: int = 64
    D_out: int = 10
    expected_dim: int = 51850  # D_in*h + h + h*D_out + D_out

    # Orbit construction
    scale_log_range: float = 1.0  # scales in [10^-1, 10^1]

    # Evaluation
    threshold: float = 0.05
    n_boot: int = 1000

    # Output paths
    results_path: str = "docs/youra_research/h-e1/results.json"
    figures_dir: str = "docs/youra_research/h-e1/figures"
```

---

## YAML Schema

```yaml
hf_dataset_id: "ModelZoos/ModelZooDataset"
hf_config: "mnist-mlp"
hf_split: "train"
n_models: 1000
K: 5
seed: 42
D_in: 784
h: 64
D_out: 10
expected_dim: 51850
scale_log_range: 1.0
threshold: 0.05
n_boot: 1000
results_path: "docs/youra_research/h-e1/results.json"
figures_dir: "docs/youra_research/h-e1/figures"
```

---

## A-5: Visualization Config [Complexity: 1, Budget: 1]

**Applied**: Single flat dataclass pattern

### Configuration

```python
from dataclasses import dataclass, field
from typing import Dict, Tuple

@dataclass
class FigureConfig:
    dpi: int = 150
    sizes: Dict[str, Tuple[int, int]] = field(default_factory=lambda: {
        "gate_bar":     (8, 5),
        "distribution": (10, 6),
        "scatter":      (8, 8),
        "scale_diam":   (8, 6),
    })
    colors: Dict[str, str] = field(default_factory=lambda: {
        "scaling":  "#2196F3",
        "signflip": "#FF5722",
        "combined": "#4CAF50",
    })
    threshold_color: str = "#E53935"
    threshold_linestyle: str = "--"
    fontsize_title: int = 14
    fontsize_axis: int = 12
    fontsize_tick: int = 10
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | FigureConfig | Define figure sizes, colors, font sizes for visualization module |

---

## Results JSON Schema

```json
{
  "hypothesis_id": "H-E1",
  "seed": 42,
  "n_models": 1000,
  "K": 5,
  "gate": {
    "pass": true,
    "mean_cosine_scaling": 0.0,
    "frac_above_scaling": 0.0,
    "ci_lower_scaling": 0.0
  },
  "stats": {
    "scaling": {
      "mean": 0.0,
      "std": 0.0,
      "p5": 0.0,
      "p95": 0.0,
      "frac_above": 0.0,
      "ci_lower": 0.0,
      "ci_upper": 0.0
    },
    "signflip": {
      "mean": 0.0,
      "std": 0.0,
      "p5": 0.0,
      "p95": 0.0,
      "frac_above": 0.0,
      "ci_lower": 0.0,
      "ci_upper": 0.0
    },
    "combined": {
      "mean": 0.0,
      "std": 0.0,
      "p5": 0.0,
      "p95": 0.0,
      "frac_above": 0.0,
      "ci_lower": 0.0,
      "ci_upper": 0.0
    }
  }
}
```
