# Logic: h-m1

**Applied**: sequential statistical pipeline pattern (statsmodels OLS, sklearn permutation_importance)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-e1)
**Status**: API signatures verified from actual h-e1 code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**:
- `load_and_validate(csv_path: str) -> pd.DataFrame` — reads CSV with `index_col=0`, dropna on 3 columns, assert N>=200
- `compute_vif(df: pd.DataFrame) -> dict` — uses raw `win_rate`/`avg_length` columns (NOT standardized); returns `{'win_rate': float, 'avg_length': float, 'any_high_vif': bool}`
- `save_all_figures(df, boot_rs, vif, corr_result, output_dir) -> list` — h-m1 uses different signature
- `evaluate_gate(r_partial, p_val, boot_ci_lower) -> dict` — h-m1 replaces entirely

---

## External Dependencies API (Base Hypothesis)

Signatures verified from actual h-e1 code — NOT from spec:

```python
# From: docs/youra_research/h-e1/code/data_loader.py
def load_and_validate(csv_path: str) -> pd.DataFrame:
    # index_col=0, dropna(['win_rate','length_controlled_winrate','avg_length']), assert N>=200
    ...

# From: docs/youra_research/h-e1/code/statistical_analysis.py
def compute_vif(df: pd.DataFrame) -> dict:
    # Uses df[['win_rate', 'avg_length']] (raw, not standardized)
    # Returns: {'win_rate': float, 'avg_length': float, 'any_high_vif': bool}
    ...
```

**Note**: h-m1 inlines both functions (no cross-hypothesis imports). `compute_vif` in h-m1 operates on `win_rate_std`/`avg_length_std` columns — adapted from h-e1 pattern.

---

## A-2: Data Loader [Complexity: 6, Budget: 1]

### API Signatures

```python
def load_and_validate(csv_path: str) -> pd.DataFrame:
    """Load CSV, drop NaN rows, assert N>=200."""
    ...

def standardize(df: pd.DataFrame) -> pd.DataFrame:
    """Add win_rate_std and avg_length_std columns via StandardScaler."""
    ...
```

### Pseudo-code

```
load_and_validate(csv_path):
    df = pd.read_csv(csv_path, index_col=0)
    df = df.dropna(subset=['win_rate', 'length_controlled_winrate', 'avg_length'])
    assert len(df) >= 200
    return df

standardize(df):
    scaler = StandardScaler()
    df = df.copy()
    df['win_rate_std'] = scaler.fit_transform(df[['win_rate']])
    df['avg_length_std'] = scaler.fit_transform(df[['avg_length']])
    assert abs(df['win_rate_std'].mean()) < 1e-10
    assert abs(df['win_rate_std'].std() - 1.0) < 1e-10
    assert abs(df['avg_length_std'].mean()) < 1e-10
    assert abs(df['avg_length_std'].std() - 1.0) < 1e-10
    return df
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | DataLoader | load_and_validate + standardize with assertions |

---

## A-3: VIF Diagnostic [Complexity: 5, Budget: 1]

### API Signatures

```python
def compute_vif(df: pd.DataFrame) -> dict:
    """VIF on standardized columns. Returns win_rate, avg_length, any_high_vif."""
    ...
```

### Pseudo-code

```
compute_vif(df):
    X = df[['win_rate_std', 'avg_length_std']].copy()
    X_const = sm.add_constant(X)
    vif_win = variance_inflation_factor(X_const.values, 1)
    vif_len = variance_inflation_factor(X_const.values, 2)
    if math.isinf(vif_win) or math.isinf(vif_len):
        any_high = True
    else:
        any_high = any(v >= 5.0 for v in [vif_win, vif_len])
    return {'win_rate': float(vif_win), 'avg_length': float(vif_len), 'any_high_vif': any_high}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | VIF | compute_vif on standardized columns |

---

## A-4: Baseline OLS [Complexity: 7, Budget: 1]

### API Signatures

```python
def fit_baseline_ols(df: pd.DataFrame) -> dict:
    """OLS: LC_winrate ~ avg_length_std. Returns beta_avg_length, r2, pvalue."""
    ...
```

### Pseudo-code

```
fit_baseline_ols(df):
    X = sm.add_constant(df['avg_length_std'])
    y = df['length_controlled_winrate']
    model = sm.OLS(y, X).fit()
    return {
        'beta_avg_length': float(model.params['avg_length_std']),
        'r2': float(model.rsquared),
        'pvalue': float(model.pvalues['avg_length_std'])
    }
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | BaselineOLS | verbosity-only null model |

---

## A-5: Full OLS [Complexity: 9, Budget: 1]

### API Signatures

```python
def fit_full_ols(df: pd.DataFrame) -> dict:
    """OLS: LC_winrate ~ win_rate_std + avg_length_std. Full results dict."""
    ...
```

### Pseudo-code

```
fit_full_ols(df):
    X = sm.add_constant(df[['win_rate_std', 'avg_length_std']])
    y = df['length_controlled_winrate']
    model = sm.OLS(y, X).fit()
    return {
        'beta_win': float(model.params['win_rate_std']),
        'beta_len': float(model.params['avg_length_std']),
        'p_win':    float(model.pvalues['win_rate_std']),
        'p_len':    float(model.pvalues['avg_length_std']),
        'r2':       float(model.rsquared),
        'r2_adj':   float(model.rsquared_adj),
        'residuals': np.array(model.resid),
        'fitted':    np.array(model.fittedvalues),
        '_model':   model   # kept for diagnostics; not serialized
    }
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | FullOLS | beta extraction, R², residuals, fitted |

---

## A-6: OLS Diagnostics [Complexity: 8, Budget: 1]

### API Signatures

```python
def run_ols_diagnostics(ols_result: dict, df: pd.DataFrame) -> dict:
    """Breusch-Pagan test. Returns bp_stat, bp_pvalue, heteroscedastic."""
    ...

def run_permutation_fallback(df: pd.DataFrame) -> dict:
    """sklearn permutation importance (VIF>=5 path). Returns imp_win, imp_len."""
    ...
```

### Pseudo-code

```
run_ols_diagnostics(ols_result, df):
    model = ols_result['_model']
    X_exog = model.model.exog
    bp_stat, bp_pvalue, _, _ = het_breuschpagan(model.resid, X_exog)
    return {
        'bp_stat': float(bp_stat),
        'bp_pvalue': float(bp_pvalue),
        'heteroscedastic': bool(bp_pvalue < 0.05)
    }

run_permutation_fallback(df):
    X = df[['win_rate_std', 'avg_length_std']].values
    y = df['length_controlled_winrate'].values
    lr = LinearRegression().fit(X, y)
    perm = permutation_importance(lr, X, y, n_repeats=30, random_state=42)
    return {
        'imp_win': float(perm.importances_mean[0]),
        'imp_len': float(perm.importances_mean[1])
    }
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Diagnostics | Breusch-Pagan + permutation fallback |

---

## A-8: Gate Evaluator [Complexity: 6, Budget: 1]

### API Signatures

```python
def evaluate_gate(ols_result: dict, vif: dict, perm_result: dict | None = None) -> dict:
    """VIF-contingent dominance decision. Returns passes_gate, path, dominant."""
    ...
```

### Pseudo-code

```
evaluate_gate(ols_result, vif, perm_result=None):
    if not vif['any_high_vif']:  # OLS path (VIF < 5)
        abs_win = abs(ols_result['beta_win'])
        abs_len = abs(ols_result['beta_len'])
        passes = (abs_win > abs_len) and (ols_result['p_win'] < 0.05)
        return {
            'passes_gate': passes,
            'path': 'OLS_beta',
            'beta_win': ols_result['beta_win'],
            'beta_len': ols_result['beta_len'],
            'p_win': ols_result['p_win'],
            'dominant': 'win_rate' if abs_win > abs_len else 'avg_length'
        }
    else:  # Permutation fallback (VIF >= 5)
        passes = perm_result['imp_win'] > perm_result['imp_len']
        return {
            'passes_gate': passes,
            'path': 'permutation_importance',
            'beta_win': ols_result['beta_win'],
            'beta_len': ols_result['beta_len'],
            'p_win': ols_result['p_win'],
            'dominant': 'win_rate' if passes else 'avg_length'
        }
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | GateEval | VIF-contingent dominance gate |

---

## A-9: Visualizations [Complexity: 14, Budget: 2]

### API Signatures

```python
def save_all_figures(
    df: pd.DataFrame,
    ols_result: dict,
    vif: dict,
    gate_result: dict,
    figures_dir: str
) -> list[str]:
    """Generate 6 figures. Returns list of absolute file paths."""
    ...

def _dominance_bar(ols_result: dict, figures_dir: str) -> str:
    """fig1: |beta_win| vs |beta_len| bar chart with p-value annotations."""
    ...

def _coef_plot(ols_result: dict, figures_dir: str) -> str:
    """fig2: horizontal bar with 95% CI error bars for both standardized coefficients."""
    ...

def _vif_bar(vif: dict, figures_dir: str) -> str:
    """fig3: VIF bar chart with threshold line at 5.0. Mirrors h-e1 _vif_diagnostic."""
    ...

def _residuals_vs_fitted(ols_result: dict, figures_dir: str) -> str:
    """fig4: residuals vs fitted scatter for heteroscedasticity check."""
    ...

def _qq_plot(ols_result: dict, figures_dir: str) -> str:
    """fig5: Q-Q plot of OLS residuals for normality check."""
    ...

def _scatter_by_length_quartile(df: pd.DataFrame, figures_dir: str) -> str:
    """fig6: win_rate_std vs LC_winrate colored by avg_length quartile."""
    ...
```

### Pseudo-code

```
save_all_figures(df, ols_result, vif, gate_result, figures_dir):
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    paths = [
        _dominance_bar(ols_result, figures_dir),
        _coef_plot(ols_result, figures_dir),
        _vif_bar(vif, figures_dir),
        _residuals_vs_fitted(ols_result, figures_dir),
        _qq_plot(ols_result, figures_dir),
        _scatter_by_length_quartile(df, figures_dir),
    ]
    assert len(paths) == 6
    return paths

_dominance_bar(ols_result, figures_dir):
    labels = ['|β_win_rate_std|', '|β_avg_length_std|']
    values = [abs(ols_result['beta_win']), abs(ols_result['beta_len'])]
    colors = ['steelblue', 'tomato']
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, values, color=colors, alpha=0.8)
    # annotate p-values above bars
    ax.text(0, values[0] + 0.01, f"p={ols_result['p_win']:.2e}", ha='center')
    ax.text(1, values[1] + 0.01, f"p={ols_result['p_len']:.2e}", ha='center')
    ax.set_ylabel('|Standardized Coefficient|')
    ax.set_title('Dominance: Capability vs Verbosity (OLS β)')
    save to fig1_dominance_bar.png; return path

_coef_plot(ols_result, figures_dir):
    model = ols_result['_model']
    params = model.params[['win_rate_std', 'avg_length_std']]
    ci = model.conf_int().loc[['win_rate_std', 'avg_length_std']]
    xerr_lo = params.values - ci[0].values
    xerr_hi = ci[1].values - params.values
    fig, ax = plt.subplots(figsize=(7, 4))
    y_pos = [1, 0]
    ax.barh(y_pos, params.values, xerr=[xerr_lo, xerr_hi], align='center', alpha=0.8)
    ax.axvline(0, color='gray', lw=0.8)
    ax.set_yticks(y_pos); ax.set_yticklabels(['win_rate_std', 'avg_length_std'])
    ax.set_xlabel('Standardized Coefficient (95% CI)')
    ax.set_title('OLS Coefficient Plot')
    save to fig2_coef_plot.png; return path

_vif_bar(vif, figures_dir):
    # same logic as h-e1 _vif_diagnostic but uses win_rate_std/avg_length_std labels
    labels = ['win_rate_std', 'avg_length_std']
    values = [vif['win_rate'], vif['avg_length']]
    colors = ['tomato' if v >= 5.0 else 'steelblue' for v in values]
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, values, color=colors, alpha=0.8)
    ax.axhline(5.0, color='red', linestyle='--', lw=1.5, label='VIF=5.0 threshold')
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f'{val:.3f}', ha='center')
    ax.legend(fontsize=9); ax.set_ylabel('VIF')
    ax.set_title('Variance Inflation Factor (Standardized Predictors)')
    save to fig3_vif_bar.png; return path

_residuals_vs_fitted(ols_result, figures_dir):
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(ols_result['fitted'], ols_result['residuals'], alpha=0.5, s=20, color='steelblue')
    ax.axhline(0, color='red', linestyle='--', lw=1)
    ax.set_xlabel('Fitted Values'); ax.set_ylabel('Residuals')
    ax.set_title('OLS Residuals vs Fitted')
    save to fig4_residuals_vs_fitted.png; return path

_qq_plot(ols_result, figures_dir):
    fig, ax = plt.subplots(figsize=(6, 5))
    scipy.stats.probplot(ols_result['residuals'], dist='norm', plot=ax)
    ax.set_title('Q-Q Plot of OLS Residuals')
    save to fig5_qq_plot.png; return path

_scatter_by_length_quartile(df, figures_dir):
    # mirrors h-e1 _scatter_winrate_lc but uses win_rate_std on x-axis
    quartiles = df['avg_length'].quantile([0.25, 0.5, 0.75])
    colors = [pick color by avg_length quartile (same 4-color scheme as h-e1)]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(df['win_rate_std'], df['length_controlled_winrate'], c=colors, alpha=0.6, s=20)
    ax.set_xlabel('win_rate_std'); ax.set_ylabel('LC_winrate')
    ax.set_title('win_rate_std vs LC_winrate (color = avg_length quartile)')
    [add legend patches matching h-e1 color scheme]
    save to fig6_scatter_by_length_quartile.png; return path
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | Figs 1-3 | dominance_bar, coef_plot, vif_bar |
| L-9-2 | Figs 4-6 | residuals_vs_fitted, qq_plot, scatter_by_length_quartile |

---

## A-10: Report Writer [Complexity: 8, Budget: 1]

### API Signatures

```python
def write_validation_report(
    gate_result: dict,
    ols_result: dict,
    baseline_result: dict,
    vif: dict,
    diagnostics: dict,
    figure_paths: list[str],
    output_path: str
) -> None:
    """Write 04_validation.md with full results and h-e1 comparison row."""
    ...
```

### Pseudo-code

```
write_validation_report(...):
    lines = [
        "# Validation: h-m1",
        f"**Gate**: {'PASS' if gate_result['passes_gate'] else 'FAIL'}",
        f"**Path**: {gate_result['path']}",
        "",
        "## OLS Results",
        f"| β_win_rate_std | {ols_result['beta_win']:.4f} |",
        f"| β_avg_length_std | {ols_result['beta_len']:.4f} |",
        f"| p_win | {ols_result['p_win']:.4e} |",
        f"| p_len | {ols_result['p_len']:.4e} |",
        f"| R² | {ols_result['r2']:.4f} |",
        f"| R²_adj | {ols_result['r2_adj']:.4f} |",
        "",
        "## Baseline OLS (verbosity-only null model)",
        f"| β_avg_length_std | {baseline_result['beta_avg_length']:.4f} |",
        f"| R² | {baseline_result['r2']:.4f} |",
        "",
        "## VIF Diagnostic",
        f"| win_rate_std | {vif['win_rate']:.3f} |",
        f"| avg_length_std | {vif['avg_length']:.3f} |",
        f"| any_high_vif | {vif['any_high_vif']} |",
        "",
        "## OLS Diagnostics",
        f"| Breusch-Pagan stat | {diagnostics['bp_stat']:.4f} |",
        f"| Breusch-Pagan p | {diagnostics['bp_pvalue']:.4f} |",
        f"| heteroscedastic | {diagnostics['heteroscedastic']} |",
        "",
        "## Comparison with h-e1",
        "| Metric | h-e1 | h-m1 |",
        "| r_partial | 0.9851 | N/A (OLS) |",
        f"| Dominant predictor | win_rate | {gate_result['dominant']} |",
        "",
        "## Figures",
        [f"- {p}" for p in figure_paths],
    ]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text('\n'.join(lines))
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | ReportWriter | write 04_validation.md with all sections |

---

## A-11: Orchestration [Complexity: 9, Budget: 2]

### API Signatures

```python
# Constants (module-level)
CSV_PATH: str = "docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv"
FIGURES_DIR: str = "docs/youra_research/h-m1/figures/"
OUTPUT_PATH: str = "docs/youra_research/h-m1/04_validation.md"
RANDOM_STATE: int = 42
ALPHA: float = 0.05
VIF_THRESHOLD: float = 5.0
N_MIN: int = 200

def main() -> None:
    """End-to-end pipeline. sys.exit(0) on PASS, sys.exit(1) on FAIL."""
    ...
```

### Pseudo-code

```
main():
    df = load_and_validate(CSV_PATH)
    df = standardize(df)

    vif = compute_vif(df)
    print(f"VIF: win_rate_std={vif['win_rate']:.3f}, avg_length_std={vif['avg_length']:.3f}")

    baseline = fit_baseline_ols(df)
    ols = fit_full_ols(df)
    diagnostics = run_ols_diagnostics(ols, df)

    perm = None
    if vif['any_high_vif']:
        perm = run_permutation_fallback(df)

    gate = evaluate_gate(ols, vif, perm)
    print(f"Gate: {'PASS' if gate['passes_gate'] else 'FAIL'} via {gate['path']}")
    print(f"  |beta_win|={abs(ols['beta_win']):.4f}, |beta_len|={abs(ols['beta_len']):.4f}")
    print(f"  p_win={ols['p_win']:.4e}")

    fig_paths = save_all_figures(df, ols, vif, gate, FIGURES_DIR)
    write_validation_report(gate, ols, baseline, vif, diagnostics, fig_paths, OUTPUT_PATH)

    sys.exit(0 if gate['passes_gate'] else 1)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-11-1 | main() | sequential pipeline, sys.exit |
| L-11-2 | Integration | smoke test: run main(), check gate PASS, check 6 figures exist |

---

## Subtask Budget Summary

| Task | Budget | Used |
|------|--------|------|
| A-2 Data Loader | 1 | 1 |
| A-3 VIF | 1 | 1 |
| A-4 Baseline OLS | 1 | 1 |
| A-5 Full OLS | 1 | 1 |
| A-6 Diagnostics | 1 | 1 |
| A-8 Gate Evaluator | 1 | 1 |
| A-9 Visualizations | 2 | 2 |
| A-10 Report Writer | 1 | 1 |
| A-11 Orchestration | 2 | 2 |
| **Total** | **11** | **11** |

Budget focus on A-9 (2), A-5 (full pseudo-code), A-11 (2) as specified.
