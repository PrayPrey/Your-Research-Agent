"""H-M3 figures: 5 required plots."""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


CONDITION_COLORS = {
    'A': '#2196F3', 'B': '#4CAF50', 'C': '#FF9800',
    'D': '#F44336', 'E': '#9C27B0', 'F': '#607D8B',
}
CONDITION_LABELS = {
    'A': 'Raw (A)', 'B': 'Scale (B)', 'C': 'Sign (C)',
    'D': 'Both (D)', 'E': 'RandCtrl (E)', 'F': 'Linear (F)',
}


def _savefig(fig, path, figures_dir):
    os.makedirs(figures_dir, exist_ok=True)
    fig.savefig(os.path.join(figures_dir, path), dpi=150, bbox_inches='tight')
    plt.close(fig)


def fig1_rho_by_condition(agg_results, label_names, figures_dir):
    """FR-8.1: Bar chart of mean Spearman ρ per condition × label."""
    conditions = [c for c in ['A', 'B', 'C', 'D', 'E', 'F'] if c in agg_results]
    n_cond = len(conditions)
    n_labels = len(label_names)
    fig, axes = plt.subplots(1, n_labels, figsize=(5 * n_labels, 4), sharey=False)
    if n_labels == 1:
        axes = [axes]

    for ax, label in zip(axes, label_names):
        rhos = [agg_results[c][label]['rho_mean'] for c in conditions]
        ci_los = [agg_results[c][label]['ci_lo'] for c in conditions]
        ci_his = [agg_results[c][label]['ci_hi'] for c in conditions]
        yerr_lo = [r - lo for r, lo in zip(rhos, ci_los)]
        yerr_hi = [hi - r for r, hi in zip(rhos, ci_his)]
        colors = [CONDITION_COLORS.get(c, '#888') for c in conditions]
        bars = ax.bar(range(n_cond), rhos, color=colors,
                      yerr=[yerr_lo, yerr_hi], capsize=4, alpha=0.85)
        ax.set_xticks(range(n_cond))
        ax.set_xticklabels([CONDITION_LABELS.get(c, c) for c in conditions], rotation=30)
        ax.set_ylabel("Spearman ρ")
        ax.set_title(label.replace('_', ' '))
        ax.axhline(0, color='black', linewidth=0.5, linestyle='--')

    fig.suptitle("H-M3: Spearman ρ by Condition (mean ± 95% CI)", fontsize=12)
    fig.tight_layout()
    _savefig(fig, "fig1_rho_by_condition.png", figures_dir)


def fig2_delta_rho_heatmap(agg_results, label_names, figures_dir):
    """FR-8.2: Heatmap of Δρ = ρ_cond - ρ_A."""
    conditions = [c for c in ['B', 'C', 'D', 'E', 'F'] if c in agg_results]
    data = np.array([
        [agg_results[c][label]['rho_mean'] - agg_results['A'][label]['rho_mean']
         for label in label_names]
        for c in conditions
    ])
    fig, ax = plt.subplots(figsize=(6, 3))
    im = ax.imshow(data, cmap='RdYlGn', aspect='auto',
                   vmin=-0.2, vmax=0.2)
    ax.set_xticks(range(len(label_names)))
    ax.set_xticklabels([l.replace('_', '\n') for l in label_names])
    ax.set_yticks(range(len(conditions)))
    ax.set_yticklabels([CONDITION_LABELS.get(c, c) for c in conditions])
    plt.colorbar(im, ax=ax, label='Δρ vs Condition A')
    for i in range(len(conditions)):
        for j in range(len(label_names)):
            ax.text(j, i, f"{data[i,j]:+.3f}", ha='center', va='center', fontsize=9)
    ax.set_title("H-M3: Δρ = ρ_cond − ρ_A (heatmap)")
    fig.tight_layout()
    _savefig(fig, "fig2_delta_rho_heatmap.png", figures_dir)


def fig3_d_vs_e_comparison(agg_results, label_names, figures_dir):
    """FR-8.3: D vs E (symmetry-specific vs random norm control)."""
    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.arange(len(label_names))
    w = 0.35
    for offset, cond in [(-w/2, 'D'), (w/2, 'E')]:
        rhos = [agg_results[cond][label]['rho_mean'] for label in label_names]
        ci_los = [agg_results[cond][label]['ci_lo'] for label in label_names]
        ci_his = [agg_results[cond][label]['ci_hi'] for label in label_names]
        yerr_lo = [r - lo for r, lo in zip(rhos, ci_los)]
        yerr_hi = [hi - r for r, hi in zip(rhos, ci_his)]
        ax.bar(x + offset, rhos, w, label=CONDITION_LABELS[cond],
               color=CONDITION_COLORS[cond], yerr=[yerr_lo, yerr_hi], capsize=4, alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels([l.replace('_', '\n') for l in label_names])
    ax.set_ylabel("Spearman ρ")
    ax.set_title("H-M3: Condition D vs E (symmetry-specific vs random control)")
    ax.legend()
    ax.axhline(0, color='black', linewidth=0.5, linestyle='--')
    fig.tight_layout()
    _savefig(fig, "fig3_d_vs_e.png", figures_dir)


def fig4_frozen_encoder(frozen_results, figures_dir):
    """FR-8.4: Frozen vs full encoder Spearman ρ."""
    if not frozen_results:
        return
    conditions = list(frozen_results.keys())
    labels = list(frozen_results[conditions[0]]['rho_frozen'].keys())
    fig, axes = plt.subplots(1, len(labels), figsize=(5 * len(labels), 4), sharey=False)
    if len(labels) == 1:
        axes = [axes]
    for ax, label in zip(axes, labels):
        frozen_rhos = [frozen_results[c]['rho_frozen'].get(label, 0) for c in conditions]
        full_rhos = [frozen_results[c]['rho_full'].get(label, {})
                     if isinstance(frozen_results[c]['rho_full'].get(label, 0), (int, float))
                     else frozen_results[c]['rho_full'].get(label, {}).get('rho_mean', 0)
                     for c in conditions]
        x = np.arange(len(conditions))
        w = 0.35
        ax.bar(x - w/2, frozen_rhos, w, label='Frozen enc', color='#90CAF9', alpha=0.85)
        ax.bar(x + w/2, full_rhos, w, label='Full train', color='#F44336', alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(conditions)
        ax.set_ylabel("Spearman ρ")
        ax.set_title(label.replace('_', ' '))
        ax.legend()
    fig.suptitle("H-M3: Frozen Encoder vs Full Training", fontsize=12)
    fig.tight_layout()
    _savefig(fig, "fig4_frozen_encoder.png", figures_dir)


def fig5_gate_summary(p1_results, p2_result, figures_dir):
    """FR-8.5: Gate check summary table."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis('off')
    rows = [["Gate", "Label", "Δρ", "CI excl 0", "Pass"]]
    for label, p1 in p1_results.items():
        rows.append([
            "P1", label,
            f"{p1['delta_rho']:+.3f}",
            str(p1['ci_excludes_zero']),
            "✓" if p1['pass'] else "✗",
        ])
    rows.append([
        "P2", f"n_pass={p2_result['n_pass']}/{len(p2_result['per_task'])}",
        "ρ_D > ρ_E", f"≥{p2_result['n_required']}/3",
        "✓" if p2_result['pass'] else "✗",
    ])
    table = ax.table(cellText=rows[1:], colLabels=rows[0],
                     loc='center', cellLoc='center')
    table.auto_set_font_size(True)
    table.scale(1, 1.8)
    ax.set_title("H-M3: Gate Check Summary (SHOULD_WORK)", fontsize=12, pad=20)
    fig.tight_layout()
    _savefig(fig, "fig5_gate_summary.png", figures_dir)


def generate_all_figures(agg_results, label_names, p1_results, p2_result,
                         frozen_results, figures_dir):
    fig1_rho_by_condition(agg_results, label_names, figures_dir)
    fig2_delta_rho_heatmap(agg_results, label_names, figures_dir)
    if 'D' in agg_results and 'E' in agg_results:
        fig3_d_vs_e_comparison(agg_results, label_names, figures_dir)
    if frozen_results:
        fig4_frozen_encoder(frozen_results, figures_dir)
    fig5_gate_summary(p1_results, p2_result, figures_dir)
    print(f"Figures saved to {figures_dir}")
