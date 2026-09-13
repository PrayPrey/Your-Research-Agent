# Architecture: H-M5 (MECHANISM Validation)

**Hypothesis:** Concentration-diversity cycle reinforces itself via positive feedback loop (HHI_{t-1} → Entropy_t, tested via lagged panel FE regression + Granger causality).

Applied: no relevant KB pattern found (searched "panel regression fixed effects econometrics" — top hit similarity 0.33, unrelated diffusion-model repos); reused H-M4's file-split pattern (data_loader → analyze → visualize) extended with lag construction, PanelOLS FE, and Granger tests.

---

## Codebase Analysis (Serena)

**Project Type**: green-field (no base_hypothesis code reuse — H-M5 uses H-E1 data only, not H-M4 code)
**Status**: `h-m5/code/` does not exist; `h-m4/code/` also does not exist (H-M4 unimplemented, spec-only). No importable modules.
**Analyzed Path**: `h-m5/code/`, `h-m4/code/` (both absent)
**Findings**: Green-field project — no existing code to analyze. Following H-M4's architecture *spec* structurally (data_loader/analyze/visualize split) since it establishes the project convention, but no code import.

---

## File Structure (Minimal — statistical analysis, not a training pipeline)

```
h-m5/code/
├── data_loader.py   # Load H-E1 panel CSV, set MultiIndex, construct lags
├── models.py          # Pooled OLS baseline, PanelOLS 2-way FE, robustness variants
├── granger.py         # Per-venue Granger causality tests, both directions
├── analyze.py          # entrypoint: run models, gate check, save results
└── visualize.py         # required + additional figures
```

Single entrypoint (`analyze.py`), no config.py (constants: VENUES, LAG, SEED live in data_loader.py).

---

## Modules

### data_loader.py

**Dependencies**: pandas

```python
E1_DATA_PATH = "docs/youra_research/h-e1/data/venue_year_metrics.csv"

def load_panel_data(path: str = E1_DATA_PATH) -> pd.DataFrame:
    """Load H-E1 CSV, set MultiIndex (venue, year), sort index.
    Returns DataFrame[hhi, entropy, paper_count] indexed by (venue, year)."""
    ...

def add_lags(df: pd.DataFrame, lag: int = 1) -> pd.DataFrame:
    """Groupby venue, shift hhi/entropy by `lag` -> hhi_lag{lag}, entropy_lag{lag}.
    Also adds delta_hhi, delta_entropy (diff by venue). Does NOT drop NaN."""
    ...

def prepare_analysis_df(df: pd.DataFrame, lag: int = 1) -> pd.DataFrame:
    """add_lags then dropna() (drops first `lag` years per venue).
    Returns clean panel ready for PanelOLS."""
    ...
```

### models.py

**Dependencies**: linearmodels.panel (PooledOLS, PanelOLS), statsmodels.api

```python
def fit_baseline(df: pd.DataFrame, hhi_col: str = "hhi_lag1") -> dict:
    """Pooled OLS: entropy ~ const + hhi_lag1 + paper_count, no FE.
    Returns {beta, p_value, r_squared, conf_int}."""
    ...

def fit_panel_fe(
    df: pd.DataFrame, hhi_col: str = "hhi_lag1",
    entity_effects: bool = True, time_effects: bool = True,
) -> dict:
    """PanelOLS(entropy ~ const + hhi_col + paper_count, entity_effects, time_effects),
    cov_type='clustered', cluster_entity=True.
    Returns {beta, p_value, conf_int_lower, conf_int_upper, r_squared, n_obs, results_obj}."""
    ...

def fit_delta_spec(df: pd.DataFrame) -> dict:
    """Delta robustness: delta_entropy ~ const + delta_hhi_lag1 (Pooled OLS on diffs).
    Returns same dict shape as fit_baseline."""
    ...

def run_robustness_suite(df_lag1: pd.DataFrame, df_lag2: pd.DataFrame) -> dict:
    """Runs: (a) fit_panel_fe with lag2 col, (b) fit_panel_fe(time_effects=False),
    (c) fit_delta_spec. Returns {lag2, entity_only, delta_spec}."""
    ...
```

### granger.py

**Dependencies**: statsmodels.tsa.stattools.grangercausalitytests

```python
def granger_per_venue(
    df: pd.DataFrame, cause: str, effect: str, maxlag: int = 2, min_obs: int = 4
) -> dict[str, dict[int, float]]:
    """For each venue with >= min_obs rows: grangercausalitytests(df[[effect,cause]],
    maxlag), extract ssr_ftest p-value per lag. Returns {venue: {lag: p_value}}."""
    ...

def run_bidirectional_granger(df: pd.DataFrame, maxlag: int = 2) -> dict:
    """Calls granger_per_venue twice: hhi->entropy and entropy->hhi.
    Returns {hhi_to_entropy: {...}, entropy_to_hhi: {...},
    n_significant_forward, n_significant_reverse} (count p<0.05 at any lag, per venue)."""
    ...
```

### analyze.py (entrypoint)

**Dependencies**: data_loader, models, granger, visualize

```python
def gate_check(fe_result: dict, granger_result: dict) -> bool:
    """beta < 0 AND p_value < 0.05 (primary). Logs secondary Granger pass/fail
    but does not gate on it (per PRD: secondary priority)."""
    ...

def main() -> None:
    """1. load_panel_data() 2. prepare_analysis_df(lag=1) + prepare_analysis_df(lag=2)
    3. fit_baseline() 4. fit_panel_fe() 5. run_robustness_suite()
    6. run_bidirectional_granger() 7. gate_check()
    8. visualize.generate_all() 9. save results dict to results/h_m5_results.json."""
    ...
```

### visualize.py

**Dependencies**: matplotlib/seaborn, analyze (results dict + prepared df)

```python
def plot_gate_metrics(fe_result: dict, out_path: str) -> None:
    """Beta coefficient with 95% CI errorbar, zero/significance reference line.
    -> figures/gate_metrics.png"""
    ...

def plot_hhi_entropy_scatter(df: pd.DataFrame, out_path: str) -> None:
    """Scatter hhi_lag1 vs entropy, regression line, color by venue."""
    ...

def plot_time_series(df: pd.DataFrame, out_path: str) -> None:
    """Dual y-axis line plot: HHI and entropy trends per venue over years."""
    ...

def plot_granger_heatmap(granger_result: dict, out_path: str) -> None:
    """Heatmap of p-values: venues x lags, both directions (2 subplots)."""
    ...

def plot_residual_diagnostics(fe_result: dict, out_path: str) -> None:
    """QQ plot + residuals vs fitted, from fe_result['results_obj'].resids."""
    ...

def generate_all(fe_result: dict, granger_result: dict, df: pd.DataFrame, out_dir: str = "figures/") -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Panel data loading + MultiIndex | Load H-E1 CSV, set (venue, year) index, sort | 3 | 1+1+0+1 |
| A-2 | Lag construction | Groupby-shift for hhi_lag1/2, entropy_lag1, delta cols, dropna handling | 5 | 2+1+2+0 |
| A-3 | Baseline Pooled OLS | linearmodels PooledOLS, extract beta/p/R² | 4 | 1+1+1+1 |
| A-4 | Primary PanelOLS 2-way FE | Entity+time effects, clustered SE, extract beta/p/CI/R² | 7 | 2+2+2+1 |
| A-5 | Robustness suite | Lag-2 spec, entity-only spec, delta spec (3 model variants) | 6 | 2+2+1+1 |
| A-6 | Granger causality (bidirectional) | Per-venue tests both directions, maxlag=2, aggregate significance counts | 7 | 2+2+3+0 |
| A-7 | Gate check + results export | Gate logic, assemble results dict, save JSON | 3 | 1+1+1+0 |
| A-8 | Visualization suite | 5 figures (gate metrics, scatter, time series, granger heatmap, residuals) | 8 | 3+2+1+2 |
| A-9 | Pipeline integration | Wire main(), run end-to-end, verify <30s runtime | 4 | 1+2+1+0 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6, A-7, A-8, A-9]

---

## Dependencies (external)

- pandas, numpy
- linearmodels>=7.0 (panel.PooledOLS, panel.PanelOLS)
- statsmodels>=0.14 (tsa.stattools.grangercausalitytests, api)
- matplotlib>=3.7, seaborn>=0.12
- H-E1 data file (input, no import — file read only): `docs/youra_research/h-e1/data/venue_year_metrics.csv`
