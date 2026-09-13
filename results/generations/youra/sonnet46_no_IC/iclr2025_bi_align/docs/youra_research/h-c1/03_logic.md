# Logic: h-c1

**Applied: single-file statistical experiment (incremental DV swap from h-m3)**

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-m3 code
**Analyzed Path**: `docs/youra_research/h-m3/code/experiment_hm3.py`
**Relevant Symbols**: `load_data`, `run_kruskal_wallis`, `run_dunn_posthoc`, `evaluate_gate`, `run_spearman`, `main` — all verified from actual implementation

---

## External Dependencies API

### API Signatures (From Actual h-m3 Code)

```python
# From: docs/youra_research/h-m3/code/experiment_hm3.py (ACTUAL CODE)

def load_data(csv_path: Path) -> pd.DataFrame:
    # Loads CSV, drops NaN on [win_rate, length_controlled_winrate, avg_length],
    # asserts len >= MIN_N_CLEAN, computes df['delta'] = lc_winrate - win_rate,
    # adds df['quartile'] via pd.qcut(win_rate, q=N_QUARTILES, labels=QUARTILE_LABELS).
    ...

def run_kruskal_wallis(df: pd.DataFrame) -> dict:
    # Uses df['delta'] as DV — h-c1 changes to df['length_controlled_winrate']
    # Returns: {H_stat, kw_p, epsilon_sq, quartile_medians, quartile_means,
    #           quartile_sizes, quartile_q25, quartile_q75, monotonic_trend, N, k}
    ...

def run_dunn_posthoc(df: pd.DataFrame) -> pd.DataFrame:
    # Uses val_col='delta' — h-c1 changes to val_col='length_controlled_winrate'
    # Returns 4x4 DataFrame of Bonferroni-corrected p-values
    ...

def evaluate_gate(kw_p: float, alpha: float, quartile_medians: dict) -> dict:
    # h-m3 signature: 3 params, single KW condition only
    # Returns: {passes_gate, monotonic_trend, gate_label, gate_type}
    # h-c1 ADDS dunn_q1q4_p param; gate requires BOTH kw_p < alpha AND dunn_q1q4_p < alpha
    ...

def run_spearman(df: pd.DataFrame, n_bootstrap: int = 1000, random_state: int = 42) -> dict:
    # Uses df['delta'] as corr target — h-c1 changes to df['length_controlled_winrate']
    # Returns: {rho, p, ci_lower, ci_upper}
    ...

def main() -> None:
    # h-m3 call: evaluate_gate(kw_results['kw_p'], ALPHA, kw_results['quartile_medians'])
    # h-m3 call: save_all_figures(df, kw_results, dunn_matrix, spearman_results, FIGURES_DIR)
    # h-m3 call: write_validation_report(kw_results, gate_result, dunn_matrix,
    #            spearman_results, ols_results, figure_paths, OUTPUT_PATH)
    # h-c1: adds bootstrap_results; drops ols_results; adds dunn_q1q4_p to gate call
    ...
```

**Verified from**: `docs/youra_research/h-m3/code/experiment_hm3.py` lines 40–474

---

## Adapted Functions (DV Swap — Annotated vs h-m3)

```python
def load_data(csv_path: Path) -> pd.DataFrame:
    """Load CSV, bin into quartiles. Keeps delta column for comparison figure only."""
    # SAME as h-m3 — delta kept but is NOT the primary DV
    # Change: add print for lc_winrate range alongside delta range

def run_kruskal_wallis(df: pd.DataFrame) -> dict:
    """KW H-test on length_controlled_winrate (was delta in h-m3)."""
    # CHANGE: df[df['quartile'] == q]['length_controlled_winrate'].values
    #         (was 'delta')
    # Return dict: identical keys to h-m3

def run_dunn_posthoc(df: pd.DataFrame) -> pd.DataFrame:
    """Dunn post-hoc Bonferroni on length_controlled_winrate (was delta)."""
    # CHANGE: val_col='length_controlled_winrate'  (was 'delta')
    # Return: identical 4x4 DataFrame structure

def run_spearman(df: pd.DataFrame, n_bootstrap: int = 1000, random_state: int = 42) -> dict:
    """Spearman rho(win_rate, length_controlled_winrate). Secondary metric."""
    # CHANGE: corr target = 'length_controlled_winrate'  (was 'delta')
    # CHANGE: remove NOTE about mathematical dependency
    # Return dict: identical keys {rho, p, ci_lower, ci_upper}

def _boxplot_lc_by_quartile(df: pd.DataFrame, kw_results: dict) -> plt.Figure:
    """Boxplot of length_controlled_winrate per quartile (was delta)."""
    # CHANGE: val_col='length_controlled_winrate', axis label 'LC_winrate (%)'

def _dunn_heatmap(dunn_matrix: pd.DataFrame) -> plt.Figure:
    """4x4 Bonferroni p-value heatmap. Identical logic to h-m3."""
    # SAME structure; title updated to 'LC_winrate'

def _bar_quartile_medians(kw_results: dict) -> plt.Figure:
    """Bar chart of quartile median LC_winrate with bootstrap CI error bars."""
    # CHANGE: y-axis label 'Median LC_winrate (%)'

def _gate_metrics_bar(kw_p: float, dunn_q1q4_p: float, alpha: float) -> plt.Figure:
    """NEW vs h-m3: dual gate condition bar (KW p and Dunn Q1 vs Q4 p vs 0.05)."""
    # NEW function — no h-m3 equivalent

def _comparison_hm3_hc1(kw_results: dict) -> plt.Figure:
    """NEW vs h-m3: side-by-side quartile medians Δ (h-m3) vs LC_winrate (h-c1)."""
    # Uses HM3_QUARTILE_MEDIANS_DELTA constant for h-m3 bars
    # NEW function — no h-m3 equivalent

def save_all_figures(
    df: pd.DataFrame,
    kw_results: dict,
    dunn_matrix: pd.DataFrame | None,
    bootstrap_results: dict | None,   # NEW param vs h-m3
    figures_dir: Path
) -> list[Path]:
    """Save all figures. CHANGE: bootstrap_results replaces spearman_results param."""
    # h-m3 had: save_all_figures(df, kw_results, dunn_matrix, spearman_results, FIGURES_DIR)
    # h-c1 has: save_all_figures(df, kw_results, dunn_matrix, bootstrap_results, figures_dir)

def write_validation_report(
    kw_results: dict,
    gate_result: dict,
    dunn_matrix: pd.DataFrame | None,
    bootstrap_results: dict | None,   # NEW param vs h-m3
    spearman_results: dict,
    figure_paths: list[Path],
    output_path: Path
) -> None:
    """Write 04_validation.md. CHANGE: adds bootstrap_results; drops ols_results."""
    # h-m3 had: write_validation_report(kw_results, gate_result, dunn_matrix,
    #            spearman_results, ols_results, figure_paths, OUTPUT_PATH)
    # h-c1 has: adds bootstrap_results, drops ols_results

def main() -> None:
    """Orchestrate: load → KW → gate → Dunn → bootstrap → spearman → figures → report."""
    # h-m3: evaluate_gate(kw_results['kw_p'], ALPHA, kw_results['quartile_medians'])
    # h-c1: evaluate_gate(kw_results['kw_p'], dunn_q1q4_p, ALPHA, kw_results['quartile_medians'])
    # h-c1: run_bootstrap_dunn_ci called after run_dunn_posthoc (always, not gated)
    # h-c1: drops run_ols_delta entirely
    # h-c1: hypothesis_id='h-c1' in JSON; adds 'bootstrap_dunn_ci' key
```

---

## A-5: run_bootstrap_dunn_ci [Complexity: 9, Budget: 2 subtasks]

**Applied: Standard PyTorch** (pure scipy/numpy, no DL)

### API Signatures

```python
def run_bootstrap_dunn_ci(
    df: pd.DataFrame,
    n_bootstrap: int = 1000,
    random_state: int = 42,
) -> dict:
    """Bootstrap 95% CI on Dunn Q1 vs Q4 Bonferroni p-value.
    Returns ci_lower, ci_upper, bootstrap_p_values (list[float])."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| df | [N, cols] | Full dataframe, N~222 |
| boot_ps | [n_bootstrap] | p-value per resample |
| ci_lower, ci_upper | scalar | 2.5th / 97.5th percentile |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | bootstrap_loop | Full pseudo-code: resample → Dunn → extract Q1 vs Q4 p |
| L-5-2 | evaluate_gate_dual | Dual condition logic: KW AND Dunn Q1 vs Q4 |

---

## L-5-1: run_bootstrap_dunn_ci — Full Pseudo-code

```
INPUT: df [N rows], n_bootstrap=1000, random_state=42

1. rng = np.random.default_rng(random_state)
2. n = len(df)
3. boot_ps = []

4. FOR _ in range(n_bootstrap):
     a. idx = rng.choice(n, size=n, replace=True)           # resample with replacement
     b. df_boot = df.iloc[idx].reset_index(drop=True)       # [N, cols]
     c. dunn_boot = sp.posthoc_dunn(
            df_boot,
            val_col='length_controlled_winrate',
            group_col='quartile',
            p_adjust='bonferroni'
        )                                                    # 4x4 DataFrame
     d. p_q1q4 = float(dunn_boot.loc['Q1', 'Q4'])
     e. boot_ps.append(p_q1q4)

5. boot_ps = np.array(boot_ps)                              # [1000]
6. ci_lower, ci_upper = np.percentile(boot_ps, [2.5, 97.5])

7. print(f"Bootstrap Dunn Q1 vs Q4 CI 95%: [{ci_lower:.4e}, {ci_upper:.4e}]")

RETURN {
    'ci_lower': float(ci_lower),
    'ci_upper': float(ci_upper),
    'bootstrap_p_values': boot_ps.tolist(),   # 1000 floats for diagnostics
}
```

**Note**: `sp.posthoc_dunn` is called 1000 times — expected runtime ~30-60s on N=222. Acceptable per NFR (<5 min).

---

## L-5-2: evaluate_gate — Dual Condition Logic

### API Signatures

```python
def evaluate_gate(
    kw_p: float,
    dunn_q1q4_p: float,       # NEW vs h-m3 (h-m3 had no dunn param)
    alpha: float,
    quartile_medians: dict,
) -> dict:
    """Dual gate: PASS iff kw_p < alpha AND dunn_q1q4_p < alpha."""
    ...
```

### Pseudo-code

```
both_conditions_met = (kw_p < alpha) AND (dunn_q1q4_p < alpha)
passes_gate = both_conditions_met

monotonic_trend = all(
    quartile_medians[QUARTILE_LABELS[i]] < quartile_medians[QUARTILE_LABELS[i+1]]
    for i in range(len(QUARTILE_LABELS) - 1)
)

gate_label = 'PASS' if passes_gate else 'FAIL'

RETURN {
    'passes_gate': passes_gate,
    'both_conditions_met': both_conditions_met,    # NEW key vs h-m3
    'monotonic_trend': monotonic_trend,
    'gate_label': gate_label,
    'gate_type': 'SHOULD_WORK',
    'kw_passed': kw_p < alpha,                     # NEW key vs h-m3
    'dunn_passed': dunn_q1q4_p < alpha,            # NEW key vs h-m3
}
```

**Key difference from h-m3**: h-m3 `evaluate_gate(kw_p, alpha, quartile_medians)` — 3 params, single condition. H-c1 adds `dunn_q1q4_p` as second required condition. Caller must extract `dunn_matrix.loc['Q1', 'Q4']` before calling.

---

## Subtask Summary

| ID | Subtask | Owner Task |
|----|---------|-----------|
| L-5-1 | bootstrap_loop | A-5 |
| L-5-2 | evaluate_gate_dual | A-4 + A-5 |
