# Configuration: h-e1-v3
# Global Percentile Threshold Language Retention Disparity Analysis

Applied: custom config — KB returned irrelevant content (vision/diffusers) for dataclass query
Applied: matplotlib colormaps page found for visualization query — using YlOrRd heatmap, tab10 palette per KB

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Config Files Found**: None — new config
**Pattern Used**: dataclass (single source of truth, importable by all 5 modules)

---

## Main Experiment Config

```python
# code/config.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

# Anchor: resolve paths relative to repo root regardless of invocation directory.
# All modules import REPO_ROOT from here; no __file__ gymnastics scattered across code.
REPO_ROOT = Path(__file__).parent.parent  # code/../ = repo root


@dataclass
class ExperimentConfig:
    # --- data ---
    k_values: list[int]               = field(default_factory=lambda: [10, 20, 30, 40, 50])
    cache_path: str                   = "docs/youra_research/redpajama_sample.parquet"
    min_rows: int                     = 190_000

    # --- output ---
    output_dir: str                   = "docs/youra_research/h-e1-v3"
    figures_dir: str                  = "docs/youra_research/h-e1-v3/figures"

    # --- gate thresholds ---
    gate_v_range: tuple[float, float] = (0.29, 0.41)
    gate_holm_alpha: float            = 0.001

    # --- reproducibility ---
    seed: int                         = 42

    def abs_cache_path(self) -> Path:
        return REPO_ROOT / self.cache_path

    def abs_output_dir(self) -> Path:
        return REPO_ROOT / self.output_dir

    def abs_figures_dir(self) -> Path:
        return REPO_ROOT / self.figures_dir


CFG = ExperimentConfig()
```

---

## Path Resolution Strategy

All paths are stored as **repo-relative strings** in the dataclass.
`REPO_ROOT = Path(__file__).parent.parent` anchors to the repository root from `code/config.py`.

Modules call `CFG.abs_cache_path()` / `CFG.abs_output_dir()` / `CFG.abs_figures_dir()` to get
absolute paths. This means the script can be invoked from any working directory:

```bash
# Both work:
python code/run_h_e1_v3.py
cd code && python run_h_e1_v3.py
```

Do NOT require invocation from repo root. The `__file__`-anchored approach is more robust.

---

## A-3: Visualization Configuration [Complexity: 9, Budget: 1 subtask]

Applied: custom config — no matching KB visualization pattern

```python
# Append to code/config.py (or keep in visualization.py as module-level constants)

import matplotlib
matplotlib.use("Agg")  # CPU-only, no display
import matplotlib.pyplot as plt
import seaborn as sns

# --- shared ---
DPI        = 150
LANG_ORDER = ["en", "de", "fr", "es", "it"]

# --- language color palette (KDE plot + heatmap axis labels) ---
# tab10 first 5 colors: blue, orange, green, red, purple
LANG_PALETTE = dict(zip(LANG_ORDER, sns.color_palette("tab10", 5)))

# --- gate_metrics.png (FR-5.1) ---
GATE_FIG_SIZE       = (7, 4)
GATE_BAR_COLOR_IN   = "#2ca02c"   # green — V within [0.29, 0.41]
GATE_BAR_COLOR_OUT  = "#d62728"   # red   — V outside range
GATE_REF_COLOR      = "#2ca02c"   # dashed green reference lines
GATE_REF_STYLE      = "--"
GATE_REF_ALPHA      = 0.7
GATE_Y_LIM          = (0.0, 0.5)

# --- retention_heatmap.png (FR-5.2) ---
HEATMAP_FIG_SIZE    = (7, 4)
HEATMAP_CMAP        = "YlOrRd"    # low retention = yellow, high = red
HEATMAP_ANNOT       = True
HEATMAP_FMT         = ".2f"
HEATMAP_LANG_ORDER  = LANG_ORDER  # rows
# Non-standard: YlOrRd chosen because high retention (Italian ~88%) should be visually
# alarming (red) relative to low retention (English ~36%), matching the disparity narrative.

# --- perplexity_kde.png (FR-5.3) ---
KDE_FIG_SIZE        = (8, 5)
KDE_ALPHA           = 0.6
KDE_LINEWIDTH       = 1.5
KDE_PALETTE         = LANG_PALETTE

# --- gap_vs_k.png (FR-5.4) ---
GAP_FIG_SIZE        = (6, 4)
GAP_COLOR           = "#1f77b4"   # blue line
GAP_MARKER          = "o"
GAP_LINEWIDTH       = 2.0
GAP_MARKERSIZE      = 7
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Visualization Config | matplotlib/seaborn constants for all 4 figures (sizes, DPI, colors, colormaps) |

---

## Usage in Modules

```python
# Any module — example in visualization.py
from config import CFG, DPI, GATE_FIG_SIZE, GATE_BAR_COLOR_IN, GATE_BAR_COLOR_OUT
from config import GATE_REF_COLOR, GATE_REF_STYLE, GATE_Y_LIM, HEATMAP_FIG_SIZE
from config import HEATMAP_CMAP, KDE_FIG_SIZE, KDE_PALETTE, GAP_FIG_SIZE
from config import GAP_COLOR, GAP_MARKER, LANG_ORDER

# Example: gate_metrics figure bar color logic
colors = [
    GATE_BAR_COLOR_IN if CFG.gate_v_range[0] <= v <= CFG.gate_v_range[1] else GATE_BAR_COLOR_OUT
    for v in cramers_v_values
]
```
