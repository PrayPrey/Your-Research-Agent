# Logic: h-m2 (Residual Capability Signal Confirmation)

Applied: residual-based partial correlation via lstsq (pgmpy/python-fiddle pattern)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental on h-e1 and h-m1)
**Status**: API signatures verified from actual base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`, `docs/youra_research/h-m1/code/`
**Relevant Symbols** (verified from actual files):
- `load_and_validate(csv_path: str) -> pd.DataFrame` — h-e1/code/data_loader.py
- `bootstrap_partial_corr(df, n_bootstrap, random_state) -> (float, float, list)` — h-e1/code/statistical_analysis.py; uses `rng.choice`, NOT `rng.integers`
- `evaluate_gate(r_partial, p_val, boot_ci_lower) -> dict` — h-e1/code/gate_evaluator.py; gate checks `abs(r_partial) >= 0.15`
- `write_validation_report(gate_result, corr_result, boot_ci, vif, figure_paths, output_path)` — h-e1/code/report_writer.py
- `save_all_figures(df, boot_rs, vif, corr_result, output_dir) -> list` — h-e1/code/visualizer.py

**Note**: h-m2 copies data_loader.py unchanged. All other modules are new. No runtime imports from h-e1/h-m1.

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: docs/youra_research/h-e1/code/data_loader.py (ACTUAL CODE)
def load_and_validate(csv_path: str) -> pd.DataFrame:
    # pd.read_csv(csv_path, index_col=0)
    # dropna on ['win_rate', 'length_controlled_winrate', 'avg_length']
    # assert len(df) >= 200
    ...

# From: docs/youra_research/h-e1/code/statistical_analysis.py (ACTUAL CODE)
def bootstrap_partial_corr(
    df: pd.DataFrame,
    n_bootstrap: int = 1000,
    random_state: int = 42,
) -> tuple[float, float, list]:
    """Returns: (ci_lower, ci_upper, boot_rs_list). Uses rng.choice NOT rng.integers."""
    ...

# From: docs/youra_research/h-e1/code/gate_evaluator.py (ACTUAL CODE)
def evaluate_gate(
    r_partial: float,   # ← param name is r_partial, NOT rho
    p_val: float,       # ← param name is p_val, NOT p_value
    boot_ci_lower: float,
) -> dict:
    # Gate: r_partial > 0 AND p_val < 0.05 AND abs(r_partial) >= 0.15
    # Returns: {passes_gate, r_partial, p_val, boot_ci_lower, r_threshold, alpha}
    ...
```

**Verified from**: actual implementation in `docs/youra_research/h-e1/code/` (NOT specs)

**CRITICAL**: h-m2 defines its OWN `evaluate_gate` with different gate logic (CI-based, not r_threshold). Do NOT reuse h-e1's gate_evaluator.py.

---

## A-2: Data Pipeline [Complexity: 5]

**Applied**: Standard — copy verbatim from h-e1.

### API Signatures

```python
# data_loader.py — copied from h-e1/code/data_loader.py unchanged
def load_and_validate(csv_path: str) -> pd.DataFrame:
    """Load CSV, dropna on 3 cols, assert N>=200. index_col=0."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Copy data_loader.py | cp from h-e1; verify import works in h-m2/code/ |

---

## A-3: OLS Residualization [Complexity: 9]

**Applied**: lstsq residualization (pgmpy.ci_tests.pearsonr, python-fiddle pattern)

### API Signatures

```python
# residualizer.py
import numpy as np
import pandas as pd


def regress_out(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, float]:
    """OLS-regress x out of y. Returns (residuals [N,], r_squared)."""
    ...


def compute_residuals(df: pd.DataFrame) -> dict:
    """
    Regress avg_length out of win_rate and length_controlled_winrate.
    Returns: {win_rate_resid [N,], lc_resid [N,], r2_win, r2_lc, n}
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | regress_out() | lstsq with intercept; compute R²; guard ss_tot==0 |
| L-3-2 | compute_residuals() | Call regress_out twice; print R²; return dict |

### L-3-1: regress_out() full implementation

```python
def regress_out(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, float]:
    """OLS-regress x out of y. Returns (residuals [N,], r_squared)."""
    X_mat = np.column_stack([np.ones(len(x)), x])          # [N, 2]
    coefs = np.linalg.lstsq(X_mat, y, rcond=None)[0]       # [2,]
    residuals = y - X_mat @ coefs                           # [N,]
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return residuals, float(r_squared)
```

### L-3-2: compute_residuals() full implementation

```python
def compute_residuals(df: pd.DataFrame) -> dict:
    avg_len = df['avg_length'].values                              # [N,]
    win_resid, r2_win = regress_out(df['win_rate'].values, avg_len)
    lc_resid,  r2_lc  = regress_out(df['length_controlled_winrate'].values, avg_len)
    print(f"R²(win_rate ~ avg_length) = {r2_win:.4f}")
    print(f"R²(lc_winrate ~ avg_length) = {r2_lc:.4f}")
    return {
        'win_rate_resid': win_resid,   # [N,]
        'lc_resid':       lc_resid,    # [N,]
        'r2_win':         r2_win,
        'r2_lc':          r2_lc,
        'n':              len(avg_len),
    }
```

---

## A-4: Spearman + Bootstrap [Complexity: 10]

**Applied**: h-e1 bootstrap pattern (rng.choice, percentile CI)

### API Signatures

```python
# spearman_analysis.py
import numpy as np
import pandas as pd
import pingouin
from scipy import stats

H_E1_R_PARTIAL: float = 0.9851


def spearman_residuals(
    win_resid: np.ndarray,   # [N,]
    lc_resid: np.ndarray,    # [N,]
) -> dict:
    """Returns: {rho: float, p_value: float}"""
    ...


def bootstrap_spearman(
    win_resid: np.ndarray,   # [N,]
    lc_resid: np.ndarray,    # [N,]
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> tuple[float, float, np.ndarray]:
    """Returns: (ci_lower, ci_upper, boot_rhos [n_bootstrap,])"""
    ...


def fwl_consistency_check(
    rho: float,
    h_e1_r_partial: float = H_E1_R_PARTIAL,
) -> dict:
    """Returns: {fwl_delta: float, fwl_consistent: bool}"""
    ...


def pingouin_cross_validate(df: pd.DataFrame) -> dict:
    """Returns: {pingouin_r: float, pingouin_p: float}"""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | bootstrap_spearman() | rng.choice bootstrap; percentile CI; return ndarray |
| L-4-2 | spearman_residuals() + fwl_consistency_check() + pingouin_cross_validate() | Full implementations with exact return dicts |

### L-4-1: bootstrap_spearman() full implementation

```python
def bootstrap_spearman(
    win_resid: np.ndarray,
    lc_resid: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> tuple[float, float, np.ndarray]:
    rng = np.random.default_rng(seed)
    n = len(win_resid)
    boot_rhos = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        idx = rng.choice(n, size=n, replace=True)            # [N,] — matches h-e1 pattern
        boot_rhos[i] = stats.spearmanr(win_resid[idx], lc_resid[idx])[0]
    ci_lower = float(np.percentile(boot_rhos, 2.5))
    ci_upper = float(np.percentile(boot_rhos, 97.5))
    return ci_lower, ci_upper, boot_rhos                     # boot_rhos: [1000,]
```

### L-4-2: Remaining spearman_analysis.py functions

```python
def spearman_residuals(win_resid: np.ndarray, lc_resid: np.ndarray) -> dict:
    rho, p_value = stats.spearmanr(win_resid, lc_resid)
    return {'rho': float(rho), 'p_value': float(p_value)}


def fwl_consistency_check(rho: float, h_e1_r_partial: float = H_E1_R_PARTIAL) -> dict:
    fwl_delta = abs(rho - h_e1_r_partial)
    return {'fwl_delta': float(fwl_delta), 'fwl_consistent': bool(fwl_delta < 0.02)}


def pingouin_cross_validate(df: pd.DataFrame) -> dict:
    result = pingouin.partial_corr(
        data=df,
        x='win_rate',
        y='length_controlled_winrate',
        covar='avg_length',
        method='spearman',
    )
    return {
        'pingouin_r': float(result['r'].iloc[0]),
        'pingouin_p': float(result['p-val'].iloc[0]),
    }
```

---

## A-5: FWL + Pingouin Checks [Complexity: 8]

Functions live in `spearman_analysis.py` — see A-4 L-4-2. No separate module.

---

## A-6: Gate Evaluator [Complexity: 6]

**Applied**: Standard — new gate logic for h-m2 (CI-based, not r_threshold-based).

### API Signatures

```python
# gate_evaluator.py
def evaluate_gate(
    rho: float,
    p_value: float,
    ci_lower: float,
    fwl_delta: float,
) -> dict:
    """
    Gate: rho > 0 AND p_value < 0.05 AND ci_lower > 0.
    Returns: {passes_gate, fwl_consistent, gate_reason}
    """
    passes_gate = (rho > 0) and (p_value < 0.05) and (ci_lower > 0)
    fwl_consistent = (fwl_delta < 0.02)
    if passes_gate:
        gate_reason = f"rho={rho:.4f}>0, p={p_value:.2e}<0.05, CI_lower={ci_lower:.4f}>0"
    else:
        parts = []
        if rho <= 0:
            parts.append(f"rho={rho:.4f}<=0")
        if p_value >= 0.05:
            parts.append(f"p={p_value:.4f}>=0.05")
        if ci_lower <= 0:
            parts.append(f"CI_lower={ci_lower:.4f}<=0")
        gate_reason = "FAILED: " + "; ".join(parts)
    return {
        'passes_gate':    passes_gate,
        'fwl_consistent': fwl_consistent,
        'gate_reason':    gate_reason,
    }
```

---

## A-7: Visualization Suite [Complexity: 12]

**Applied**: matplotlib/statsmodels pattern from h-e1/code/visualizer.py

### API Signatures

```python
# visualizer.py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from pathlib import Path

H_E1_R_PARTIAL: float = 0.9851


def save_all_figures(
    df: pd.DataFrame,
    win_resid: np.ndarray,       # [N,]
    lc_resid: np.ndarray,        # [N,]
    boot_rhos: np.ndarray,       # [1000,]
    rho: float,
    ci: tuple[float, float],
    fwl_delta: float,
    figures_dir: str,
) -> list[str]:
    """Save 5 figures; return list of absolute file paths."""
    ...


def _residuals_scatter(
    win_resid: np.ndarray,  # [N,]
    lc_resid: np.ndarray,   # [N,]
    rho: float,
    out_path: str,
) -> str: ...


def _residual_distributions(
    win_resid: np.ndarray,  # [N,]
    lc_resid: np.ndarray,   # [N,]
    out_path: str,
) -> str: ...


def _partial_regression(df: pd.DataFrame, out_path: str) -> str: ...


def _fwl_consistency(
    rho: float,
    h_e1_r_partial: float,
    fwl_delta: float,
    out_path: str,
) -> str: ...


def _bootstrap_distribution(
    boot_rhos: np.ndarray,  # [1000,]
    ci: tuple[float, float],
    out_path: str,
) -> str: ...
```

### Subtasks [5/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | save_all_figures() | Dispatcher; mkdir; call 5 private functions; return paths |
| L-7-2 | _residuals_scatter() | scatter + polyfit line + rho/N annotation |
| L-7-3 | _residual_distributions() | subplots(1,2) histograms of both residuals |
| L-7-4 | _partial_regression() | sm.OLS residuals for both vars; scatter + polyfit line |
| L-7-5 | _fwl_consistency() + _bootstrap_distribution() | bar comparison; bootstrap hist with CI and null vlines |

### L-7-1: save_all_figures() implementation

```python
def save_all_figures(df, win_resid, lc_resid, boot_rhos, rho, ci, fwl_delta, figures_dir) -> list[str]:
    d = Path(figures_dir)
    d.mkdir(parents=True, exist_ok=True)
    return [
        _residuals_scatter(win_resid, lc_resid, rho, str(d / 'fig1_residuals_scatter.png')),
        _residual_distributions(win_resid, lc_resid, str(d / 'fig2_residual_distributions.png')),
        _partial_regression(df, str(d / 'fig3_partial_regression.png')),
        _fwl_consistency(rho, H_E1_R_PARTIAL, fwl_delta, str(d / 'fig4_fwl_consistency.png')),
        _bootstrap_distribution(boot_rhos, ci, str(d / 'fig5_bootstrap_distribution.png')),
    ]
```

### L-7-2 through L-7-5: Implementation notes

```
_residuals_scatter:
  scatter(win_resid, lc_resid, alpha=0.5, s=20)
  m, b = np.polyfit(win_resid, lc_resid, 1)
  ax.plot(x_line, m*x_line+b, color='tomato')
  ax.annotate(f"Spearman ρ={rho:.4f}\nN={len(win_resid)}", xy=(0.05,0.90), xycoords='axes fraction')
  xlabel='win_rate residual | avg_length', ylabel='LC_winrate residual | avg_length'

_residual_distributions:
  fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
  ax1.hist(win_resid, bins=30); ax2.hist(lc_resid, bins=30)
  titles: 'win_rate Residuals', 'LC_winrate Residuals'

_partial_regression:
  X_ctrl = sm.add_constant(df['avg_length'])
  resid_win = sm.OLS(df['win_rate'], X_ctrl).fit().resid
  resid_lc  = sm.OLS(df['length_controlled_winrate'], X_ctrl).fit().resid
  scatter(resid_win, resid_lc) + polyfit line
  (same approach as h-e1 visualizer._partial_regression)

_fwl_consistency:
  ax.bar(['H-E1 r_partial', 'H-M2 ρ'], [h_e1_r_partial, rho], color=['steelblue','tomato'])
  ax.axhspan(h_e1_r_partial-0.02, h_e1_r_partial+0.02, alpha=0.15, label='±0.02 tolerance')
  ax.annotate(f"Δ={fwl_delta:.4f}")

_bootstrap_distribution:
  ax.hist(boot_rhos, bins=40, color='steelblue', alpha=0.7)
  ax.axvline(ci[0], color='tomato', linestyle='--', label=f'95% CI [{ci[0]:.3f}, {ci[1]:.3f}]')
  ax.axvline(ci[1], color='tomato', linestyle='--')
  ax.axvline(0.0, color='black', lw=0.8, label='null ρ=0')
  ax.axvline(rho, color='gold', lw=2, label=f'ρ={rho:.4f}')
```

---

## A-8: Report Writer + Orchestrator [Complexity: 9]

**Applied**: h-e1 write_validation_report pattern (pathlib.Path.write_text, markdown tables)

### API Signatures

```python
# report_writer.py
from pathlib import Path


def write_validation_report(
    gate_result: dict,         # {passes_gate, fwl_consistent, gate_reason}
    rho: float,
    p_value: float,
    ci: tuple[float, float],
    fwl_result: dict,          # {fwl_delta, fwl_consistent}
    pingouin_result: dict,     # {pingouin_r, pingouin_p}
    residual_stats: dict,      # {r2_win, r2_lc, n}
    figure_paths: list[str],
    output_path: str,
) -> None:
    """Write 04_validation.md. Uses Path(output_path).parent.mkdir + write_text."""
    ...
```

```python
# run_experiment.py
import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../..'))
os.chdir(project_root)

CSV_PATH       = 'docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv'
FIGURES_DIR    = 'docs/youra_research/h-m2/figures'
OUTPUT_PATH    = 'docs/youra_research/h-m2/04_validation.md'
N_BOOTSTRAP    = 1000
RANDOM_STATE   = 42
ALPHA          = 0.05
H_E1_R_PARTIAL = 0.9851

from data_loader       import load_and_validate
from residualizer      import compute_residuals
from spearman_analysis import (spearman_residuals, bootstrap_spearman,
                               fwl_consistency_check, pingouin_cross_validate)
from gate_evaluator    import evaluate_gate
from visualizer        import save_all_figures
from report_writer     import write_validation_report


def main() -> None: ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | main() + write_validation_report() | Full orchestration pseudo-code + report markdown structure |

### L-8-1: main() pseudo-code

```
1. df = load_and_validate(CSV_PATH)
   print(f"N_clean = {len(df)}")

2. resid = compute_residuals(df)
   # prints R² for both regressions internally

3. corr = spearman_residuals(resid['win_rate_resid'], resid['lc_resid'])
   rho, p_value = corr['rho'], corr['p_value']
   print(f"Spearman ρ={rho:.4f}, p={p_value:.4e}")

4. ci_lower, ci_upper, boot_rhos = bootstrap_spearman(
       resid['win_rate_resid'], resid['lc_resid'], N_BOOTSTRAP, RANDOM_STATE)
   print(f"Bootstrap 95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")

5. fwl = fwl_consistency_check(rho, H_E1_R_PARTIAL)
   print(f"FWL delta={fwl['fwl_delta']:.4f}, consistent={fwl['fwl_consistent']}")

6. pg = pingouin_cross_validate(df)
   print(f"Pingouin r={pg['pingouin_r']:.4f}")

7. gate = evaluate_gate(rho, p_value, ci_lower, fwl['fwl_delta'])
   print(f"Gate: {'PASS' if gate['passes_gate'] else 'FAIL'} — {gate['gate_reason']}")

8. figure_paths = save_all_figures(
       df, resid['win_rate_resid'], resid['lc_resid'], boot_rhos,
       rho, (ci_lower, ci_upper), fwl['fwl_delta'], FIGURES_DIR)
   print(f"Figures saved: {len(figure_paths)}")

9. write_validation_report(
       gate, rho, p_value, (ci_lower, ci_upper),
       fwl, pg, resid, figure_paths, OUTPUT_PATH)
   print(f"Report written: {OUTPUT_PATH}")

10. sys.exit(0 if gate['passes_gate'] else 1)
```

---

## Data Shapes Reference

| Variable | Shape | Note |
|----------|-------|------|
| df | (N, ≥3) | N = 222-223 after dropna |
| avg_len / win / lc | (N,) | raw column .values |
| X_mat (design matrix) | (N, 2) | [ones, avg_length] — input to lstsq |
| coefs | (2,) | lstsq solution [intercept, slope] |
| win_rate_resid, lc_resid | (N,) | orthogonal to avg_length by construction |
| boot_rhos | (1000,) | n_bootstrap Spearman samples |
| ci | scalar tuple (2,) | (ci_lower, ci_upper) from percentile |
