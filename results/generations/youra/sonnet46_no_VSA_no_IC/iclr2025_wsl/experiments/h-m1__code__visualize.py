import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import config


def plot_gate_metrics_bar(results: dict, save_path: Path) -> None:
    names = [k for k, v in results.items() if v is not None]
    vals = [results[k]["max_diff"] for k in names]
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ["steelblue" if v < config.TOL_EQUIV else "tomato" for v in vals]
    ax.bar(names, vals, color=colors)
    ax.axhline(config.TOL_EQUIV, color="red", linestyle="--", label=f"tol={config.TOL_EQUIV:.0e}")
    ax.set_yscale("log")
    ax.set_ylabel("Max Abs Diff")
    ax.set_title("Permutation Equivariance: Max Abs Diff per Encoder")
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=100)
    plt.close()


def plot_cdf(results: dict, save_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    for name, stats in results.items():
        if stats is None:
            continue
        diffs = np.sort(stats["all_diffs"])
        cdf = np.arange(1, len(diffs) + 1) / len(diffs)
        ax.plot(diffs + 1e-12, cdf, label=name)
    ax.set_xscale("log")
    ax.axvline(config.TOL_EQUIV, color="red", linestyle="--", label=f"tol={config.TOL_EQUIV:.0e}")
    ax.set_xlabel("Max Abs Diff")
    ax.set_ylabel("CDF")
    ax.set_title("CDF of Per-Permutation Max Abs Diff")
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=100)
    plt.close()


def plot_diff_histograms(results: dict, save_path: Path) -> None:
    names = [k for k, v in results.items() if v is not None]
    fig, axes = plt.subplots(1, len(names), figsize=(5 * len(names), 4))
    if len(names) == 1:
        axes = [axes]
    for ax, name in zip(axes, names):
        diffs = np.array(results[name]["all_diffs"])
        ax.hist(diffs, bins=50, color="steelblue", edgecolor="white")
        ax.set_title(f"{name}\nmax={results[name]['max_diff']:.2e}")
        ax.set_xlabel("Max Abs Diff")
        ax.set_ylabel("Count")
    plt.tight_layout()
    plt.savefig(save_path, dpi=100)
    plt.close()


def save_all_figures(results: dict) -> None:
    Path(config.FIGURES_DIR).mkdir(parents=True, exist_ok=True)
    plot_gate_metrics_bar(results, Path(config.FIGURES_DIR) / "gate_metrics_bar.png")
    plot_cdf(results, Path(config.FIGURES_DIR) / "cdf_comparison.png")
    plot_diff_histograms(results, Path(config.FIGURES_DIR) / "diff_histograms.png")
    print(f"Figures saved to {config.FIGURES_DIR}")
