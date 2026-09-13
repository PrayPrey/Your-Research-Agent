# Architecture: h-m2 (Residual Capability Signal)

Applied: residual-based partial correlation pattern (FWL theorem, lstsq residualization)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental on h-e1 and h-m1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`, `docs/youra_research/h-m1/code/`
**Findings**: h-e1 uses 6-module structure (data_loader, statistical_analysis, gate_evaluator, visualizer, report_writer, run_experiment). h-m1 follows identical pattern, adding ols_analysis.py. Both share `load_and_validate()` with same signature. h-m2 adds `residualizer.py` into the same flat-file structure.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Function | File Location |
|--------|----------|---------------|
| load_and_validate | `from data_loader import load_and_validate` | `h-e1/code/data_loader.py` |
| compute_vif | `from statistical_analysis import compute_vif` | `h-e1/code/statistical_analysis.py` |
| bootstrap_partial_corr | `from statistical_analysis import bootstrap_partial_corr` | `h-e1/code/statistical_analysis.py` |
| evaluate_gate | `from gate_evaluator import evaluate_gate` | `h-e1/code/gate_evaluator.py` |
| write_validation_report | `from report_writer import write_validation_report` | `h-e1/code/report_writer.py` |

**Verified from**: `docs/youra_research/h-e1/code/` and `docs/youra_research/h-m1/code/` (actual implementation)

**Note**: h-m2 does NOT import from h-e1/h-m1 directly. It copies the reusable modules and adds new ones. Same pattern as h-m1 did relative to h-e1.

---

## File Organization

```
docs/youra_research/h-m2/code/
├── data_loader.py        # copied from h-e1 (load_and_validate unchanged)
├── residualizer.py       # NEW — core h-m2 OLS residualization
├── spearman_analysis.py  # NEW — Spearman on residuals + bootstrap + FWL + pingouin check
├── gate_evaluator.py     # adapted from h-e1 (new gate thresholds)
├── visualizer.py         # NEW — 5 required figures
├── report_writer.py      # adapted from h-e1 (new fields)
└── run_experiment.py     # orchestrator

docs/youra_research/h-m2/figures/   # output dir for 5 figures
docs/youra_research/h-m2/04_validation.md  # output report
```

---

## Module Definitions

### DataLoader (`code/data_loader.py`)

**Dependencies**: pandas

**Copied from h-e1 unchanged** — same function signature, same logic.

```python
def load_and_validate(csv_path: str) -> pd.DataFrame: ...
# loads CSV, dropna on ['win_rate','length_controlled_winrate','avg_length'], asserts N>=200
```

---

### Residualizer (`code/residualizer.py`)

**Dependencies**: numpy, pandas

```python
def regress_out(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, float]:
    """OLS residualization. Returns (residuals, r_squared)."""
    ...

def compute_residuals(df: pd.DataFrame) -> dict:
    """
    Regress avg_length out of win_rate and length_controlled_winrate.
    Returns dict with keys:
      win_rate_resid, lc_resid,
      r2_win, r2_lc  (R² of each preliminary regression)
    """
    ...
```

---

### SpearmanAnalysis (`code/spearman_analysis.py`)

**Dependencies**: numpy, scipy.stats, pingouin, Residualizer output

```python
def spearman_residuals(win_resid: np.ndarray, lc_resid: np.ndarray) -> dict:
    """
    Returns: {rho, p_value}
    """
    ...

def bootstrap_spearman(
    win_resid: np.ndarray,
    lc_resid: np.ndarray,
    n_bootstrap: int,
    seed: int,
) -> tuple[float, float, np.ndarray]:
    """
    Returns: (ci_lower, ci_upper, boot_rhos)
    """
    ...

def fwl_consistency_check(rho: float, h_e1_r_partial: float = 0.9851) -> dict:
    """
    Returns: {fwl_delta, fwl_consistent}
    """
    ...

def pingouin_cross_validate(df: pd.DataFrame) -> dict:
    """
    pingouin.partial_corr(x='win_rate', y='length_controlled_winrate', covar='avg_length')
    Returns: {pingouin_r, pingouin_p, consistent_with_residual}
    """
    ...
```

---

### GateEvaluator (`code/gate_evaluator.py`)

**Dependencies**: none

```python
def evaluate_gate(
    rho: float,
    p_value: float,
    ci_lower: float,
    fwl_delta: float,
) -> dict:
    """
    Returns: {passes_gate, fwl_consistent, gate_reason}
    Gate: rho > 0 AND p_value < 0.05 AND ci_lower > 0
    Consistency: fwl_delta < 0.02
    """
    ...
```

---

### Visualizer (`code/visualizer.py`)

**Dependencies**: matplotlib, seaborn, statsmodels, numpy

```python
def save_all_figures(
    df: pd.DataFrame,
    win_resid: np.ndarray,
    lc_resid: np.ndarray,
    boot_rhos: np.ndarray,
    rho: float,
    ci: tuple[float, float],
    fwl_delta: float,
    figures_dir: str,
) -> list[str]:
    """
    Saves 5 figures; returns list of file paths.
    Figures:
      1. residuals_scatter.png
      2. residual_distributions.png
      3. partial_regression.png
      4. fwl_consistency.png
      5. bootstrap_distribution.png
    """
    ...

def _residuals_scatter(win_resid, lc_resid, rho, out_path): ...
def _residual_distributions(win_resid, lc_resid, out_path): ...
def _partial_regression(df, out_path): ...
def _fwl_consistency(rho, h_e1_r_partial, fwl_delta, out_path): ...
def _bootstrap_distribution(boot_rhos, ci, out_path): ...
```

---

### ReportWriter (`code/report_writer.py`)

**Dependencies**: pathlib

```python
def write_validation_report(
    gate_result: dict,
    rho: float,
    p_value: float,
    ci: tuple[float, float],
    fwl_result: dict,
    pingouin_result: dict,
    residual_stats: dict,
    figure_paths: list[str],
    output_path: str,
) -> None:
    """Writes 04_validation.md."""
    ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: all modules above

```python
# Constants
CSV_PATH: str       # docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv
FIGURES_DIR: str    # docs/youra_research/h-m2/figures/
OUTPUT_PATH: str    # docs/youra_research/h-m2/04_validation.md
N_BOOTSTRAP: int    # 1000
RANDOM_STATE: int   # 42
ALPHA: float        # 0.05
H_E1_R_PARTIAL: float  # 0.9851

def main() -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Verify deps installed (numpy, scipy, statsmodels, pingouin, matplotlib, seaborn), create figures/ dir, confirm CSV present | 4 | 1+1+1+1 |
| A-2 | Data Pipeline | Copy h-e1 data_loader.py, verify load_and_validate works on CSV, assert N>=200 | 5 | 1+1+1+2 |
| A-3 | OLS Residualization | Implement residualizer.py: regress_out() via lstsq, compute_residuals() for both variables, log R² | 9 | 2+2+3+2 |
| A-4 | Spearman + Bootstrap | Implement spearman_analysis.py: spearman_residuals(), bootstrap_spearman(n=1000, seed=42), return rho/p/CI | 10 | 2+2+3+3 |
| A-5 | FWL + Pingouin Checks | Implement fwl_consistency_check() and pingouin_cross_validate(); verify |Δ|<0.02 | 8 | 2+2+2+2 |
| A-6 | Gate Evaluator | Implement evaluate_gate(): rho>0 AND p<0.05 AND CI excludes 0; FWL flag | 6 | 1+1+2+2 |
| A-7 | Visualization Suite | Implement all 5 figures in visualizer.py; save to figures/ | 12 | 3+2+4+3 |
| A-8 | Report Writer + Orchestrator | Implement report_writer.py (04_validation.md) and run_experiment.py main(); end-to-end run | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4, A-7, A-8], Low(4-8): [A-1, A-2, A-5, A-6]
