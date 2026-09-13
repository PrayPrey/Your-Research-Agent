# H-M1 Configuration

Applied: dataclass pattern (matched H-E1 ProfileConfig style)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: config classes verified from actual code (`h-e1/code/profile_mbpp.py`)
**Config Files Found**: `profile_mbpp.py` - `ProfileConfig` dataclass
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

From `/h-e1/code/profile_mbpp.py` (actual code, verified):

```python
@dataclass
class ProfileConfig:
    model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    seed: int = 42
    variance_threshold: float = 0.1
    min_count: int = 50
    results_dir: str = "docs/youra_research/h-e1/results"
    figures_dir: str = "docs/youra_research/h-e1/figures"
    # ... (k, temperature, top_p, max_new_tokens, etc.)
```

H-M1 reuses `seed=42`, `results_dir` pattern, and `matplotlib.use("Agg")` convention.

---

## C-1: Experiment Parameters [Complexity: 1, Budget: 1]

Applied: Standard dataclass defaults

```python
from dataclasses import dataclass

@dataclass
class H_M1Config:
    # Input
    profiling_json: str = "docs/youra_research/h-e1/results/mbpp_variance_profile.json"
    fallback_script: str = "docs/youra_research/h-e1/code/profile_mbpp.py"

    # Selection
    k: int = 50                          # top-k by variance
    seed: int = 42

    # Output
    results_dir: str = "docs/youra_research/h-m1/results"
    figures_dir: str = "docs/youra_research/h-m1/figures"

    # Gate
    min_mean_var_difference: float = 0.0  # any positive difference passes
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ExperimentParams | H_M1Config dataclass with input/selection/output/gate fields |

---

## C-2: Figure Config [Complexity: 1, Budget: 1]

Applied: matplotlib Agg defaults, dpi=150 from H-E1 convention

```python
# All figures: matplotlib.use("Agg"), dpi=150, tight_layout=True

FIG1_MEAN_COMPARISON = {
    "figsize": (8, 5),
    "colors": {"variance_50": "steelblue", "random_50": "darkorange"},
    "strip_jitter": 0.15,
    "strip_alpha": 0.5,
    "strip_size": 4,
}

FIG2_HISTOGRAMS = {
    "figsize": (8, 5),
    "bins": 10,
    "range": [0.0, 0.25],
    "alpha": 0.6,
    "colors": {"variance_50": "steelblue", "random_50": "darkorange"},
}

FIG3_RANK_PLOT = {
    "figsize": (9, 5),
    "boundary_color": "red",
    "boundary_linestyle": "--",
    "shaded_alpha": 0.12,
    "shaded_color": "steelblue",
}

FIG4_CDF = {
    "figsize": (8, 5),
    "linestyles": {"variance_50": "-", "random_50": "--"},
    "colors": {"variance_50": "steelblue", "random_50": "darkorange"},
    "legend_loc": "lower right",
}

FIGURE_DEFAULTS = {
    "dpi": 150,
    "tight_layout": True,
    "backend": "Agg",
}
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | FigureConfig | Per-figure dicts for 4 plots + shared FIGURE_DEFAULTS |
