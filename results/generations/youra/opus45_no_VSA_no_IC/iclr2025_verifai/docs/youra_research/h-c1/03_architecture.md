# Architecture: H-C1 (Cross-Model SA-Correctness Generalization)

**Type**: CONDITION | **Gate**: SHOULD_WORK

Applied: reuse-validated-mechanism-pipeline (H-M1 modules directly importable; no ML training, statistical groupby only). Archon KB had no relevant match (only diffusion-model results returned, similarity <0.47) — pattern chosen from PRD/brief reference implementation instead.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1) — VALIDATED, fully implemented
**Status**: `h-m1/code/` contains flat-file modules (not a package): `config.py`, `dataset.py`, `completions.py`, `sa_tools.py`, `metrics.py`, `correlate.py`, `visualize.py`, `run.py`. Serena MCP tool unavailable (no active project registered for this path); verified directly via file reads instead.
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**:
- `dataset.py::load_all_problems()` returns `list[Problem]` (HumanEval+MBPP, no dedupe logic present despite spec claim — 421 total, not 591).
- `metrics.py::build_dataframe(problems, completions, passed)` runs pylint/mypy/radon per sample, returns DataFrame with `task_id, passed, pylint_score, mypy_errors, radon_cc, loc` — **no `model_id` column**, must wrap.
- `correlate.py::partial_corr_loc(df, metric)` computes single LOC-controlled partial r for a whole DataFrame — reusable per-model by filtering df first.
- `completions.py::load_completions_jsonl(path)` takes one path per call — must invoke once per model with per-model JSONL files.
- `config.py::CONFIG` is a frozen dataclass singleton; H-C1 needs its own `Config` (multi-model paths, variance threshold) rather than mutating shared one.

---

## File Structure

- `code/config.py` - fixed config (model list, per-model paths, variance threshold)
- `code/multi_model_data.py` - load completions per model, tag with `model_id`, build combined DataFrame (imports h-m1 `dataset.py`, `completions.py`, `metrics.py`, `eval_pass1.py`)
- `code/cross_correlate.py` - per-model partial correlation + cross-model variance (imports h-m1 `correlate.py`)
- `code/visualize.py` - per-model bar chart, correlation heatmap, distribution violin plot
- `code/run.py` - main pipeline orchestration
- `requirements.txt` - same as H-M1 + no new packages

---

## Module Interfaces

### config.py

```python
MODELS: list[str] = ["gpt4", "claude3", "codellama", "codestral"]
COMPLETIONS_DIR: str = "data/completions"  # expects {model}.jsonl per model
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"
VARIANCE_THRESHOLD: float = 0.15
MEAN_R_THRESHOLD: float = 0.35
ALPHA: float = 0.05
MIN_MODELS: int = 3
```

### multi_model_data.py (`code/multi_model_data.py`)

**Dependencies**: h-m1 `dataset.py`, `completions.py`, `eval_pass1.py`, `metrics.py`, pandas

```python
def load_model_dataframe(model_id: str, problems: list, completions_path: str) -> pd.DataFrame:
    ...  # loads completions, evaluates pass@1, builds SA-metric df (h-m1 metrics.build_dataframe), adds model_id col

def build_multi_model_dataframe(models: list[str], completions_dir: str) -> pd.DataFrame:
    ...  # concat per-model dfs -> task_id, model_id, passed, pylint_score, radon_cc, mypy_errors, loc
```

### cross_correlate.py (`code/cross_correlate.py`)

**Dependencies**: h-m1 `correlate.py`, pandas, numpy

```python
def compute_per_model_correlations(
    df: pd.DataFrame, metric: str = "pylint_score", models: list[str] = MODELS
) -> dict[str, tuple[float, float]]: ...  # model -> (r_partial, p_partial), reuses correlate.partial_corr_loc per model subset

def cross_model_variance(correlations: dict[str, tuple[float, float]]) -> tuple[float, float, float]:
    ...  # returns (mean_r, std_r, min_r)

def determine_gate_pass(
    mean_r: float, std_r: float, min_r: float,
    variance_threshold: float = VARIANCE_THRESHOLD,
) -> bool: ...  # std_r < threshold AND mean_r > MEAN_R_THRESHOLD AND min_r > 0.20
```

### visualize.py (`code/visualize.py`)

**Dependencies**: matplotlib, pandas, config

```python
def plot_per_model_bar(correlations: dict[str, tuple[float, float]], mean_r: float, std_r: float, out_path: str) -> None: ...
def plot_correlation_heatmap(df: pd.DataFrame, metrics: list[str], models: list[str], out_path: str) -> None: ...
def plot_distribution_violin(df: pd.DataFrame, metric: str, out_path: str) -> None: ...
def generate_all_figures(df: pd.DataFrame, correlations: dict) -> None: ...
```

### run.py (`code/run.py`)

**Dependencies**: all modules above, h-m1 modules (via sys.path), json

```python
def main() -> None: ...
# 1. load_all_problems (h-m1 dataset.py)
# 2. build_multi_model_dataframe over MODELS (skip missing completions file, require >= MIN_MODELS)
# 3. compute_per_model_correlations (pylint_score primary, radon_cc secondary)
# 4. cross_model_variance -> mean_r, std_r, min_r
# 5. determine_gate_pass -> bool
# 6. write results/h_c1_correlations.json, h_c1_data.csv, h_c1_summary.json
# 7. generate_all_figures
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Setup & config | Config for models/paths/thresholds, requirements check | 4 | 1+1+1+1 |
| C-2 | Multi-model data loading | Per-model completion loading + pass@1 eval, model_id tagging | 9 | 3+3+2+1 |
| C-3 | SA metric extraction (reuse) | Wire h-m1 metrics.build_dataframe per model, combine into single df | 6 | 2+2+1+1 |
| C-4 | Per-model correlation | Groupby model, reuse h-m1 partial_corr_loc per subset | 7 | 2+2+2+1 |
| C-5 | Cross-model variance & gate | std(r)/mean(r)/min(r) computation, gate pass/fail logic | 6 | 1+2+2+1 |
| C-6 | Visualization | Bar chart w/ error bars, heatmap, violin plot | 6 | 2+1+1+2 |
| C-7 | Pipeline orchestration | run.py end-to-end, result file writing, min-model check | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [C-2], Low(4-8): [C-1, C-3, C-4, C-5, C-6, C-7]

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| Problem, load_all_problems | `from dataset import Problem, load_all_problems` | `h-m1/code/dataset.py` |
| Completion, load_completions_jsonl | `from completions import Completion, load_completions_jsonl` | `h-m1/code/completions.py` |
| run_test, evaluate_all | `from eval_pass1 import run_test, evaluate_all` | `h-m1/code/eval_pass1.py` |
| run_pylint, run_mypy, run_radon | `from sa_tools import run_pylint, run_mypy, run_radon` | `h-m1/code/sa_tools.py` |
| build_dataframe, compute_loc | `from metrics import build_dataframe, compute_loc` | `h-m1/code/metrics.py` |
| partial_corr_loc, point_biserial | `from correlate import partial_corr_loc, point_biserial` | `h-m1/code/correlate.py` |

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation, direct file read since files are flat scripts, not a package — Phase 4 coder must add h-m1 code dir to `sys.path` or copy relevant modules into `h-c1/code/`).

**Note**: H-M1 modules import each other by bare module name (e.g. `metrics.py` does `from sa_tools import ...`), confirming flat script layout with no package `__init__.py`. H-C1 code must either symlink/copy H-M1 `.py` files into `h-c1/code/` or run with H-M1's dir prepended to `PYTHONPATH`.

---

## Self-Validation

- [x] No ASCII diagrams
- [x] Interface-only module code
- [x] 7 Epic tasks (within 6-8 CONDITION range) with complexity
- [x] Codebase Analysis (Serena) section included (Serena tool unavailable, direct file verification substituted, documented)
- [x] External Dependencies section with verified import paths
- [x] Total length < 500 lines
