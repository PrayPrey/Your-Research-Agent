# Logic: h-m1
# Reward Density Mechanism Verification — API Design

Applied: Log-analysis pipeline pattern
Applied: Wilcoxon paired non-parametric test (scipy.stats)
Applied: Subprocess training invocation with CUDA_VISIBLE_DEVICES

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-e1 code (direct file reads)
**Analyzed Path**: `docs/youra_research/20260502_dl4c/h-e1/code/`
**Relevant Symbols**:
- `compute_reward_density(rewards_group: list[float]) -> float` — uses `std > REWARD_EPSILON (1e-8)`
- `RewardDensityCallback.__init__(condition: str, log_dir: str)` — writes `reward_density_{condition}.csv`
- `RewardDensityCallback.on_step_end` — logs every step → 5000 rows for full training
- `CONFIG["log_dir"] = "h-e1/logs"`, `CONFIG["save_steps"] = 500`, `CONFIG["max_steps"] = 5000`
- `CONDITIONS = ["curriculum", "uniform", "easy_only", "hard_only"]`

---

## External Dependencies API

### API Signatures (From Actual h-e1 Code)

```python
# From: h-e1/code/training/reward.py (ACTUAL CODE)
REWARD_EPSILON: float  # = 1e-8 (from CONFIG["reward_epsilon"])

def compute_reward_density(rewards_group: list[float]) -> float:
    """Returns 1.0 if std(rewards_group) > REWARD_EPSILON, else 0.0."""
    # NOT max(group) > 0 — uses std check!
    ...

def execution_reward_fn(
    completions: list[str],
    prompts: list[Any],
    **kwargs,
) -> list[float]:
    """TRL reward_funcs callable."""
    ...

# From: h-e1/code/training/callbacks.py (ACTUAL CODE)
class RewardDensityCallback(TrainerCallback):
    def __init__(self, condition: str, log_dir: str = LOG_DIR) -> None: ...
    # Writes: {log_dir}/reward_density_{condition}.csv
    # CSV columns: ["step", "reward_density"]
    # Logs ONE row per training step → 5000 rows total

# From: h-e1/code/config.py (ACTUAL CODE)
CONFIG = {
    "log_dir": "h-e1/logs",
    "save_steps": 500,
    "max_steps": 5000,
    "curriculum_step": 2500,
    "reward_epsilon": 1e-8,
}
CONDITIONS = ["curriculum", "uniform", "easy_only", "hard_only"]
```

**Verified from**: `h-e1/code/` actual implementation.

---

## A-8: Full Training Execution [Complexity: 14, Budget: 4 subtasks]

Applied: Subprocess sequential execution with per-condition CUDA isolation

### API Signatures

```python
# h-m1/code/run_training.py

CONDITIONS: list[str] = ["curriculum", "uniform", "easy_only", "hard_only"]
H_E1_TRAIN_SCRIPT: str = "h-e1/code/training/train.py"
LOG_DIR: str = "h-e1/logs"
MIN_ROWS: int = 5000

def check_logs_sufficient(
    log_dir: str = LOG_DIR,
    min_rows: int = MIN_ROWS,
) -> tuple[bool, dict[str, int]]:
    """Check if all 4 condition CSVs exist with >= min_rows rows.
    Returns (all_sufficient, {condition: row_count})."""
    ...

def run_full_training(
    condition: str,
    cuda_device: str = "0",
    train_script: str = H_E1_TRAIN_SCRIPT,
) -> int:
    """Run training for one condition via subprocess.
    Returns subprocess returncode (0 = success)."""
    ...

def run_all_conditions(
    cuda_device: str = "0",
    force: bool = False,
) -> dict[str, int]:
    """Run all 4 conditions sequentially. Skips if logs sufficient (unless force=True).
    Returns {condition: returncode}."""
    ...

def validate_training_outputs(
    log_dir: str = LOG_DIR,
    expected_rows: int = MIN_ROWS,
) -> tuple[bool, dict[str, int]]:
    """Post-training check: verify all CSVs have exactly expected_rows rows.
    Returns (all_valid, {condition: actual_row_count})."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Log sufficiency check | `check_logs_sufficient`: count rows in each CSV; return (bool, counts dict) |
| L-8-2 | Subprocess training invocation | `run_full_training`: build env with `CUDA_VISIBLE_DEVICES`, call `python h-e1/code/training/train.py --condition {condition}` via `subprocess.run` |
| L-8-3 | Condition sequencing and error handling | `run_all_conditions`: iterate CONDITIONS, call `run_full_training`, abort on non-zero returncode, print per-condition status |
| L-8-4 | Post-training log validation | `validate_training_outputs`: re-read CSVs after training, assert row counts >= 5000, raise RuntimeError with details on failure |

### Pseudo-code (L-8-2 subprocess call)

```
env = os.environ.copy()
env["CUDA_VISIBLE_DEVICES"] = cuda_device
cmd = [sys.executable, train_script, "--condition", condition]
result = subprocess.run(cmd, env=env, check=False)
return result.returncode
```

### Pseudo-code (L-8-1 sufficiency check)

```
for condition in CONDITIONS:
    csv_path = f"{log_dir}/reward_density_{condition}.csv"
    if not os.path.exists(csv_path):
        counts[condition] = 0; continue
    with open(csv_path) as f:
        counts[condition] = sum(1 for _ in f) - 1  # subtract header
all_sufficient = all(v >= min_rows for v in counts.values())
return all_sufficient, counts
```

---

## A-9: Analysis and Gate Evaluation [Complexity: 12, Budget: 2 subtasks]

Applied: Gate evaluation with dual condition (p-value + direction)

### API Signatures

```python
# h-m1/code/analysis/analyze_reward_density.py

RESULTS_DIR: str = "h-m1/results"

RESULTS_SCHEMA = {
    "gate_passed": bool,           # p < 0.05 AND curriculum_mean > uniform_mean
    "wilcoxon": {
        "statistic": float,
        "p_value": float,
        "passed": bool,
        "curriculum_mean": float,
        "uniform_mean": float,
        "delta": float,            # curriculum_mean - uniform_mean
    },
    "assumption_a1": {
        "passed": bool,
        "easy_only_mean": float,
        "curriculum_mean": float,
        "delta": float,
    },
    "phase_stats": {
        # {condition: {early: {mean, std}, late: {mean, std}}}
    },
    "figure_paths": list[str],     # 4 paths
    "results_path": str,
}

def run_analysis(
    log_dir: str = "h-e1/logs",
    figures_dir: str = "h-m1/figures",
) -> dict:
    """Orchestrate load → validate → extract → test → visualize → report.
    Returns full results dict with gate_passed bool."""
    ...

def save_results(
    results: dict,
    results_dir: str = RESULTS_DIR,
) -> str:
    """Write results to {results_dir}/wilcoxon_results.json. Returns path."""
    ...

def print_summary(results: dict) -> None:
    """Print gate PASSED/FAILED, p_value, curriculum_mean, uniform_mean, delta."""
    ...
```

### Gate Logic

```
gate_passed = (wilcoxon["p_value"] < 0.05) AND (wilcoxon["curriculum_mean"] > wilcoxon["uniform_mean"])
exit_code = 0 if gate_passed else 1
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | Gate evaluation logic | Compute `gate_passed = p < 0.05 AND curriculum_mean > uniform_mean`; set exit code 0/1 |
| L-9-2 | Results JSON schema and serialization | Build results dict per RESULTS_SCHEMA; `json.dump` with indent=2 to `wilcoxon_results.json` |

---

## A-4: Visualizer [Complexity: 11, Budget: 2 subtasks]

Applied: Standard matplotlib bar/box plots with error bars and annotation

### API Signatures

```python
# h-m1/code/analysis/visualize.py
import matplotlib.pyplot as plt
import numpy as np

FIGURES_DIR: str = "h-m1/figures"

def plot_early_phase_bar(
    phase_stats: dict,  # {condition: {early: {mean: float, std: float}}}
    figures_dir: str = FIGURES_DIR,
) -> str:
    """Bar chart of mean reward density (steps 0-2500) per condition with std error bars.
    Returns saved figure path."""
    # x-axis: CONDITIONS (4 bars)
    # y-axis: mean reward_density [0.0, 1.0]
    # error bars: std
    # output: {figures_dir}/reward_density_early_phase_bar.png
    ...

def plot_timeseries(
    logs: dict,  # {condition: pd.DataFrame(columns=[step, reward_density])}
    figures_dir: str = FIGURES_DIR,
) -> str:
    """Line plot of reward density at each 500-step checkpoint for all 4 conditions.
    Returns saved figure path."""
    # x-axis: checkpoints [500, 1000, ..., 5000]
    # y-axis: mean reward_density per 500-step window
    # output: {figures_dir}/reward_density_timeseries.png
    ...

def plot_wilcoxon_boxplot(
    curriculum_vals: np.ndarray,  # shape (5,) — early-phase checkpoints
    uniform_vals: np.ndarray,     # shape (5,)
    p_value: float,
    figures_dir: str = FIGURES_DIR,
) -> str:
    """Boxplot of curriculum vs uniform early-phase values with p-value annotation.
    Returns saved figure path."""
    # x-axis: ["curriculum", "uniform"]
    # y-axis: reward_density
    # annotation: f"p={p_value:.4f}" at top of figure
    # output: {figures_dir}/reward_density_wilcoxon_boxplot.png
    ...

def plot_phase_comparison(
    phase_stats: dict,  # {condition: {early: {mean, std}, late: {mean, std}}}
    figures_dir: str = FIGURES_DIR,
) -> str:
    """Side-by-side bar chart of early vs late phase reward density per condition.
    Returns saved figure path."""
    # grouped bars: early (blue) and late (orange) per condition
    # output: {figures_dir}/reward_density_phase_comparison.png
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Bar chart with std error bars | `plot_early_phase_bar`: `ax.bar(conditions, means, yerr=stds, capsize=5)`; labels: x="Condition", y="Mean Reward Density (steps 0-2500)" |
| L-4-2 | Wilcoxon boxplot with p-value annotation | `plot_wilcoxon_boxplot`: `ax.boxplot([curriculum_vals, uniform_vals])`; annotate p-value via `ax.text` or `ax.set_title` |

---

## A-2: LogLoader [Complexity: 10, Budget: 2 subtasks]

Applied: Window aggregation over per-step CSV rows

### API Signatures

```python
# h-m1/code/analysis/loader.py
import pandas as pd
import numpy as np

CONDITIONS: list[str] = ["curriculum", "uniform", "easy_only", "hard_only"]
LOG_DIR: str = "h-e1/logs"
WINDOW_SIZE: int = 500   # steps per checkpoint window

def load_reward_density_logs(
    log_dir: str = LOG_DIR,
) -> dict[str, pd.DataFrame]:
    """Load all 4 condition CSVs. Returns {condition: DataFrame(columns=[step, reward_density])}."""
    ...

def validate_full_training(
    logs: dict[str, pd.DataFrame],
    min_rows: int = 10,
) -> tuple[bool, dict[str, int]]:
    """Validate all conditions have >= min_rows. Returns (all_valid, {condition: row_count}).
    Raises ValueError with guidance if any condition fails."""
    ...

def compute_early_phase_density(
    df: pd.DataFrame,
    max_step: int = 2500,
    window_size: int = WINDOW_SIZE,
) -> np.ndarray:
    """Aggregate per-step rows into per-checkpoint windows for steps <= max_step.
    Returns shape (5,) — mean density for windows [1-500, 501-1000, ..., 2001-2500]."""
    ...

def compute_late_phase_density(
    df: pd.DataFrame,
    min_step: int = 2501,
    window_size: int = WINDOW_SIZE,
) -> np.ndarray:
    """Aggregate per-step rows into per-checkpoint windows for steps > min_step.
    Returns shape (5,) — mean density for windows [2501-3000, ..., 4501-5000]."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| early_vals | (5,) | Mean per 500-step window, steps 1-2500 |
| late_vals | (5,) | Mean per 500-step window, steps 2501-5000 |
| df | (5000, 2) | Full training CSV: [step, reward_density] |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Per-step to per-checkpoint window aggregation | Bin rows into 500-step groups using `df[df["step"] <= max_step]`, then groupby `(step-1)//500` → `.mean()["reward_density"]`; return as np.ndarray shape (5,) |
| L-2-2 | Validation and error handling | `validate_full_training`: count rows per condition; raise `ValueError(f"Condition {c} has {n} rows, expected >= {min_rows}. Run run_training.py first.")` if insufficient |

---

## A-3: StatsTester [Complexity: 9, Budget: 2 subtasks]

Applied: scipy.stats.wilcoxon one-tailed paired test

### API Signatures

```python
# h-m1/code/analysis/stats.py
import numpy as np
from scipy import stats

def run_wilcoxon_test(
    curriculum_vals: np.ndarray,  # shape (5,)
    uniform_vals: np.ndarray,     # shape (5,)
) -> dict:
    """One-tailed Wilcoxon signed-rank test: H1 = curriculum > uniform.
    Returns {statistic, p_value, passed, curriculum_mean, uniform_mean, delta}."""
    # scipy.stats.wilcoxon(curriculum_vals, uniform_vals, alternative='greater')
    ...

def check_assumption_a1(
    easy_only_vals: np.ndarray,   # shape (5,)
    curriculum_vals: np.ndarray,  # shape (5,)
) -> dict:
    """Check if curriculum_mean > easy_only_mean (curriculum exceeds easy-only).
    Returns {passed, easy_only_mean, curriculum_mean, delta}."""
    ...

def compute_phase_stats(
    logs: dict[str, pd.DataFrame],
) -> dict:
    """Compute early and late phase stats for all conditions.
    Returns {condition: {early: {mean: float, std: float}, late: {mean: float, std: float}}}."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Wilcoxon test wrapper | Call `scipy.stats.wilcoxon(x=curriculum_vals, y=uniform_vals, alternative='greater')`; extract `statistic`, `pvalue`; set `passed = pvalue < 0.05` |
| L-3-2 | Phase stats computation | Call `compute_early_phase_density` and `compute_late_phase_density` per condition; compute `{mean: float(np.mean(vals)), std: float(np.std(vals))}` for each phase |
