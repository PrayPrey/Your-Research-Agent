# Architecture: h-m1

**Applied**: minimal-pipeline pattern (sequential statistical analysis, no training loop)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-e1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: h-e1 has 6 files with clean single-function modules. `data_loader.py` has `load_and_validate()` (read CSV, dropna, assert N≥200). `statistical_analysis.py` has `compute_vif`, `spearman_partial_corr`, `bootstrap_partial_corr`. `run_experiment.py` orchestrates via `main()`. h-m1 reuses data_loader wholesale and replaces statistical_analysis with OLS-based analysis.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_and_validate | `from h_e1.data_loader import load_and_validate` | `docs/youra_research/h-e1/code/data_loader.py` |
| compute_vif | `from h_e1.statistical_analysis import compute_vif` | `docs/youra_research/h-e1/code/statistical_analysis.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

**Note**: h-m1 code lives in `docs/youra_research/h-m1/code/`. To avoid cross-hypothesis imports (fragile paths), h-m1 will copy/inline the two reused functions rather than import from h-e1. This matches h-e1's pattern of self-contained files.

---

## File Organization

- `docs/youra_research/h-m1/code/`
  - `data_loader.py` — load + standardize (extends h-e1 version)
  - `ols_analysis.py` — VIF, baseline OLS, full OLS, diagnostics, permutation fallback
  - `visualizer.py` — 6 figures
  - `gate_evaluator.py` — dominance gate logic
  - `report_writer.py` — write 04_validation.md
  - `run_experiment.py` — orchestration entry point
- `docs/youra_research/h-m1/figures/` — output figures

---

## Modules

### DataLoader (`code/data_loader.py`)

**Dependencies**: pandas, sklearn.preprocessing.StandardScaler

```python
def load_and_validate(csv_path: str) -> pd.DataFrame:
    # Same as h-e1: read_csv, dropna, assert N>=200
    ...

def standardize(df: pd.DataFrame) -> pd.DataFrame:
    # Adds win_rate_std, avg_length_std columns via StandardScaler
    # Asserts mean~0, std~1 for each
    ...
```

---

### OLSAnalysis (`code/ols_analysis.py`)

**Dependencies**: statsmodels, sklearn, scipy, pandas, numpy

```python
def compute_vif(df: pd.DataFrame) -> dict:
    # Returns {win_rate: float, avg_length: float, any_high_vif: bool}
    # Replicates h-e1 compute_vif; uses standardized columns
    ...

def fit_baseline_ols(df: pd.DataFrame) -> dict:
    # OLS: LC_winrate ~ avg_length_std
    # Returns {beta_avg_length: float, r2: float, pvalue: float}
    ...

def fit_full_ols(df: pd.DataFrame) -> dict:
    # OLS: LC_winrate ~ win_rate_std + avg_length_std
    # Returns {beta_win: float, beta_len: float, p_win: float, p_len: float,
    #          r2: float, r2_adj: float, residuals: np.ndarray, fitted: np.ndarray}
    ...

def run_ols_diagnostics(ols_result: dict, df: pd.DataFrame) -> dict:
    # Breusch-Pagan test via statsmodels.stats.diagnostic.het_breuschpagan
    # Returns {bp_stat: float, bp_pvalue: float, heteroscedastic: bool}
    ...

def run_permutation_fallback(df: pd.DataFrame) -> dict:
    # sklearn LinearRegression + permutation_importance(n_repeats=30, random_state=42)
    # Returns {imp_win: float, imp_len: float}
    ...
```

---

### GateEvaluator (`code/gate_evaluator.py`)

**Dependencies**: None (pure logic)

```python
def evaluate_gate(ols_result: dict, vif: dict,
                  perm_result: dict | None = None) -> dict:
    # Selects OLS path (VIF<5) or permutation fallback (VIF>=5)
    # Returns {passes_gate: bool, path: str, beta_win: float, beta_len: float,
    #          p_win: float, dominant: str}
    ...
```

---

### Visualizer (`code/visualizer.py`)

**Dependencies**: matplotlib, seaborn, pandas, numpy

```python
def save_all_figures(df: pd.DataFrame, ols_result: dict,
                     vif: dict, gate_result: dict,
                     figures_dir: str) -> list[str]:
    # Generates all 6 figures, returns list of saved paths
    ...

def _dominance_bar(ols_result: dict, figures_dir: str) -> str: ...
def _coef_plot(ols_result: dict, figures_dir: str) -> str: ...
def _vif_bar(vif: dict, figures_dir: str) -> str: ...
def _residuals_vs_fitted(ols_result: dict, figures_dir: str) -> str: ...
def _qq_plot(ols_result: dict, figures_dir: str) -> str: ...
def _scatter_by_length_quartile(df: pd.DataFrame, figures_dir: str) -> str: ...
```

---

### ReportWriter (`code/report_writer.py`)

**Dependencies**: pathlib

```python
def write_validation_report(gate_result: dict, ols_result: dict,
                             baseline_result: dict, vif: dict,
                             diagnostics: dict, figure_paths: list[str],
                             output_path: str) -> None:
    # Writes 04_validation.md with gate, betas, R2, VIF, diagnostics, figure paths
    # Includes h-e1 comparison row (r_partial=0.9851)
    ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: all modules above

```python
# Constants
CSV_PATH: str       # docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv
FIGURES_DIR: str    # docs/youra_research/h-m1/figures/
OUTPUT_PATH: str    # docs/youra_research/h-m1/04_validation.md
RANDOM_STATE: int   # 42
ALPHA: float        # 0.05
VIF_THRESHOLD: float  # 5.0
N_MIN: int          # 200

def main() -> None:
    # 1. load_and_validate -> standardize
    # 2. compute_vif
    # 3. fit_baseline_ols
    # 4. fit_full_ols -> run_ols_diagnostics
    # 5. run_permutation_fallback (only if VIF >= 5)
    # 6. evaluate_gate
    # 7. save_all_figures
    # 8. write_validation_report
    # sys.exit(0 if passes_gate else 1)
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create directory structure, constants, requirements | 4 | 1+1+1+1 |
| A-2 | Data Loader | `load_and_validate` + `standardize` with assertions | 6 | 2+1+2+1 |
| A-3 | VIF Diagnostic | `compute_vif` on standardized columns | 5 | 1+2+1+1 |
| A-4 | Baseline OLS | `fit_baseline_ols` (verbosity-only null model) | 7 | 2+2+2+1 |
| A-5 | Full OLS | `fit_full_ols` with beta extraction, R², residuals | 9 | 2+2+3+2 |
| A-6 | OLS Diagnostics | Breusch-Pagan + residuals/fitted arrays | 8 | 2+2+3+1 |
| A-7 | Permutation Fallback | `run_permutation_fallback` (VIF>=5 path) | 7 | 2+2+2+1 |
| A-8 | Gate Evaluator | VIF-contingent dominance decision logic | 6 | 1+2+2+1 |
| A-9 | Visualizations | All 6 figures (dominance bar, coef plot, VIF bar, residuals, Q-Q, scatter) | 14 | 3+2+4+5 |
| A-10 | Report Writer | Write 04_validation.md with full results + h-e1 comparison | 8 | 2+1+3+2 |
| A-11 | Orchestration | `run_experiment.py` main(), integration test | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-9], Medium(9-13): [A-5, A-11], Low(4-8): [A-1, A-2, A-3, A-4, A-6, A-7, A-8, A-10]
