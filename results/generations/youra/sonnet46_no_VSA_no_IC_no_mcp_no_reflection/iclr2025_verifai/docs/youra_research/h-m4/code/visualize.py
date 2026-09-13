"""H-M4 visualization: 5 required figures."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from config import CATEGORIES, CATEGORY_COLORS, FigureConfig, LogScaleConfig

_CFG = FigureConfig()
_LOG = LogScaleConfig()


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _apply_log_scale(ax, cfg: LogScaleConfig = None) -> None:
    if cfg is None:
        cfg = _LOG
    ax.set_yscale("log", base=cfg.log_base)
    ax.set_yticks(cfg.tick_positions)
    ax.set_yticklabels(cfg.tick_labels)


def plot_efficiency_ratios(
    ratios: dict[str, float],
    ci_bounds: dict[str, tuple],
    output_dir: str,
) -> None:
    _ensure_dir(output_dir)
    fig, ax = plt.subplots(figsize=_CFG.fig_size_bar)
    cats = CATEGORIES
    vals = [ratios.get(c, 0.0) for c in cats]
    colors = [CATEGORY_COLORS[c] for c in cats]

    # Error bars from CI bounds
    yerr_low = [max(0, vals[i] - (ci_bounds.get(cats[i], (vals[i], vals[i]))[0]))
                for i in range(len(cats))]
    yerr_high = [(ci_bounds.get(cats[i], (vals[i], vals[i]))[1] - vals[i])
                 for i in range(len(cats))]

    bars = ax.bar(cats, vals, color=colors, yerr=[yerr_low, yerr_high],
                  capsize=6, edgecolor='black', linewidth=0.8)
    ax.set_xlabel("Feedback Category", fontsize=_CFG.font_size_label)
    ax.set_ylabel("Efficiency Ratio (Δpass@1 / mean overhead s)", fontsize=_CFG.font_size_label)
    ax.set_title("H-M4: Efficiency Ratios per Feedback Category\n(with 95% Bootstrap CI)",
                 fontsize=_CFG.font_size_title)
    ax.tick_params(labelsize=_CFG.font_size_tick)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig_efficiency_ratios.png"), dpi=_CFG.dpi)
    plt.close()


def plot_overhead_boxplots(overhead_by_cat: dict[str, list[float]], output_dir: str) -> None:
    _ensure_dir(output_dir)
    fig, ax = plt.subplots(figsize=_CFG.fig_size_boxplot)
    data = [overhead_by_cat.get(c, [0.001]) for c in CATEGORIES]
    bp = ax.boxplot(data, labels=CATEGORIES, patch_artist=True, notch=False)
    for patch, cat in zip(bp['boxes'], CATEGORIES):
        patch.set_facecolor(CATEGORY_COLORS[cat])
        patch.set_alpha(0.7)
    _apply_log_scale(ax)
    ax.set_xlabel("Feedback Category", fontsize=_CFG.font_size_label)
    ax.set_ylabel("Wall-clock Overhead (s, log scale)", fontsize=_CFG.font_size_label)
    ax.set_title("H-M4: Per-Problem Overhead by Category", fontsize=_CFG.font_size_title)
    ax.tick_params(labelsize=_CFG.font_size_tick)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig_overhead_boxplots.png"), dpi=_CFG.dpi)
    plt.close()


def plot_overhead_violins(overhead_by_cat: dict[str, list[float]], output_dir: str) -> None:
    _ensure_dir(output_dir)
    fig, ax = plt.subplots(figsize=_CFG.fig_size_violin)
    parts = ax.violinplot(
        [overhead_by_cat.get(c, [0.001]) for c in CATEGORIES],
        positions=range(len(CATEGORIES)),
        showmedians=True,
    )
    for i, (pc, cat) in enumerate(zip(parts['bodies'], CATEGORIES)):
        pc.set_facecolor(CATEGORY_COLORS[cat])
        pc.set_alpha(0.7)
    ax.set_xticks(range(len(CATEGORIES)))
    ax.set_xticklabels(CATEGORIES, fontsize=_CFG.font_size_tick)
    _apply_log_scale(ax)
    ax.set_xlabel("Feedback Category", fontsize=_CFG.font_size_label)
    ax.set_ylabel("Wall-clock Overhead (s, log scale)", fontsize=_CFG.font_size_label)
    ax.set_title("H-M4: Overhead Distributions (Violin)", fontsize=_CFG.font_size_title)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig_overhead_violins.png"), dpi=_CFG.dpi)
    plt.close()


def plot_efficiency_scatter(
    delta_pass: dict[str, float], mean_overhead: dict[str, float], output_dir: str
) -> None:
    _ensure_dir(output_dir)
    fig, ax = plt.subplots(figsize=_CFG.fig_size_scatter)
    for cat in CATEGORIES:
        x = mean_overhead.get(cat, 0.0)
        y = delta_pass.get(cat, 0.0)
        ax.scatter(x, y, color=CATEGORY_COLORS[cat], s=120, label=cat, zorder=5)
        ax.annotate(cat, (x, y), textcoords="offset points", xytext=(6, 4),
                    fontsize=_CFG.font_size_tick)
    ax.set_xscale("log")
    ax.set_xlabel("Mean Wall-clock Overhead (s, log scale)", fontsize=_CFG.font_size_label)
    ax.set_ylabel("Δpass@1 (after repair – baseline)", fontsize=_CFG.font_size_label)
    ax.set_title("H-M4: Efficiency Scatter\n(Δpass@1 vs. mean overhead)", fontsize=_CFG.font_size_title)
    ax.legend(fontsize=_CFG.font_size_tick)
    ax.tick_params(labelsize=_CFG.font_size_tick)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig_efficiency_scatter.png"), dpi=_CFG.dpi)
    plt.close()


def plot_overhead_heatmap(
    overhead_matrix: np.ndarray,
    task_ids: list[str],
    categories: list[str],
    output_dir: str,
) -> None:
    _ensure_dir(output_dir)
    fig, ax = plt.subplots(figsize=_CFG.fig_size_heatmap)
    log_matrix = np.log10(np.clip(overhead_matrix, _LOG.heatmap_vmin, _LOG.heatmap_vmax))
    im = ax.imshow(log_matrix.T, aspect="auto", cmap="viridis",
                   vmin=np.log10(_LOG.heatmap_vmin), vmax=np.log10(_LOG.heatmap_vmax))
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("log10(overhead s)", fontsize=_CFG.font_size_label)
    ax.set_yticks(range(len(categories)))
    ax.set_yticklabels(categories, fontsize=_CFG.font_size_tick)
    ax.set_xlabel("Problem index", fontsize=_CFG.font_size_label)
    ax.set_ylabel("Feedback Category", fontsize=_CFG.font_size_label)
    ax.set_title("H-M4: Per-Problem Overhead Heatmap (538 × 4, log scale)", fontsize=_CFG.font_size_title)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig_overhead_heatmap.png"), dpi=_CFG.dpi)
    plt.close()


def generate_all_figures(results: list[dict], ratios: dict, ci_bounds: dict, output_dir: str) -> None:
    from collections import defaultdict

    overhead_by_cat: dict[str, list[float]] = defaultdict(list)
    for r in results:
        overhead_by_cat[r['category']].append(r['total_overhead_s'])

    # Δpass@1 per category
    pass_after = {}
    for cat in CATEGORIES:
        cat_results = [r for r in results if r['category'] == cat]
        if cat_results:
            pass_after[cat] = float(np.mean([r['final_pass'] for r in cat_results]))
        else:
            pass_after[cat] = 0.0
    baseline_vals = [float(r.get('initial_pass', False)) for r in results if r['category'] == CATEGORIES[0]]
    baseline_rate = float(np.mean(baseline_vals)) if baseline_vals else 0.0
    delta_pass = {cat: pass_after.get(cat, 0.0) - baseline_rate for cat in CATEGORIES}
    mean_overhead = {cat: float(np.mean(overhead_by_cat[cat])) if overhead_by_cat[cat] else 0.0
                     for cat in CATEGORIES}

    # Build overhead matrix (n_problems × n_cats)
    task_ids = sorted({r['task_id'] for r in results})
    task_idx = {tid: i for i, tid in enumerate(task_ids)}
    cat_idx = {cat: i for i, cat in enumerate(CATEGORIES)}
    matrix = np.full((len(task_ids), len(CATEGORIES)), fill_value=_LOG.heatmap_vmin)
    for r in results:
        i = task_idx.get(r['task_id'])
        j = cat_idx.get(r['category'])
        if i is not None and j is not None:
            matrix[i, j] = max(r['total_overhead_s'], _LOG.heatmap_vmin)

    plot_efficiency_ratios(ratios, ci_bounds, output_dir)
    plot_overhead_boxplots(dict(overhead_by_cat), output_dir)
    plot_overhead_violins(dict(overhead_by_cat), output_dir)
    plot_efficiency_scatter(delta_pass, mean_overhead, output_dir)
    plot_overhead_heatmap(matrix, task_ids, CATEGORIES, output_dir)

    print(f"All 5 figures saved to {output_dir}")
