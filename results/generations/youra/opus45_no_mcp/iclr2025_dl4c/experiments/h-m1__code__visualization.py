"""Visualization functions for H-M1 gradient concentration analysis."""
import numpy as np
import matplotlib.pyplot as plt
import os


def plot_gradient_comparison(
    error_grad: float,
    other_grad: float,
    out_path: str,
) -> None:
    """Required figure: bar chart of error-line vs other-lines gradient."""
    fig, ax = plt.subplots(figsize=(8, 6))

    bars = ax.bar(
        ['Error Line', 'Other Lines'],
        [error_grad, other_grad],
        color=['#d62728', '#1f77b4'],
        edgecolor='black',
        linewidth=1.5
    )

    ax.set_ylabel('Mean Gradient Magnitude', fontsize=12)
    ax.set_title('Gradient Concentration: Error Line vs Other Lines', fontsize=14)

    for bar, val in zip(bars, [error_grad, other_grad]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{val:.4f}', ha='center', va='bottom', fontsize=10)

    ratio = error_grad / max(other_grad, 1e-8)
    ax.text(0.95, 0.95, f'Concentration Ratio: {ratio:.2f}',
            transform=ax.transAxes, ha='right', va='top',
            fontsize=11, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")


def plot_concentration_histogram(
    ratios: list,
    threshold: float = 1.0,
    out_path: str = None,
) -> None:
    """Distribution of concentration ratios across samples."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(ratios, bins=30, color='#1f77b4', edgecolor='black', alpha=0.7)
    ax.axvline(x=threshold, color='#d62728', linestyle='--', linewidth=2,
               label=f'Threshold = {threshold}')

    pct_above = sum(1 for r in ratios if r > threshold) / len(ratios) * 100
    ax.text(0.95, 0.95, f'{pct_above:.1f}% above threshold',
            transform=ax.transAxes, ha='right', va='top',
            fontsize=11, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax.set_xlabel('Concentration Ratio (error_line / other_lines)', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Distribution of Gradient Concentration Ratios', fontsize=14)
    ax.legend()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")


def plot_line_gradient_heatmap(
    samples: list,
    out_path: str,
    window: int = 5,
) -> None:
    """Heatmap with error line centered, shows gradient spread."""
    n_samples = min(len(samples), 50)

    heatmap_data = np.zeros((n_samples, 2 * window + 1))

    for i, sample in enumerate(samples[:n_samples]):
        line_grads = sample.get("line_gradients", {})
        error_line = sample.get("error_line", 0)

        for offset in range(-window, window + 1):
            target_line = error_line + offset
            grad = line_grads.get(target_line, 0.0)
            heatmap_data[i, offset + window] = grad

    row_sums = heatmap_data.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    heatmap_data = heatmap_data / row_sums

    fig, ax = plt.subplots(figsize=(12, 8))

    im = ax.imshow(heatmap_data, aspect='auto', cmap='YlOrRd')
    ax.set_xticks(range(2 * window + 1))
    ax.set_xticklabels([f'{i}' for i in range(-window, window + 1)])

    ax.axvline(x=window, color='black', linestyle='--', linewidth=2, alpha=0.5)

    ax.set_xlabel('Line Offset from Error Line', fontsize=12)
    ax.set_ylabel('Sample Index', fontsize=12)
    ax.set_title('Gradient Distribution Relative to Error Line', fontsize=14)

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Normalized Gradient Magnitude', fontsize=10)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")


def plot_error_type_comparison(
    u_line_ratio: float,
    u_ignore_ratio: float,
    random_ratio: float,
    out_path: str,
) -> None:
    """Bar chart comparing concentration by error type."""
    fig, ax = plt.subplots(figsize=(8, 6))

    categories = ['U_line\n(Reliable)', 'U_ignore\n(Unreliable)', 'Random\n(Baseline)']
    values = [u_line_ratio, u_ignore_ratio, random_ratio]
    colors = ['#2ca02c', '#ff7f0e', '#7f7f7f']

    bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=1.5)

    ax.axhline(y=1.0, color='#d62728', linestyle='--', linewidth=2,
               label='Threshold = 1.0')

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{val:.2f}', ha='center', va='bottom', fontsize=11)

    ax.set_ylabel('Mean Concentration Ratio', fontsize=12)
    ax.set_title('Gradient Concentration by Error Type', fontsize=14)
    ax.legend()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")


def plot_within_lines_distribution(
    within_pcts: list,
    threshold: float = 0.80,
    out_path: str = None,
) -> None:
    """Distribution of '% gradient within +/-2 lines' metric."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(within_pcts, bins=30, color='#2ca02c', edgecolor='black', alpha=0.7)
    ax.axvline(x=threshold, color='#d62728', linestyle='--', linewidth=2,
               label=f'Threshold = {threshold}')

    pct_above = sum(1 for w in within_pcts if w > threshold) / len(within_pcts) * 100
    ax.text(0.05, 0.95, f'{pct_above:.1f}% above threshold',
            transform=ax.transAxes, ha='left', va='top',
            fontsize=11, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax.set_xlabel('Fraction of Gradient Within +/-2 Lines of Error', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Distribution of Gradient Locality', fontsize=14)
    ax.legend()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")


def generate_all_figures(results: dict, figures_dir: str) -> None:
    """Generate all required and optional figures."""
    os.makedirs(figures_dir, exist_ok=True)

    all_results = results.get("all", {})
    per_sample = all_results.get("per_sample_results", [])

    if per_sample:
        error_grad = np.mean([r["error_line_gradient"] for r in per_sample])
        other_grad = np.mean([r["other_line_gradient"] for r in per_sample])
        plot_gradient_comparison(error_grad, other_grad,
                                 os.path.join(figures_dir, "gradient_comparison.png"))

        ratios = [r["concentration_ratio"] for r in per_sample]
        plot_concentration_histogram(ratios, threshold=1.0,
                                     out_path=os.path.join(figures_dir, "concentration_histogram.png"))

        within_pcts = [r["within_2_lines_pct"] for r in per_sample]
        plot_within_lines_distribution(within_pcts, threshold=0.80,
                                       out_path=os.path.join(figures_dir, "within_lines_distribution.png"))

    u_line = results.get("u_line", {})
    u_ignore = results.get("u_ignore", {})
    random_baseline = results.get("random", {})

    u_line_ratio = u_line.get("mean_concentration_ratio", 0) if u_line else 0
    u_ignore_ratio = u_ignore.get("mean_concentration_ratio", 0) if u_ignore else 0
    random_ratio = random_baseline.get("mean_concentration_ratio", 1.0) if random_baseline else 1.0

    plot_error_type_comparison(
        u_line_ratio, u_ignore_ratio, random_ratio,
        os.path.join(figures_dir, "error_type_comparison.png")
    )

    print(f"All figures generated in {figures_dir}")
