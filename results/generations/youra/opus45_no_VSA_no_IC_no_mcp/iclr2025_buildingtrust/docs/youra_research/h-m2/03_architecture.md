# Architecture: h-m2 (Pareto-Optimal ECE Analysis)

**Type**: MECHANISM | **Gate**: SHOULD_WORK

Applied: statistical-hypothesis-test-pipeline (KB pattern: load -> derive groups -> compute metric -> Welch t-test -> effect size -> plot)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1 data) + reused module (h-m1 ece.py)
**Status**: Actual code read directly (Serena unavailable in this env; used Read tool on h-e1/code/config.py, h-e1/code/analysis.py, h-m1/code/config.py, h-m1/code/ece.py, h-e1/code/results/scores.csv)
**Analyzed Path**: `h-e1/code/`, `h-m1/code/`
**Findings**: h-e1 `config.py` has `MODELS` list (id/family/params), NOT `MODEL_PARAMS` dict. h-m1 `config.py` defines `MODEL_PARAMS` dict (model_id -> params) and `MODELS` list of ids — `ece.py::generate_synthetic_ece` does `from config import MODEL_PARAMS`, so h-m2 must provide a local `config.py` with `MODEL_PARAMS` (copy from h-m1, not h-e1). `scores.csv` columns verified: model, family, params, log_params, truthfulqa_mc1, advglue_avg (14 rows).

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| scores.csv (data) | `pd.read_csv(H_E1_SCORES)` | `h-e1/code/results/scores.csv` |
| ece.py (copied, not imported cross-dir) | `from ece import generate_synthetic_ece` | copy of `h-m1/code/ece.py` into `h-m2/code/ece.py` |

**Verified from**: `h-e1/code/` and `h-m1/code/` (actual implementation). h-m1's `ece.py` imports `from config import MODEL_PARAMS` (relative, same-dir) — cross-repo import won't work, so `ece.py` is copied verbatim into `h-m2/code/` alongside a local `config.py` containing `MODEL_PARAMS`.

## File Structure

```
h-m2/code/
  config.py       # paths, MODEL_PARAMS (copied from h-m1), thresholds
  pareto.py        # Pareto frontier dominance check
  ece.py            # copied verbatim from h-m1/code/ece.py
  analysis.py       # Welch t-test, Cohen's d, baselines
  visualize.py      # pareto scatter + ECE boxplot
  run.py            # orchestration
```

## Modules

### config.py (`h-m2/code/config.py`)

**Dependencies**: none

```python
H_E1_SCORES: Path        # = h-e1/code/results/scores.csv
OUTPUT_PATH: Path         # = h-m2/code/results
FIGURES_PATH: Path        # = h-m2/figures
SEED: int = 42
N_BINS: int = 15
MODEL_PARAMS: dict[str, int]   # copied from h-m1/code/config.py
P_THRESHOLD: float = 0.05
D_THRESHOLD: float = 0.5   # Cohen's d medium effect
```

### pareto.py (`h-m2/code/pareto.py`)

**Dependencies**: pandas

```python
def identify_pareto_optimal(df: pd.DataFrame, x_col: str = "truthfulqa_mc1", y_col: str = "advglue_avg") -> list[str]: ...
def label_pareto(df: pd.DataFrame, pareto_models: list[str]) -> pd.DataFrame: ...  # adds 'is_pareto' bool col
```

### ece.py (`h-m2/code/ece.py`)

**Dependencies**: numpy, config (MODEL_PARAMS)

Copied verbatim from `h-m1/code/ece.py`:
```python
def compute_ece(confidences: np.ndarray, predictions: np.ndarray, labels: np.ndarray, n_bins: int = 15) -> float: ...
def generate_synthetic_ece(model_id: str, seed: int = 42) -> float: ...
def compute_all_ece(models: list, seed: int = 42) -> dict: ...
```

### analysis.py (`h-m2/code/analysis.py`)

**Dependencies**: numpy, scipy.stats, pareto, ece

```python
def welch_ttest(pareto_ece: np.ndarray, non_pareto_ece: np.ndarray) -> dict: ...  # t, p, mean_pareto, mean_non_pareto
def cohens_d(a: np.ndarray, b: np.ndarray) -> float: ...
def random_split_baseline(df: pd.DataFrame, seed: int = 42) -> dict: ...
def size_matched_baseline(df: pd.DataFrame) -> dict: ...  # controls for log_params
def run_analysis(df: pd.DataFrame) -> dict: ...  # full pipeline, returns gate_passed bool
```

### visualize.py (`h-m2/code/visualize.py`)

**Dependencies**: matplotlib, pandas

```python
def plot_pareto_frontier(df: pd.DataFrame, pareto_models: list[str], out_path: Path) -> None: ...
def plot_ece_comparison(df: pd.DataFrame, out_path: Path) -> None: ...  # boxplot by is_pareto
```

### run.py (`h-m2/code/run.py`)

**Dependencies**: all above

```python
def main() -> dict: ...  # load -> pareto -> ece -> analysis -> plots -> save results json
```

## Codebase Analysis Note

Green-field for h-m2 code itself; base data/module fully verified via direct Read (Serena MCP tool not invoked — not available in this environment; Read tool used as substitute per fallback, findings equivalent).

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | config.py | Paths + MODEL_PARAMS (copy from h-m1) + thresholds | 5 | 1+1+1+2 |
| A-2 | pareto.py | O(n^2) dominance check + labeling | 8 | 2+1+3+2 |
| A-3 | ece.py | Copy h-m1 ece.py, adapt import | 4 | 1+1+1+1 |
| A-4 | analysis.py: welch_ttest + cohens_d | Core stat test | 7 | 2+2+2+1 |
| A-5 | analysis.py: baselines | Random-split + size-matched control | 9 | 2+2+3+2 |
| A-6 | analysis.py: run_analysis orchestrator | Combine group split, ECE, stats, gate verdict | 8 | 2+3+2+1 |
| A-7 | visualize.py | Pareto scatter + ECE boxplot | 7 | 2+1+2+2 |
| A-8 | run.py | Full pipeline orchestration + results JSON | 8 | 2+3+1+2 |
| A-9 | Integration test | Run end-to-end, verify N>=3/N>=5, runtime <30s | 6 | 1+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-5], Low(4-8): [A-1, A-3, A-4, A-6, A-7, A-8, A-9]
