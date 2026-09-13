# Configuration: H-M3 Adaptive PBT Contribution Experiment

Applied: standard-dataclass-defaults pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3 extends H-M1)
**Status**: config fields verified from actual H-M1 code
**Config Files Found**: `h-m1/code/run_experiment.py` (flat constants, no dataclass), `h-m1/code/visualization.py` (inline style constants)
**Pattern Used**: hardcoded constants in H-M1; H-M3 uses dataclass for run_experiment.py (more params), inline dict for visualization

---

## Inherited Configuration (Base Hypothesis)

### Verified Constants from H-M1 Actual Code

```python
# From: h-m1/code/run_experiment.py (ACTUAL CODE — flat module-level constants)
N_WORKERS = 8
TIMEOUT_PER_INPUT = 5        # seconds per input (not per triple)
SEED = 42

# From: h-m1/code/run_experiment.py — aggregate_stats() call
N_BOOTSTRAP = 10_000
GAP_THRESHOLD = 0.10
CU_THRESHOLD = 0.05
P_THRESHOLD = 0.01

# From: h-m1/code/visualization.py — _save helper
DPI = 150                    # fig.savefig(..., dpi=150, bbox_inches="tight")

# From: h-m1/code/visualization.py — figure sizes used per plot
FIGSIZE_DOUBLE = (10, 5)     # plot_gate_metrics: (10, 5)
FIGSIZE_SCATTER = (7, 6)     # plot_scatter_failure_rates: (7, 6)
FIGSIZE_VIOLIN = (6, 5)      # plot_gap_distribution: (6, 5)

# From: h-m1/code/visualization.py — colors
COLOR_PRIMARY = "steelblue"
COLOR_SECONDARY = "darkorange"
COLOR_THRESHOLD = "red"
ALPHA_BAR = 0.8
ALPHA_SCATTER = 0.4
```

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation)

---

## A-8: Visualization (6 figures) [Complexity: 10, Budget: 2 subtasks]

Applied: standard-dataclass-defaults pattern

### Configuration (Python dict — inline in visualization.py)

```python
# h-m3/code/visualization.py — module-level constants (consistent with H-M1 style)

STYLE = {
    # Figure sizes — per plot
    "figsize_gate": (10, 5),        # gate bar chart (2 panels)
    "figsize_scatter": (7, 6),      # Exp_A vs Exp_B scatter
    "figsize_hist_gap": (6, 5),     # adaptive gap histogram
    "figsize_hist_filter": (6, 5),  # filter rate histogram
    "figsize_model_bars": (10, 5),  # model-stratified bars (5 models)
    "figsize_task_bars": (6, 5),    # task-type bars (2 types)
    "dpi": 150,                     # matches H-M1 _save()
    # Colors
    "color_exp_b": "steelblue",     # adaptive PBT bars/points
    "color_exp_a": "darkorange",    # static oracle reference
    "color_threshold": "red",
    "color_humaneval": "steelblue",
    "color_mbpp": "darkorange",
    "color_positive_gap": "#98df8a",
    "color_negative_gap": "#ff9896",
    "alpha_bar": 0.8,
    "alpha_scatter": 0.4,
    "scatter_s": 20,
    # Labels
    "xlabel_exp_a": "Static failure rate (Exp A)",
    "ylabel_exp_b": "Adaptive failure rate (Exp B)",
    "ylabel_gap": "Adaptive gap (Exp_B − Exp_A)",
    "ylabel_filter": "Filter rate (1 − n_valid / 5000)",
    "ylabel_contribution": "Mean adaptive contribution",
    # Thresholds shown as reference lines
    "threshold_gap": 0.03,          # secondary success criterion
    "threshold_filter_high": 0.95,  # high-filter flag line
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Figure specs | Figure sizes, DPI, axis labels, threshold lines for all 6 H-M3 plots |
| C-8-2 | Plot style dict | Module-level STYLE dict consistent with H-M1 visualization style |

---

## A-9: Orchestration [Complexity: 9, Budget: 1 subtask]

Applied: standard-dataclass-defaults pattern

### Configuration (Python Dataclass)

```python
# h-m3/code/run_experiment.py
from dataclasses import dataclass, field
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent  # TEST_verifai root

@dataclass
class ExperimentConfig:
    # Parallelism
    n_workers: int = 16

    # Experiment B runner
    budget: int = 5000               # max_examples per triple (icontract-hypothesis)
    timeout_secs: int = 60           # wall-clock timeout per triple (SIGALRM)
    rng_seed: int = 42

    # Compatibility pre-check
    precheck_n_tasks: int = 20
    precheck_min_passing: int = 15   # ≥15/20 tasks must yield ≥100 valid examples

    # Yield thresholds
    yield_min_valid: int = 100       # triple is low-yield if n_valid < this
    yield_max_filter_rate: float = 0.95  # triple is low-yield if filter_rate > this

    # Statistical analysis
    bootstrap_n: int = 10_000
    significance_threshold: float = 0.05   # Wilcoxon p_holm < this to pass gate

    # Paths
    h1_results_path: str = str(_ROOT / "h-m1" / "results" / "oracle_isolation_results.json")
    output_dir: str = str(Path(__file__).parent.parent / "results")
    figures_dir: str = str(Path(__file__).parent.parent / "figures")
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | ExperimentConfig dataclass | All tunable parameters for run_experiment.py orchestration |
