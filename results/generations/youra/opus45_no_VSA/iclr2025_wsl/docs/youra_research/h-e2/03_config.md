# Config: h-e2 (CV_PR vs ImageNet Accuracy Correlation — EXISTENCE PoC)

**Applied**: No matching domain-specific pattern in KB — standard dict config per EXISTENCE rules.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (h-e1 provides only a data file, no config pattern to inherit)
**Config Files Found**: None - new config
**Pattern Used**: Hardcoded dict

---

## A-1: Correlation Analysis [Complexity: 1, Budget: 0 subtasks — EXISTENCE PoC]

**Applied**: Standard scipy/pandas defaults, no tuning (EXISTENCE rules).

### Configuration (Hardcoded Dict)

```python
CONFIG = {
    # Paths
    "cv_pr_path": "h-e1/h-e1/results/results.csv",
    "accuracy_url": "https://raw.githubusercontent.com/huggingface/pytorch-image-models/main/results/results-imagenet.csv",
    "results_path": "h-e2/results/correlation_results.json",
    "figure_path": "h-e2/figures/scatter_cv_pr_vs_accuracy.png",

    # Success thresholds
    "r_threshold": -0.3,
    "p_threshold": 0.05,
    "min_matched_models": 80,

    # Bootstrap CI
    "n_iterations": 10000,
    "ci_level": 0.95,

    # Reproducibility
    "seed": 42,

    # Visualization
    "figure_dpi": 150,
    "figure_size": (8, 6),
    "scatter_alpha": 0.6,
    "regression_ci": True,
}
```

No hyperparameter grid, no ablation configs, no subtask decomposition (EXISTENCE PoC — budget 0 subtasks).
