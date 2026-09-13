---
hypothesis_id: H-M3
date: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Config: H-M3 — ECE Calibration Measurement

Applied: flat-module constants pattern (reused from H-M1/H-M2)
Applied: Guo-2017 15-bin ECE defaults (WebSearch fallback — Archon MCP unavailable)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending H-M2)
**Status**: Config classes verified from base code
**Config Files Found**: `h-m2/code/config.py`, `h-m1/code/config.py`
**Pattern Used**: flat module-level constants (no dataclass in base code)

---

## Inherited Configuration (Base Hypothesis)

Fields reused verbatim from H-M1/H-M2 actual code:

```python
# From h-m1/code/config.py (actual code)
N_BINS: int = 15
SEED: int = 1
CLEAN_ECE_H_E1: float = 0.279
DELTA_ECE_H_E1: float = 0.071
PRESERVE_RATE_GATE: float = 0.80

# From h-m2/code/config.py (actual code)
DELTA_ACC_GATE: float = -0.10
CONF_WRONG_GATE: float = 0.70
GATE_RATE: float = 0.60
TASK_FILE_MAP: dict  # same structure, extended below
MODEL: str = "Llama-2-7b-hf"
```

---

## Main Experiment Config (H-M3)

```python
"""H-M3 configuration constants."""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

_PROJECT_ROOT = os.environ.get(
    "YOURA_PROJECT_ROOT",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
)

@dataclass
class PathConfig:
    h_e1_results_dir: Path = Path(_PROJECT_ROOT) / "docs/youra_research/h-e1/docs/youra_research/h-e1/results"
    h_m1_subset_file: Optional[Path] = None
    output_dir: Path = Path(_PROJECT_ROOT) / "docs/youra_research/h-m3/results"
    figures_dir: Path = Path(_PROJECT_ROOT) / "docs/youra_research/h-m3/figures"

@dataclass
class TaskConfig:
    task_list: List[str] = field(default_factory=lambda: [
        "advglue_mnli", "advglue_qqp",
        "anli_r1", "anli_r2", "anli_r3"
    ])
    model_list: List[str] = field(default_factory=lambda: ["Llama-2-7b-hf"])

@dataclass
class ECEConfig:
    n_bins: int = 15
    confidence_method: str = "softmax_max"
    gate_threshold: float = 0.05
    stat_alpha: float = 0.05

@dataclass
class AblationConfig:
    bin_counts: List[int] = field(default_factory=lambda: [10, 15, 20])
    thresholds: List[float] = field(default_factory=lambda: [0.03, 0.05, 0.10])
    run_label_filter_ablation: bool = True
```

---

## A-6: Visualizer [Complexity: 13, Budget: 2 subtasks]

Applied: matplotlib rcParams defaults pattern

### C-6-1: FigureConfig

```python
@dataclass
class FigureConfig:
    dpi: int = 150
    figure_size_bar: Tuple[int, int] = (12, 6)
    figure_size_reliability: Tuple[int, int] = (8, 6)
    colormap: str = "RdYlGn"
    gate_line_color: str = "red"
    save_format: str = "png"

MATPLOTLIB_RC = {
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.dpi": 150,
}
```

### C-6-2: ReliabilityDiagramConfig

```python
@dataclass
class ReliabilityDiagramConfig:
    n_bins_display: int = 15
    n_representative_cells: int = 3       # top-3 highest ΔECE cells
    overlay_alpha: float = 0.6
    include_netcal_fallback: bool = True  # Non-standard: netcal as fallback if sklearn unavailable
    # Cell priority: sort cells by |adv_ece - clean_ece| descending, take first n_representative_cells
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | FigureConfig | Static figure layout params + rcParams defaults |
| C-6-2 | ReliabilityDiagramConfig | Reliability diagram display params; prioritizes highest ΔECE cells |

---

## YAML Schema (experiment_config.yaml)

```yaml
paths:
  h_e1_results_dir: null   # override via YOURA_PROJECT_ROOT or set explicitly
  h_m1_subset_file: null
  output_dir: null
  figures_dir: null

tasks:
  task_list:
    - advglue_mnli
    - advglue_qqp
    - anli_r1
    - anli_r2
    - anli_r3
  model_list:
    - Llama-2-7b-hf

ece:
  n_bins: 15
  confidence_method: softmax_max
  gate_threshold: 0.05
  stat_alpha: 0.05

ablation:
  bin_counts: [10, 15, 20]
  thresholds: [0.03, 0.05, 0.10]
  run_label_filter_ablation: true

figure:
  dpi: 150
  figure_size_bar: [12, 6]
  figure_size_reliability: [8, 6]
  colormap: RdYlGn
  gate_line_color: red
  save_format: png

reliability_diagram:
  n_bins_display: 15
  n_representative_cells: 3
  overlay_alpha: 0.6
  include_netcal_fallback: true
```
