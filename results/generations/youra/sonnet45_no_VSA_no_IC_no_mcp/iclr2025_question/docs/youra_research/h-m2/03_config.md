# Configuration: H-M2 Bayesian Gate 2 Posterior Prediction

**Date:** 2026-08-25
**Hypothesis:** H-M2 (MECHANISM)
**Budget:** 4 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type:** Green-field
**Status:** New implementation - H-M1 has no code/ directory (validation results only)
**Config Files Found:** None - designing new config schema
**Pattern Used:** Hardcoded dict (consistent with H-M1 pattern)

---

## Applied Patterns

**Applied:** Standard scipy.stats Bayesian inference defaults

---

## Statistical Validation Thresholds

**Applied:** Standard statistical significance thresholds from scipy documentation

```python
VALIDATION_THRESHOLDS = {
    "reduction_target": 40.0,      # Target error reduction % for PASS
    "reduction_partial": 20.0,     # Threshold for PARTIAL result
    "p_value": 0.05,               # Statistical significance level
    "min_sample_size": 10,         # Minimum hypotheses with Gate 2 data
}
```

---

## Bayesian Parameters

**Applied:** scipy.stats Gaussian inference pattern

```python
BAYESIAN_CONFIG = {
    "k": 1.000,                    # Scaling factor from H-M1 validation
    "prior_variance": 0.01,        # Gate 1 prior uncertainty
    "likelihood_variance": 0.005,  # Gate 2 likelihood uncertainty (lower = more samples)
}
```

Rationale for non-standard values:
- `prior_variance=0.01`: Moderate uncertainty at 10 samples
- `likelihood_variance=0.005`: Lower uncertainty at 100 samples (10x more data)

---

## Visualization Configuration

**Applied:** Publication-ready matplotlib defaults (reused from H-M1 pattern)

```python
VIZ_CONFIG = {
    "figsize": (8, 6),
    "dpi": 300,
    "format": "png",
    "tight_layout": True,
    
    "colors": {
        "gate1": "#1f77b4",        # blue
        "gate2": "#ff7f0e",        # orange
        "reduction": "#2ca02c",    # green
    },
    
    "histogram": {
        "bins": 20,
        "alpha": 0.7,
        "edgecolor": "black",
    },
    
    "scatter": {
        "marker_size": 100,
        "alpha": 0.7,
        "edgecolor": "black",
        "linewidth": 0.5,
    },
    
    "box": {
        "widths": 0.6,
        "showmeans": True,
        "meanline": True,
    },
    
    "annotations": {
        "fontsize": 12,
        "bbox_style": "round,pad=0.5",
        "bbox_facecolor": "white",
        "bbox_alpha": 0.8,
    },
    
    "output_dir": "figures",
    "filenames": {
        "histogram": "error_reduction_histogram.png",
        "scatter": "gate_comparison_scatter.png",
        "paired": "paired_errors.png",
        "boxplot": "statistical_comparison_boxplot.png",
        "metrics": "metrics_comparison.png",
    },
}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Error reduction histogram | Distribution of per-hypothesis reductions |
| C-7-2 | Gate comparison scatter | O_pred vs O_full for both gates |
| C-7-3 | Paired error plot | Connecting lines showing reduction |
| C-7-4 | Metrics comparison (mandatory) | Target vs actual bar chart |

---

## Data Paths

```python
DATA_PATHS = {
    "h_m1_validation": "../h-m1/04_validation.md",
    "output_dir": "h-m2/figures",
    "validation_output": "h-m2/04_validation.md",
}
```

---

## Usage Example

```python
# Bayesian predictor initialization
predictor = Gate2BayesianPredictor(
    k=BAYESIAN_CONFIG["k"],
    prior_var=BAYESIAN_CONFIG["prior_variance"],
    likelihood_var=BAYESIAN_CONFIG["likelihood_variance"]
)

# Success evaluation
evaluator = SuccessEvaluator(
    reduction_threshold=VALIDATION_THRESHOLDS["reduction_target"],
    p_threshold=VALIDATION_THRESHOLDS["p_value"]
)

# Visualizer setup
visualizer = Gate2Visualizer(output_dir=VIZ_CONFIG["output_dir"])
plt.figure(figsize=VIZ_CONFIG["figsize"], dpi=VIZ_CONFIG["dpi"])
```

---

**Total Subtasks:** 4/4 used
**Lines:** 147
