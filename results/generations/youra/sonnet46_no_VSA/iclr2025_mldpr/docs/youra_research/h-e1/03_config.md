# Configuration: H-E1 — Data Pipeline Validation & FAIL FAST Gate Verification

**Applied**: Standard Python dataclass for typed constants (no ML hyperparameter tuning needed)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — new config design
**Config Files Found**: None — new config
**Pattern Used**: Python module-level constants (flat dict-style in config.py)

---

## Core Pipeline Configuration

```python
# code/config.py
from dataclasses import dataclass

@dataclass
class H1Config:
    # --- Dataset ---
    hf_dataset_id: str = "pwc-archive/evaluation-tables"
    panel_path: str = "h_e2_panel.csv"
    output_csv: str = "h_e2_panel_with_diversity.csv"
    figures_dir: str = "figures"
    seed: int = 1

    # --- Fuzzy join ---
    # token_sort_ratio=85: empirically standard threshold for task slug matching;
    # below 80 produces false positives on short slug pairs, above 90 misses
    # legitimate abbreviation variants (e.g., "image-classification" vs "img-clf").
    fuzzy_threshold: int = 85
    # n_benchmarks: ground truth count from h-e2 panel (87 plurality-displacement tasks)
    n_benchmarks: int = 87

    # --- Gate thresholds ---
    # G0: >=80% coverage ensures statistical power; <80% means too many benchmarks
    # lack diversity data, invalidating downstream Cox regression.
    g0_coverage_min: float = 0.80

    # G1/G2: partial_r²>0.01 is the conventional "small effect" floor (Cohen 1988).
    # Values below indicate the predictor is essentially explained by time alone,
    # meaning it carries no independent information for survival modeling.
    g1_partial_r2_min: float = 0.01
    g2_partial_r2_min: float = 0.01

    # G3: std>0.10 ensures cross-benchmark diversity ratio is not degenerate.
    # A constant predictor has zero variance and is uninformative for regression.
    # 0.10 is a practical lower bound for a ratio bounded in [0,1].
    g3_std_min: float = 0.10

    # G4: VIF thresholds follow standard econometric practice:
    # VIF>5 → warn (moderate collinearity, flag for review)
    # VIF>10 → hard stop (severe collinearity, Cox coefficients unreliable)
    g4_vif_warn: float = 5.0
    g4_vif_max: float = 10.0

    # Collinearity failsafe: |r|>0.95 between the two diversity predictors means
    # they are near-redundant; only one enters the Cox model to avoid suppression effects.
    collinearity_r_max: float = 0.95


# Singleton instance — import this in all modules
CFG = H1Config()
```

---

## YAML Schema (experiment-level)

```yaml
# h-e1/config.yaml — mirrors H1Config dataclass for CLI / reproducibility logging

dataset:
  hf_dataset_id: "pwc-archive/evaluation-tables"   # HF Hub path; CC-BY-SA-4.0
  panel_path: "h_e2_panel.csv"                      # Internal h-e2 panel (87 tasks)
  output_csv: "h_e2_panel_with_diversity.csv"        # Enriched panel artifact
  figures_dir: "figures"                             # Auto-created output dir
  seed: 1                                            # Reproducibility seed

fuzzy_join:
  fuzzy_threshold: 85    # token_sort_ratio cutoff; 85 balances recall vs. precision
  n_benchmarks: 87       # Ground-truth benchmark count from h-e2 panel

gates:
  g0_coverage_min: 0.80  # >=80% of 87 benchmarks must match (statistical power floor)
  g1_partial_r2_min: 0.01  # log_count time-independence: Cohen "small effect" floor
  g2_partial_r2_min: 0.01  # diversity_ratio time-independence: same basis
  g3_std_min: 0.10         # diversity_ratio cross-benchmark std; degenerate if <0.10
  g4_vif_warn: 5.0         # VIF moderate-collinearity warning (econometric standard)
  g4_vif_max: 10.0         # VIF hard-stop threshold (coefficients unreliable above)
  collinearity_r_max: 0.95 # Pearson |r| failsafe; >0.95 → drop one predictor
```

---

## C1: E7 — Visualization Configuration [Complexity: 11, Budget: 1]

**Applied**: Standard matplotlib/seaborn figure constants

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | FigureConfig | Figure size, DPI, color palette, style constants for all 5 plots |

### Configuration

```python
# Append to code/config.py (or import from config in output.py)
from dataclasses import dataclass, field
from typing import Dict, Tuple

@dataclass
class FigureConfig:
    dpi: int = 150
    # Standard academic figure width; single-column = 6in, two-panel = 10in
    fig_size_single: Tuple[float, float] = (8, 5)
    fig_size_wide: Tuple[float, float] = (12, 5)
    fig_size_square: Tuple[float, float] = (7, 6)

    # Semantic colors: green=pass, red=fail (colorblind-safe pair from ColorBrewer)
    color_pass: str = "#2ecc71"
    color_fail: str = "#e74c3c"
    color_neutral: str = "#3498db"    # bars with no pass/fail meaning
    color_warn: str = "#f39c12"       # VIF warn-level indicator

    # Seaborn palette for correlation/heatmap (diverging, zero-centered)
    corr_palette: str = "coolwarm"
    corr_vmin: float = -1.0
    corr_vmax: float = 1.0

    font_size_title: int = 13
    font_size_label: int = 11
    font_size_tick: int = 9

    # Per-figure filenames (saved under figures_dir)
    fname_gate_metrics: str = "gate_metrics.png"
    fname_coverage_heatmap: str = "coverage_heatmap.png"
    fname_predictor_distributions: str = "predictor_distributions.png"
    fname_correlation_matrix: str = "correlation_matrix.png"
    fname_partial_r2: str = "partial_r2.png"


FIG_CFG = FigureConfig()
```

**Figure-specific notes:**

- `plot_gate_metrics`: `fig_size_wide`, bars colored by `color_pass`/`color_fail` per gate result, threshold line in black dashed.
- `plot_coverage_heatmap`: `fig_size_single`, matched tasks in `color_pass`, unmatched in `color_fail`.
- `plot_predictor_distributions`: `fig_size_wide` (two side-by-side histograms), `color_neutral` fill.
- `plot_correlation_matrix`: `fig_size_square`, `corr_palette` ("coolwarm"), annotated with r values.
- `plot_partial_r2`: `fig_size_single`, bars in `color_neutral`, threshold line at 0.01 in red dashed.
