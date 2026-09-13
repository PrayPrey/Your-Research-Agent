"""
03_generate_figures.py — H-M2 Figure Generation
4 figures at 300 DPI: gate bar, tag count dist, partial regression, forest plot.
"""

import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

PROJECT_ROOT   = Path(__file__).resolve().parents[4]
MODEL_RESULTS  = PROJECT_ROOT / "docs/youra_research/h-m2/results/model_results.json"
TAGGED_PARQUET = PROJECT_ROOT / "docs/youra_research/h-m2/results/tagged_subset.parquet"
FIGURES_DIR    = PROJECT_ROOT / "docs/youra_research/h-m2/figures"

GATE_THRESHOLD = 1.05

# H-E1 color palette
PRIMARY   = '#2196F3'
THRESHOLD = '#F44336'
CI_COLOR  = '#90CAF9'
SECONDARY = '#4CAF50'


def fig1_gate_metrics(results: dict) -> None:
    iv = results['proposed_with_fe']['log_tag_count_p1_stats']
    irr = iv['irr']
    ci_lower = iv['ci_lower']
    ci_upper = iv['ci_upper']
    passed = (ci_lower >= GATE_THRESHOLD) and (iv['pval'] < 0.05)
    label = 'PASS' if passed else 'INFORMATIVE_NEGATIVE'

    fig, ax = plt.subplots(figsize=(7, 5))
    bar = ax.bar(['IRR (log_tag_count+1)'], [irr], color=PRIMARY, width=0.4,
                 yerr=[[irr - ci_lower], [ci_upper - irr]],
                 capsize=8, error_kw={'color': CI_COLOR, 'linewidth': 2})
    ax.axhline(y=GATE_THRESHOLD, color=THRESHOLD, linestyle='--', linewidth=2,
               label=f'Gate threshold ({GATE_THRESHOLD})')
    ax.axhline(y=1.0, color='gray', linestyle=':', linewidth=1, label='IRR=1.0 (null)')
    ax.set_ylabel('Incidence Rate Ratio (IRR)', fontsize=12)
    ax.set_title(f'H-M2 Gate Metrics — {label}\n'
                 f'IRR={irr:.4f} (95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]), p={iv["pval"]:.4e}',
                 fontsize=11)
    ax.legend(fontsize=10)
    ax.set_ylim(bottom=max(0, ci_lower * 0.9), top=ci_upper * 1.1)
    color = SECONDARY if passed else THRESHOLD
    ax.text(0, irr + (ci_upper - irr) * 1.2, label, ha='center', va='bottom',
            fontsize=12, fontweight='bold', color=color)
    plt.tight_layout()
    out = FIGURES_DIR / 'fig1_gate_metrics.png'
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved {out}")


def fig2_tag_count_distribution(df_tagged: pd.DataFrame) -> None:
    tag_counts = df_tagged['tag_count']
    fig, ax = plt.subplots(figsize=(8, 5))
    use_log = (tag_counts.max() / tag_counts.median()) > 10

    if use_log:
        bins = np.logspace(np.log10(max(1, tag_counts.min())), np.log10(tag_counts.max()), 40)
        ax.hist(tag_counts, bins=bins, color=PRIMARY, edgecolor='white', alpha=0.8)
        ax.set_xscale('log')
        ax.set_xlabel('Tag Count (log scale)', fontsize=12)
    else:
        ax.hist(tag_counts, bins=40, color=PRIMARY, edgecolor='white', alpha=0.8)
        ax.set_xlabel('Tag Count', fontsize=12)

    ax.axvline(x=tag_counts.median(), color=THRESHOLD, linestyle='--', linewidth=2,
               label=f'Median={tag_counts.median():.1f}')
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title(f'H-M2 Tag Count Distribution (has_tags=1 subset, N={len(df_tagged)})', fontsize=12)
    ax.legend(fontsize=10)
    plt.tight_layout()
    out = FIGURES_DIR / 'fig2_tag_count_distribution.png'
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved {out}")


def fig3_partial_regression(df_tagged: pd.DataFrame, results: dict) -> None:
    """Added variable plot: partial out controls via OLS, then scatter log_tag_count_p1 vs residual."""
    import statsmodels.formula.api as smf_ols

    controls = "log_n_instances + log_n_features + age_years + age_sq + C(decade)"

    # Partial out controls from both IV and DV via OLS
    try:
        res_y = smf_ols.ols(f"N_tasks ~ {controls}", data=df_tagged).fit()
        res_x = smf_ols.ols(f"log_tag_count_p1 ~ {controls}", data=df_tagged).fit()
        y_resid = res_y.resid.values
        x_resid = res_x.resid.values

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(x_resid, y_resid, alpha=0.3, s=8, color=PRIMARY, label='Observations')

        # Regression line through residuals
        m, b = np.polyfit(x_resid, y_resid, 1)
        xline = np.linspace(x_resid.min(), x_resid.max(), 200)
        ax.plot(xline, m * xline + b, color=THRESHOLD, linewidth=2, label=f'OLS fit (slope={m:.2f})')

        ax.set_xlabel('Residual log(tag_count+1) | controls', fontsize=12)
        ax.set_ylabel('Residual N_tasks | controls', fontsize=12)
        ax.set_title('H-M2 Partial Regression Plot\n(Added Variable Plot for log_tag_count+1)', fontsize=11)
        ax.legend(fontsize=10)
        ax.axhline(0, color='gray', linestyle=':', linewidth=1)
        ax.axvline(0, color='gray', linestyle=':', linewidth=1)
        plt.tight_layout()
    except Exception as e:
        # Fallback: simple scatter
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(df_tagged['log_tag_count_p1'], df_tagged['N_tasks'], alpha=0.3, s=8, color=PRIMARY)
        ax.set_xlabel('log(tag_count+1)', fontsize=12)
        ax.set_ylabel('N_tasks', fontsize=12)
        ax.set_title(f'H-M2: log(tag_count+1) vs N_tasks (N={len(df_tagged)})\n[Partial regression unavailable: {e}]', fontsize=10)
        plt.tight_layout()

    out = FIGURES_DIR / 'fig3_partial_regression.png'
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved {out}")


def fig4_attenuation_forest(results: dict) -> None:
    iv_with = results['proposed_with_fe']['log_tag_count_p1_stats']
    iv_no   = results['proposed_no_fe']['log_tag_count_p1_stats']

    labels = ['With C(decade) FE', 'Without C(decade) FE']
    irrs   = [iv_with['irr'], iv_no['irr']]
    ci_lo  = [iv_with['ci_lower'], iv_no['ci_lower']]
    ci_hi  = [iv_with['ci_upper'], iv_no['ci_upper']]

    fig, ax = plt.subplots(figsize=(8, 5))
    y_pos = [1, 0]
    colors = [PRIMARY, SECONDARY]

    for i, (y, irr, lo, hi, lbl, col) in enumerate(zip(y_pos, irrs, ci_lo, ci_hi, labels, colors)):
        ax.plot([lo, hi], [y, y], color=col, linewidth=3)
        ax.plot(irr, y, 'o', color=col, markersize=10, zorder=5, label=f'{lbl}: IRR={irr:.4f}')

    ax.axvline(x=1.0, color='gray', linestyle=':', linewidth=1.5, label='IRR=1.0')
    ax.axvline(x=GATE_THRESHOLD, color=THRESHOLD, linestyle='--', linewidth=2,
               label=f'Gate threshold ({GATE_THRESHOLD})')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlabel('Incidence Rate Ratio (IRR) for log(tag_count+1)', fontsize=12)
    attenuation = results.get('attenuation_ratio', None)
    title = 'H-M2 Forest Plot — Attenuation Check'
    if attenuation:
        title += f'\nAttenuation ratio = {attenuation:.4f}'
    ax.set_title(title, fontsize=11)
    ax.legend(fontsize=9, loc='lower right')
    ax.set_ylim(-0.5, 1.8)
    plt.tight_layout()
    out = FIGURES_DIR / 'fig4_attenuation_forest.png'
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved {out}")


def main():
    print("=" * 60)
    print("H-M2 Step 03: Generate Figures")
    print("=" * 60)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n[1] Loading model_results.json...")
    with open(MODEL_RESULTS) as f:
        results = json.load(f)

    print(f"\n[2] Loading tagged_subset.parquet...")
    df_tagged = pd.read_parquet(TAGGED_PARQUET)
    print(f"  N={len(df_tagged)} rows")

    print("\n[3] Generating Fig 1 — Gate Metrics...")
    fig1_gate_metrics(results)

    print("\n[4] Generating Fig 2 — Tag Count Distribution...")
    fig2_tag_count_distribution(df_tagged)

    print("\n[5] Generating Fig 3 — Partial Regression...")
    fig3_partial_regression(df_tagged, results)

    print("\n[6] Generating Fig 4 — Attenuation Forest Plot...")
    fig4_attenuation_forest(results)

    print("\n Figure generation complete")


if __name__ == "__main__":
    main()
