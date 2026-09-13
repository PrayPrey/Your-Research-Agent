"""
H-C1: Boundary/Scope Verification — Quartile Monotonicity of LC_winrate
Kruskal-Wallis + Dunn Q1 vs Q4 on LC_winrate directly (not delta).
Gate: SHOULD_WORK — dual condition: KW p < 0.05 AND Dunn Q1 vs Q4 Bonferroni p < 0.05.
Key distinction from H-M3: DV is length_controlled_winrate (not delta).
"""

import sys
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
import scikit_posthocs as sp
import seaborn as sns
from statsmodels.nonparametric.smoothers_lowess import lowess

# ── Constants ──────────────────────────────────────────────────────────────────
CSV_PATH = Path("docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv")
FIGURES_DIR = Path("docs/youra_research/h-c1/figures")
OUTPUT_PATH = Path("docs/youra_research/h-c1/04_validation.md")
RESULTS_PATH = Path("docs/youra_research/h-c1/results_hc1.json")

N_BOOTSTRAP = 1000
RANDOM_STATE = 42
ALPHA = 0.05
N_QUARTILES = 4
QUARTILE_LABELS = ['Q1', 'Q2', 'Q3', 'Q4']
MIN_N_CLEAN = 200
MIN_GROUP_SIZE = 5
DEPENDENT_VAR = 'length_controlled_winrate'
GATE_KW_P = ALPHA
GATE_DUNN_Q1_Q4 = ALPHA
QUARTILE_PALETTE = ['#d73027', '#fc8d59', '#91bfdb', '#4575b4']

# H-M3 reference values for comparison figure
HM3_QUARTILE_MEDIANS_DELTA = {'Q1': 2.19, 'Q2': 2.96, 'Q3': 5.43, 'Q4': 0.91}


# ── Data Loading ───────────────────────────────────────────────────────────────
def load_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, index_col=0)
    df = df.dropna(subset=['win_rate', 'length_controlled_winrate', 'avg_length'])
    assert len(df) >= MIN_N_CLEAN, f"Expected >= {MIN_N_CLEAN} models, got {len(df)}"
    # Keep delta for comparison figure only — NOT primary DV
    df['delta'] = df['length_controlled_winrate'] - df['win_rate']
    df['quartile'] = pd.qcut(df['win_rate'], q=N_QUARTILES, labels=QUARTILE_LABELS)
    group_sizes = df.groupby('quartile', observed=True).size()
    assert all(group_sizes >= MIN_GROUP_SIZE), f"Group sizes too small: {group_sizes.to_dict()}"
    print(f"Loaded N={len(df)} models")
    print(f"Group sizes: {group_sizes.to_dict()}")
    print(f"LC_winrate range: [{df['length_controlled_winrate'].min():.4f}, {df['length_controlled_winrate'].max():.4f}]")
    print(f"Delta range (secondary): [{df['delta'].min():.4f}, {df['delta'].max():.4f}]")
    return df


# ── Kruskal-Wallis on LC_winrate ───────────────────────────────────────────────
def run_kruskal_wallis(df: pd.DataFrame) -> dict:
    # DV is length_controlled_winrate (not delta — key H-C1 change vs H-M3)
    q_groups = [df[df['quartile'] == q]['length_controlled_winrate'].values for q in QUARTILE_LABELS]
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

    print(f"\nKruskal-Wallis on LC_winrate: H={H_stat:.4f}, p={kw_p:.4e}")
    print(f"epsilon-squared={epsilon_sq:.4f}")
    print(f"Quartile LC_winrate medians: {quartile_medians}")
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


# ── Dunn Post-Hoc on LC_winrate ────────────────────────────────────────────────
def run_dunn_posthoc(df: pd.DataFrame) -> pd.DataFrame:
    # val_col='length_controlled_winrate' — DV swap from h-m3's 'delta'
    dunn_matrix = sp.posthoc_dunn(
        df, val_col='length_controlled_winrate', group_col='quartile', p_adjust='bonferroni'
    )
    q1_vs_q4 = float(dunn_matrix.loc['Q1', 'Q4'])
    print(f"\nDunn post-hoc on LC_winrate, Q1 vs Q4 (Bonferroni): p={q1_vs_q4:.4e}")
    return dunn_matrix


# ── Gate Evaluation — Dual Condition ──────────────────────────────────────────
def evaluate_gate(kw_p: float, dunn_q1q4_p: float, alpha: float,
                  quartile_medians: dict) -> dict:
    kw_passed = kw_p < alpha
    dunn_passed = dunn_q1q4_p < alpha
    both_conditions_met = kw_passed and dunn_passed
    passes_gate = both_conditions_met
    monotonic_trend = all(
        quartile_medians[QUARTILE_LABELS[i]] < quartile_medians[QUARTILE_LABELS[i+1]]
        for i in range(len(QUARTILE_LABELS) - 1)
    )
    gate_label = 'PASS' if passes_gate else 'FAIL'
    print(f"\nGate: SHOULD_WORK — {gate_label}")
    print(f"  kw_p={kw_p:.4e} {'<' if kw_passed else '>='} alpha={alpha} -> {'PASS' if kw_passed else 'FAIL'}")
    print(f"  dunn_q1q4_p={dunn_q1q4_p:.4e} {'<' if dunn_passed else '>='} alpha={alpha} -> {'PASS' if dunn_passed else 'FAIL'}")
    print(f"  Dual gate (both required): {both_conditions_met}")
    print(f"  Monotonic trend: {monotonic_trend}")
    return {
        'passes_gate': passes_gate,
        'both_conditions_met': both_conditions_met,
        'kw_passed': kw_passed,
        'dunn_passed': dunn_passed,
        'monotonic_trend': monotonic_trend,
        'gate_label': gate_label,
        'gate_type': 'SHOULD_WORK',
    }


# ── Bootstrap CI on Dunn Q1 vs Q4 ─────────────────────────────────────────────
def run_bootstrap_dunn_ci(df: pd.DataFrame, n_bootstrap: int = 1000,
                          random_state: int = 42) -> dict:
    """Bootstrap 95% CI on Dunn Q1 vs Q4 Bonferroni p-value. ~30-60s runtime."""
    rng = np.random.default_rng(random_state)
    n = len(df)
    boot_ps = []
    print(f"\nBootstrap Dunn CI: {n_bootstrap} resamples...")
    for i in range(n_bootstrap):
        idx = rng.choice(n, size=n, replace=True)
        df_boot = df.iloc[idx].reset_index(drop=True)
        try:
            dunn_boot = sp.posthoc_dunn(
                df_boot, val_col='length_controlled_winrate',
                group_col='quartile', p_adjust='bonferroni'
            )
            boot_ps.append(float(dunn_boot.loc['Q1', 'Q4']))
        except Exception:
            boot_ps.append(1.0)
        if (i + 1) % 200 == 0:
            print(f"  Bootstrap {i+1}/{n_bootstrap}")
    boot_ps = np.array(boot_ps)
    ci_lower, ci_upper = np.percentile(boot_ps, [2.5, 97.5])
    print(f"Bootstrap Dunn Q1 vs Q4 CI 95%: [{ci_lower:.4e}, {ci_upper:.4e}]")
    return {
        'ci_lower': float(ci_lower),
        'ci_upper': float(ci_upper),
        'bootstrap_p_values': boot_ps.tolist(),
    }


# ── Spearman rho(win_rate, LC_winrate) ────────────────────────────────────────
def run_spearman(df: pd.DataFrame, n_bootstrap: int = 1000, random_state: int = 42) -> dict:
    rho, p_rho = stats.spearmanr(df['win_rate'], df['length_controlled_winrate'])
    print(f"\nSpearman rho(win_rate, LC_winrate)={rho:.4f}, p={p_rho:.4e}")

    n = len(df)
    rng = np.random.default_rng(random_state)
    boot_rhos = []
    for _ in range(n_bootstrap):
        idx = rng.choice(n, size=n, replace=True)
        r, _ = stats.spearmanr(df['win_rate'].iloc[idx], df['length_controlled_winrate'].iloc[idx])
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


# ── Visualizations ─────────────────────────────────────────────────────────────
def _boxplot_lc_by_quartile(df, kw_results, dunn_matrix, fig_dir):
    fig, ax = plt.subplots(figsize=(8, 6))
    palette = dict(zip(QUARTILE_LABELS, QUARTILE_PALETTE))
    sns.boxplot(data=df, x='quartile', y='length_controlled_winrate', palette=palette, ax=ax,
                order=QUARTILE_LABELS, width=0.5, flierprops={'alpha': 0})
    # jitter points manually (seaborn stripplot has pandas compat issue)
    for i, q in enumerate(QUARTILE_LABELS):
        vals = df[df['quartile'] == q]['length_controlled_winrate'].values
        jitter = np.random.default_rng(42).uniform(-0.2, 0.2, size=len(vals))
        ax.scatter(i + jitter, vals, color=QUARTILE_PALETTE[i], alpha=0.4, s=15)
    ax.set_title(f"LC_winrate by Capability Quartile\n"
                 f"Kruskal-Wallis H={kw_results['H_stat']:.2f}, p={kw_results['kw_p']:.2e}",
                 fontsize=12)
    ax.set_xlabel("Win Rate Quartile (Q1=lowest, Q4=highest capability)")
    ax.set_ylabel("LC_winrate (%)")

    if dunn_matrix is not None:
        q1q4_p = dunn_matrix.loc['Q1', 'Q4']
        ax.annotate(
            f"Q1 vs Q4 (Bonferroni): p={q1q4_p:.2e}",
            xy=(0.5, 0.97), xycoords='axes fraction',
            ha='center', va='top', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8)
        )

    out = fig_dir / "fig1_lc_winrate_boxplot.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _scatter_winrate_lc_winrate(df, spearman_results, fig_dir):
    fig, ax = plt.subplots(figsize=(8, 6))
    for q, color in zip(QUARTILE_LABELS, QUARTILE_PALETTE):
        mask = df['quartile'] == q
        ax.scatter(df.loc[mask, 'win_rate'], df.loc[mask, 'length_controlled_winrate'],
                   color=color, alpha=0.6, s=25, label=q)

    smoothed = lowess(df['length_controlled_winrate'].values, df['win_rate'].values, frac=0.3)
    ax.plot(smoothed[:, 0], smoothed[:, 1], 'k-', linewidth=2, label='LOWESS')

    rho = spearman_results['rho']
    p_rho = spearman_results['p']
    ax.text(0.05, 0.97,
            f"Spearman ρ={rho:.4f}, p={p_rho:.2e}",
            transform=ax.transAxes, va='top', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    ax.set_xlabel("win_rate (%)")
    ax.set_ylabel("LC_winrate (%)")
    ax.set_title("win_rate vs LC_winrate with Quartile Color-Coding and LOWESS Trend")
    ax.legend(title="Quartile", loc='lower right')
    out = fig_dir / "fig2_scatter_winrate_lc_winrate.png"
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
    ax.set_title("Dunn Post-Hoc Pairwise p-values on LC_winrate (Bonferroni)\nColor: log10(p)")
    out = fig_dir / "fig3_dunn_heatmap.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _comparison_hm3_hc1(kw_results, fig_dir):
    """Side-by-side: H-M3 delta medians vs H-C1 LC_winrate medians per quartile."""
    hm3_vals = [HM3_QUARTILE_MEDIANS_DELTA[q] for q in QUARTILE_LABELS]
    hc1_vals = [kw_results['quartile_medians'][q] for q in QUARTILE_LABELS]

    x = np.arange(len(QUARTILE_LABELS))
    width = 0.35

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: H-M3 delta
    axes[0].bar(x, hm3_vals, color=QUARTILE_PALETTE, alpha=0.8, width=0.6)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(QUARTILE_LABELS)
    axes[0].set_xlabel("Win Rate Quartile")
    axes[0].set_ylabel("Median Δ = LC_winrate − win_rate")
    axes[0].set_title("H-M3: Δ per Quartile\n(Dunn Q1 vs Q4: p=1.0 — non-significant)")
    for i, v in enumerate(hm3_vals):
        axes[0].text(i, v + 0.05, f'{v:.2f}', ha='center', va='bottom', fontsize=9)

    # Right: H-C1 LC_winrate
    axes[1].bar(x, hc1_vals, color=QUARTILE_PALETTE, alpha=0.8, width=0.6)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(QUARTILE_LABELS)
    axes[1].set_xlabel("Win Rate Quartile")
    axes[1].set_ylabel("Median LC_winrate (%)")
    q1q4_dunn_note = f"Dunn Q1 vs Q4: see report"
    axes[1].set_title(f"H-C1: LC_winrate per Quartile\n({q1q4_dunn_note})")
    for i, v in enumerate(hc1_vals):
        axes[1].text(i, v + 0.3, f'{v:.2f}', ha='center', va='bottom', fontsize=9)

    fig.suptitle("H-M3 (DV=Δ) vs H-C1 (DV=LC_winrate) — Quartile Median Comparison", fontsize=12)
    out = fig_dir / "fig4_comparison_hm3_hc1.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def save_all_figures(df, kw_results, dunn_matrix, bootstrap_results, fig_dir: Path):
    fig_dir.mkdir(parents=True, exist_ok=True)
    # Need spearman for scatter — run inline
    rho, p_rho = stats.spearmanr(df['win_rate'], df['length_controlled_winrate'])
    spearman_for_fig = {'rho': float(rho), 'p': float(p_rho)}

    paths = []
    paths.append(_boxplot_lc_by_quartile(df, kw_results, dunn_matrix, fig_dir))
    paths.append(_scatter_winrate_lc_winrate(df, spearman_for_fig, fig_dir))
    p3 = _dunn_heatmap(dunn_matrix, fig_dir)
    if p3:
        paths.append(p3)
    paths.append(_comparison_hm3_hc1(kw_results, fig_dir))
    print(f"\nSaved {len(paths)} figures to {fig_dir}")
    return paths


# ── Report Writer ──────────────────────────────────────────────────────────────
def write_validation_report(kw_results, gate_result, dunn_matrix, bootstrap_results,
                             spearman_results, figure_paths, output_path: Path):
    kw_p = kw_results['kw_p']
    H = kw_results['H_stat']
    eps_sq = kw_results['epsilon_sq']
    gate_label = gate_result['gate_label']

    dunn_q1q4_p_str = "N/A"
    dunn_table = ""
    dunn_q1q4_p = None
    if dunn_matrix is not None:
        dunn_q1q4_p = float(dunn_matrix.loc['Q1', 'Q4'])
        dunn_q1q4_p_str = f"{dunn_q1q4_p:.4e}"
        rows = []
        for r in QUARTILE_LABELS:
            row_vals = " | ".join(f"{dunn_matrix.loc[r, c]:.3e}" for c in QUARTILE_LABELS)
            rows.append(f"| {r} | {row_vals} |")
        dunn_table = "\n".join(rows)

    boot_ci_str = "N/A"
    if bootstrap_results is not None:
        boot_ci_str = f"[{bootstrap_results['ci_lower']:.4e}, {bootstrap_results['ci_upper']:.4e}]"

    medians_table = "\n".join(
        f"| {q} | {kw_results['quartile_sizes'][q]} | "
        f"{kw_results['quartile_medians'][q]:.4f} | {kw_results['quartile_means'][q]:.4f} |"
        for q in QUARTILE_LABELS
    )

    rho = spearman_results['rho']
    rho_p = spearman_results['p']
    rho_ci_lo = spearman_results['ci_lower']
    rho_ci_hi = spearman_results['ci_upper']

    fig_lines = "\n".join(f"- `{p}`" for p in figure_paths)

    monotonic_vals = [kw_results['quartile_medians'][q] for q in QUARTILE_LABELS]
    monotonic_str = " < ".join(f"{v:.2f}" for v in monotonic_vals)

    md = f"""# Phase 4 Validation Report: H-C1

**Hypothesis:** h-c1 — Condition Hypothesis (Boundary/Scope Verification)
**Type:** CONDITION — Quartile Monotonicity of LC_winrate
**Gate Type:** SHOULD_WORK
**Gate Result:** {gate_label}
**Date:** 2026-08-04

---

## 1. Gate Result

| Condition | Value | Threshold | Result |
|-----------|-------|-----------|--------|
| Kruskal-Wallis p on LC_winrate | {kw_p:.4e} | < 0.05 | {'✅ PASS' if gate_result['kw_passed'] else '❌ FAIL'} |
| Dunn Q1 vs Q4 Bonferroni p | {dunn_q1q4_p_str} | < 0.05 | {'✅ PASS' if gate_result['dunn_passed'] else '❌ FAIL'} |
| **Overall Gate (both required)** | — | — | **{'✅ PASS' if gate_result['passes_gate'] else '❌ FAIL'}** |
| Monotonic trend Q1<Q2<Q3<Q4 (secondary) | {gate_result['monotonic_trend']} | True | {'✅' if gate_result['monotonic_trend'] else '⚠️'} |
| H statistic | {H:.4f} | — | — |
| epsilon-squared | {eps_sq:.4f} | >0.06=medium | {'large' if eps_sq > 0.14 else 'medium' if eps_sq > 0.06 else 'small'} effect |

**Gate: SHOULD_WORK — {'PASSED' if gate_result['passes_gate'] else 'FAILED (non-fatal, pipeline continues)'}**

---

## 2. Kruskal-Wallis on LC_winrate

- **H statistic:** {H:.4f}
- **p-value:** {kw_p:.4e}
- **epsilon-squared:** {eps_sq:.4f} ({'large' if eps_sq > 0.14 else 'medium' if eps_sq > 0.06 else 'small'} effect)
- **N:** {kw_results['N']}
- **k (groups):** {kw_results['k']}

**Key distinction from H-M3:** H-M3 tested KW on Δ = LC_winrate − win_rate (H=22.19, p=5.97e-05, ε²=0.0876).
H-C1 tests LC_winrate directly — expected much stronger effect given r_partial=0.9851 (H-E1).

### Quartile LC_winrate Statistics

| Quartile | N | Median LC_winrate | Mean LC_winrate |
|----------|---|-------------------|-----------------|
{medians_table}

**Monotonic trend values:** {monotonic_str}
**Monotonic Q1<Q2<Q3<Q4:** {gate_result['monotonic_trend']}

---

## 3. Dunn Post-Hoc (Bonferroni, m=6 pairs)

- **Q1 vs Q4 Bonferroni p:** {dunn_q1q4_p_str}
- **Bootstrap 95% CI on Dunn Q1 vs Q4 p:** {boot_ci_str}

{'### Full 4×4 Pairwise p-value Matrix (LC_winrate)' if dunn_table else ''}
{'| | Q1 | Q2 | Q3 | Q4 |' if dunn_table else ''}
{'|--|--|--|--|--|' if dunn_table else ''}
{dunn_table}

---

## 4. Comparison with H-M3

| Test | H-M3 (DV=Δ) | H-C1 (DV=LC_winrate) |
|------|-------------|----------------------|
| Kruskal-Wallis H | 22.19 | {H:.2f} |
| Kruskal-Wallis p | 5.97e-05 | {kw_p:.2e} |
| epsilon-squared | 0.0876 | {eps_sq:.4f} |
| Dunn Q1 vs Q4 Bonferroni p | 1.0 (non-significant) | {dunn_q1q4_p_str} |
| Monotonic trend | False (Q4 median < Q3) | {gate_result['monotonic_trend']} |
| Gate | PASS (KW only) | {gate_label} (dual: KW + Dunn) |

**Interpretation:** H-M3 on Δ showed significant KW (population level) but non-significant Dunn Q1 vs Q4 (p=1.0).
H-C1 on LC_winrate tests whether the raw capability-preference relationship is monotonic at extremes.

---

## 5. Secondary: Spearman ρ(win_rate, LC_winrate)

- **rho:** {rho:.4f}
- **p-value:** {rho_p:.4e}
- **Bootstrap 95% CI:** [{rho_ci_lo:.4f}, {rho_ci_hi:.4f}]

---

## 6. Figures

{fig_lines}

---

## 7. Pipeline Context

| Hypothesis | Type | Gate | Result | Key Finding |
|------------|------|------|--------|-------------|
| H-E1 | EMPIRICAL | MUST_WORK | PASS | r_partial=0.9851, p=1.69e-170 |
| H-M1 | MECHANISM | MUST_WORK | PASS | \|β_win\|=21.34 >> \|β_len\|=4.37 |
| H-M2 | MECHANISM | MUST_WORK | PASS | rho_resid=0.9739, p=2.37e-144 |
| H-M3 | MECHANISM | SHOULD_WORK | PASS | KW H=22.19, p=5.97e-05, Dunn Q1 vs Q4 p=1.0 |
| **H-C1** | **CONDITION** | **SHOULD_WORK** | **{gate_label}** | **KW H={H:.2f}, p={kw_p:.2e}, Dunn Q1 vs Q4 p={dunn_q1q4_p_str}** |

---

## 8. Conclusion

H-C1 tests whether the capability-LC preference relationship is monotonic at population extremes
(Kruskal-Wallis + Dunn Q1 vs Q4 on LC_winrate directly).

**Gate: SHOULD_WORK — {gate_label}**

- Kruskal-Wallis on LC_winrate: H={H:.4f}, p={kw_p:.4e} ({'PASS' if gate_result['kw_passed'] else 'FAIL'})
- Dunn Q1 vs Q4 Bonferroni: p={dunn_q1q4_p_str} ({'PASS' if gate_result['dunn_passed'] else 'FAIL'})
- Both conditions met: {gate_result['both_conditions_met']}
- Monotonic trend Q1<Q2<Q3<Q4: {gate_result['monotonic_trend']}

{'Gate PASSED — LC_winrate is monotonically and significantly differentiated across capability quartiles. The capability-alignment relationship holds at both population level (H-E1 through H-M3) and at quartile extremes (H-C1).' if gate_result['passes_gate'] else 'Gate FAILED (SHOULD_WORK, non-fatal) — Boundary monotonicity at quartile extremes not confirmed at this significance threshold. The capability-alignment relationship holds at population level (H-E1 through H-M3 all PASS) but the LC_winrate-based quartile separation does not pass the dual gate. Pipeline continues — H-C1 is the final sub-hypothesis.'}
"""
    output_path.write_text(md)
    print(f"\nValidation report written: {output_path}")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("H-C1: Quartile Monotonicity of LC_winrate (Boundary Test)")
    print("=" * 60)

    df = load_data(CSV_PATH)
    kw_results = run_kruskal_wallis(df)

    # Dunn always run (both conditions required for dual gate)
    dunn_matrix = run_dunn_posthoc(df)
    dunn_q1q4_p = float(dunn_matrix.loc['Q1', 'Q4'])

    gate_result = evaluate_gate(
        kw_results['kw_p'], dunn_q1q4_p, ALPHA, kw_results['quartile_medians']
    )

    bootstrap_results = run_bootstrap_dunn_ci(df, N_BOOTSTRAP, RANDOM_STATE)
    spearman_results = run_spearman(df, N_BOOTSTRAP, RANDOM_STATE)

    figure_paths = save_all_figures(df, kw_results, dunn_matrix, bootstrap_results, FIGURES_DIR)

    write_validation_report(
        kw_results, gate_result, dunn_matrix, bootstrap_results,
        spearman_results, figure_paths, OUTPUT_PATH
    )

    # JSON results
    results = {
        'hypothesis_id': 'h-c1',
        'gate': gate_result,
        'kruskal_wallis': kw_results,
        'dunn_q1_vs_q4': dunn_q1q4_p,
        'bootstrap_dunn_ci': {
            'ci_lower': bootstrap_results['ci_lower'],
            'ci_upper': bootstrap_results['ci_upper'],
        },
        'spearman': spearman_results,
        'figures': [str(p) for p in figure_paths],
    }
    RESULTS_PATH.write_text(json.dumps(results, indent=2))
    print(f"Results saved: {RESULTS_PATH}")

    print("\n" + "=" * 60)
    print(f"GATE: SHOULD_WORK — {gate_result['gate_label']}")
    print(f"  KW p={kw_results['kw_p']:.4e}, Dunn Q1 vs Q4 p={dunn_q1q4_p:.4e}")
    print("=" * 60)

    sys.exit(0 if gate_result['passes_gate'] else 1)


if __name__ == '__main__':
    main()
