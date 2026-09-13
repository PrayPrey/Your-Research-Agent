from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

from distributional_moments import SegmentMoments
from directional_tests import DirectionalTestResults
from verifier import GateResult


def plot_gate_metrics(
    results: DirectionalTestResults,
    gate: GateResult,
    figures_dir: Path,
) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    bars = ax.bar(
        ['skew_pre', 'skew_post'],
        [results.skew_pre, results.skew_post],
        color=['#2196F3', '#4CAF50' if results.metric1_pass else '#F44336']
    )
    ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax.set_title(f'Metric 1: Skewness Direction\n{"PASS" if results.metric1_pass else "FAIL"}')
    ax.set_ylabel('Fisher-Pearson G1 skewness (bias=False)')
    for bar, val in zip(bars, [results.skew_pre, results.skew_post]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f'{val:.3f}', ha='center', va='bottom')

    ax = axes[1]
    metric_labels = ['M1\nskew\ndirection', 'M2\np10\nlower tail',
                     'M3\nperm p\n(skew diff)', 'M4\nMW p\n(pre>post)']
    metric_values = [
        1.0 if results.metric1_pass else 0.0,
        1.0 if results.metric2_pass else 0.0,
        results.perm_p_skew_diff,
        results.mw_pvalue,
    ]
    pass_flags = [results.metric1_pass, results.metric2_pass,
                  results.metric3_pass, results.metric4_pass]
    colors = ['#4CAF50' if p else '#F44336' for p in pass_flags]
    ax.bar(metric_labels, metric_values, color=colors, alpha=0.8)
    ax.axhline(0.10, color='orange', linewidth=1.5, linestyle='--', label='p=0.10 threshold')
    ax.set_ylim(0, 1.1)
    ax.set_ylabel('p-value / pass indicator')
    ax.set_title(
        f'Gate: {"PASS" if gate.gate_passed else "EXPLORE"} '
        f'({gate.metrics_passed}/4 metrics consistent with H1)'
    )
    ax.legend()

    figures_dir.mkdir(parents=True, exist_ok=True)
    out = figures_dir / "gate_metrics.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out


def plot_histogram_overlay(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    pre_moments: SegmentMoments,
    post_moments: SegmentMoments,
    figures_dir: Path,
) -> Path:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(pre_segment, bins=20, alpha=0.4, color='#F44336', label=f'Pre (n={pre_moments.n})', density=True)
    ax.hist(post_segment, bins=20, alpha=0.4, color='#2196F3', label=f'Post (n={post_moments.n})', density=True)

    x_range = np.linspace(
        min(pre_segment.min(), post_segment.min()) - 0.05,
        max(pre_segment.max(), post_segment.max()) + 0.05,
        300
    )
    kde_pre = gaussian_kde(pre_segment)
    kde_post = gaussian_kde(post_segment)
    ax.plot(x_range, kde_pre(x_range), color='#C62828', linewidth=2, label='Pre KDE')
    ax.plot(x_range, kde_post(x_range), color='#0D47A1', linewidth=2, label='Post KDE')

    ax.axvline(pre_moments.p10, color='#C62828', linestyle=':', linewidth=1.5,
               label=f'Pre p10={pre_moments.p10:.3f}')
    ax.axvline(post_moments.p10, color='#0D47A1', linestyle=':', linewidth=1.5,
               label=f'Post p10={post_moments.p10:.3f}')

    ax.set_xlabel('Residual CoV')
    ax.set_ylabel('Density')
    ax.set_title(
        f'Pre vs Post Residual CoV Distribution\n'
        f'skew_pre={pre_moments.skewness:.3f}, skew_post={post_moments.skewness:.3f}'
    )
    ax.legend()

    out = figures_dir / "histogram_overlay.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out


def plot_moments_table(
    pre_moments: SegmentMoments,
    post_moments: SegmentMoments,
    figures_dir: Path,
) -> Path:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis('off')

    rows = ['Mean', 'Variance', 'Skewness', 'Kurtosis (excess)']
    pre_vals = [f'{pre_moments.mean:.4f}', f'{pre_moments.variance:.6f}',
                f'{pre_moments.skewness:.4f}', f'{pre_moments.kurtosis:.4f}']
    post_vals = [f'{post_moments.mean:.4f}', f'{post_moments.variance:.6f}',
                 f'{post_moments.skewness:.4f}', f'{post_moments.kurtosis:.4f}']

    table = ax.table(
        cellText=[[r, p, q] for r, p, q in zip(rows, pre_vals, post_vals)],
        colLabels=['Moment', f'Pre (n={pre_moments.n})', f'Post (n={post_moments.n})'],
        cellLoc='center', loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.8)
    ax.set_title('Distribution Moments: Pre vs Post Segments', pad=20, fontsize=14)

    out = figures_dir / "moments_table.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out


def plot_ecdf(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    pre_moments: SegmentMoments,
    post_moments: SegmentMoments,
    figures_dir: Path,
) -> Path:
    fig, ax = plt.subplots(figsize=(10, 6))

    pre_sorted = np.sort(pre_segment)
    pre_cdf = np.arange(1, len(pre_sorted) + 1) / len(pre_sorted)
    ax.step(pre_sorted, pre_cdf, color='#C62828', linewidth=2, label=f'Pre (n={pre_moments.n})')

    post_sorted = np.sort(post_segment)
    post_cdf = np.arange(1, len(post_sorted) + 1) / len(post_sorted)
    ax.step(post_sorted, post_cdf, color='#0D47A1', linewidth=2, label=f'Post (n={post_moments.n})')

    x_low = min(pre_moments.p10, post_moments.p10)
    x_high = max(pre_moments.p25, post_moments.p25)
    ax.axvspan(x_low, x_high, alpha=0.15, color='gold', label='Lower tail (p10-p25 region)')

    ax.axvline(pre_moments.p10, color='#C62828', linestyle=':', alpha=0.7)
    ax.axvline(post_moments.p10, color='#0D47A1', linestyle=':', alpha=0.7)

    ax.set_xlabel('Residual CoV')
    ax.set_ylabel('Cumulative Probability')
    ax.set_title('Empirical CDF: Pre vs Post Residual CoV (Lower-Tail Focus)')
    ax.legend()

    out = figures_dir / "ecdf.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out


def plot_qq(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    figures_dir: Path,
) -> Path:
    fig, ax = plt.subplots(figsize=(8, 8))

    n_quantiles = min(len(pre_segment), len(post_segment))
    probs = np.linspace(0, 1, n_quantiles + 2)[1:-1]
    q_pre = np.quantile(pre_segment, probs)
    q_post = np.quantile(post_segment, probs)

    ax.scatter(q_pre, q_post, alpha=0.7, color='#7B1FA2', s=40, label='Quantile pairs')

    lo = min(q_pre.min(), q_post.min())
    hi = max(q_pre.max(), q_post.max())
    ax.plot([lo, hi], [lo, hi], 'k--', linewidth=1.2, label='y=x (equal distributions)')

    ax.set_xlabel('Pre-segment quantiles')
    ax.set_ylabel('Post-segment quantiles')
    ax.set_title('Q-Q Plot: Pre vs Post Residual CoV\n(Points below diagonal: post concentrated lower)')
    ax.legend()

    out = figures_dir / "qq_plot.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out


def save_all_figures(
    pre_segment: np.ndarray,
    post_segment: np.ndarray,
    pre_moments: SegmentMoments,
    post_moments: SegmentMoments,
    results: DirectionalTestResults,
    gate: GateResult,
    figures_dir: Path,
) -> list:
    figures_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        plot_gate_metrics(results, gate, figures_dir),
        plot_histogram_overlay(pre_segment, post_segment, pre_moments, post_moments, figures_dir),
        plot_moments_table(pre_moments, post_moments, figures_dir),
        plot_ecdf(pre_segment, post_segment, pre_moments, post_moments, figures_dir),
        plot_qq(pre_segment, post_segment, figures_dir),
    ]
    print(f"Saved {len(paths)} figures to {figures_dir}")
    return paths
