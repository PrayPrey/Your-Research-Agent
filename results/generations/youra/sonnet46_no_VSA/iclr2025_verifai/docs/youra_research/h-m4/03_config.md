# Config: H-M4 Cross-Model Contract-Satisfaction Statistical Analysis

Applied: flat-constants + dataclass pattern (consistent with H-M3)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config field names verified from H-M3 actual code
**Config Files Found**: `h-m3/code/run_experiment.py` (path constants), `h-m3/code/visualization.py` (figure defaults)
**Pattern Used**: Hardcoded module-level constants + dataclass for grouped settings

---

## Inherited Configuration (Base Hypothesis)

H-M3 uses no config.py — constants are inlined in `run_experiment.py`:

```python
# From: h-m3/code/run_experiment.py (ACTUAL CODE)
CODE_DIR = Path(__file__).parent
RESULTS_DIR = CODE_DIR.parent / "results"
FIGURES_DIR = CODE_DIR.parent / "figures"
```

H-M3 visualization defaults (from `h-m3/code/visualization.py`):
- `figsize=(6, 4)` for bar charts, `(6, 6)` for scatter, `(7, 4)` for histograms
- `bins=60` for gap distribution histogram
- `color="steelblue"`, threshold lines in `"red"` (dashed)

**Verified from**: `docs/youra_research/h-m3/code/` (actual implementation)

---

## Global Constants

```python
# config.py — H-M4
from pathlib import Path
from dataclasses import dataclass

# --- Paths ---
CODE_DIR = Path(__file__).parent
H_M3_RESULTS_DIR = CODE_DIR.parent.parent / "h-m3" / "results"
EXP_B_CSV = H_M3_RESULTS_DIR / "experiment_b_per_model_task_rates.csv"
CONTRACT_EVAL_JSON = CODE_DIR.parent.parent.parent / "data" / "ContractEval" / "data" / "contract_eval_tasks.json"
RESULTS_DIR = CODE_DIR.parent / "results"
FIGURES_DIR = CODE_DIR.parent / "figures"

# --- Gate Thresholds ---
TAU_THRESHOLD = 0.6          # Kendall τ must be ≤ this (orthogonality gate)
DELTA_R2_THRESHOLD = 0.10    # Partial ΔR² for model identity in MixedLM
GAP_THRESHOLD = 0.10         # Cross-model family gap (best vs worst)
ALPHA = 0.05                 # Permutation test significance level

# --- Bootstrap ---
N_BOOTSTRAP = 1000
SEED = 42

# --- Model Metadata ---
# Sizes in billions of parameters (estimated where marked)
MODEL_SIZES = {
    "gpt-4o-mini":            8.0,   # estimated (OpenAI undisclosed)
    "deepseek-coder-v2-lite": 16.0,  # published
    "claude-3-haiku":         20.0,  # estimated
    "codellama-34b":          34.0,  # published
    "codellama-13b":          13.0,  # published
}

MODEL_FAMILIES = {
    "gpt-4o-mini":            "openai",
    "deepseek-coder-v2-lite": "deepseek",
    "claude-3-haiku":         "anthropic",
    "codellama-34b":          "meta",
    "codellama-13b":          "meta",
}

# EvalPlus pass@1* scores — from published leaderboard (evalplus.github.io)
# claude-3-haiku, codellama values are estimated; marked with _EST suffix in comments
PASS_AT_1_FALLBACK = {
    "gpt-4o-mini":            {"humaneval_plus": 0.835, "mbpp_plus": 0.722},
    "deepseek-coder-v2-lite": {"humaneval_plus": 0.823, "mbpp_plus": 0.751},
    "claude-3-haiku":         {"humaneval_plus": 0.730, "mbpp_plus": 0.660},  # estimated
    "codellama-34b":          {"humaneval_plus": 0.650, "mbpp_plus": 0.600},  # estimated
    "codellama-13b":          {"humaneval_plus": 0.580, "mbpp_plus": 0.530},  # estimated
}
```

---

## A-8: Visualization Config [Complexity: 2, Budget: 2 subtasks]

Applied: Standard matplotlib defaults pattern

### C-8-1: Figure Settings [1/2]

```python
@dataclass
class FigureConfig:
    dpi: int = 300
    output_dir: Path = FIGURES_DIR

    # Per-plot sizes (width, height) in inches
    scatter_figsize: tuple = (7, 7)
    bar_figsize: tuple = (8, 5)
    histogram_figsize: tuple = (7, 4)
    heatmap_figsize: tuple = (8, 6)

    # Color palette — one color per model (5 models)
    model_colors: dict = None  # set in __post_init__
    threshold_color: str = "red"
    threshold_linestyle: str = "--"
    threshold_linewidth: float = 1.5

    def __post_init__(self):
        if self.model_colors is None:
            self.model_colors = {
                "gpt-4o-mini":            "#4C72B0",
                "deepseek-coder-v2-lite": "#DD8452",
                "claude-3-haiku":         "#55A868",
                "codellama-34b":          "#C44E52",
                "codellama-13b":          "#8172B2",
            }
```

### C-8-2: Plot-Specific Settings [2/2]

```python
@dataclass
class PlotConfig:
    # Scatter: ranking divergence plot
    scatter_label_offset: float = 0.01   # fraction of axis range
    scatter_alpha: float = 0.8
    scatter_point_size: int = 80

    # Bar chart: gate metrics summary
    bar_order: list = None  # None = sorted by contract_satisfaction_rate descending

    # Permutation test histogram
    perm_hist_bins: int = 50
    perm_observed_color: str = "red"
    perm_null_color: str = "steelblue"
    perm_null_alpha: float = 0.7
```

### Subtasks [2/2]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | FigureConfig dataclass | DPI, output dir, per-model colors, threshold line style |
| C-8-2 | PlotConfig dataclass | Scatter offsets, bar ordering, permutation histogram bins |

---

## A-2: Data Loading Config [Complexity: 2, Budget: 2 subtasks]

Applied: Standard path constants pattern

### C-2-1: Path Config [1/2]

```python
@dataclass
class PathConfig:
    exp_b_csv: Path = EXP_B_CSV
    contract_eval_json: Path = CONTRACT_EVAL_JSON
    results_dir: Path = RESULTS_DIR
    figures_dir: Path = FIGURES_DIR
    # EvalPlus source: "fallback" uses PASS_AT_1_FALLBACK dict; "package" tries evalplus pkg first
    evalplus_source: str = "fallback"
```

### C-2-2: Validation Thresholds [2/2]

```python
@dataclass
class ValidationConfig:
    min_models: int = 5
    min_tasks_per_model: int = 300   # >80% of 364 ContractEval tasks
    max_nan_rate: float = 0.05       # max fraction of NaN contract_satisfaction_rate
```

### Subtasks [2/2]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | PathConfig dataclass | H-M3 CSV, ContractEval JSON, output dirs, EvalPlus source toggle |
| C-2-2 | ValidationConfig dataclass | min_models, min_tasks_per_model, max_nan_rate |

---

## A-6: Subgroup Analysis Config [Complexity: 1, Budget: 1 subtask]

Applied: Standard dataclass pattern

### C-6-1: Subgroup Settings [1/1]

```python
@dataclass
class SubgroupConfig:
    task_types: list = None   # set in __post_init__
    divergence_threshold: float = 0.2   # min rank divergence to flag subgroup split
    min_tasks_per_subgroup: int = 50    # guard against low-N subgroups

    def __post_init__(self):
        if self.task_types is None:
            self.task_types = ["humaneval_plus", "mbpp_plus"]
```

### Subtasks [1/1]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | SubgroupConfig dataclass | task_types list, divergence_threshold, min subgroup size guard |

---

## Instantiation (copy-paste ready)

```python
# In config.py or run_experiment.py:
figure_cfg = FigureConfig()
plot_cfg = PlotConfig()
path_cfg = PathConfig()
val_cfg = ValidationConfig()
subgroup_cfg = SubgroupConfig()
```
