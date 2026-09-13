# H-M2 Architecture: Predictive Validity of Epistemic Composite for Adversarial Robustness

Applied: statistical-analysis-pipeline-reuse (BCa bootstrap partial Spearman + LOO-AUC from H-M1)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260430_buildingtrust/h-m1/code/`
**Findings**: H-M1 uses modular flat layout — `data_loader.py`, `analyzers.py`, `visualizer.py`, `reporter.py`, `config.py`, `main.py`. BCa bootstrap lives in `analyzers._bca_bootstrap_partial`. Score matrix loaded via `data_loader.load_score_matrix` using `config.REQUIRED_COLS`. H-M2 extends this by adding LOO logistic regression and ΔR² bootstrap to the analyzers layer.

---

## File Organization

- `h-m2/code/`
  - `run_experiment.py` — single-script orchestrator (< 500 lines)
  - `config.py` — all constants, paths, thresholds
  - `data_loader.py` — load + validate score matrix (reuse H-M1 pattern)
  - `analyzers.py` — partial corr, LOO logistic regression, delta AUC bootstrap
  - `visualizer.py` — 6 figures → `h-m2/figures/`
  - `reporter.py` — JSON results + validation markdown
  - `tests/` — unit tests per module
- `h-m2/figures/` — output figure directory
- `h-m2/results/` — JSON + markdown outputs

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_score_matrix | reimplement in h-m2/code/data_loader.py | h-m1/code/data_loader.py (pattern source) |
| validate_schema | reimplement in h-m2/code/data_loader.py | h-m1/code/data_loader.py |
| _bca_bootstrap_partial | reimplement in h-m2/code/analyzers.py | h-m1/code/analyzers.py (pattern source) |
| score_matrix.csv | `../h-e1/results/score_matrix.csv` | h-m1/code/config.py line 8 confirms path |

**Verified from**: `h-m1/code/` (actual implementation)
**Score matrix path pattern**: `os.path.join(_BASE, "h-e1", "results", "score_matrix.csv")` where `_BASE` = research folder containing both `h-e1/` and `h-m2/`.

---

## Module Definitions

### Config (`h-m2/code/config.py`)

**Dependencies**: none

```python
_CODE_DIR: str  # h-m2/code/
_HM2_DIR: str   # h-m2/
_BASE: str      # research folder (contains h-e1/, h-m1/, h-m2/)

SCORE_MATRIX_PATH: str     # _BASE/h-e1/results/score_matrix.csv
RESULTS_DIR: str           # _BASE/h-m2/results/
FIGURES_DIR: str           # _BASE/h-m2/figures/

N_BOOTSTRAP: int           # 10_000
BOOTSTRAP_SEED: int        # 42

COMPOSITE_COLS: list[str]  # ["ECE", "TruthfulQA_pct", "Brier"]
BASELINE_COLS: list[str]   # ["MMLU_acc"]
TARGET_COL: str            # "top_quartile_advglue"
PARTIAL_X: str             # "ECE"
PARTIAL_Y_ADV: str         # "AdvGLUE_drop"
PARTIAL_Y_ANLI: str        # "ANLI_drop"
COVARIATE: str             # "MMLU_acc"

REQUIRED_COLS: list[str]   # ["model_id","ECE","Brier","TruthfulQA_pct","AdvGLUE_drop","ANLI_drop","MMLU_acc","HumanEval_pass1"]
GATE_COLS: list[str]       # ["ECE","Brier","TruthfulQA_pct","AdvGLUE_drop","MMLU_acc"]
MIN_MODELS: int            # 25

AUC_THRESHOLD: float       # 0.70
DELTA_AUC_THRESHOLD: float # 0.10
PARTIAL_RHO_THRESHOLD: float # 0.40
ANLI_RHO_THRESHOLD: float  # 0.30

LR_C: float                # 1.0
LR_MAX_ITER: int           # 1000
TOP_QUARTILE: float        # 0.75

FIGURE_DPI: int            # 150
FIGURE_FORMAT: str         # "png"
FIGURE_NAMES: dict[str, str]
```

---

### DataLoader (`h-m2/code/data_loader.py`)

**Dependencies**: config

```python
def load_score_matrix(path: str) -> pd.DataFrame: ...
def validate_schema(df: pd.DataFrame, required_cols: list[str], gate_cols: list[str]) -> bool: ...
def add_top_quartile_label(df: pd.DataFrame, col: str, quantile: float) -> pd.DataFrame: ...
```

---

### Analyzers (`h-m2/code/analyzers.py`)

**Dependencies**: config

```python
def _bca_bootstrap_partial(
    df: pd.DataFrame, x: str, y: str, covar: str,
    n_boot: int, seed: int, alpha: float = 0.05,
) -> tuple[float, float]: ...

def compute_partial_rho_advglue(
    df: pd.DataFrame, n_boot: int, seed: int,
) -> dict: ...
# Returns: {rho_partial_advglue, bca_ci_low, bca_ci_high, ci_excludes_zero, passes_threshold,
#           rho_partial_anli, anli_bca_ci_low, anli_bca_ci_high}

def _run_loo_logistic(
    X: np.ndarray, y: np.ndarray, seed: int,
) -> np.ndarray: ...
# Returns: y_proba array of shape (N,)

def compute_loo_auc(
    df: pd.DataFrame, feature_cols: list[str], target_col: str, seed: int,
) -> dict: ...
# Returns: {auc, y_proba, y_true, feature_cols}

def compute_delta_auc_bootstrap(
    df: pd.DataFrame, composite_cols: list[str], baseline_cols: list[str],
    target_col: str, n_boot: int, seed: int,
) -> dict: ...
# Returns: {auc_composite, auc_baseline, delta_auc, delta_auc_ci, ci_excludes_zero,
#           passes_delta_threshold, passes_auc_threshold}

def evaluate_gate(auc_result: dict, delta_result: dict) -> bool: ...
# Returns True iff auc_composite >= AUC_THRESHOLD AND delta_auc >= DELTA_AUC_THRESHOLD AND ci_excludes_zero
```

---

### Visualizer (`h-m2/code/visualizer.py`)

**Dependencies**: config, analyzers output dicts

```python
def plot_auc_comparison_bar(
    delta_result: dict, auc_threshold: float, figures_dir: Path,
) -> None: ...
# fig1: LOO-AUC composite vs MMLU-only with CI error bars

def plot_partial_rho_comparison(
    partial_result: dict, hm1_partial_rho: float, figures_dir: Path,
) -> None: ...
# fig2: partial rho(ECE, AdvGLUE|MMLU), partial rho(ECE, ANLI|MMLU) vs H-M1 reference

def plot_roc_curves(
    composite_auc: dict, baseline_auc: dict, figures_dir: Path,
) -> None: ...
# fig3: ROC curve overlay for composite vs MMLU-only

def plot_advglue_distribution(
    df: pd.DataFrame, q75_threshold: float, figures_dir: Path,
) -> None: ...
# fig4: histogram of AdvGLUE_drop with top-quartile threshold line

def plot_feature_importance(
    df: pd.DataFrame, composite_cols: list[str], target_col: str,
    seed: int, figures_dir: Path,
) -> None: ...
# fig5: standardized LOO logistic regression coefficients with variability

def plot_composite_scatter(
    df: pd.DataFrame, figures_dir: Path,
) -> None: ...
# fig6: composite epistemic score (PC1 proxy) vs AdvGLUE_drop scatter
```

---

### Reporter (`h-m2/code/reporter.py`)

**Dependencies**: config

```python
def write_results_json(
    partial_result: dict,
    composite_auc: dict,
    baseline_auc: dict,
    delta_result: dict,
    gate_pass: bool,
    path: Path,
) -> None: ...

def write_validation_md(
    partial_result: dict,
    composite_auc: dict,
    baseline_auc: dict,
    delta_result: dict,
    gate_pass: bool,
    path: Path,
) -> None: ...
```

---

### RunExperiment (`h-m2/code/run_experiment.py`)

**Dependencies**: config, data_loader, analyzers, visualizer, reporter

```python
def main() -> dict: ...
# Orchestrates: load → partial_rho → loo_auc_composite → loo_auc_baseline →
#               delta_bootstrap → gate_eval → visualize (6 figs) → report
# Returns: {"PASS": bool, "partial_result": dict, "composite_auc": dict,
#           "baseline_auc": dict, "delta_result": dict}

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result["PASS"] else 1)
```

---

## Data Flow

- `config.SCORE_MATRIX_PATH` → `data_loader.load_score_matrix` → `df` (N=30 × 8)
- `data_loader.add_top_quartile_label(df, "AdvGLUE_drop", 0.75)` → `df` with `top_quartile_advglue`
- `analyzers.compute_partial_rho_advglue(df)` → `partial_result`
- `analyzers.compute_loo_auc(df, COMPOSITE_COLS, TARGET_COL)` → `composite_auc`
- `analyzers.compute_loo_auc(df, BASELINE_COLS, TARGET_COL)` → `baseline_auc`
- `analyzers.compute_delta_auc_bootstrap(df, ...)` → `delta_result`
- `analyzers.evaluate_gate(composite_auc, delta_result)` → `gate_pass`
- `visualizer.*` → 6 PNG files in `h-m2/figures/`
- `reporter.*` → `h-m2/results/hm2_results.json` + `h-m2/04_validation.md`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | File structure, config.py, requirements.txt, figures/results dirs | 5 | 1+1+1+2 |
| A-2 | Data Loader | load_score_matrix + validate_schema + add_top_quartile_label | 6 | 2+1+1+2 |
| A-3 | Partial Rho Analyzers | compute_partial_rho_advglue (primary + ANLI) + BCa CI (reuse H-M1 _bca_bootstrap_partial pattern) | 10 | 3+2+3+2 |
| A-4 | LOO Logistic Regression | _run_loo_logistic + compute_loo_auc for composite and baseline predictors | 11 | 3+2+3+3 |
| A-5 | Delta AUC Bootstrap | compute_delta_auc_bootstrap (10k resamples, nested LOO) + evaluate_gate | 13 | 3+3+4+3 |
| A-6 | Visualizer — AUC Figures | plot_auc_comparison_bar + plot_roc_curves + plot_advglue_distribution | 9 | 2+2+3+2 |
| A-7 | Visualizer — Correlation + Feature Figures | plot_partial_rho_comparison + plot_feature_importance + plot_composite_scatter | 10 | 2+2+3+3 |
| A-8 | Reporter | write_results_json + write_validation_md with gate pass/fail formatting | 7 | 2+1+2+2 |
| A-9 | Orchestrator | run_experiment.py main() wiring all modules, logging, sys.exit gate | 8 | 2+2+2+2 |
| A-10 | Tests | Unit tests for data_loader, analyzers, reporter; smoke test run_experiment | 9 | 2+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4, A-5, A-6, A-7, A-10], Low(4-8): [A-1, A-2, A-8, A-9]

**Total subtask budget**: 88 (within 30-task-per-epic limit when broken down per epic)

---

## Gate Logic

```
PASS = (
    abs(partial_rho_advglue) >= 0.40 AND ci_excludes_zero  [secondary, informative]
    AND auc_composite >= 0.70                               [primary gate 1]
    AND delta_auc >= 0.10 AND delta_auc_ci[0] > 0          [primary gate 2]
)
PARTIAL = 0.60 <= auc_composite < 0.70 OR 0.05 <= delta_auc < 0.10
EXPLORE = auc_composite < 0.60 OR delta_auc_ci includes zero
→ Proceed to H-M3 in all cases
```
