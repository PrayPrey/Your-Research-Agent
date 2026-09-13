# Configuration: H-E2
## MST Minimum Evaluation Set + Bootstrap Topology Stability

**Hypothesis:** H-E2 (EXISTENCE / PoC — INCREMENTAL on H-E1)
**Date:** 2026-08-04

Applied: Standard argparse pattern (no KB match for this domain)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code
**Config Files Found**: `h-e1/code/analysis.py` (AnalysisConfig dataclass), `h-e1/code/main.py` (argparse)
**Pattern Used**: dataclass for AnalysisConfig; argparse in `__main__`

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual H-E1 Code)

```python
# From: h-e1/code/analysis.py (ACTUAL CODE — verified)
@dataclass
class AnalysisConfig:
    alpha: float = 0.05
    bonferroni_alpha: float = 0.0033   # 0.05 / 15 pairs
    n_pairs: int = 15
    rho_threshold: float = 0.5
    n_covariates: int = 2              # log10_params, is_RLHF
    df_residual: int = 12              # n - 2 - k = 16 - 2 - 2
    silhouette_threshold: float = 0.3
```

### H-E1 Argparse (Actual, from h-e1/code/main.py)

```
--results-dir   default="TrustLLM/results"
--output-dir    default="."
```

### H-E1 Visualization Conventions (from h-e1/code/visualization.py)

- DPI: 300
- RLHF color: `"tomato"` | Base color: `"steelblue"`
- Figure sizes: `(12, 5)`, `(14, 6)`, `(8, 5)`, `(12, 5)`
- Heatmap colormap: `"RdBu_r"`, vmin=-1, vmax=1

---

## A-4: Visualization Config [Complexity: 10, Budget: 2 subtasks]

Applied: Standard matplotlib/seaborn defaults; H-E1 color conventions inherited

### C-4-1: Visualization Configuration

```python
# h-e2/code/visualization.py — top-level constants (copy-paste ready)

DPI = 300

# Node colors: inherit H-E1 cluster convention
COLOR_RLHF_SENSITIVE   = "tomato"      # cluster 1: RLHF-sensitive
COLOR_RLHF_INSENSITIVE = "steelblue"   # cluster 0: RLHF-insensitive
COLOR_LEAF_HIGHLIGHT   = "gold"        # leaf nodes in MST graph
COLOR_EDGE_DEFAULT     = "gray"
COLOR_MST_EDGE_OVERLAY = "black"       # MST edges on heatmaps

# Threshold values
MST_MIN_SET_THRESHOLD      = 4
BOOTSTRAP_STABILITY_THRESHOLD = 0.90

# Figure sizes (width, height) in inches
FIG_SIZES = {
    "gate_bar":           (8, 5),    # 2-bar gate metric chart
    "mst_graph":          (8, 7),    # NetworkX MST node-edge drawing
    "bootstrap_heatmap":  (8, 7),    # 6x6 edge-frequency heatmap
    "distance_heatmap":   (8, 7),    # 6x6 d_ij = 1-|rho_partial|
    "mst_comparison":     (14, 6),   # side-by-side raw vs partial MST
}

# Heatmap colormap
HEATMAP_CMAP = "YlOrRd"    # 0..1 range for distance/frequency
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Visualization Config | Constants for figure sizes, colors, thresholds (above) |
| C-4-2 | ExperimentConfig dataclass | Full experiment hyperparameter schema (below) |

---

## C-4-2: Experiment Config Dataclass

### ExperimentConfig

```python
# h-e2/code/main.py — dataclass + argparse (copy-paste ready)
from dataclasses import dataclass, field
from typing import List


@dataclass
class ExperimentConfig:
    # I/O
    h_e1_results_path: str = "../h-e1/experiment_results_phase3.json"
    out_dir: str = ".."

    # Bootstrap hyperparameters
    n_bootstrap: int = 1000        # standard (Musciotto et al. 2018)
    subsample_size: int = 14       # 14/16 model subsamples
    seed: int = 42

    # Gate thresholds
    gate_min_set_threshold: int = 4
    gate_stability_threshold: float = 0.90

    # Visualization
    figure_dpi: int = 300

    # Dimension names (fixed; must match H-E1 DIMENSIONS order)
    dim_names: List[str] = field(default_factory=lambda: [
        "truthfulness",
        "safety",
        "fairness",
        "robustness",
        "privacy",
        "machine_ethics",
    ])
```

### Argparse (for `__main__` in main.py)

```python
if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="H-E2 MST Stability Analysis")
    parser.add_argument("--h-e1-results",
                        default="../h-e1/experiment_results_phase3.json",
                        help="Path to h-e1 experiment_results_phase3.json")
    parser.add_argument("--out-dir", default="..",
                        help="Output directory for results and figures")
    parser.add_argument("--n-boot", type=int, default=1000,
                        help="Number of bootstrap iterations")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    cfg = ExperimentConfig(
        h_e1_results_path=args.h_e1_results,
        out_dir=args.out_dir,
        n_bootstrap=args.n_boot,
        seed=args.seed,
    )
    results = run_experiment(cfg)
    sys.exit(0 if results["gate_passed"] else 1)
```

---

## Bootstrap Hyperparameters Schema (Summary)

| Parameter | Value | Source |
|-----------|-------|--------|
| n_bootstrap | 1000 | Musciotto et al. 2018 |
| subsample_size | 14 | 14/16 models (fixed in PRD) |
| seed | 42 | Reproducibility convention |
| gate_min_set_threshold | 4 | H-E2 gate definition |
| gate_stability_threshold | 0.90 | H-E2 gate definition |
| figure_dpi | 300 | Publication quality |
