"""visualizer.py — 4 required figures for H-M1."""
from __future__ import annotations
from pathlib import Path
from typing import List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
try:
    import seaborn as sns
    _HAS_SNS = True
except ImportError:
    _HAS_SNS = False


def plot_variance_bar(
    global_var: float,
    pre_var: float,
    post_var: float,
    p_one_tailed: float,
    out_dir: Path,
) -> Path:
    """Bar chart: global_var vs pre_var vs post_var with F-test p annotation."""
    fig, ax = plt.subplots(figsize=(7, 5))
    labels = ["Global (N=111)", "Pre-breakpoint", "Post-breakpoint"]
    values = [global_var, pre_var, post_var]
    colors = ["steelblue", "royalblue", "tomato"]
    bars = ax.bar(labels, values, color=colors, edgecolor="black", linewidth=0.8)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.02,
                f"{val:.4f}", ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("Variance (ddof=1)")
    ax.set_title(f"Residual CoV Variance by Segment\nF-test p (one-tailed) = {p_one_tailed:.4f}")
    ax.set_ylim(0, max(values) * 1.25)
    sig_str = "p < 0.10 ✓" if p_one_tailed < 0.10 else f"p = {p_one_tailed:.4f}"
    ax.annotate(sig_str, xy=(1, pre_var), xytext=(1.3, pre_var * 1.15),
                fontsize=10, color="darkgreen" if p_one_tailed < 0.10 else "red",
                arrowprops=dict(arrowstyle="->", color="gray"))
    fig.tight_layout()
    out_path = out_dir / "fig01_variance_bar.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")
    return out_path


def plot_scatter_with_breakpoint(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
    out_dir: Path,
) -> Path:
    """Scatter residual_CoV vs paper_count, vertical line at breakpoint."""
    fig, ax = plt.subplots(figsize=(8, 5))
    pre_pc = paper_counts[:paper_count_star_idx]
    post_pc = paper_counts[paper_count_star_idx:]
    pre_rc = residual_cov[:paper_count_star_idx]
    post_rc = residual_cov[paper_count_star_idx:]

    ax.scatter(pre_pc, pre_rc, color="royalblue", label="Pre-breakpoint", alpha=0.7, s=40, zorder=3)
    ax.scatter(post_pc, post_rc, color="tomato", label="Post-breakpoint", alpha=0.7, s=40, zorder=3)

    bp_val = paper_counts[paper_count_star_idx] if paper_count_star_idx < len(paper_counts) else paper_counts[paper_count_star_idx - 1]
    ax.axvline(x=bp_val, color="black", linestyle="--", linewidth=1.5, label=f"paper_count* = {bp_val}")
    ax.axhline(y=0, color="gray", linestyle=":", linewidth=0.8)

    ax.set_xlabel("Paper Count")
    ax.set_ylabel("Residual CoV")
    ax.set_title("Residual CoV vs Paper Count (OLS-detrended)")
    ax.legend()
    fig.tight_layout()
    out_path = out_dir / "fig02_scatter.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")
    return out_path


def plot_kde_overlay(
    pre: np.ndarray,
    post: np.ndarray,
    residual_cov: np.ndarray,
    out_dir: Path,
) -> Path:
    """KDE of pre / post / full-series residual_CoV."""
    fig, ax = plt.subplots(figsize=(7, 5))
    if _HAS_SNS:
        sns.kdeplot(pre, ax=ax, label=f"Pre (n={len(pre)})", color="royalblue", fill=True, alpha=0.3)
        sns.kdeplot(post, ax=ax, label=f"Post (n={len(post)})", color="tomato", fill=True, alpha=0.3)
        sns.kdeplot(residual_cov, ax=ax, label=f"Full (N={len(residual_cov)})", color="gray", linestyle="--")
    else:
        for arr, label, color, ls in [
            (pre, f"Pre (n={len(pre)})", "royalblue", "-"),
            (post, f"Post (n={len(post)})", "tomato", "-"),
            (residual_cov, f"Full (N={len(residual_cov)})", "gray", "--"),
        ]:
            from scipy.stats import gaussian_kde
            kde = gaussian_kde(arr)
            x = np.linspace(arr.min() - 0.1, arr.max() + 0.1, 300)
            ax.plot(x, kde(x), label=label, color=color, linestyle=ls)

    ax.axvline(0, color="black", linestyle=":", linewidth=0.8)
    ax.set_xlabel("Residual CoV")
    ax.set_ylabel("Density")
    ax.set_title("KDE: Pre / Post / Full-Series Residual CoV")
    ax.legend()
    fig.tight_layout()
    out_path = out_dir / "fig03_kde.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")
    return out_path


def plot_boxplot(
    pre: np.ndarray,
    post: np.ndarray,
    residual_cov: np.ndarray,
    out_dir: Path,
) -> Path:
    """Box plots: pre / post / full-series residual_CoV distributions."""
    fig, ax = plt.subplots(figsize=(7, 5))
    data = [pre, post, residual_cov]
    labels = [f"Pre\n(n={len(pre)})", f"Post\n(n={len(post)})", f"Full\n(N={len(residual_cov)})"]
    bp = ax.boxplot(data, labels=labels, patch_artist=True, notch=False)
    colors = ["royalblue", "tomato", "lightgray"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.axhline(0, color="gray", linestyle=":", linewidth=0.8)
    ax.set_ylabel("Residual CoV")
    ax.set_title("Residual CoV Distributions: Pre / Post / Full")
    fig.tight_layout()
    out_path = out_dir / "fig04_boxplot.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")
    return out_path


def save_all_figures(
    paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    paper_count_star_idx: int,
    results: dict,
    out_dir: Path,
) -> List[Path]:
    """Call all 4 plot functions. Return list of saved paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    pre = residual_cov[:paper_count_star_idx]
    post = residual_cov[paper_count_star_idx:]
    paths = [
        plot_variance_bar(
            results["global_variance"], results["pre_variance"],
            results["post_variance"], results["p_one_tailed"], out_dir
        ),
        plot_scatter_with_breakpoint(paper_counts, residual_cov, paper_count_star_idx, out_dir),
        plot_kde_overlay(pre, post, residual_cov, out_dir),
        plot_boxplot(pre, post, residual_cov, out_dir),
    ]
    return paths
