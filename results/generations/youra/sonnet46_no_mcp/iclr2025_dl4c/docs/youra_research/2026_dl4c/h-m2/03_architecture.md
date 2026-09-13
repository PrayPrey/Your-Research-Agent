# Architecture: H-M2 — Reward Entropy & Predictive Correlation

**Applied**: log-analysis pipeline pattern (CSV-in / figures-out, no training)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from actual base code
**Analyzed Path**: `h-e1/code/`
**Findings**: `compute_reward_density()` returns binary 0.0/1.0 (std > epsilon check — NOT a fraction). `RewardDensityCallback` logs per-step values to `h-e1/logs/reward_density_{condition}.csv` (columns: `step, reward_density`). EvalPlus checkpoint sweep saves `eval_results_{condition}.json` per condition (not per-checkpoint CSVs). Pass@1 checkpoint CSVs not confirmed — fallback must scan JSON files.

---

## File Structure

```
h-m2/code/
├── analysis/
│   ├── load_data.py
│   ├── compute_entropy.py
│   ├── compute_gains.py
│   └── pearson_correlation.py
├── visualization/
│   └── generate_figures.py
└── run_analysis.py
h-m2/results/
h-m2/figures/
```

---

## Module Definitions

### DataLoader (`analysis/load_data.py`)

**Dependencies**: pandas, os, json

```python
CONDITIONS: list[str] = ["curriculum", "uniform", "easy_only", "hard_only"]
H_E1_LOG_DIR: str = "../../h-e1/logs"
H_E1_RESULTS_DIR: str = "../../h-e1/results"

def load_reward_density(log_dir: str, condition: str) -> pd.DataFrame:
    # Returns DataFrame(columns=["step","reward_density"]), sorted by step
    # Asserts >= 10 rows and required columns
    ...

def load_pass1_checkpoints(log_dir: str, condition: str) -> pd.DataFrame:
    # Primary: reads pass1_checkpoint_{condition}.csv (columns: step, pass1)
    # Fallback: scans eval_results_{condition}.json in results_dir
    #           builds DataFrame from checkpoint sweep results list
    # Asserts >= 5 rows (minimum viable)
    ...

def load_all_conditions(
    log_dir: str = H_E1_LOG_DIR,
    results_dir: str = H_E1_RESULTS_DIR,
) -> dict[str, dict[str, pd.DataFrame]]:
    # Returns {condition: {"density": df, "pass1": df}} for all 4 conditions
    ...
```

---

### EntropyComputer (`analysis/compute_entropy.py`)

**Dependencies**: numpy, pandas

```python
def compute_entropy_from_density(density: float) -> float:
    # Binary entropy H(p) = -p*log2(p) - (1-p)*log2(1-p)
    # NOTE: density from H-E1 is binary (0.0 or 1.0), not a fraction.
    # For intermediate checkpoint aggregates, density may be mean over window.
    # Edge: p <= 0.0 or p >= 1.0 -> return 0.0
    ...

def add_entropy_column(density_df: pd.DataFrame) -> pd.DataFrame:
    # Adds "entropy" column to density_df; returns new DataFrame
    ...

def compute_early_mean_entropy(
    density_df: pd.DataFrame,
    max_step: int = 2500,
) -> float:
    # Mean entropy for rows where step <= max_step
    ...

def compare_entropy_direction(
    data: dict[str, dict[str, pd.DataFrame]],
) -> dict:
    # Returns {
    #   "mean_entropy_curriculum_early": float,
    #   "mean_entropy_uniform_early": float,
    #   "delta_entropy": float,
    # }
    ...
```

---

### GainsComputer (`analysis/compute_gains.py`)

**Dependencies**: numpy, pandas

```python
def compute_pass1_gains(pass1_df: pd.DataFrame) -> np.ndarray:
    # Sort by step, compute np.diff(pass1_values) -> shape (n-1,)
    # Returns array of 9 gains from 10 checkpoints
    ...

def build_pooled_observations(
    data: dict[str, dict[str, pd.DataFrame]],
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    # Returns (all_densities, all_gains, condition_labels)
    # all_densities: reward_density at steps 500..4500 (first 9 per condition)
    # all_gains: pass1_gain from T to T+500 (9 per condition)
    # condition_labels: repeated condition name for each observation (for plotting)
    # Validates len == 36 (warns if fewer due to missing checkpoints)
    ...
```

---

### CorrelationAnalyzer (`analysis/pearson_correlation.py`)

**Dependencies**: numpy, scipy.stats

```python
def pearson_with_ci(x: np.ndarray, y: np.ndarray) -> dict:
    # Returns {r, p_twotailed, p_onetailed, ci_low, ci_high, n}
    # CI via Fisher z-transformation
    ...

def per_condition_correlations(
    data: dict[str, dict[str, pd.DataFrame]],
) -> dict[str, dict]:
    # Returns {condition: {r, p_onetailed, n}} for each condition
    ...

def wilcoxon_entropy_test(
    entropy_curriculum_early: np.ndarray,
    entropy_uniform_early: np.ndarray,
) -> dict:
    # One-tailed Wilcoxon signed-rank test (curriculum > uniform)
    # Returns {statistic, p_value, direction_correct}
    ...

def evaluate_gate(pearson_result: dict) -> bool:
    # Returns True if r > 0.5 AND p_onetailed < 0.05
    ...

def save_results(
    pooled_pearson: dict,
    entropy_comparison: dict,
    per_condition_r: dict,
    wilcoxon_result: dict,
    output_path: str,
) -> None:
    # Writes results_summary.json with all gate metrics
    ...
```

---

### FigureGenerator (`visualization/generate_figures.py`)

**Dependencies**: matplotlib, numpy, scipy.stats (linregress)

```python
COLORS: dict[str, str] = {
    "curriculum": "blue",
    "uniform": "orange",
    "easy_only": "green",
    "hard_only": "red",
}

def plot_scatter_density_vs_gain(
    all_densities: np.ndarray,
    all_gains: np.ndarray,
    condition_labels: list[str],
    pearson_r: float,
    output_path: str,
) -> None:
    # Scatter plot color-coded by condition, regression line, r annotation
    # Saves to h-m2/figures/scatter_density_vs_gain.png at 200 DPI
    ...

def plot_entropy_timeseries(
    data: dict[str, dict[str, pd.DataFrame]],
    output_path: str,
) -> None:
    # Line plot: entropy per checkpoint for all 4 conditions
    # Vertical line at step 2500
    # Saves to h-m2/figures/entropy_timeseries.png
    ...

def plot_entropy_density_comparison(
    data: dict[str, dict[str, pd.DataFrame]],
    output_path: str,
) -> None:
    # Side-by-side bar chart (early phase 0-2500): density and entropy per condition
    # Saves to h-m2/figures/entropy_density_comparison.png
    ...

def plot_per_condition_scatter(
    data: dict[str, dict[str, pd.DataFrame]],
    output_path: str,
) -> None:
    # 2x2 subplot grid, one per condition, density vs gain with regression
    # Saves to h-m2/figures/per_condition_scatter.png
    ...

def plot_pass1_gain_timeseries(
    data: dict[str, dict[str, pd.DataFrame]],
    output_path: str,
) -> None:
    # Line plot: pass@1 gain per interval for all 4 conditions
    # Saves to h-m2/figures/pass1_gain_timeseries.png
    ...

def generate_all_figures(
    data: dict[str, dict[str, pd.DataFrame]],
    all_densities: np.ndarray,
    all_gains: np.ndarray,
    condition_labels: list[str],
    pearson_r: float,
    figures_dir: str,
) -> None:
    # Calls all 5 plot functions; creates figures_dir if missing
    ...
```

---

### RunAnalysis (`run_analysis.py`)

**Dependencies**: all analysis modules, pathlib, json

```python
BASE_DIR: str  # absolute path to h-m2/
H_E1_LOG_DIR: str
H_E1_RESULTS_DIR: str
RESULTS_DIR: str
FIGURES_DIR: str

def main() -> None:
    # 1. load_all_conditions()
    # 2. add_entropy_column() for each condition
    # 3. compare_entropy_direction()
    # 4. build_pooled_observations()  -> (densities, gains, labels)
    # 5. pearson_with_ci(densities, gains)
    # 6. per_condition_correlations()
    # 7. wilcoxon_entropy_test()
    # 8. evaluate_gate()
    # 9. save_results() -> results_summary.json
    # 10. save entropy_timeseries.csv, correlation_data.csv
    # 11. generate_all_figures()
    # 12. print gate result to stdout
    ...

if __name__ == "__main__":
    main()
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| compute_reward_density | `from h_e1.training.reward import compute_reward_density` | `h-e1/code/training/reward.py` |
| RewardDensityCallback | `from h_e1.training.callbacks import RewardDensityCallback` | `h-e1/code/training/callbacks.py` |
| evaluate_all_checkpoints | `from h_e1.evaluation.evaluate import evaluate_all_checkpoints` | `h-e1/code/evaluation/evaluate.py` |

**Note**: H-M2 does NOT import H-E1 code at runtime — it reads CSV/JSON output files. The table above documents provenance of data formats only.

**CRITICAL implementation note**: `compute_reward_density()` in H-E1 returns **binary 0.0 or 1.0** (std > epsilon check), NOT a fraction. The reward density CSVs contain per-step binary values. H-M2 must aggregate these per 500-step window (mean over 500 rows) to get a meaningful density fraction for entropy computation and Pearson correlation. The per-checkpoint CSV likely has 10 rows = 10 window-mean values, but if the raw CSV has 5000 rows (one per step), H-M2 must aggregate first.

**Verified from**: `h-e1/code/training/reward.py` line 140-151 (actual implementation)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & data audit | Create h-m2/code/ structure; audit h-e1/logs/ for CSV existence and row counts; document what exists vs missing | 7 | 2+1+1+3 |
| A-2 | Implement DataLoader | load_data.py with primary CSV path + fallback JSON scan; handle binary density aggregation (500-step windows) | 11 | 3+2+3+3 |
| A-3 | Implement EntropyComputer | compute_entropy.py: binary entropy function, add_entropy_column, compare_entropy_direction | 8 | 2+2+2+2 |
| A-4 | Implement GainsComputer | compute_gains.py: pass@1 gain per interval, build_pooled_observations (36 obs validation) | 9 | 2+2+3+2 |
| A-5 | Implement CorrelationAnalyzer | pearson_correlation.py: Pearson r with 95% CI, per-condition r, Wilcoxon, gate check, save_results JSON | 12 | 3+3+3+3 |
| A-6 | Implement FigureGenerator | generate_figures.py: all 5 required figures at 200 DPI with consistent color scheme | 13 | 3+2+4+4 |
| A-7 | Implement RunAnalysis | run_analysis.py: orchestrate full pipeline, save CSVs, print gate result | 8 | 2+3+1+2 |
| A-8 | Handle pass@1 fallback | If pass1_checkpoint_{condition}.csv absent, scan h-e1/results/ JSON and build CSV; verify ≥5 checkpoints per condition | 11 | 2+2+4+3 |
| A-9 | Integration test & gate eval | Run end-to-end; verify 36 pooled obs; print GATE PASSED/FAILED with r and p values | 10 | 2+3+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4, A-5, A-6, A-8, A-9], Low(4-8): [A-1, A-3, A-7]
