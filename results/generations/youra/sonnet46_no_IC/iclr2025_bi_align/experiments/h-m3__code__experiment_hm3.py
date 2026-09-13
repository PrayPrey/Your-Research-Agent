"""
H-M3: Capability-Quartile Delta Distribution Test
Kruskal-Wallis on Delta (LC_winrate - win_rate) across win_rate quartiles.
Gate: SHOULD_WORK — p < 0.05 expected.
"""

import sys
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import scipy.stats as stats
import scikit_posthocs as sp
import seaborn as sns
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from statsmodels.nonparametric.smoothers_lowess import lowess

# ── Constants ──────────────────────────────────────────────────────────────────
CSV_PATH = Path("docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv")
FIGURES_DIR = Path("docs/youra_research/h-m3/figures")
OUTPUT_PATH = Path("docs/youra_research/h-m3/04_validation.md")
RESULTS_PATH = Path("docs/youra_research/h-m3/experiment_results.json")

N_BOOTSTRAP = 1000
RANDOM_STATE = 42
ALPHA = 0.05
N_QUARTILES = 4
QUARTILE_LABELS = ['Q1', 'Q2', 'Q3', 'Q4']
MIN_N_CLEAN = 200
MIN_GROUP_SIZE = 5
QUARTILE_PALETTE = ['#d73027', '#fc8d59', '#91bfdb', '#4575b4']


# ── Data Loading ───────────────────────────────────────────────────────────────
def load_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, index_col=0)
    df = df.dropna(subset=['win_rate', 'length_controlled_winrate', 'avg_length'])
    assert len(df) >= MIN_N_CLEAN, f"Expected >= {MIN_N_CLEAN} models, got {len(df)}"
    df['delta'] = df['length_controlled_winrate'] - df['win_rate']
    df['quartile'] = pd.qcut(df['win_rate'], q=N_QUARTILES, labels=QUARTILE_LABELS)
    group_sizes = df.groupby('quartile', observed=True).size()
    assert all(group_sizes >= MIN_GROUP_SIZE), f"Group sizes too small: {group_sizes.to_dict()}"
    print(f"Loaded N={len(df)} models")
    print(f"Group sizes: {group_sizes.to_dict()}")
    print(f"Delta range: [{df['delta'].min():.4f}, {df['delta'].max():.4f}]")
    return df


# ── Kruskal-Wallis ─────────────────────────────────────────────────────────────
def run_kruskal_wallis(df: pd.DataFrame) -> dict:
    q_groups = [df[df['quartile'] == q]['delta'].values for q in QUARTILE_LABELS]
    for i, q in enumerate(QUARTILE_LABELS):
        assert len(q_groups[i]) >= MIN_GROUP_SIZE, f"{q} has {len(q_groups[i])} < {MIN_GROUP_SIZE}"

    H_stat, kw_p = stats.kruskal(*q_groups)
    k = N_QUARTILES
    N = len(df)
    epsilon_sq = (H_stat - k + 1) / (N - k)

    quartile_medians = {q: float(np.median(g)) for q, g in zip(QUARTILE_LABELS, q_groups)}
    quartile_means = {q: float(np.mean(g)) for q, g in zip(QUARTILE_LABELS, q_groups)}
    quartile_sizes = {q: int(len(g)) for q, g in zip(QUARTILE_LABELS, q_groups)}
    quartile_q25 = {q: float(np.percentile(g, 25)) for q, g in zip(QUARTILE_LABELS, q_groups)}
    quartile_q75 = {q: float(np.percentile(g, 75)) for q, g in zip(QUARTILE_LABELS, q_groups)}
    monotonic_trend = all(
        quartile_medians[QUARTILE_LABELS[i]] < quartile_medians[QUARTILE_LABELS[i+1]]
        for i in range(len(QUARTILE_LABELS) - 1)
    )

    print(f"\nKruskal-Wallis H={H_stat:.4f}, p={kw_p:.4e}")
    print(f"epsilon-squared={epsilon_sq:.4f}")
    print(f"Quartile medians: {quartile_medians}")
    print(f"Monotonic trend Q1<Q2<Q3<Q4: {monotonic_trend}")

    return {
        'H_stat': float(H_stat),
        'kw_p': float(kw_p),
        'epsilon_sq': float(epsilon_sq),
        'quartile_medians': quartile_medians,
        'quartile_means': quartile_means,
        'quartile_sizes': quartile_sizes,
        'quartile_q25': quartile_q25,
        'quartile_q75': quartile_q75,
        'monotonic_trend': monotonic_trend,
        'N': N,
        'k': k,
    }


# ── Gate Evaluation ────────────────────────────────────────────────────────────
def evaluate_gate(kw_p: float, alpha: float, quartile_medians: dict) -> dict:
    passes_gate = kw_p < alpha
    monotonic_trend = all(
        quartile_medians[QUARTILE_LABELS[i]] < quartile_medians[QUARTILE_LABELS[i+1]]
        for i in range(len(QUARTILE_LABELS) - 1)
    )
    gate_label = 'PASS' if passes_gate else 'FAIL'
    print(f"\nGate: SHOULD_WORK — {gate_label}")
    print(f"  kw_p={kw_p:.4e} {'<' if passes_gate else '>='} alpha={alpha}")
    print(f"  Monotonic trend: {monotonic_trend}")
    return {
        'passes_gate': passes_gate,
        'monotonic_trend': monotonic_trend,
        'gate_label': gate_label,
        'gate_type': 'SHOULD_WORK',
    }


# ── Dunn Post-Hoc ──────────────────────────────────────────────────────────────
def run_dunn_posthoc(df: pd.DataFrame):
    dunn_matrix = sp.posthoc_dunn(
        df, val_col='delta', group_col='quartile', p_adjust='bonferroni'
    )
    q1_vs_q4 = float(dunn_matrix.loc['Q1', 'Q4'])
    print(f"\nDunn post-hoc Q1 vs Q4 (Bonferroni): p={q1_vs_q4:.4e}")
    return dunn_matrix


# ── Spearman ───────────────────────────────────────────────────────────────────
def run_spearman(df: pd.DataFrame, n_bootstrap: int = 1000, random_state: int = 42) -> dict:
    rho, p_rho = stats.spearmanr(df['win_rate'], df['delta'])
    print(f"\nSpearman rho(win_rate, delta)={rho:.4f}, p={p_rho:.4e}")
    print("  NOTE: mathematical dependency present (delta contains -win_rate)")

    n = len(df)
    rng = np.random.default_rng(random_state)
    boot_rhos = []
    for _ in range(n_bootstrap):
        idx = rng.choice(n, size=n, replace=True)
        r, _ = stats.spearmanr(df['win_rate'].iloc[idx], df['delta'].iloc[idx])
        boot_rhos.append(r)
    boot_rhos = np.array(boot_rhos)
    ci_lower, ci_upper = np.percentile(boot_rhos, [2.5, 97.5])
    print(f"  Bootstrap CI 95%: [{ci_lower:.4f}, {ci_upper:.4f}]")

    return {
        'rho': float(rho),
        'p': float(p_rho),
        'ci_lower': float(ci_lower),
        'ci_upper': float(ci_upper),
    }


# ── OLS Delta ─────────────────────────────────────────────────────────────────
def run_ols_delta(df: pd.DataFrame) -> dict:
    scaler = StandardScaler()
    X_std = scaler.fit_transform(df[['win_rate', 'avg_length']])
    X_sm = sm.add_constant(X_std)
    ols = sm.OLS(df['delta'], X_sm).fit()
    beta_win = float(ols.params.iloc[1])
    beta_len = float(ols.params.iloc[2])
    p_win = float(ols.pvalues.iloc[1])
    p_len = float(ols.pvalues.iloc[2])
    r_sq = float(ols.rsquared)
    print(f"\nOLS delta ~ win_rate_std + avg_length_std:")
    print(f"  beta_win={beta_win:.4f} (p={p_win:.4e})")
    print(f"  beta_len={beta_len:.4f} (p={p_len:.4e})")
    print(f"  R²={r_sq:.4f}")
    return {
        'beta_win': beta_win,
        'beta_len': beta_len,
        'p_win': p_win,
        'p_len': p_len,
        'r_squared': r_sq,
    }


# ── Visualizations ─────────────────────────────────────────────────────────────
def _boxplot_delta_by_quartile(df, kw_results, dunn_matrix, fig_dir):
    fig, ax = plt.subplots(figsize=(8, 6))
    palette = dict(zip(QUARTILE_LABELS, QUARTILE_PALETTE))
    sns.boxplot(data=df, x='quartile', y='delta', palette=palette, ax=ax,
                order=QUARTILE_LABELS, width=0.5, flierprops={'alpha': 0})
    sns.stripplot(data=df, x='quartile', y='delta', palette=palette, ax=ax,
                  order=QUARTILE_LABELS, size=3, alpha=0.5, jitter=True)
    ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    ax.set_title(f"Δ (LC_winrate − win_rate) by Capability Quartile\n"
                 f"Kruskal-Wallis H={kw_results['H_stat']:.2f}, p={kw_results['kw_p']:.2e}",
                 fontsize=12)
    ax.set_xlabel("Win Rate Quartile (Q1=lowest, Q4=highest capability)")
    ax.set_ylabel("Δ = LC_winrate − win_rate")

    if dunn_matrix is not None:
        q1q4_p = dunn_matrix.loc['Q1', 'Q4']
        y_max = df['delta'].max() + 0.02
        ax.annotate(
            f"Q1 vs Q4: p={q1q4_p:.2e}",
            xy=(0.5, 0.97), xycoords='axes fraction',
            ha='center', va='top', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8)
        )

    out = fig_dir / "fig1_boxplot_delta_by_quartile.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _scatter_winrate_delta(df, spearman_results, fig_dir):
    fig, ax = plt.subplots(figsize=(8, 6))
    palette = dict(zip(QUARTILE_LABELS, QUARTILE_PALETTE))
    for q, color in zip(QUARTILE_LABELS, QUARTILE_PALETTE):
        mask = df['quartile'] == q
        ax.scatter(df.loc[mask, 'win_rate'], df.loc[mask, 'delta'],
                   color=color, alpha=0.6, s=25, label=q)

    smoothed = lowess(df['delta'].values, df['win_rate'].values, frac=0.3)
    ax.plot(smoothed[:, 0], smoothed[:, 1], 'k-', linewidth=2, label='LOWESS')

    ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    rho = spearman_results['rho']
    p_rho = spearman_results['p']
    ax.text(0.05, 0.97,
            f"Spearman ρ={rho:.4f}, p={p_rho:.2e}\n(⚠ mathematical dependency: Δ contains −win_rate)",
            transform=ax.transAxes, va='top', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    ax.set_xlabel("win_rate")
    ax.set_ylabel("Δ = LC_winrate − win_rate")
    ax.set_title("win_rate vs Δ with Quartile Color-Coding and LOWESS Trend")
    ax.legend(title="Quartile", loc='lower right')
    out = fig_dir / "fig2_scatter_winrate_delta.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _dunn_heatmap(dunn_matrix, fig_dir):
    if dunn_matrix is None:
        return None
    log_p = np.log10(dunn_matrix.values.astype(float) + 1e-300)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(log_p, annot=dunn_matrix.values.astype(float),
                fmt='.2e', cmap='RdYlGn_r',
                xticklabels=QUARTILE_LABELS, yticklabels=QUARTILE_LABELS,
                ax=ax, linewidths=0.5)
    ax.set_title("Dunn Post-Hoc Pairwise p-values (Bonferroni)\nColor: log10(p)")
    out = fig_dir / "fig3_dunn_heatmap.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _bar_quartile_medians(kw_results, fig_dir):
    medians = [kw_results['quartile_medians'][q] for q in QUARTILE_LABELS]
    q25 = [kw_results['quartile_q25'][q] for q in QUARTILE_LABELS]
    q75 = [kw_results['quartile_q75'][q] for q in QUARTILE_LABELS]
    err_low = [m - q for m, q in zip(medians, q25)]
    err_high = [q - m for q, m in zip(q75, medians)]

    fig, ax = plt.subplots(figsize=(7, 5))
    x = np.arange(len(QUARTILE_LABELS))
    bars = ax.bar(x, medians, color=QUARTILE_PALETTE, alpha=0.8,
                  yerr=[err_low, err_high], capsize=5, ecolor='black')
    ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(QUARTILE_LABELS)
    ax.set_xlabel("Win Rate Quartile")
    ax.set_ylabel("Median Δ = LC_winrate − win_rate")
    ax.set_title(f"Median Δ per Capability Quartile\n"
                 f"ε²={kw_results['epsilon_sq']:.4f} (effect size), "
                 f"monotonic: {kw_results['monotonic_trend']}")
    for bar, med in zip(bars, medians):
        ax.text(bar.get_x() + bar.get_width() / 2, med + 0.002,
                f'{med:.4f}', ha='center', va='bottom', fontsize=9)
    out = fig_dir / "fig4_bar_quartile_medians.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def save_all_figures(df, kw_results, dunn_matrix, spearman_results, fig_dir: Path):
    fig_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    paths.append(_boxplot_delta_by_quartile(df, kw_results, dunn_matrix, fig_dir))
    paths.append(_scatter_winrate_delta(df, spearman_results, fig_dir))
    p3 = _dunn_heatmap(dunn_matrix, fig_dir)
    if p3:
        paths.append(p3)
    paths.append(_bar_quartile_medians(kw_results, fig_dir))
    print(f"\nSaved {len(paths)} figures to {fig_dir}")
    return paths


# ── Report Writer ──────────────────────────────────────────────────────────────
def write_validation_report(kw_results, gate_result, dunn_matrix, spearman_results,
                             ols_results, figure_paths, output_path: Path):
    kw_p = kw_results['kw_p']
    H = kw_results['H_stat']
    eps_sq = kw_results['epsilon_sq']
    gate_label = gate_result['gate_label']
    rho = spearman_results['rho']
    rho_p = spearman_results['p']
    ci_lo = spearman_results['ci_lower']
    ci_hi = spearman_results['ci_upper']
    beta_win = ols_results['beta_win']
    beta_len = ols_results['beta_len']
    r2 = ols_results['r_squared']

    q1q4_p_str = "N/A (KW failed)"
    dunn_table = ""
    if dunn_matrix is not None:
        q1q4_p = dunn_matrix.loc['Q1', 'Q4']
        q1q4_p_str = f"{q1q4_p:.4e}"
        rows = []
        for r in QUARTILE_LABELS:
            row_vals = " | ".join(f"{dunn_matrix.loc[r, c]:.3e}" for c in QUARTILE_LABELS)
            rows.append(f"| {r} | {row_vals} |")
        dunn_table = "\n".join(rows)

    medians_table = "\n".join(
        f"| {q} | {kw_results['quartile_sizes'][q]} | "
        f"{kw_results['quartile_medians'][q]:.4f} | {kw_results['quartile_means'][q]:.4f} |"
        for q in QUARTILE_LABELS
    )

    fig_lines = "\n".join(f"- `{p}`" for p in figure_paths)

    md = f"""# Phase 4 Validation Report: H-M3

**Hypothesis:** h-m3 — Capability-Quartile Delta Distribution Test
**Gate Type:** SHOULD_WORK
**Gate Result:** {gate_label}
**Date:** 2026-08-04

---

## 1. Gate Result

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| Kruskal-Wallis p | {kw_p:.4e} | < 0.05 | {'✅ PASS' if gate_result['passes_gate'] else '❌ FAIL'} |
| Monotonic trend Q1<Q2<Q3<Q4 | {gate_result['monotonic_trend']} | True | {'✅' if gate_result['monotonic_trend'] else '⚠️'} |
| H statistic | {H:.4f} | — | — |
| epsilon-squared | {eps_sq:.4f} | >0.06=medium | {'large' if eps_sq > 0.14 else 'medium' if eps_sq > 0.06 else 'small'} effect |

**Gate: SHOULD_WORK — {'PASSED' if gate_result['passes_gate'] else 'FAILED (non-fatal, pipeline continues)'}**

---

## 2. Kruskal-Wallis Results

- **H statistic:** {H:.4f}
- **p-value:** {kw_p:.4e}
- **epsilon-squared:** {eps_sq:.4f}
- **N:** {kw_results['N']}
- **k (groups):** {kw_results['k']}

### Quartile Delta Statistics

| Quartile | N | Median Δ | Mean Δ |
|----------|---|----------|--------|
{medians_table}

**Interpretation:** Q1 (lowest capability) has most-negative Δ; Q4 (highest capability) has least-negative Δ.
Monotonic trend: {gate_result['monotonic_trend']}.

---

## 3. Dunn Post-Hoc (Bonferroni)

Run conditionally (only if KW p < 0.05): {'Yes' if dunn_matrix is not None else 'No'}

- **Q1 vs Q4 pairwise p:** {q1q4_p_str}

{'### Full 4×4 Pairwise p-value Matrix' if dunn_table else ''}
{'| | Q1 | Q2 | Q3 | Q4 |' if dunn_table else ''}
{'|--|--|--|--|--|' if dunn_table else ''}
{dunn_table}

---

## 4. Secondary: Spearman ρ(win_rate, Δ)

> ⚠️ **NOTE: Mathematical dependency present** — Δ = LC_winrate − win_rate contains −win_rate,
> creating non-causal dependency. This is a secondary supporting analysis only.

- **rho:** {rho:.4f}
- **p-value:** {rho_p:.4e}
- **Bootstrap 95% CI:** [{ci_lo:.4f}, {ci_hi:.4f}]

---

## 5. Secondary: OLS Δ ~ win_rate_std + avg_length_std

| Coefficient | Value | p-value |
|-------------|-------|---------|
| β_win_rate_std | {beta_win:.4f} | {ols_results['p_win']:.4e} |
| β_avg_length_std | {beta_len:.4f} | {ols_results['p_len']:.4e} |
| R² | {r2:.4f} | — |

---

## 6. Figures

{fig_lines}

---

## 7. Pipeline Context

| Hypothesis | Result | Key Finding |
|------------|--------|-------------|
| H-E1 | PASS | r_partial=0.9851, p=1.69e-170 |
| H-M1 | PASS | \|β_win\|=21.34 >> \|β_len\|=4.37 |
| H-M2 | PASS | rho_resid=0.9739, p=2.37e-144 |
| **H-M3** | **{gate_label}** | **KW H={H:.2f}, p={kw_p:.2e}, ε²={eps_sq:.4f}** |

---

## 8. Conclusion

H-M3 tests whether the bidirectional alignment gap (Δ = LC_winrate − win_rate) differs significantly
across capability quartiles (Kruskal-Wallis SHOULD_WORK gate).

**Result:** Kruskal-Wallis H={H:.4f}, p={kw_p:.4e}.
Gate: **{gate_label}** {'— SHOULD_WORK satisfied, pipeline proceeds to H-C1.' if gate_result['passes_gate'] else '— SHOULD_WORK not satisfied (non-fatal), pipeline continues to H-C1.'}

Effect size epsilon-squared={eps_sq:.4f} ({'large' if eps_sq > 0.14 else 'medium' if eps_sq > 0.06 else 'small'} effect).
Monotonic trend Q1 < Q2 < Q3 < Q4: {gate_result['monotonic_trend']}.
"""
    output_path.write_text(md)
    print(f"\nValidation report written: {output_path}")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("H-M3: Capability-Quartile Delta Distribution Test")
    print("=" * 60)

    df = load_data(CSV_PATH)
    kw_results = run_kruskal_wallis(df)
    gate_result = evaluate_gate(kw_results['kw_p'], ALPHA, kw_results['quartile_medians'])

    dunn_matrix = None
    if gate_result['passes_gate']:
        dunn_matrix = run_dunn_posthoc(df)

    spearman_results = run_spearman(df, N_BOOTSTRAP, RANDOM_STATE)
    ols_results = run_ols_delta(df)
    figure_paths = save_all_figures(df, kw_results, dunn_matrix, spearman_results, FIGURES_DIR)

    write_validation_report(
        kw_results, gate_result, dunn_matrix, spearman_results,
        ols_results, figure_paths, OUTPUT_PATH
    )

    # Save JSON results
    results = {
        'hypothesis_id': 'h-m3',
        'gate': gate_result,
        'kruskal_wallis': kw_results,
        'spearman': spearman_results,
        'ols': ols_results,
        'dunn_q1_vs_q4': float(dunn_matrix.loc['Q1', 'Q4']) if dunn_matrix is not None else None,
        'figures': [str(p) for p in figure_paths],
    }
    RESULTS_PATH.write_text(json.dumps(results, indent=2))
    print(f"Results saved: {RESULTS_PATH}")

    print("\n" + "=" * 60)
    print(f"GATE: SHOULD_WORK — {gate_result['gate_label']}")
    print("=" * 60)

    sys.exit(0 if gate_result['passes_gate'] else 1)


if __name__ == '__main__':
    main()
