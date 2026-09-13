# Configuration: H-M1 Correlation Analysis

**Date:** 2026-08-25
**Hypothesis:** H-M1 (MECHANISM)
**Budget:** 4 subtasks allocated to A-5 (Visualizer)

---

## Codebase Analysis (Serena)

**Project Type:** Green-field with reference to existing corpus
**Status:** New implementation - designing new config schema
**Config Files Found:** h-e1 corpus collection config (reference only)
**Pattern Used:** Hardcoded dict (consistent with existing codebase pattern)

---

## Applied Patterns

**Applied:** Standard matplotlib visualization defaults with publication-ready settings

---

## A-5: Visualizer Configuration [Complexity: 14, Budget: 4]

**Applied:** Publication-ready matplotlib defaults from scipy/sklearn examples

### Configuration (Python Hardcoded Dict)

```python
CONFIG = {
    # ===== Figure Settings =====
    "figsize": (8, 6),
    "dpi": 300,
    "format": "png",
    "tight_layout": True,
    
    # ===== Color Schemes by Hypothesis Type =====
    "type_colors": {
        "attention": "#1f77b4",      # blue
        "gradient": "#ff7f0e",       # orange
        "regularization": "#2ca02c", # green
        "normalization": "#d62728",  # red
    },
    
    # ===== Scatter Plot (Correlation) =====
    "scatter": {
        "marker_size": 100,
        "alpha": 0.7,
        "edgecolor": "black",
        "linewidth": 0.5,
        "regression_line_color": "gray",
        "regression_line_style": "--",
        "regression_line_width": 2,
    },
    
    # ===== Bar Chart (Scaling Factors) =====
    "bar": {
        "width": 0.6,
        "alpha": 0.8,
        "edgecolor": "black",
        "linewidth": 1,
    },
    
    # ===== Residual Plot =====
    "residual": {
        "marker": "o",
        "marker_size": 80,
        "color": "#9467bd",  # purple
        "alpha": 0.6,
        "edgecolor": "black",
        "linewidth": 0.5,
        "zero_line_color": "red",
        "zero_line_style": "--",
        "zero_line_width": 1.5,
    },
    
    # ===== Annotation Formats =====
    "annotations": {
        "r_format": "r = {:.3f}",
        "p_format": "p = {:.4f}",
        "k_format": "k = {:.2f}",
        "fontsize": 12,
        "bbox_style": "round,pad=0.5",
        "bbox_facecolor": "white",
        "bbox_alpha": 0.8,
    },
    
    # ===== Axis Labels =====
    "labels": {
        "fontsize": 12,
        "fontweight": "normal",
    },
    
    # ===== File Save Paths =====
    "output_dir": "figures",
    "filenames": {
        "scatter": "correlation_scatter.png",
        "bar": "scaling_factors.png",
        "residual": "residuals.png",
    },
}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Scatter plot with regression | O_10 vs O_full colored by type, annotated with r/p |
| C-5-2 | Bar chart of k values | Per-type scaling factors with color scheme |
| C-5-3 | Residual plot | Prediction error vs O_10 to validate linearity |
| C-5-4 | File I/O and directory setup | Create output_dir, save 3 figures with proper paths |

---

## Statistical Validation Thresholds

**Applied:** Standard statistical significance thresholds from scipy documentation

```python
VALIDATION_THRESHOLDS = {
    "r_success": 0.7,      # Pearson r threshold for success
    "r_explore": 0.5,      # Threshold for exploring non-linear models
    "p_value": 0.05,       # Statistical significance level
    "r2_target": 0.5,      # Goodness of fit target
    "cv_consistent": 0.3,  # CV <30% = consistent scaling
    "cv_calibration": 0.5, # CV >50% = requires per-type calibration
}
```

---

## Data Paths

```python
DATA_PATHS = {
    "corpus_input": "experiments/h-e1_corpus_collection/data/retrospective_corpus/papers_metadata.json",
    "output_dir": "h-m1/figures",
    "validation_output": "h-m1/04_validation.md",
}
```

---

## Usage Example

```python
from config import CONFIG

# Visualizer initialization
visualizer = Visualizer(output_dir=CONFIG["output_dir"])

# Scatter plot with config
plt.figure(figsize=CONFIG["figsize"], dpi=CONFIG["dpi"])
plt.scatter(o10, ofull, c=colors, s=CONFIG["scatter"]["marker_size"], 
            alpha=CONFIG["scatter"]["alpha"])
plt.savefig(f"{CONFIG['output_dir']}/{CONFIG['filenames']['scatter']}", 
            format=CONFIG["format"], dpi=CONFIG["dpi"], bbox_inches="tight")
```

---

**Total Subtasks:** 4/4 used
**Lines:** 147
