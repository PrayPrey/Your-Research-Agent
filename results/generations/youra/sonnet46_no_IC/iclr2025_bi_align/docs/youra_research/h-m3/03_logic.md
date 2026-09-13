# Logic: h-m3

**Applied**: Standard scipy/seaborn statistical analysis pattern (green-field API design; KB query returned diffusion sampling — not applicable)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m2 PASSED)
**Status**: API signatures verified from base code
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Relevant Symbols**:
- `load_and_validate(csv_path: str) -> pd.DataFrame` — data_loader.py:3-7
- `save_all_figures(df, win_resid, lc_resid, boot_rhos, rho, ci, fwl_delta, figures_dir) -> list` — visualizer.py:11-30
- `write_validation_report(gate_result, rho, p_value, ci, fwl_result, pingouin_result, residual_stats, figure_paths, output_path) -> None` — report_writer.py:3-106

Note: h-m3 does NOT import h-m2 directly. Patterns are replicated. h-m2 `write_validation_report` has h-m2-specific params — h-m3 defines its own with different signature.

---

## External Dependencies API (Base Hypothesis)

Verified from actual h-m2 code, not spec:

```python
# From: docs/youra_research/h-m2/code/data_loader.py (ACTUAL CODE)
def load_and_validate(csv_path: str) -> pd.DataFrame:
    # Loads CSV (index_col=0), drops NaN on [win_rate, lc_winrate, avg_length], asserts N>=200
    # h-m3 replicates inline — no import, adds delta/quartile columns after
    ...

# From: docs/youra_research/h-m2/code/visualizer.py (ACTUAL CODE)
def save_all_figures(
    df: pd.DataFrame,
    win_resid: np.ndarray,
    lc_resid: np.ndarray,
    boot_rhos: np.ndarray,
    rho: float,
    ci: tuple,
    fwl_delta: float,
    figures_dir: str,
) -> list:
    # h-m3 does NOT call this — defines its own save_all_figures with different params
    ...
```

**Verified from**: `docs/youra_research/h-m2/code/` (actual implementation)

---

## A-2: Kruskal-Wallis Analysis [Complexity: 9, Budget: 1 subtask]

**Applied**: Standard scipy.stats.kruskal pattern

### API Signatures

```python
# analysis.py

def run_kruskal_wallis(df: pd.DataFrame) -> dict:
    """Primary gate: KW H-test on delta across Q1–Q4.
    Returns dict with H_stat, kw_p, epsilon_sq, quartile_medians, quartile_sizes.
    """
    ...

def evaluate_gate(kw_p: float, alpha: float, quartile_medians: dict) -> dict:
    """Gate evaluation: passes_gate, monotonic_trend, gate_label."""
    ...
```

### Pseudo-code: run_kruskal_wallis

```python
def run_kruskal_wallis(df: pd.DataFrame) -> dict:
    quartile_labels = ['Q1', 'Q2', 'Q3', 'Q4']
    q_groups = [df[df['quartile'] == q]['delta'].values for q in quartile_labels]

    # Guard: verify group sizes >= 5
    for q, grp in zip(quartile_labels, q_groups):
        assert len(grp) >= 5, f"Kruskal-Wallis requires >=5 per group; {q} has {len(grp)}"

    H_stat, kw_p = scipy.stats.kruskal(*q_groups)

    k = len(q_groups)   # 4
    N = len(df)
    epsilon_sq = (H_stat - k + 1) / (N - k)

    quartile_medians = {q: float(np.median(grp)) for q, grp in zip(quartile_labels, q_groups)}
    quartile_sizes   = {q: len(grp)              for q, grp in zip(quartile_labels, q_groups)}

    return {
        'H_stat': H_stat,
        'kw_p': kw_p,
        'epsilon_sq': epsilon_sq,
        'quartile_medians': quartile_medians,   # {'Q1': float, ..., 'Q4': float}
        'quartile_sizes': quartile_sizes,        # {'Q1': int, ..., 'Q4': int}
    }
```

### Pseudo-code: evaluate_gate

```python
def evaluate_gate(kw_p: float, alpha: float, quartile_medians: dict) -> dict:
    passes_gate = kw_p < alpha
    monotonic_trend = quartile_medians['Q1'] < quartile_medians['Q4']
    gate_label = 'PASS' if passes_gate else 'FAIL'
    return {'passes_gate': passes_gate, 'monotonic_trend': monotonic_trend, 'gate_label': gate_label}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | KW core + gate | run_kruskal_wallis (guard, H-test, epsilon_sq, descriptives) + evaluate_gate |

---

## A-4: Secondary Analyses [Complexity: 10, Budget: 1 subtask]

**Applied**: numpy bootstrap loop pattern (avoids scipy.stats.bootstrap deprecation)

### API Signatures

```python
# analysis.py

def run_spearman(df: pd.DataFrame, n_bootstrap: int = 1000, random_state: int = 42) -> dict:
    """Spearman rho(win_rate, delta) with bootstrap CI.
    Returns: {rho, p, ci_lower, ci_upper}
    NOTE: mathematical dependency present (delta contains -win_rate term).
    """
    ...

def run_ols_delta(df: pd.DataFrame) -> dict:
    """OLS: delta ~ win_rate_std + avg_length_std via statsmodels.
    Returns: {beta_win, beta_len, p_win, p_len, r_squared, ols_result}
    """
    ...

def run_dunn_posthoc(df: pd.DataFrame) -> pd.DataFrame:
    """Dunn post-hoc with Bonferroni via scikit-posthocs.
    Returns 4x4 pairwise p-value DataFrame. Only called if kw_p < 0.05.
    """
    ...
```

### Pseudo-code: run_spearman

```python
def run_spearman(df, n_bootstrap=1000, random_state=42):
    rng = np.random.default_rng(random_state)
    rho, p = scipy.stats.spearmanr(df['win_rate'], df['delta'])

    # Bootstrap CI via numpy loop (not scipy.stats.bootstrap)
    boot_rhos = np.empty(n_bootstrap)
    n = len(df)
    for i in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        boot_rhos[i], _ = scipy.stats.spearmanr(
            df['win_rate'].iloc[idx], df['delta'].iloc[idx]
        )
    ci_lower, ci_upper = np.percentile(boot_rhos, [2.5, 97.5])

    return {'rho': rho, 'p': p, 'ci_lower': ci_lower, 'ci_upper': ci_upper}
```

### Pseudo-code: run_ols_delta

```python
def run_ols_delta(df):
    scaler = StandardScaler()
    X_std = scaler.fit_transform(df[['win_rate', 'avg_length']])  # [N, 2]
    X_const = sm.add_constant(X_std)                               # [N, 3] with intercept
    model = sm.OLS(df['delta'], X_const).fit()

    # params: [intercept, beta_win, beta_len]
    return {
        'beta_win': model.params[1],
        'beta_len': model.params[2],
        'p_win':    model.pvalues[1],
        'p_len':    model.pvalues[2],
        'r_squared': model.rsquared,
        'ols_result': model,          # full statsmodels RegressionResultsWrapper
    }
```

### Pseudo-code: run_dunn_posthoc

```python
def run_dunn_posthoc(df):
    # scikit_posthocs.posthoc_dunn returns DataFrame[4x4] of Bonferroni-corrected p-values
    dunn_matrix = scikit_posthocs.posthoc_dunn(
        df, val_col='delta', group_col='quartile', p_adjust='bonferroni'
    )
    return dunn_matrix  # pd.DataFrame, index/cols = ['Q1','Q2','Q3','Q4']
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Spearman + OLS + Dunn | run_spearman (numpy bootstrap loop), run_ols_delta (StandardScaler + statsmodels params[1]/[2]), run_dunn_posthoc |

---

## A-6: Visualization [Complexity: 12, Budget: 2 subtasks]

**Applied**: seaborn boxplot + matplotlib scatter pattern

### API Signatures

```python
# visualization.py

def save_all_figures(
    df: pd.DataFrame,
    kw_results: dict,
    dunn_matrix: pd.DataFrame,
    spearman_results: dict,
    figures_dir: str,
) -> list[str]:
    """Saves 4 figures, returns list of file paths."""
    ...

def _boxplot_delta_by_quartile(
    df: pd.DataFrame,
    kw_p: float,
    dunn_matrix: pd.DataFrame,
    out_path: str,
) -> str:
    """fig1: boxplot per quartile + jitter + KW p annotation + Dunn Q1vQ4 bracket."""
    ...

def _scatter_winrate_delta(
    df: pd.DataFrame,
    spearman_results: dict,
    out_path: str,
) -> str:
    """fig2: scatter win_rate vs delta, quartile-colored, LOWESS trend."""
    ...

def _dunn_heatmap(
    dunn_matrix: pd.DataFrame,
    out_path: str,
) -> str:
    """fig3: 4x4 heatmap of Bonferroni p-values, log10 color scale."""
    ...

def _bar_quartile_medians(
    kw_results: dict,
    df: pd.DataFrame,
    out_path: str,
) -> str:
    """fig4: grouped bar of median delta per quartile with IQR error bars."""
    ...
```

### Pseudo-code: _boxplot_delta_by_quartile

```python
def _boxplot_delta_by_quartile(df, kw_p, dunn_matrix, out_path):
    fig, ax = plt.subplots(figsize=(8, 6))
    order = ['Q1', 'Q2', 'Q3', 'Q4']

    # Seaborn boxplot (no jitter built-in)
    sns.boxplot(data=df, x='quartile', y='delta', order=order, ax=ax,
                palette='Blues', width=0.5, showfliers=False)

    # Jittered strip overlay
    sns.stripplot(data=df, x='quartile', y='delta', order=order, ax=ax,
                  color='black', alpha=0.3, jitter=True, size=3)

    # KW p-value annotation (top-left)
    ax.text(0.02, 0.97, f'Kruskal-Wallis p={kw_p:.2e}',
            transform=ax.transAxes, va='top', fontsize=9)

    # Dunn Q1 vs Q4 significance bracket
    q1_vs_q4_p = dunn_matrix.loc['Q1', 'Q4']
    sig_label = '***' if q1_vs_q4_p < 0.001 else ('**' if q1_vs_q4_p < 0.01 else '*')
    # Draw bracket from x=0 (Q1) to x=3 (Q4) above plot
    y_max = df['delta'].max()
    y_bracket = y_max * 1.05
    ax.plot([0, 0, 3, 3], [y_bracket, y_bracket * 1.02, y_bracket * 1.02, y_bracket],
            lw=1, color='black')
    ax.text(1.5, y_bracket * 1.03, sig_label, ha='center', fontsize=10)

    ax.set_title('Delta Distribution by Win-Rate Quartile')
    ax.set_xlabel('Win-Rate Quartile (Q1=lowest, Q4=highest)')
    ax.set_ylabel('Delta (LC_winrate - win_rate)')
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path
```

### Pseudo-code: _scatter_winrate_delta

```python
def _scatter_winrate_delta(df, spearman_results, out_path):
    fig, ax = plt.subplots(figsize=(8, 6))
    palette = {'Q1': '#1f77b4', 'Q2': '#ff7f0e', 'Q3': '#2ca02c', 'Q4': '#d62728'}

    for q in ['Q1', 'Q2', 'Q3', 'Q4']:
        mask = df['quartile'] == q
        ax.scatter(df.loc[mask, 'win_rate'], df.loc[mask, 'delta'],
                   color=palette[q], label=q, alpha=0.6, s=25)

    # LOWESS trend via statsmodels
    from statsmodels.nonparametric.smoothers_lowess import lowess
    sorted_idx = df['win_rate'].argsort()
    smoothed = lowess(df['delta'].values[sorted_idx], df['win_rate'].values[sorted_idx], frac=0.3)
    ax.plot(smoothed[:, 0], smoothed[:, 1], 'k-', lw=2, label='LOWESS')

    rho, p = spearman_results['rho'], spearman_results['p']
    ax.text(0.02, 0.97,
            f'ρ={rho:.3f}, p={p:.2e}\n(NOTE: math dependency present)',
            transform=ax.transAxes, va='top', fontsize=8)

    ax.set_xlabel('Win Rate')
    ax.set_ylabel('Delta (LC_winrate - win_rate)')
    ax.set_title('Win Rate vs Delta by Quartile')
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path
```

### Pseudo-code: _dunn_heatmap

```python
def _dunn_heatmap(dunn_matrix, out_path):
    fig, ax = plt.subplots(figsize=(6, 5))
    # Log10 transform for color scale; clip tiny p-values to avoid -inf
    log_matrix = np.log10(dunn_matrix.values.clip(min=1e-300))

    sns.heatmap(log_matrix, annot=dunn_matrix.round(4), fmt='.4f',
                xticklabels=dunn_matrix.columns,
                yticklabels=dunn_matrix.index,
                cmap='RdYlGn_r', ax=ax,
                cbar_kws={'label': 'log10(p-value Bonferroni)'})

    ax.set_title('Dunn Post-Hoc Pairwise p-values (Bonferroni)')
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path
```

### Pseudo-code: _bar_quartile_medians

```python
def _bar_quartile_medians(kw_results, df, out_path):
    order = ['Q1', 'Q2', 'Q3', 'Q4']
    medians = [kw_results['quartile_medians'][q] for q in order]

    # IQR error bars: [median - Q25, Q75 - median]
    q25 = [df[df['quartile'] == q]['delta'].quantile(0.25) for q in order]
    q75 = [df[df['quartile'] == q]['delta'].quantile(0.75) for q in order]
    yerr_lo = [medians[i] - q25[i] for i in range(4)]
    yerr_hi = [q75[i] - medians[i] for i in range(4)]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(order, medians, yerr=[yerr_lo, yerr_hi], capsize=4,
           color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'], alpha=0.8)

    # Monotonic trend annotation
    is_mono = medians[0] < medians[1] < medians[2] < medians[3]
    trend_str = 'Monotonic Q1<Q2<Q3<Q4: YES' if is_mono else 'Monotonic: NO'
    ax.text(0.02, 0.97, trend_str, transform=ax.transAxes, va='top', fontsize=9)

    ax.set_xlabel('Win-Rate Quartile')
    ax.set_ylabel('Median Delta')
    ax.set_title('Median Delta per Quartile (IQR error bars)')
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Fig1 + Fig2 | _boxplot_delta_by_quartile (seaborn box+strip, KW annotation, Dunn bracket), _scatter_winrate_delta (quartile scatter + LOWESS) |
| L-6-2 | Fig3 + Fig4 | _dunn_heatmap (log10 color scale), _bar_quartile_medians (IQR error bars, monotonic annotation) |

---

## Summary: Subtask Budget

| Task | Budget | Used |
|------|--------|------|
| A-2 | 1 | 1 (L-2-1) |
| A-4 | 1 | 1 (L-4-1) |
| A-6 | 2 | 2 (L-6-1, L-6-2) |
| **Total** | **4** | **4** |
