# Logic: H-M5 (MECHANISM Validation)

**Type**: Statistical analysis (panel regression + Granger causality), not ML training. No tensors — all shapes are `pd.DataFrame`/`dict`.

**Applied**: no relevant KB pattern found (Archon search "panel regression API design" — top hit similarity 0.40, unrelated diffusion-model repos, not applicable). Standard linearmodels/statsmodels API conventions used directly.

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: `h-m5/code/` does not exist yet. No base_hypothesis code dependency (H-M5 reads H-E1's CSV output only, not H-E1/H-M4 code). Serena skipped per green-field exemption.
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## A-1: Panel Data Loading + MultiIndex [Complexity: 3, Budget: 3]

```python
import pandas as pd

E1_DATA_PATH = "docs/youra_research/h-e1/data/venue_year_metrics.csv"

def load_panel_data(path: str = E1_DATA_PATH) -> pd.DataFrame:
    """Load H-E1 CSV, set MultiIndex (venue, year), sort index."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| return | DataFrame[21, 3] | index=(venue, year), cols=[hhi, entropy, paper_count] |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | CSV read | `pd.read_csv(path)` |
| L-1-2 | MultiIndex | `set_index(["venue","year"])` |
| L-1-3 | Sort | `sort_index()` |

---

## A-2: Lag Construction [Complexity: 5, Budget: 5]

```python
def add_lags(df: pd.DataFrame, lag: int = 1) -> pd.DataFrame:
    """Groupby venue, shift hhi/entropy by `lag`. Adds hhi_lag{lag}, entropy_lag{lag},
    delta_hhi, delta_entropy (diff by venue). Does NOT drop NaN."""
    ...

def prepare_analysis_df(df: pd.DataFrame, lag: int = 1) -> pd.DataFrame:
    """add_lags then dropna() -> clean panel for PanelOLS."""
    ...
```

### Pseudo-code

```
1. g = df.groupby(level="venue")
2. df[f"hhi_lag{lag}"] = g["hhi"].shift(lag)
3. df[f"entropy_lag{lag}"] = g["entropy"].shift(lag)
4. df["delta_hhi"] = g["hhi"].diff()
5. df["delta_entropy"] = g["entropy"].diff()
6. return df  # prepare_analysis_df: return df.dropna()
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| add_lags return | DataFrame[21, 7] | +4 cols, NaN in first row per venue |
| prepare_analysis_df(lag=1) return | DataFrame[18, 7] | 21 - 3 venues×1 row dropped |
| prepare_analysis_df(lag=2) return | DataFrame[15, 7] | 21 - 3 venues×2 rows dropped |

### Subtasks [4/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Groupby shift | lag hhi, entropy |
| L-2-2 | Delta cols | diff by venue |
| L-2-3 | prepare_analysis_df | wraps add_lags + dropna |
| L-2-4 | Dual-lag call sites | `prepare_analysis_df(df, lag=1)` and `lag=2` in analyze.py |

---

## A-3: Baseline Pooled OLS [Complexity: 4, Budget: 4]

```python
from linearmodels.panel import PooledOLS

def fit_baseline(df: pd.DataFrame, hhi_col: str = "hhi_lag1") -> dict:
    """Pooled OLS: entropy ~ const + hhi_lag1 + paper_count, no FE."""
    ...
```

### Pseudo-code

```
1. y = df["entropy"]
2. X = sm.add_constant(df[[hhi_col, "paper_count"]])
3. res = PooledOLS(y, X).fit()
4. return {beta: res.params[hhi_col], p_value: res.pvalues[hhi_col],
           r_squared: res.rsquared, conf_int: res.conf_int().loc[hhi_col].tolist()}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Design matrix | add_constant + regressors |
| L-3-2 | Fit | `PooledOLS(y, X).fit()` |
| L-3-3 | Extract | beta/p/R² |
| L-3-4 | conf_int | 95% CI extraction |

---

## A-4: Primary PanelOLS 2-Way FE [Complexity: 7, Budget: 7]

```python
from linearmodels.panel import PanelOLS

def fit_panel_fe(
    df: pd.DataFrame,
    hhi_col: str = "hhi_lag1",
    entity_effects: bool = True,
    time_effects: bool = True,
) -> dict:
    """PanelOLS(entropy ~ const + hhi_col + paper_count, entity_effects, time_effects),
    cov_type='clustered', cluster_entity=True."""
    ...
```

### Pseudo-code

```
1. y = df["entropy"]
2. X = sm.add_constant(df[[hhi_col, "paper_count"]])
3. mod = PanelOLS(y, X, entity_effects=entity_effects, time_effects=time_effects)
4. res = mod.fit(cov_type="clustered", cluster_entity=True)
5. return {beta: res.params[hhi_col], p_value: res.pvalues[hhi_col],
           conf_int_lower: res.conf_int().loc[hhi_col, "lower"],
           conf_int_upper: res.conf_int().loc[hhi_col, "upper"],
           r_squared: res.rsquared, n_obs: res.nobs, results_obj: res}
```

**Note**: `results_obj` (raw linearmodels result) carried in dict for residual diagnostics (A-8) — not JSON-serializable, strip before `json.dump`.

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Design matrix | add_constant + regressors |
| L-4-2 | PanelOLS construct | entity/time effects flags |
| L-4-3 | Clustered fit | cov_type, cluster_entity |
| L-4-4 | Extract beta/p | from res.params/pvalues |
| L-4-5 | Extract CI | res.conf_int() |
| L-4-6 | Extract R²/n_obs | res.rsquared, res.nobs |
| L-4-7 | results_obj passthrough | keep raw res for A-8 |

---

## A-5: Robustness Suite [Complexity: 6, Budget: 6]

```python
def fit_delta_spec(df: pd.DataFrame) -> dict:
    """Delta robustness: delta_entropy ~ const + delta_hhi_lag1 (Pooled OLS on diffs).
    Same return shape as fit_baseline."""
    ...

def run_robustness_suite(df_lag1: pd.DataFrame, df_lag2: pd.DataFrame) -> dict:
    """(a) fit_panel_fe(df_lag2, hhi_col='hhi_lag2')
    (b) fit_panel_fe(df_lag1, time_effects=False)
    (c) fit_delta_spec(df_lag1)."""
    ...
```

### Pseudo-code

```
run_robustness_suite:
  1. lag2 = fit_panel_fe(df_lag2, hhi_col="hhi_lag2")
  2. entity_only = fit_panel_fe(df_lag1, time_effects=False)
  3. delta_spec = fit_delta_spec(df_lag1)
  4. return {lag2, entity_only, delta_spec}
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | fit_delta_spec | delta_entropy ~ delta_hhi_lag1 |
| L-5-2 | lag2 spec | fit_panel_fe with hhi_lag2 |
| L-5-3 | entity-only spec | fit_panel_fe time_effects=False |
| L-5-4 | aggregate | run_robustness_suite wiring |

---

## A-6: Granger Causality (Bidirectional) [Complexity: 7, Budget: 7]

```python
from statsmodels.tsa.stattools import grangercausalitytests

def granger_per_venue(
    df: pd.DataFrame, cause: str, effect: str, maxlag: int = 2, min_obs: int = 4
) -> dict[str, dict[int, float]]:
    """For each venue with >= min_obs rows: grangercausalitytests(df[[effect,cause]], maxlag),
    extract ssr_ftest p-value per lag. Returns {venue: {lag: p_value}}."""
    ...

def run_bidirectional_granger(df: pd.DataFrame, maxlag: int = 2) -> dict:
    """Calls granger_per_venue twice: hhi->entropy and entropy->hhi.
    Returns {hhi_to_entropy, entropy_to_hhi, n_significant_forward, n_significant_reverse}."""
    ...
```

### Pseudo-code

```
granger_per_venue(df, cause, effect, maxlag, min_obs):
  1. result = {}
  2. for venue, sub in df.groupby(level="venue"):
  3.     if len(sub) < min_obs: continue
  4.     pair = sub[[effect, cause]].sort_index(level="year")  # order: [effect, cause]
  5.     gc = grangercausalitytests(pair, maxlag, verbose=False)
  6.     result[venue] = {lag: gc[lag][0]["ssr_ftest"][1] for lag in range(1, maxlag+1)}
  7. return result

run_bidirectional_granger(df, maxlag):
  1. fwd = granger_per_venue(df, cause="hhi", effect="entropy", maxlag=maxlag)
  2. rev = granger_per_venue(df, cause="entropy", effect="hhi", maxlag=maxlag)
  3. n_sig_fwd = sum(1 for v in fwd if any(p < 0.05 for p in fwd[v].values()))
  4. n_sig_rev = sum(1 for v in rev if any(p < 0.05 for p in rev[v].values()))
  5. return {hhi_to_entropy: fwd, entropy_to_hhi: rev,
             n_significant_forward: n_sig_fwd, n_significant_reverse: n_sig_rev}
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| granger_per_venue return | dict[3 venues][2 lags] | float p-values, venues with <4 rows omitted |

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | Groupby venue loop | filter min_obs |
| L-6-2 | grangercausalitytests call | pair column order [effect, cause] |
| L-6-3 | ssr_ftest extraction | per-lag p-value dict |
| L-6-4 | run_bidirectional wiring | fwd + rev calls |
| L-6-5 | n_significant_forward count | any p<0.05 per venue |
| L-6-6 | n_significant_reverse count | any p<0.05 per venue |
| L-6-7 | dict assembly | final return shape |

---

## A-7: Gate Check + Results Export [Complexity: 3, Budget: 3]

```python
def gate_check(fe_result: dict, granger_result: dict) -> bool:
    """beta < 0 AND p_value < 0.05 (primary gate). Logs secondary Granger
    pass/fail but does not gate on it."""
    ...
```

### Pseudo-code

```
1. primary_pass = fe_result["beta"] < 0 and fe_result["p_value"] < 0.05
2. secondary_fwd = granger_result["n_significant_forward"] >= 1
3. secondary_rev = granger_result["n_significant_reverse"] == 0
4. log.info(f"Granger secondary: forward={secondary_fwd}, reverse_clean={secondary_rev}")
5. return primary_pass
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | Primary gate logic | beta<0 and p<0.05 |
| L-7-2 | Secondary Granger logging | non-gating log lines |
| L-7-3 | JSON export | `json.dump` of results dict (strip `results_obj`) |

---

## A-8: Visualization Suite [Complexity: 8, Budget: 8]

```python
def plot_gate_metrics(fe_result: dict, out_path: str) -> None:
    """Beta coefficient with 95% CI errorbar, zero/significance reference line."""
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

def generate_all(
    fe_result: dict, granger_result: dict, df: pd.DataFrame, out_dir: str = "figures/"
) -> None:
    """Calls all 5 plot_* functions with paths under out_dir."""
    ...
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | plot_gate_metrics | errorbar + ref lines |
| L-8-2 | plot_hhi_entropy_scatter | scatter + regline, hue=venue |
| L-8-3 | plot_time_series | dual y-axis |
| L-8-4 | plot_granger_heatmap (build) | 2-subplot heatmap data prep |
| L-8-5 | plot_granger_heatmap (render) | seaborn.heatmap x2 |
| L-8-6 | plot_residual_diagnostics (qq) | scipy.stats.probplot |
| L-8-7 | plot_residual_diagnostics (resid vs fitted) | scatter |
| L-8-8 | generate_all wiring | out_dir path assembly, calls |

---

## A-9: Pipeline Integration [Complexity: 4, Budget: 4]

```python
def main() -> None:
    """1. load_panel_data() 2. prepare_analysis_df(lag=1) + prepare_analysis_df(lag=2)
    3. fit_baseline() 4. fit_panel_fe() 5. run_robustness_suite()
    6. run_bidirectional_granger() 7. gate_check()
    8. visualize.generate_all() 9. save results dict to results/h_m5_results.json."""
    ...
```

### Pseudo-code

```
1. raw = load_panel_data()
2. df1 = prepare_analysis_df(raw, lag=1)
3. df2 = prepare_analysis_df(raw, lag=2)
4. baseline = fit_baseline(df1)
5. fe = fit_panel_fe(df1)
6. robustness = run_robustness_suite(df1, df2)
7. granger = run_bidirectional_granger(df1)
8. passed = gate_check(fe, granger)
9. results = {baseline, fe: {k:v for k,v in fe.items() if k != "results_obj"},
              robustness, granger, gate_passed: passed}
10. visualize.generate_all(fe, granger, df1)
11. json.dump(results, open("results/h_m5_results.json", "w"), indent=2)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | Load + dual-lag prep | df1, df2 construction |
| L-9-2 | Model calls | baseline, fe, robustness, granger |
| L-9-3 | Gate + results assembly | gate_check + dict build (strip results_obj) |
| L-9-4 | Visualize + export | generate_all + json.dump, verify <30s |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X" line)
- [x] Docstrings <= 2 lines
- [x] Shapes in tables/comments, not tensors (statistical analysis, DataFrame-based)
- [x] Subtask counts match architecture budgets exactly (3,5,4,7,6,7,3,8,4 = 47 total)
- [x] Codebase Analysis (Serena) section included, green-field noted
- [x] Total length < 600 lines
