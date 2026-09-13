"""H-M3: Generate 5 figures from model results."""
import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
FIGURES_DIR = os.path.join(BASE_DIR, 'figures')
BONF_ALPHA = 0.0167
CATEGORIES = ["0", "1-2", "3-5", "6+"]


def load_results():
    with open(os.path.join(RESULTS_DIR, 'primary_results.json')) as f:
        return json.load(f)


def load_model_results():
    with open(os.path.join(RESULTS_DIR, 'model_results.json')) as f:
        return json.load(f)


def fig1_irr_bar_chart(results, model_results, save_dir):
    cats = ["0", "1-2", "3-5", "6+"]
    irr_vals = [1.0] + [results['irr_by_category'].get(c, 1.0) for c in cats[1:]]
    ci_lo = [1.0] + [results['ci_lower'].get(c, 1.0) for c in cats[1:]]
    ci_hi = [1.0] + [results['ci_upper'].get(c, 1.0) for c in cats[1:]]
    pvals = {c: results['pvalues'].get(c, 1.0) for c in cats[1:]}

    colors = ['#aaaaaa', '#4292c6', '#2166ac', '#053061']
    err_lo = [v - lo for v, lo in zip(irr_vals, ci_lo)]
    err_hi = [hi - v for v, hi in zip(irr_vals, ci_hi)]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(cats, irr_vals, color=colors, alpha=0.85, width=0.6,
                  yerr=[err_lo, err_hi], capsize=5, error_kw={'linewidth': 1.5})

    ax.axhline(1.0, color='black', linestyle='--', linewidth=1.5, label='IRR=1.0 (null)')
    ax.axhline(1.1, color='orange', linestyle=':', linewidth=1.5, label='IRR=1.1 (H-E1 threshold)')

    for i, (cat, irr) in enumerate(zip(cats, irr_vals)):
        ax.text(i, irr + err_hi[i] + 0.05, f'{irr:.3f}', ha='center', va='bottom', fontsize=9)

    ax.set_xlabel('Tag Count Category', fontsize=12)
    ax.set_ylabel('Incidence Rate Ratio (IRR)', fontsize=12)
    ax.set_title('H-M3: Categorical Tag Count Dose-Response\n(NB-2, reference="0")', fontsize=13)
    ax.legend(fontsize=10)
    ax.set_ylim(0, max(irr_vals) * 1.25 + 0.3)
    plt.tight_layout()
    path = os.path.join(save_dir, 'fig1_irr_bar_chart.png')
    fig.savefig(path, dpi=300)
    plt.close(fig)
    print(f"Saved: {path}")


def fig2_dose_response(results, save_dir):
    cats = ["0", "1-2", "3-5", "6+"]
    irr_vals = [1.0] + [results['irr_by_category'].get(c, 1.0) for c in cats[1:]]
    adj_pvals = {
        '0-1-2': results.get('adj_pvals', {}).get('0-1-2'),
        '1-2-3-5': results.get('adj_pvals', {}).get('1-2-3-5'),
        '3-5-6+': results.get('adj_pvals', {}).get('3-5-6+'),
    }

    def color_for(p):
        if p is None: return 'gray'
        if p < BONF_ALPHA: return 'green'
        if p < 0.05: return 'orange'
        return 'red'

    segment_colors = [
        color_for(adj_pvals.get('0-1-2')),
        color_for(adj_pvals.get('1-2-3-5')),
        color_for(adj_pvals.get('3-5-6+')),
    ]

    fig, ax = plt.subplots(figsize=(8, 5))
    xs = list(range(len(cats)))
    ax.plot(xs, irr_vals, 'ko-', markersize=8)
    for i in range(len(cats) - 1):
        ax.plot([xs[i], xs[i+1]], [irr_vals[i], irr_vals[i+1]], '-', color=segment_colors[i], linewidth=2.5)

    ax.axhline(1.0, color='black', linestyle='--', linewidth=1)
    ax.set_xticks(xs)
    ax.set_xticklabels(cats)
    ax.set_xlabel('Tag Count Category', fontsize=12)
    ax.set_ylabel('IRR vs Reference "0"', fontsize=12)
    ax.set_title('H-M3: Dose-Response by Category\n(green=sig p<0.0167, orange=marginal, red=not sig)', fontsize=12)
    for x, y in zip(xs, irr_vals):
        ax.annotate(f'{y:.3f}', (x, y), textcoords='offset points', xytext=(0, 10), ha='center', fontsize=9)
    plt.tight_layout()
    path = os.path.join(save_dir, 'fig2_dose_response.png')
    fig.savefig(path, dpi=300)
    plt.close(fig)
    print(f"Saved: {path}")


def fig3_category_distribution(results, save_dir):
    bin_counts = results.get('bin_counts', {})
    cats = ["0", "1-2", "3-5", "6+"]
    counts = [bin_counts.get(c, 0) for c in cats]
    colors = ['#aaaaaa', '#4292c6', '#2166ac', '#053061']

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(cats, counts, color=colors, alpha=0.85, width=0.6)
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                str(count), ha='center', va='bottom', fontsize=10)
    ax.set_xlabel('Tag Count Category', fontsize=12)
    ax.set_ylabel('Number of Datasets', fontsize=12)
    ax.set_title('H-M3: Dataset Distribution by Tag Count Category\n(N=5,217 total)', fontsize=12)
    plt.tight_layout()
    path = os.path.join(save_dir, 'fig3_category_distribution.png')
    fig.savefig(path, dpi=300)
    plt.close(fig)
    print(f"Saved: {path}")


def fig4_contrast_forest(results, save_dir):
    adj_pvals = results.get('adj_pvals', {})
    contrast_labels = ['1-2 vs 0', '3-5 vs 1-2', '6+ vs 3-5']
    contrast_keys = ['0-1-2', '1-2-3-5', '3-5-6+']

    cat_irr = results.get('irr_by_category', {})
    cat_irr_full = {'0': 1.0, '1-2': cat_irr.get('1-2', 1.0), '3-5': cat_irr.get('3-5', 1.0), '6+': cat_irr.get('6+', 1.0)}
    ci_lo = {'0': 1.0, '1-2': results['ci_lower'].get('1-2', 1.0),
              '3-5': results['ci_lower'].get('3-5', 1.0), '6+': results['ci_lower'].get('6+', 1.0)}
    ci_hi = {'0': 1.0, '1-2': results['ci_upper'].get('1-2', 1.0),
              '3-5': results['ci_upper'].get('3-5', 1.0), '6+': results['ci_upper'].get('6+', 1.0)}

    fig, ax = plt.subplots(figsize=(8, 5))
    ys = list(range(len(contrast_labels)))

    for i, (label, key) in enumerate(zip(contrast_labels, contrast_keys)):
        parts = label.split(' vs ')
        b_cat = parts[0].strip()
        a_cat = parts[1].strip()
        irr_ratio = cat_irr_full.get(b_cat, 1.0) / cat_irr_full.get(a_cat, 1.0)
        lo_ratio = ci_lo.get(b_cat, 1.0)
        hi_ratio = ci_hi.get(b_cat, 1.0)

        p = adj_pvals.get(key)
        color = 'green' if (p is not None and p < BONF_ALPHA) else 'red'
        ax.plot(irr_ratio, i, 'o', color=color, markersize=10)
        ax.plot([lo_ratio, hi_ratio], [i, i], '-', color=color, linewidth=2)
        p_str = f'p={p:.4f}' if p is not None else 'p=N/A'
        ax.text(max(hi_ratio, irr_ratio) + 0.05, i, p_str, va='center', fontsize=9)

    ax.axvline(1.0, color='black', linestyle='--', linewidth=1.5)
    ax.set_yticks(ys)
    ax.set_yticklabels(contrast_labels)
    ax.set_xlabel('IRR Ratio (higher/lower category)', fontsize=11)
    ax.set_title('H-M3: Adjacent Contrast Forest Plot\n(Bonferroni-corrected; green=sig p<0.0167)', fontsize=12)
    plt.tight_layout()
    path = os.path.join(save_dir, 'fig4_contrast_forest.png')
    fig.savefig(path, dpi=300)
    plt.close(fig)
    print(f"Saved: {path}")


def fig5_attenuation(results, model_results, save_dir):
    cats = ["1-2", "3-5", "6+"]
    irr_with_fe = [results['irr_by_category'].get(c, 1.0) for c in cats]
    cat_irr_no_fe = model_results.get('cat_irr_no_fe', {})
    irr_no_fe = [cat_irr_no_fe.get(c, {}).get('irr', 1.0) for c in cats]

    x = np.arange(len(cats))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, irr_with_fe, width, label='With C(decade) FE', color='#2166ac', alpha=0.85)
    ax.bar(x + width/2, irr_no_fe, width, label='Without C(decade) FE (RC-7)', color='#ef8a62', alpha=0.85)
    ax.axhline(1.0, color='black', linestyle='--', linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(cats)
    ax.set_xlabel('Tag Count Category', fontsize=12)
    ax.set_ylabel('IRR vs Reference "0"', fontsize=12)
    ax.set_title('H-M3: Attenuation by Decade FE\n(RC-7 comparison)', fontsize=12)
    ax.legend()
    plt.tight_layout()
    path = os.path.join(save_dir, 'fig5_attenuation.png')
    fig.savefig(path, dpi=300)
    plt.close(fig)
    print(f"Saved: {path}")


def main():
    os.makedirs(FIGURES_DIR, exist_ok=True)
    results = load_results()
    model_results = load_model_results()

    fig1_irr_bar_chart(results, model_results, FIGURES_DIR)
    fig2_dose_response(results, FIGURES_DIR)
    fig3_category_distribution(results, FIGURES_DIR)
    fig4_contrast_forest(results, FIGURES_DIR)
    fig5_attenuation(results, model_results, FIGURES_DIR)
    print("All 5 figures generated.")


if __name__ == '__main__':
    main()
