"""H-M2 Visualizer: 5 figures for variance compression analysis."""
from __future__ import annotations

from pathlib import Path
from typing import List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import f as f_dist

from analyzer import VarianceCompressionResults


def plot_gate_metrics(results: VarianceCompressionResults, out_dir: Path) -> Path:
    """Bar chart: bf_p_two_tailed vs 0.05 threshold, variance_ratio vs 1.0 threshold."""
    fig, axes = plt.subplots(1, 2, figsize=(8, 6))

    # BF p-value
    ax = axes[0]
    val = results["bf_p_two_tailed"]
    color = "green" if val < 0.05 else "red"
    ax.bar(["BF p-value"], [val], color=color, alpha=0.7)
    ax.axhline(0.05, color="black", linestyle="--", label="threshold=0.05")
    ax.set_title(f"BF p={val:.4f} ({'PASS' if val < 0.05 else 'FAIL'})")
    ax.set_ylabel("p-value")
    ax.legend()

    # Variance ratio
    ax = axes[1]
    val = results["variance_ratio"]
    color = "green" if val < 1.0 else "red"
    ax.bar(["Variance ratio\n(post/pre)"], [val], color=color, alpha=0.7)
    ax.axhline(1.0, color="black", linestyle="--", label="threshold=1.0")
    ax.set_title(f"ratio={val:.4f} ({'PASS' if val < 1.0 else 'FAIL'})")
    ax.set_ylabel("Variance ratio")
    ax.legend()

    fig.suptitle("Gate Metrics: H-M2")
    fig.tight_layout()
    out_path = out_dir / "gate_metrics.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_boxplots(pre: np.ndarray, post: np.ndarray, out_dir: Path) -> Path:
    """Side-by-side box plots pre vs post residual CoV."""
    fig, ax = plt.subplots(figsize=(8, 6))
    bp = ax.boxplot(
        [pre, post],
        labels=["Pre-breakpoint", "Post-breakpoint"],
        patch_artist=True,
    )
    bp["boxes"][0].set_facecolor("orange")
    bp["boxes"][0].set_alpha(0.7)
    bp["boxes"][1].set_facecolor("steelblue")
    bp["boxes"][1].set_alpha(0.7)
    var_pre = float(np.var(pre, ddof=1))
    var_post = float(np.var(post, ddof=1))
    ax.set_title("Residual CoV Distribution by Regime")
    ax.set_ylabel("Residual CoV")
    ax.text(
        0.5, 0.95,
        f"var_pre={var_pre:.4f}, var_post={var_post:.4f}",
        transform=ax.transAxes,
        ha="center", va="top",
        fontsize=9, bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )
    fig.tight_layout()
    out_path = out_dir / "boxplots_pre_post.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_variance_bars(results: VarianceCompressionResults, out_dir: Path) -> Path:
    """Horizontal bar: var_pre vs var_post with ratio annotation."""
    fig, ax = plt.subplots(figsize=(8, 6))
    labels = ["var_pre", "var_post"]
    values = [results["var_pre"], results["var_post"]]
    colors = ["orange", "steelblue"]
    bars = ax.barh(labels, values, color=colors, alpha=0.7)
    ratio = results["variance_ratio"]
    ax.set_title("Variance Comparison: Pre vs Post Breakpoint")
    ax.set_xlabel("Variance (ddof=1)")
    ax.text(
        0.98, 0.5,
        f"ratio={ratio:.3f} (post/pre)",
        transform=ax.transAxes,
        ha="right", va="center",
        fontsize=10, bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )
    fig.tight_layout()
    out_path = out_dir / "variance_bars.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_scatter_regime(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
    results: VarianceCompressionResults,
    out_dir: Path,
) -> Path:
    """Scatter N=111 colored by regime (pre=orange, post=blue) with ±1 SD bounds."""
    fig, ax = plt.subplots(figsize=(10, 6))

    bp_value = paper_counts[paper_count_star_idx]
    pre_mask = paper_counts < bp_value
    post_mask = ~pre_mask

    ax.scatter(paper_counts[pre_mask], residual_cov[pre_mask],
               color="orange", label="Pre-breakpoint", alpha=0.7)
    ax.scatter(paper_counts[post_mask], residual_cov[post_mask],
               color="steelblue", label="Post-breakpoint", alpha=0.7)

    # ±1 SD bands per regime
    pre_vals = residual_cov[pre_mask]
    post_vals = residual_cov[post_mask]
    ax.axhspan(pre_vals.mean() - pre_vals.std(), pre_vals.mean() + pre_vals.std(),
               alpha=0.1, color="orange", label="Pre ±1 SD")
    ax.axhspan(post_vals.mean() - post_vals.std(), post_vals.mean() + post_vals.std(),
               alpha=0.1, color="steelblue", label="Post ±1 SD")

    ax.axvline(bp_value, color="black", linestyle="--", label=f"paper_count*={bp_value}")
    ax.set_title("Residual CoV by Regime (N=111)")
    ax.set_xlabel("Paper Count")
    ax.set_ylabel("Residual CoV")
    ax.legend(fontsize=8)
    fig.tight_layout()
    out_path = out_dir / "scatter_regime.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_f_distribution(results: VarianceCompressionResults, out_dir: Path) -> Path:
    """F(1, N-2) distribution with BF test statistic position annotated."""
    fig, ax = plt.subplots(figsize=(8, 5))

    df1, df2 = 1, 109  # F(1, 111-2)
    x = np.linspace(0, max(results["bf_stat"] * 1.5, 6.0), 500)
    y = f_dist.pdf(x, df1, df2)
    ax.plot(x, y, "k-", linewidth=2)

    bf_stat = results["bf_stat"]
    bf_p = results["bf_p_two_tailed"]
    critical = float(f_dist.ppf(0.95, df1, df2))

    # Shade right tail from bf_stat
    x_fill = x[x >= bf_stat]
    y_fill = f_dist.pdf(x_fill, df1, df2)
    ax.fill_between(x_fill, y_fill, alpha=0.3, color="red", label=f"p={bf_p:.4f}")

    ax.axvline(bf_stat, color="red", linestyle="-", label=f"BF stat={bf_stat:.4f}")
    ax.axvline(critical, color="black", linestyle="--", label=f"critical(α=0.05)={critical:.4f}")

    ax.set_title(f"F(1,109) — BF Test Statistic Position")
    ax.set_xlabel("F-statistic")
    ax.set_ylabel("Density")
    ax.legend(fontsize=8)
    fig.tight_layout()
    out_path = out_dir / "f_distribution.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def save_all_figures(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
    results: VarianceCompressionResults,
    out_dir: Path,
) -> List[Path]:
    """Run all 5 figure functions; return list of saved paths."""
    out_dir.mkdir(parents=True, exist_ok=True)

    pre = residual_cov[:paper_count_star_idx]
    post = residual_cov[paper_count_star_idx:]

    saved = []
    saved.append(plot_gate_metrics(results, out_dir))
    saved.append(plot_boxplots(pre, post, out_dir))
    saved.append(plot_variance_bars(results, out_dir))
    saved.append(plot_scatter_regime(paper_counts, residual_cov, paper_count_star_idx, results, out_dir))
    saved.append(plot_f_distribution(results, out_dir))

    print(f"Saved {len(saved)} figures to {out_dir}")
    return saved
