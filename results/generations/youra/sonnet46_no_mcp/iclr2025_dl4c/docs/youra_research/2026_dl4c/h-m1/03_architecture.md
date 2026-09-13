# Architecture: h-m1
# Reward Density Mechanism Verification — Log Analysis

**Applied**: Log-analysis pipeline pattern (reuse base infrastructure, new analysis layer only)
**Applied**: Wilcoxon paired non-parametric test for small-n statistical verification

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from base code (direct file reads)
**Analyzed Path**: `docs/youra_research/20260502_dl4c/h-e1/code/`
**Findings**: H-E1 has complete training infrastructure. `RewardDensityCallback` logs per-step reward density to `h-e1/logs/reward_density_{condition}.csv`. `compute_reward_density()` returns 1.0 if std(rewards_group) > REWARD_EPSILON, else 0.0. CSV logs produced with step-by-step granularity (not per-checkpoint). Config uses `log_dir: "h-e1/logs"`, `save_steps: 500`, `max_steps: 5000`. No `code/__init__.py` exists (correct — do not create one).

---

## File Organization

H-M1 introduces only one new directory: `h-m1/code/analysis/`. All training infrastructure is reused from H-E1 without modification.

- `h-m1/code/analysis/analyze_reward_density.py` — primary analysis script (main entry point)
- `h-m1/code/analysis/loader.py` — CSV loading and validation
- `h-m1/code/analysis/stats.py` — Wilcoxon test and secondary checks
- `h-m1/code/analysis/visualize.py` — figure generation (4 figures)
- `h-m1/code/run_training.py` — shell wrapper to trigger H-E1 full training (if needed)
- `h-m1/figures/` — output directory for 4 figures
- `h-m1/results/` — output directory for JSON results

**H-E1 files reused directly (no copy, no modification):**
- `h-e1/code/training/train.py`
- `h-e1/code/training/reward.py`
- `h-e1/code/training/callbacks.py`
- `h-e1/code/config.py`
- `h-e1/code/data/dataset.py`
- `h-e1/code/data/preprocessing.py`

---

## Modules

### LogLoader (`h-m1/code/analysis/loader.py`)

**Dependencies**: pandas

```python
CONDITIONS: list[str] = ["curriculum", "uniform", "easy_only", "hard_only"]
LOG_DIR: str = "h-e1/logs"

def load_reward_density_logs(log_dir: str = LOG_DIR) -> dict[str, pd.DataFrame]: ...
    # Returns {condition: DataFrame(columns=[step, reward_density])} for all 4 conditions

def validate_full_training(logs: dict[str, pd.DataFrame], min_rows: int = 10) -> tuple[bool, dict]: ...
    # Returns (all_valid, {condition: row_count})
    # Raises ValueError with guidance if any condition has < min_rows

def compute_early_phase_density(df: pd.DataFrame, max_step: int = 2500) -> np.ndarray: ...
    # Returns np.ndarray shape (5,) — steps 500, 1000, 1500, 2000, 2500

def compute_late_phase_density(df: pd.DataFrame, min_step: int = 2501) -> np.ndarray: ...
    # Returns np.ndarray shape (5,) — steps 3000, 3500, 4000, 4500, 5000
```

### StatsTester (`h-m1/code/analysis/stats.py`)

**Dependencies**: numpy, scipy

```python
def run_wilcoxon_test(
    curriculum_vals: np.ndarray,
    uniform_vals: np.ndarray,
) -> dict: ...
    # Returns: {statistic, p_value, passed, curriculum_mean, uniform_mean, delta}
    # Uses scipy.stats.wilcoxon(x, y, alternative='greater')

def check_assumption_a1(
    easy_only_vals: np.ndarray,
    curriculum_vals: np.ndarray,
) -> dict: ...
    # Returns: {passed, easy_only_mean, curriculum_mean, delta}

def compute_phase_stats(
    logs: dict[str, pd.DataFrame],
) -> dict: ...
    # Returns nested dict: {condition: {early: {mean, std}, late: {mean, std}}}
```

### Visualizer (`h-m1/code/analysis/visualize.py`)

**Dependencies**: matplotlib, numpy

```python
FIGURES_DIR: str = "h-m1/figures"

def plot_early_phase_bar(
    phase_stats: dict,
    figures_dir: str = FIGURES_DIR,
) -> str: ...
    # Bar chart — mean reward density (steps 0-2500) per condition with std error bars
    # Output: h-m1/figures/reward_density_early_phase_bar.png

def plot_timeseries(
    logs: dict[str, pd.DataFrame],
    figures_dir: str = FIGURES_DIR,
) -> str: ...
    # Line plot — reward density at each 500-step checkpoint, all 4 conditions
    # Output: h-m1/figures/reward_density_timeseries.png

def plot_wilcoxon_boxplot(
    curriculum_vals: np.ndarray,
    uniform_vals: np.ndarray,
    p_value: float,
    figures_dir: str = FIGURES_DIR,
) -> str: ...
    # Box plot — curriculum vs. uniform (steps 0-2500) with p-value annotation
    # Output: h-m1/figures/reward_density_wilcoxon_boxplot.png

def plot_phase_comparison(
    phase_stats: dict,
    figures_dir: str = FIGURES_DIR,
) -> str: ...
    # Side-by-side bar charts — early vs. late phase reward density per condition
    # Output: h-m1/figures/reward_density_phase_comparison.png
```

### RewardDensityAnalyzer (`h-m1/code/analysis/analyze_reward_density.py`)

**Dependencies**: LogLoader, StatsTester, Visualizer, json, os

```python
RESULTS_DIR: str = "h-m1/results"

def run_analysis(log_dir: str = "h-e1/logs", figures_dir: str = "h-m1/figures") -> dict: ...
    # Main pipeline: load → validate → extract → test → visualize → report
    # Returns full results dict with gate_passed bool

def save_results(results: dict, results_dir: str = RESULTS_DIR) -> str: ...
    # Writes h-m1/results/wilcoxon_results.json

def print_summary(results: dict) -> None: ...
    # Prints gate result: PASSED/FAILED with p_value, means, delta

if __name__ == "__main__":
    results = run_analysis()
    save_results(results)
    print_summary(results)
    sys.exit(0 if results["gate_passed"] else 1)
```

### TrainingWrapper (`h-m1/code/run_training.py`)

**Dependencies**: subprocess, os, sys (calls h-e1/code/training/train.py)

```python
CONDITIONS: list[str] = ["curriculum", "uniform", "easy_only", "hard_only"]
H_E1_TRAIN_SCRIPT: str = "h-e1/code/training/train.py"

def check_logs_sufficient(log_dir: str = "h-e1/logs", min_rows: int = 10) -> bool: ...
    # Returns True if all 4 CSVs exist and have >= 10 rows

def run_full_training(
    condition: str,
    cuda_device: str = "0",
) -> int: ...
    # Runs: CUDA_VISIBLE_DEVICES={cuda_device} python h-e1/code/training/train.py --condition {condition}
    # Returns subprocess return code

def run_all_conditions(cuda_device: str = "0") -> dict[str, int]: ...
    # Sequentially runs all 4 conditions; returns {condition: return_code}

if __name__ == "__main__":
    # Entry: check logs, trigger training if needed, then invoke analyze_reward_density.py
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| CONFIG | `from config import CONFIG` (with sys.path.insert) | `h-e1/code/config.py` |
| CONDITIONS | `from config import CONDITIONS` | `h-e1/code/config.py` |
| execution_reward_fn | `from training.reward import execution_reward_fn` | `h-e1/code/training/reward.py` |
| compute_reward_density | `from training.reward import compute_reward_density` | `h-e1/code/training/reward.py` |
| CurriculumCallback | `from training.callbacks import CurriculumCallback` | `h-e1/code/training/callbacks.py` |
| RewardDensityCallback | `from training.callbacks import RewardDensityCallback` | `h-e1/code/training/callbacks.py` |
| CurriculumDataset | `from data.dataset import CurriculumDataset` | `h-e1/code/data/dataset.py` |

**Verified from**: `h-e1/code/` (actual implementation)

**Critical Notes from Actual Code:**
- H-E1 `config.py` uses `log_dir: "h-e1/logs"` and `save_steps: 500` (confirmed)
- `compute_reward_density()` checks std > REWARD_EPSILON (1e-8), NOT max(group) > 0 (differs from spec!)
- `RewardDensityCallback.on_step_end` logs per-step (every step), not per-checkpoint
- Log CSV has one row per training step — 5000 rows for full training (not 10)
- H-M1 analysis must aggregate per-checkpoint window (e.g., mean of steps 1-500 for checkpoint 1)
- No `code/__init__.py` exists in H-E1 — do NOT create one in H-M1 either

---

## Dependency Graph

```
run_training.py
    → h-e1/code/training/train.py (subprocess call)

analyze_reward_density.py
    → loader.py → pandas
    → stats.py → numpy, scipy.stats
    → visualize.py → matplotlib
    → results: h-m1/results/wilcoxon_results.json
    → figures: h-m1/figures/*.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup project structure | Create h-m1/code/analysis/, h-m1/figures/, h-m1/results/; verify h-e1/logs/ paths | 5 | 1+1+1+2 |
| A-2 | Implement LogLoader | loader.py: load_reward_density_logs, validate_full_training, compute_early/late_phase_density; handle per-step aggregation to per-checkpoint windows | 10 | 2+2+3+3 |
| A-3 | Implement StatsTester | stats.py: run_wilcoxon_test (one-tailed, n=5), check_assumption_a1, compute_phase_stats | 9 | 2+2+3+2 |
| A-4 | Implement Visualizer | visualize.py: 4 figures (bar chart, timeseries, boxplot, phase comparison) with correct labels and p-value annotations | 11 | 3+2+3+3 |
| A-5 | Implement main analyzer | analyze_reward_density.py: orchestrate full pipeline, save JSON results, print gate summary, exit code 0/1 | 9 | 2+3+2+2 |
| A-6 | Implement TrainingWrapper | run_training.py: log sufficiency check, subprocess invocation of h-e1 train.py per condition, CUDA_VISIBLE_DEVICES handling | 10 | 2+3+3+2 |
| A-7 | Integration test (smoke) | Verify analysis pipeline runs end-to-end with synthetic CSV data (10 rows per condition) | 8 | 2+2+2+2 |
| A-8 | Full training execution | Run all 4 conditions × 5000 steps via run_training.py (sequentially); verify 5000-row CSVs produced | 14 | 2+4+4+4 |
| A-9 | Analysis and gate evaluation | Run analyze_reward_density.py on full training logs; verify gate: p < 0.05 AND curriculum_mean > uniform_mean | 12 | 3+3+3+3 |
| A-10 | Figure validation and results | Verify 4 figures exist in h-m1/figures/; validate wilcoxon_results.json schema; document gate result | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-8], Medium(9-13): [A-2, A-3, A-4, A-5, A-6, A-9], Low(4-8): [A-1, A-7, A-10]
