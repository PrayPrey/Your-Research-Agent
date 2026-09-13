# Architecture: H-M1 (ΔPass₁₂ Trajectory Analysis)

**Type**: MECHANISM | **Applied**: post-hoc-statistical-analysis-pipeline (KB search: no directly relevant DL-repair-analysis pattern found, similarity <0.48; using simple load-compute-test-plot pipeline per PRD/brief spec)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze. h-m1 consumes h-e1's output data file (JSONL) as a data contract only, not as imported code. No `src/` or `h-m1/code/` directory exists yet.
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. h-e1 module code (`h-e1/03_architecture.md`) is not imported; only its output artifact `h-e1_iteration_logs.jsonl` is read as input data.

---

## File Structure (Minimal — Analysis Pipeline)

```
h-m1/code/
  config.py            # fixed paths, thresholds
  data_loader.py        # load + validate h-e1 iteration logs
  trajectory.py          # ΔPass₁₂ computation per condition
  stats.py                # McNemar's test
  visualize.py             # required + optional figures
  run_analysis.py           # main entrypoint
  results/                   # output artifacts
```

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
@dataclass
class AnalysisConfig:
    logs_path: str = "../h-e1/code/results/h-e1_iteration_logs.jsonl"
    results_dir: str = "results/"
    figures_dir: str = "figures/"
    conditions: tuple[str, str] = ("static_first", "exec_first")
    iterations: tuple[int, ...] = (1, 2, 3)
    alpha: float = 0.05
```

### Data Loader (`data_loader.py`)

**Dependencies**: Config

```python
def load_logs(path: str) -> list[dict]: ...
    # json.loads per line

def validate_logs(logs: list[dict], cfg: AnalysisConfig) -> None: ...
    # asserts required fields, condition set, iteration set == {1,2,3}
    # raises AssertionError with message on mismatch (fail fast per NFR-1)
```

### Trajectory (`trajectory.py`)

**Dependencies**: data_loader.py

```python
def compute_delta_pass_12(logs: list[dict], condition: str) -> dict: ...
    # returns {delta_pass_12, pass_at_iter_1, pass_at_iter_2, n_problems, newly_solved_iter_2}

def compute_cumulative_trajectory(logs: list[dict], condition: str) -> dict[int, float]: ...
    # cumulative pass@1 at iter 1,2,3 — for trajectory plot

def compare_conditions(logs: list[dict], cfg: AnalysisConfig) -> dict: ...
    # returns {static_first, exec_first, delta_diff, hypothesis_supported}
```

### Stats (`stats.py`)

**Dependencies**: trajectory.py

```python
def mcnemar_test(static_newly_solved: set, exec_newly_solved: set, all_problems: set) -> dict: ...
    # returns {p_value, static_only, exec_only}
    # exact binomial if b+c<25, else chi2 approx (per brief pseudocode)
```

### Visualize (`visualize.py`)

**Dependencies**: trajectory.py, stats.py

```python
def plot_delta_comparison(compare_result: dict, out_path: str) -> None: ...
    # REQUIRED: bar chart, ΔPass12 static-first vs exec-first, error bars (bootstrap or binomial SE)

def plot_iteration_trajectory(traj_static: dict[int, float], traj_exec: dict[int, float], out_path: str) -> None: ...
    # cumulative pass@1 vs iteration, two lines

def plot_problem_heatmap(logs: list[dict], out_path: str) -> None: ...
    # optional: problems x iteration, solved/unsolved, per condition

def plot_early_late_gains(logs: list[dict], out_path: str) -> None: ...
    # optional: stacked bar, gains at iter1/2/3 per condition
```

### Entrypoint (`run_analysis.py`)

**Dependencies**: all modules

```python
def main() -> None: ...
    # load_logs -> validate_logs -> compare_conditions -> mcnemar_test ->
    # write results/h-m1_analysis.json ->
    # plot_delta_comparison (required) + optional figures -> print pass/fail vs success criteria
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Config + Data Loading | AnalysisConfig, JSONL load, field/condition/iteration validation | 6 | 1+1+2+2 |
| M-2 | Trajectory Computation | compute_delta_pass_12, cumulative trajectory, compare_conditions | 9 | 2+2+3+2 |
| M-3 | McNemar Statistical Test | Exact binomial + chi2-approx paired test on newly-solved sets | 8 | 2+2+3+1 |
| M-4 | Required Figure | ΔPass₁₂ bar chart with error bars, save to figures/ | 5 | 1+1+2+1 |
| M-5 | Optional Figures | Trajectory plot, problem heatmap, early/late stacked bar | 7 | 2+1+2+2 |
| M-6 | Main Pipeline + Output | Orchestrate end-to-end, write h-m1_analysis.json, print success criteria | 6 | 1+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-2, M-3], Low(4-8): [M-1, M-4, M-5, M-6]

---

## External Dependencies (Base Hypothesis)

### Data Contract (From h-e1, Not Code Import)

| Artifact | Path | Format |
|----------|------|--------|
| Iteration logs | `h-e1/code/results/h-e1_iteration_logs.jsonl` | JSONL: `{problem_id, condition, iteration, passed}` |

**Note**: h-m1 does NOT import h-e1 Python modules (`repair_loop.py`, `metrics.py`, etc.). It only reads h-e1's output JSONL as a plain data file. File not yet present (h-e1 execution pending) — `data_loader.py` must fail fast with a clear error if missing, per NFR-1/FR-2.
