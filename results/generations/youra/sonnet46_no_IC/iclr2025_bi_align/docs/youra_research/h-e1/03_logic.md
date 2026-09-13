# Logic: h-e1

**Applied**: Standard Python statistical patterns (pingouin partial_corr, statsmodels VIF, scipy linregress)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## Module Overview

Pure Python statistical study. No tensors, no GPU. Two modules get Logic-phase design:
- `statistical_analysis.py` — VIF + bootstrap (E1-2)
- `visualizer.py` — partial regression plot + delta scatter (E1-4)

---

## E1-2: Statistical Analysis [Complexity: 12, Budget: 2 subtasks]

**Applied**: Standard statsmodels VIF + pingouin partial_corr bootstrap loop

### L-2-1: compute_vif()

```python
def compute_vif(df: pd.DataFrame) -> dict[str, float]:
    """Compute VIF for win_rate and avg_length. Adds 'has_multicollinearity' bool flag."""
    # Returns: {'win_rate': float, 'avg_length': float, 'has_multicollinearity': bool}
```

**Pseudo-code:**
```
1. X = df[['win_rate', 'avg_length']].copy()
2. X_with_const = sm.add_constant(X)           # shape [N, 3]
3. For i, col in enumerate(['win_rate', 'avg_length']):
     vif_val = variance_inflation_factor(X_with_const.values, i+1)
     # i+1 because index 0 is the constant
4. result = {'win_rate': vif_win, 'avg_length': vif_len}
5. result['has_multicollinearity'] = any(v >= 5.0 for v in [vif_win, vif_len])
6. return result
```

**Implementation notes:**
- `variance_inflation_factor` expects numpy array; column index is 1-based after `add_constant`
- VIF_WARN = 5.0 (from architecture constants); flag is informational, does not stop pipeline
- Edge case: if win_rate and avg_length are perfectly collinear, VIF = inf; handle with `math.isinf` check and set flag=True

---

### L-2-2: bootstrap_partial_corr()

```python
def bootstrap_partial_corr(
    df: pd.DataFrame,
    n_bootstrap: int = 1000,
    random_state: int = 42
) -> tuple[float, float, list[float]]:
    """Bootstrap 95% CI for Spearman partial r (win_rate, LC_winrate | avg_length).

    Returns: (ci_lower, ci_upper, boot_rs) where boot_rs is list of length n_bootstrap.
    """
```

**Pseudo-code:**
```
1. rng = np.random.default_rng(random_state)
2. boot_rs = []
3. n = len(df)
4. For _ in range(n_bootstrap):
     idx = rng.choice(n, size=n, replace=True)      # [N] integer indices
     sample = df.iloc[idx].reset_index(drop=True)
     result = pingouin.partial_corr(
         data=sample,
         x='win_rate',
         y='length_controlled_winrate',
         covar='avg_length',
         method='spearman'
     )
     boot_rs.append(float(result['r'].iloc[0]))
5. arr = np.array(boot_rs)                           # [1000]
6. ci_lower = float(np.percentile(arr, 2.5))
7. ci_upper = float(np.percentile(arr, 97.5))
8. return ci_lower, ci_upper, boot_rs
```

**Implementation notes:**
- Use `np.random.default_rng` (not `np.random.seed`) for reproducibility with modern numpy API
- `pingouin.partial_corr` returns a DataFrame; extract via `result['r'].iloc[0]`
- Skip `alternative='greater'` in bootstrap loop (CI from percentiles is two-sided by construction; one-sided test is only for the primary call in `spearman_partial_corr`)
- If a resample produces a degenerate distribution (all identical ranks), pingouin may return NaN; guard with `if not np.isnan(r): boot_rs.append(r)`

---

## E1-4: Visualization [Complexity: 10, Budget: 2 subtasks]

**Applied**: statsmodels OLS residuals for partial regression; scipy.stats.linregress for delta trend

### L-4-1: plot_partial_regression()

```python
def plot_partial_regression(
    df: pd.DataFrame,
    output_dir: str
) -> str:
    """Partial regression: residualize win_rate and LC_winrate on avg_length via OLS.

    Returns: saved file path.
    """
```

**Pseudo-code:**
```
1. # Residualize win_rate on avg_length
   X_ctrl = sm.add_constant(df['avg_length'])        # [N, 2]
   res_x = sm.OLS(df['win_rate'], X_ctrl).fit()
   resid_win = res_x.resid                            # [N]

2. # Residualize LC_winrate on avg_length
   res_y = sm.OLS(df['length_controlled_winrate'], X_ctrl).fit()
   resid_lc = res_y.resid                             # [N]

3. # Scatter + trend line
   fig, ax = plt.subplots(figsize=(7, 5))
   ax.scatter(resid_win, resid_lc, alpha=0.5, s=20, color='steelblue')

4. # Trend line via numpy polyfit on residuals
   m, b = np.polyfit(resid_win, resid_lc, deg=1)
   x_line = np.linspace(resid_win.min(), resid_win.max(), 200)
   ax.plot(x_line, m * x_line + b, color='tomato', lw=1.5)

5. ax.set_xlabel('win_rate residual (partialled on avg_length)')
   ax.set_ylabel('LC_winrate residual (partialled on avg_length)')
   ax.set_title('Partial Regression: win_rate → LC_winrate | avg_length')

6. path = Path(output_dir) / 'fig2_partial_regression.png'
   fig.savefig(path, dpi=150, bbox_inches='tight')
   plt.close(fig)
   return str(path)
```

**Implementation notes:**
- `sm.add_constant` may warn if constant already present; suppress with `has_constant='skip'` or just let it pass (harmless)
- Use `np.polyfit` (not seaborn regplot) so trend line is consistent with reported Spearman r direction
- `plt.close(fig)` after save to avoid memory accumulation across 5 figures

---

### L-4-2: plot_delta_scatter()

```python
def plot_delta_scatter(
    df: pd.DataFrame,
    output_dir: str
) -> str:
    """Delta scatter: Δ = LC_winrate − win_rate vs win_rate with scipy linregress trend.

    Returns: saved file path.
    """
```

**Pseudo-code:**
```
1. delta = df['length_controlled_winrate'] - df['win_rate']   # [N]
   x = df['win_rate']                                          # [N]

2. slope, intercept, r_val, p_val, se = scipy.stats.linregress(x, delta)

3. fig, ax = plt.subplots(figsize=(7, 5))
   ax.scatter(x, delta, alpha=0.5, s=20, color='mediumpurple')
   ax.axhline(0, color='gray', lw=0.8, linestyle='--')        # zero-delta reference

4. x_line = np.linspace(x.min(), x.max(), 200)
   ax.plot(x_line, slope * x_line + intercept, color='tomato', lw=1.5,
           label=f'r={r_val:.3f}, p={p_val:.3f}')
   ax.legend(fontsize=9)

5. ax.set_xlabel('win_rate')
   ax.set_ylabel('Δ = LC_winrate − win_rate')
   ax.set_title('Length-Control Delta vs Win Rate')

6. path = Path(output_dir) / 'fig5_delta_scatter.png'
   fig.savefig(path, dpi=150, bbox_inches='tight')
   plt.close(fig)
   return str(path)
```

**Implementation notes:**
- `scipy.stats.linregress` returns a named tuple; destructure all 5 fields for legend annotation
- `axhline(0)` makes positive/negative delta visually interpretable
- delta can be negative (models where length-control hurts apparent win rate); no clipping

---

## Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | compute_vif | statsmodels VIF for win_rate + avg_length, returns dict with warning flag |
| L-2-2 | bootstrap_partial_corr | 1000-resample loop, pingouin partial_corr per sample, percentile CI |
| L-4-1 | plot_partial_regression | OLS residualize both vars on avg_length, scatter + polyfit trend line |
| L-4-2 | plot_delta_scatter | Compute Δ = LC − win, scatter vs win_rate, scipy linregress trend |
