"""Visualization for h-c1 reliability analysis."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot_alpha_bar_chart(results: dict, threshold: float, save_path: str) -> None:
    """Bar chart of Cronbach's alpha per method with CI error bars."""
    methods = [m for m in results if m != "gate_pass"]
    alphas = [results[m]["alpha"] for m in methods]
    ci_lower = [results[m]["ci_lower"] for m in methods]
    ci_upper = [results[m]["ci_upper"] for m in methods]

    yerr = [[a - l for a, l in zip(alphas, ci_lower)],
            [u - a for a, u in zip(alphas, ci_upper)]]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(methods))
    bars = ax.bar(x, alphas, yerr=yerr, capsize=5, color=['#2ecc71' if a > threshold else '#e74c3c' for a in alphas])
    ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold (α={threshold})')
    ax.set_ylabel("Cronbach's Alpha")
    ax.set_xlabel("Attribution Method")
    ax.set_title("Mode Profile Reliability by Attribution Method")
    ax.set_xticks(x)
    ax.set_xticklabels([m.upper() for m in methods])
    ax.set_ylim(0, 1)
    ax.legend()

    for i, (a, m) in enumerate(zip(alphas, methods)):
        ax.annotate(f'{a:.3f}', (i, a + 0.05), ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_reliability_heatmap(results: dict, modes: tuple, save_path: str) -> None:
    """Heatmap of item-total correlations (method x mode)."""
    methods = [m for m in results if m != "gate_pass"]
    data = np.array([
        [results[m]["item_total_correlations"].get(mode, 0) for mode in modes]
        for m in methods
    ])

    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(data, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)

    ax.set_xticks(np.arange(len(modes)))
    ax.set_yticks(np.arange(len(methods)))
    ax.set_xticklabels([m.replace('_', ' ').title() for m in modes])
    ax.set_yticklabels([m.upper() for m in methods])

    for i in range(len(methods)):
        for j in range(len(modes)):
            ax.text(j, i, f'{data[i, j]:.2f}', ha='center', va='center', fontsize=10)

    ax.set_title("Item-Total Correlations (Mode × Method)")
    fig.colorbar(im, ax=ax, label='Correlation')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_alpha_if_dropped(results: dict, modes: tuple, save_path: str) -> None:
    """Grouped bar: alpha-if-dropped per mode vs full alpha."""
    methods = [m for m in results if m != "gate_pass"]

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(methods))
    width = 0.2

    # Full alpha
    full_alphas = [results[m]["alpha"] for m in methods]
    ax.bar(x - 1.5*width, full_alphas, width, label='Full α', color='#3498db')

    # Alpha if each mode dropped
    colors = ['#e74c3c', '#2ecc71', '#f1c40f']
    for i, mode in enumerate(modes):
        dropped = [results[m]["alpha_if_dropped"].get(mode, 0) for m in methods]
        ax.bar(x + (i - 0.5)*width, dropped, width, label=f'Drop {mode}', color=colors[i])

    ax.set_ylabel("Cronbach's Alpha")
    ax.set_xlabel("Attribution Method")
    ax.set_title("Alpha-if-Dropped Analysis")
    ax.set_xticks(x)
    ax.set_xticklabels([m.upper() for m in methods])
    ax.legend(loc='lower right')
    ax.set_ylim(0, 1.1)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
