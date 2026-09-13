import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_auroc_comparison(results, cfg, out_path):
    """Bar chart: 4-method AUROC on TruthfulQA with 95% CI error bars."""
    methods = ["SE", "SCG", "TE", "VC"]
    aurocs = [results[f"auroc_{m.lower()}"] for m in methods]
    cis = [results[f"auroc_{m.lower()}_ci"] for m in methods]
    colors = [cfg.color_se, cfg.color_scg, cfg.color_te, cfg.color_vc]
    yerrs = [[(a - ci[0]), (ci[1] - a)] for a, ci in zip(aurocs, cis)]
    yerrs_arr = np.array(yerrs).T

    fig, ax = plt.subplots(figsize=cfg.fig_size_bar, dpi=cfg.figure_dpi)
    x = np.arange(len(methods))
    ax.bar(x, aurocs, color=colors, alpha=0.85, width=0.6,
           yerr=yerrs_arr, capsize=5, error_kw={"elinewidth": 1.5})
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=12)
    ax.set_ylabel("AUROC", fontsize=12)
    ax.set_title("H-C1: Four-Method AUROC on TruthfulQA (N=200)", fontsize=13)
    ax.set_ylim(0, 1.0)
    ax.axhline(0.5, color="gray", linestyle="--", linewidth=1, alpha=0.5, label="Random")
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(out_path, dpi=cfg.figure_dpi)
    plt.close()
    print(f"Saved: {out_path}")


def plot_cross_benchmark(results_hc1, hm4_baselines, cfg, out_path):
    """Grouped bar: TriviaQA (H-M4) vs TruthfulQA (H-C1) for SE, TE, VC."""
    methods = ["SE", "TE", "VC"]
    hm4_vals = [
        hm4_baselines.get("auroc_se", 0.286),
        hm4_baselines.get("auroc_te", 0.4381),
        hm4_baselines.get("auroc_vc", 0.4463),
    ]
    hc1_vals = [results_hc1[f"auroc_{m.lower()}"] for m in methods]

    fig, ax = plt.subplots(figsize=cfg.fig_size_cross, dpi=cfg.figure_dpi)
    x = np.arange(len(methods))
    width = 0.35
    ax.bar(x - width / 2, hm4_vals, width, label="TriviaQA (H-M4, N=98)",
           color="#8172B2", alpha=0.75)
    ax.bar(x + width / 2, hc1_vals, width, label="TruthfulQA (H-C1, N=200)",
           color="#C44E52", alpha=0.75)
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=12)
    ax.set_ylabel("AUROC", fontsize=12)
    ax.set_title("Cross-Benchmark AUROC: TriviaQA vs TruthfulQA", fontsize=13)
    ax.set_ylim(0, 1.0)
    ax.axhline(0.5, color="gray", linestyle="--", linewidth=1, alpha=0.5)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(out_path, dpi=cfg.figure_dpi)
    plt.close()
    print(f"Saved: {out_path}")


def plot_rank_ordering(results, cfg, out_path):
    """Point plot: method ranking with CI. Sorted by AUROC descending."""
    methods_sorted = sorted(
        [("SE", results["auroc_se"], results["auroc_se_ci"]),
         ("SCG", results["auroc_scg"], results["auroc_scg_ci"]),
         ("TE", results["auroc_te"], results["auroc_te_ci"]),
         ("VC", results["auroc_vc"], results["auroc_vc_ci"])],
        key=lambda x: x[1], reverse=True
    )
    names = [m[0] for m in methods_sorted]
    vals = [m[1] for m in methods_sorted]
    cis = [m[2] for m in methods_sorted]
    xerrs = [[(v - ci[0]), (ci[1] - v)] for v, ci in zip(vals, cis)]
    xerrs_arr = np.array(xerrs).T

    fig, ax = plt.subplots(figsize=cfg.fig_size_rank, dpi=cfg.figure_dpi)
    y = np.arange(len(names))
    ax.errorbar(vals, y, xerr=xerrs_arr, fmt="o", capsize=5,
                color="#2d2d2d", elinewidth=1.5, markersize=8)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=12)
    ax.set_xlabel("AUROC (95% CI)", fontsize=12)
    ax.set_title("H-C1 Method Ranking — TruthfulQA", fontsize=13)
    ax.axvline(0.5, color="gray", linestyle="--", linewidth=1, alpha=0.5)
    plt.tight_layout()
    plt.savefig(out_path, dpi=cfg.figure_dpi)
    plt.close()
    print(f"Saved: {out_path}")


def plot_vc_confidence_distribution(raw_confidences_hc1, hm4_baselines, cfg, out_path):
    """Histogram: VC confidence distribution TruthfulQA vs TriviaQA reference."""
    fig, ax = plt.subplots(figsize=cfg.fig_size_dist, dpi=cfg.figure_dpi)
    ax.hist(raw_confidences_hc1, bins=20, alpha=0.7, color=cfg.color_vc,
            label=f"TruthfulQA (N={len(raw_confidences_hc1)})", density=True)
    ax.set_xlabel("VC Confidence", fontsize=12)
    ax.set_ylabel("Density", fontsize=12)
    ax.set_title("VC Confidence Distribution — TruthfulQA", fontsize=13)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(out_path, dpi=cfg.figure_dpi)
    plt.close()
    print(f"Saved: {out_path}")


def plot_bootstrap_distributions(bootstrap_samples, cfg, out_path):
    """Simple bar with CI for bootstrap AUROC per method (violin approximation)."""
    # Use simple bar + CI since we store only point + CI, not full bootstrap arrays
    methods = ["SE", "SCG", "TE", "VC"]
    colors = [cfg.color_se, cfg.color_scg, cfg.color_te, cfg.color_vc]
    aurocs = [bootstrap_samples[m.lower()]["auroc"] for m in methods]
    cis = [bootstrap_samples[m.lower()]["ci"] for m in methods]
    yerrs = [[(a - ci[0]), (ci[1] - a)] for a, ci in zip(aurocs, cis)]
    yerrs_arr = np.array(yerrs).T

    fig, ax = plt.subplots(figsize=cfg.fig_size_violin, dpi=cfg.figure_dpi)
    x = np.arange(len(methods))
    ax.bar(x, aurocs, color=colors, alpha=0.75, width=0.5,
           yerr=yerrs_arr, capsize=6, error_kw={"elinewidth": 2})
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=12)
    ax.set_ylabel("AUROC", fontsize=12)
    ax.set_title("Bootstrap AUROC Distributions (95% CI) — TruthfulQA", fontsize=13)
    ax.set_ylim(0, 1.0)
    ax.axhline(0.5, color="gray", linestyle="--", linewidth=1, alpha=0.5)
    plt.tight_layout()
    plt.savefig(out_path, dpi=cfg.figure_dpi)
    plt.close()
    print(f"Saved: {out_path}")


def generate_all_figures(results, hm4_baselines, raw_confidences, cfg, figures_dir):
    """Generate all 5 figures."""
    os.makedirs(figures_dir, exist_ok=True)
    bootstrap_samples = results.get("bootstrap_samples", {})

    plot_auroc_comparison(results, cfg, os.path.join(figures_dir, cfg.fname_bar))
    plot_cross_benchmark(results, hm4_baselines, cfg, os.path.join(figures_dir, cfg.fname_cross))
    plot_rank_ordering(results, cfg, os.path.join(figures_dir, cfg.fname_rank))
    plot_vc_confidence_distribution(raw_confidences, hm4_baselines, cfg,
                                     os.path.join(figures_dir, cfg.fname_dist))
    plot_bootstrap_distributions(bootstrap_samples, cfg, os.path.join(figures_dir, cfg.fname_violin))
    print("All 5 figures generated.")
