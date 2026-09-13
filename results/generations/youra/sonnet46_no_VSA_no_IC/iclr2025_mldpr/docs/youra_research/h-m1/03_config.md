# Config: H-M1
# Pre-Breakpoint Residual CoV Variance Characterization

**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr

Applied: dataclass-with-path-defaults pattern (H-E1 `H1Config`)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from H-E1 actual code (`h-e1/code/config.py`)
**Config Files Found**: `h-e1/code/config.py` — `H1Config` dataclass with `field(default_factory=...)` for paths
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual H-E1 Code)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class H1Config:
    min_papers: int = 38
    min_cov_rows: int = 3
    pelt_model: str = "l2"
    pelt_min_size: int = 3
    pelt_jump: int = 1
    pen_range: tuple = field(default_factory=lambda: (1.0, 50.0))
    n_pen: int = 20
    n_permutations: int = 1000
    n_bootstrap: int = 1000
    seed: int = 42
    p_threshold: float = 0.05
    paper_count_star_min: int = 10
    paper_count_star_max: int = 120
    bootstrap_ci_width_max: int = 20
    figures_dir: str = field(default_factory=lambda: str(_H1_DIR / "figures"))
    results_json: str = field(default_factory=lambda: str(_H1_DIR / "experiment_results.json"))
```

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation)

H-M1 does NOT subclass H1Config. It reads H-E1 outputs as data files only.

---

## ExperimentConfig (H-M1 Main Config)

```python
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

_H_M1_DIR = Path(__file__).parent.parent  # h-m1/
_H_E1_DIR = _H_M1_DIR.parent / "h-e1"


@dataclass
class ExperimentConfig:
    # Input paths — H-E1 outputs
    data_csv_path: Path = field(
        default_factory=lambda: _H_E1_DIR / "data" / "pwc_cov_computed.csv"
    )
    h_e1_results_json_path: Path = field(
        default_factory=lambda: _H_E1_DIR / "experiment_results.json"
    )

    # Output paths
    figures_dir: Path = field(
        default_factory=lambda: _H_M1_DIR / "figures"
    )
    results_json_path: Path = field(
        default_factory=lambda: _H_M1_DIR / "experiment_results.json"
    )

    # Gate threshold (one-tailed F-test p-value)
    # Non-standard: 0.10 (relaxed vs H-E1's 0.05) — mechanism hypothesis uses lenient alpha
    f_test_alpha: float = 0.10

    # Minimum pre-segment observations required before proceeding
    min_pre_segment_n: int = 3


CFG = ExperimentConfig()
```

---

## A-6: Visualizer [Complexity: 10, Budget: 2 subtasks]

Applied: Standard matplotlib/seaborn defaults

### Configuration (Python Dataclass)

```python
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class PlotConfig:
    # Figure dimensions and resolution
    fig_width: float = 8.0
    fig_height: float = 6.0
    dpi: int = 150

    # Color palette
    pre_color: str = "blue"
    post_color: str = "red"
    global_color: str = "gray"

    # Font sizes
    title_fontsize: int = 13
    label_fontsize: int = 11
    tick_fontsize: int = 10
    annotation_fontsize: int = 9

    # P-value annotation format string
    # Non-standard: explicit one-tailed label to avoid ambiguity in figures
    p_annotation_fmt: str = "p(one-tailed)={p:.4f}"

    # Figure-specific: bar chart
    bar_width: float = 0.5
    bar_labels: list = field(default_factory=lambda: ["Global (N=111)", "Pre-segment", "Post-segment"])

    # Figure-specific: scatter
    scatter_marker_size: int = 20
    breakpoint_linewidth: float = 1.5
    breakpoint_linestyle: str = "--"

    # Figure-specific: KDE
    # bw_method=None uses Scott's rule (scipy/seaborn default); adequate for N~30-111
    kde_bw_method: str | None = None

    # Figure-specific: boxplot
    # whis=1.5 is matplotlib default (Tukey fences)
    boxplot_whis: float = 1.5
    boxplot_labels: list = field(default_factory=lambda: ["Pre-segment", "Post-segment", "Global"])

    # Save format
    save_format: str = "png"


PLOT_CFG = PlotConfig()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | PlotConfig dataclass | Figure size (8x6), DPI 150, color palette (pre=blue, post=red, global=gray), font sizes, p-value annotation format string |
| C-6-2 | Figure-specific settings | Bar labels, scatter marker size and breakpoint line style, KDE bw_method (Scott's rule default), boxplot whis=1.5 and labels; save format PNG at 150 DPI |
