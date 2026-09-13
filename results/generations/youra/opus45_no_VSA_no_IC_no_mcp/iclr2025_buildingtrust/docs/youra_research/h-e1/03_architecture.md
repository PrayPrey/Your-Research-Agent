# Architecture: h-e1 (EXISTENCE)

**Applied**: lm-eval-harness evaluation + partial-correlation residualization pattern

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis, no existing `src/`.

---

## File Structure

```
h-e1/code/
  config.py       # model list, task names, paths
  evaluate.py      # runs lm-eval-harness per model, caches JSON results
  aggregate.py     # parses results -> scores table (csv)
  analysis.py      # partial correlation + bootstrap CI
  visualize.py     # 4 figures
  run.py           # orchestrates evaluate -> aggregate -> analysis -> visualize
  results/         # raw lm-eval-harness JSON outputs (cached)
  figures/         # output PNGs
```

---

## Modules

### config.py

**Dependencies**: none

```python
MODELS: list[dict]  # [{"id": "EleutherAI/pythia-70m", "family": "pythia", "params": 70_000_000}, ...]
TASKS = ["truthful_qa_mc1", "adversarial_glue"]
RESULTS_DIR = "results/"
FIGURES_DIR = "figures/"
SEED = 42
N_BOOTSTRAP = 1000
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: config.py, lm-eval-harness (subprocess/CLI)

```python
def run_lm_eval(model_id: str, tasks: list[str], output_path: str) -> None: ...
def evaluate_all(models: list[dict]) -> None:  # skips if cached result exists
```

### aggregate.py (`code/aggregate.py`)

**Dependencies**: config.py, evaluate.py output (JSON)

```python
def parse_result_file(path: str) -> dict: ...  # {truthfulqa_mc1, advglue_avg}
def collect_scores(models: list[dict], results_dir: str) -> "pd.DataFrame": ...
    # columns: model, family, params, log_params, truthfulqa_mc1, advglue_avg
def save_scores(df, path: str) -> None: ...
```

### analysis.py (`code/analysis.py`)

**Dependencies**: aggregate.py output (DataFrame), scipy, sklearn

```python
def partial_corr(x: "np.ndarray", y: "np.ndarray", z: "np.ndarray") -> tuple[float, float]: ...
    # residualize x,y on z (np.polyfit deg=1), pearsonr(resid_x, resid_y)
def bootstrap_ci(x, y, z, n_bootstrap: int = 1000, seed: int = 42) -> dict: ...
    # returns {r, p, ci_lower, ci_upper, bootstrap_rs, n_models, gate_passed}
def run_analysis(df: "pd.DataFrame") -> dict: ...
```

### visualize.py (`code/visualize.py`)

**Dependencies**: analysis.py output, matplotlib/seaborn

```python
def plot_scatter(df, result: dict, out_path: str) -> None: ...       # mandatory gate figure
def plot_residuals(df, result: dict, out_path: str) -> None: ...
def plot_bootstrap_hist(result: dict, out_path: str) -> None: ...
def plot_family_comparison(df, out_path: str) -> None: ...
def generate_all_figures(df, result: dict, figures_dir: str) -> None: ...
```

### run.py (`code/run.py`)

**Dependencies**: all above modules

```python
def main() -> None: ...
    # evaluate_all -> collect_scores -> save_scores -> run_analysis -> generate_all_figures -> print gate result
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config setup | Define model list (15-20 models), tasks, paths | 4 | 1+1+1+1 |
| A-2 | Evaluation pipeline | lm-eval-harness runner with caching per model | 10 | 3+3+2+2 |
| A-3 | Run evaluations | Execute evaluate_all across all models (I/O heavy, long-running) | 6 | 2+2+1+1 |
| A-4 | Aggregate results | Parse JSON outputs into scores DataFrame + log(params) | 6 | 2+1+2+1 |
| A-5 | Partial correlation + bootstrap | Implement residualization, pearsonr, 1000-sample bootstrap CI | 9 | 2+2+3+2 |
| A-6 | Visualization | 4 figures (scatter, residual, bootstrap hist, family bar) | 7 | 3+1+1+2 |
| A-7 | Orchestration + gate check | run.py wiring all stages, print PASS/FAIL against 3 criteria | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-5], Low(4-8): [A-1, A-3, A-4, A-6, A-7]

---

## Notes

- Skipped: separate module for lm-eval-harness result schema validation — inline dict parsing in `aggregate.py` covers it, add if result formats diverge across model families.
- AdvGLUE avg = mean of all `adv_*` subtask accuracies in a single model's result JSON (per PRD FR-3).
- Bootstrap resampling uses `sklearn.utils.resample` with fixed `SEED` for reproducibility (NFR-1).
