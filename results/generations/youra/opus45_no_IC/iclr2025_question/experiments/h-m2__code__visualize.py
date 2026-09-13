"""H-M2 Visualization - Box plots, violin plots, heatmaps, forest plots"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from config import FIGURES_DIR, BENCHMARK_NAMES, FACTUAL_FAMILY, ENTITY_FAMILY


def plot_family_boxplot(same: list, cross: list, out_path: Path) -> None:
    """Box plot comparing same-family vs cross-family JS-divergence."""
    fig, ax = plt.subplots(figsize=(8, 6))

    data = [same, cross]
    positions = [1, 2]
    bp = ax.boxplot(data, positions=positions, patch_artist=True, widths=0.6)

    colors = ['#3498db', '#e74c3c']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    # Overlay individual points
    for i, (d, pos) in enumerate(zip(data, positions)):
        x = np.random.normal(pos, 0.04, len(d))
        ax.scatter(x, d, c=colors[i], alpha=0.8, s=50, edgecolors='black', zorder=3)

    ax.axhline(y=0.15, color='gray', linestyle='--', label='Threshold (0.15)')
    ax.set_xticks([1, 2])
    ax.set_xticklabels(['Same-Family', 'Cross-Family'])
    ax.set_ylabel('JS-Divergence')
    ax.set_title('H-M2: Same-Family vs Cross-Family JS-Divergence')
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_family_violin(same: list, cross: list, out_path: Path) -> None:
    """Violin plot with individual points overlaid."""
    fig, ax = plt.subplots(figsize=(8, 6))

    import pandas as pd
    df = pd.DataFrame({
        'JS-Divergence': same + cross,
        'Category': ['Same-Family'] * len(same) + ['Cross-Family'] * len(cross)
    })

    sns.violinplot(data=df, x='Category', y='JS-Divergence', ax=ax, palette=['#3498db', '#e74c3c'])
    sns.stripplot(data=df, x='Category', y='JS-Divergence', ax=ax, color='black', alpha=0.7, size=8)

    ax.axhline(y=0.15, color='gray', linestyle='--', label='Threshold (0.15)')
    ax.set_title('H-M2: Distribution Comparison')
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_js_heatmap_with_families(js_matrix: np.ndarray, names: list, out_path: Path) -> None:
    """6x6 heatmap with family boundary annotations."""
    fig, ax = plt.subplots(figsize=(10, 8))

    mask = np.zeros_like(js_matrix, dtype=bool)
    np.fill_diagonal(mask, True)

    sns.heatmap(
        js_matrix,
        xticklabels=names,
        yticklabels=names,
        annot=True,
        fmt='.3f',
        cmap='RdYlBu_r',
        mask=mask,
        ax=ax,
        vmin=0,
        vmax=0.6,
        cbar_kws={'label': 'JS-Divergence'}
    )

    # Draw family boundary lines
    ax.axhline(y=3, color='black', linewidth=2)
    ax.axvline(x=3, color='black', linewidth=2)

    # Add family labels
    ax.text(1.5, -0.5, 'Factual Recall', ha='center', fontsize=10, fontweight='bold')
    ax.text(4.5, -0.5, 'Entity/Claim', ha='center', fontsize=10, fontweight='bold')

    ax.set_title('H-M2: JS-Divergence Matrix with Error Family Boundaries')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_effect_size_forest(effect_size: float, ci: tuple, out_path: Path) -> None:
    """Forest plot showing Cliff's delta with confidence interval."""
    fig, ax = plt.subplots(figsize=(8, 4))

    y_pos = 0
    ax.errorbar(
        effect_size, y_pos,
        xerr=[[effect_size - ci[0]], [ci[1] - effect_size]],
        fmt='o',
        color='#3498db',
        markersize=12,
        capsize=5,
        capthick=2,
        linewidth=2
    )

    # Reference lines
    ax.axvline(x=0, color='gray', linestyle='-', linewidth=1, label='No effect')
    ax.axvline(x=-0.5, color='green', linestyle='--', linewidth=1, label='Large effect (-0.5)')
    ax.axvline(x=-0.33, color='orange', linestyle=':', linewidth=1, label='Medium effect (-0.33)')

    ax.set_xlim(-1.2, 0.5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_yticks([0])
    ax.set_yticklabels(['Same vs Cross'])
    ax.set_xlabel("Cliff's Delta")
    ax.set_title(f"H-M2: Effect Size (Cliff's δ = {effect_size:.3f})")
    ax.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
