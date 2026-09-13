"""A-8: Visualizer — 4 required figures for h-m1 corpus contamination analysis."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path

from config import FIGURES_DIR, BENCHMARKS, StyleConfig, FigureConfig

_style = StyleConfig()
_fig = FigureConfig()

AXIS_LABELS = _style.axis_labels


def sig_stars(p_value: float | None) -> str:
    """Significance markers matching h-e1 convention."""
    if p_value is None:
        return "ns"
    if p_value < 0.001:
        return "***"
    if p_value < 0.01:
        return "**"
    if p_value < 0.05:
        return "*"
    return "ns"


def _setup_style():
    sns.set_theme(style=_style.seaborn_theme, context=_style.seaborn_context)


def plot_overlap_bar(
    overlap_scores: dict,
    stats: dict,
    out: Path = FIGURES_DIR / "fig_overlap_comparison.png",
) -> None:
    """Bar chart: mean 13-gram overlap (removed vs retained) per benchmark, 95% CI, sig stars."""
    _setup_style()
    benchmarks = sorted(overlap_scores["removed"].keys())
    n = len(benchmarks)
    x = np.arange(n)
    width = 0.35

    removed_means, removed_cis = [], []
    retained_means, retained_cis = [], []
    for b in benchmarks:
        r = np.array(overlap_scores["removed"][b])
        t = np.array(overlap_scores["retained"][b])
        removed_means.append(np.mean(r))
        removed_cis.append(1.96 * np.std(r) / np.sqrt(len(r)))
        retained_means.append(np.mean(t))
        retained_cis.append(1.96 * np.std(t) / np.sqrt(len(t)))

    fig, ax = plt.subplots(figsize=_fig.bar_figsize)
    bars_r = ax.bar(x - width / 2, removed_means, width, yerr=removed_cis,
                    label="Removed", color=_fig.color_removed, alpha=0.85, capsize=4)
    bars_t = ax.bar(x + width / 2, retained_means, width, yerr=retained_cis,
                    label="Retained", color=_fig.color_retained, alpha=0.85, capsize=4)

    # Significance stars
    per_bm = stats.get("per_benchmark", {})
    for i, b in enumerate(benchmarks):
        if b in per_bm:
            p = per_bm[b].get("p_corrected")
            mark = sig_stars(p)
            ymax = max(removed_means[i] + removed_cis[i], retained_means[i] + retained_cis[i])
            ax.text(x[i], ymax * 1.05, mark, ha="center", va="bottom",
                    fontsize=_style.font_size_annot, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([AXIS_LABELS.get(b, b) for b in benchmarks],
                        fontsize=_style.font_size_tick)
    ax.set_ylabel("Mean 13-gram Overlap Rate", fontsize=_style.font_size_axis)
    ax.set_title(_style.title_bar, fontsize=_style.font_size_title)
    ax.legend(fontsize=_style.font_size_tick)
    ax.set_ylim(bottom=0)

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=_fig.dpi)
    plt.close(fig)
    print(f"✓ Saved {out}")


def plot_violin(
    overlap_scores: dict,
    out: Path = FIGURES_DIR / "fig_overlap_distributions.png",
) -> None:
    """Per-benchmark violin plots of overlap distributions (removed vs retained)."""
    _setup_style()
    benchmarks = sorted(overlap_scores["removed"].keys())
    n = len(benchmarks)
    fig, axes = plt.subplots(1, n, figsize=_fig.violin_figsize, sharey=False)
    if n == 1:
        axes = [axes]

    for ax, b in zip(axes, benchmarks):
        r = np.array(overlap_scores["removed"][b])
        t = np.array(overlap_scores["retained"][b])
        data = [r, t]
        parts = ax.violinplot(data, showmedians=True)
        colors = [_fig.color_removed, _fig.color_retained]
        for pc, color in zip(parts["bodies"], colors):
            pc.set_facecolor(color)
            pc.set_alpha(0.7)
        ax.set_xticks([1, 2])
        ax.set_xticklabels(["Removed", "Retained"], fontsize=_style.font_size_tick)
        ax.set_title(AXIS_LABELS.get(b, b), fontsize=_style.font_size_tick)
        ax.set_ylabel("Overlap Rate" if b == benchmarks[0] else "")

    fig.suptitle(_style.title_violin, fontsize=_style.font_size_title)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=_fig.dpi)
    plt.close(fig)
    print(f"✓ Saved {out}")


def plot_rank_correlation(
    stats: dict,
    out: Path = FIGURES_DIR / "fig_rank_correlation.png",
) -> None:
    """Scatter: expected contamination rank vs observed mean overlap diff (4 benchmarks)."""
    _setup_style()
    expected_rank = {"mmlu": 1, "arc_challenge": 2, "hellaswag": 3, "winogrande": 4}
    per_bm = stats.get("per_benchmark", {})

    benchmarks = [b for b in expected_rank if b in per_bm]
    if not benchmarks:
        print("  Skipping rank correlation plot: no benchmark data")
        return

    x = [expected_rank[b] for b in benchmarks]
    y = [per_bm[b]["mean_removed"] - per_bm[b]["mean_retained"] for b in benchmarks]
    labels = [AXIS_LABELS.get(b, b) for b in benchmarks]

    fig, ax = plt.subplots(figsize=_fig.rank_figsize)
    ax.scatter(x, y, s=80, color=_fig.color_removed, zorder=5)
    for xi, yi, lb in zip(x, y, labels):
        ax.annotate(lb, (xi, yi), textcoords="offset points", xytext=(6, 4),
                    fontsize=_style.font_size_annot)
    ax.set_xlabel("Expected Contamination Rank (1=highest)", fontsize=_style.font_size_axis)
    ax.set_ylabel("Mean Overlap Diff (removed − retained)", fontsize=_style.font_size_axis)
    ax.set_title(_style.title_rank, fontsize=_style.font_size_title)
    ax.invert_xaxis()

    sp = stats.get("spearman", {})
    rho = sp.get("correlation", float("nan"))
    ax.text(0.05, 0.95, f"ρ = {rho:.2f}", transform=ax.transAxes,
            fontsize=_style.font_size_annot, va="top")

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=_fig.dpi)
    plt.close(fig)
    print(f"✓ Saved {out}")


def plot_subset_breakdown(
    ablation_results: dict,
    out: Path = FIGURES_DIR / "fig_subset_breakdown.png",
) -> None:
    """Bar: mean removed-doc overlap by Pile subset per benchmark (from subset ablation)."""
    _setup_style()
    subset_data = ablation_results.get("subset_stratified", {})
    if not subset_data:
        print("  Skipping subset breakdown: no subset ablation data")
        return

    subsets = sorted(subset_data.keys())
    benchmarks = sorted(next(iter(subset_data.values())).keys())
    n_sub = len(subsets)
    n_bm = len(benchmarks)
    x = np.arange(n_sub)
    width = 0.8 / n_bm

    fig, ax = plt.subplots(figsize=_fig.subset_figsize)
    cmap = plt.get_cmap("tab10")
    for j, bm in enumerate(benchmarks):
        means = [subset_data[s][bm]["mean_removed"] for s in subsets]
        ax.bar(x + j * width - (n_bm - 1) * width / 2, means, width,
               label=AXIS_LABELS.get(bm, bm), color=cmap(j), alpha=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(subsets, rotation=30, ha="right", fontsize=_style.font_size_tick)
    ax.set_ylabel("Mean 13-gram Overlap (Removed Docs)", fontsize=_style.font_size_axis)
    ax.set_title(_style.title_subset, fontsize=_style.font_size_title)
    ax.legend(fontsize=_style.font_size_tick)

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=_fig.dpi)
    plt.close(fig)
    print(f"✓ Saved {out}")


def generate_all_figures(
    overlap_scores: dict,
    stats: dict,
    ablation_results: dict,
) -> None:
    """Generate all 4 required figures."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plot_overlap_bar(overlap_scores, stats)
    plot_violin(overlap_scores)
    plot_rank_correlation(stats)
    plot_subset_breakdown(ablation_results)
    print(f"✓ All figures saved to {FIGURES_DIR}")
