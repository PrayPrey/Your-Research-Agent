import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from config import CFG

logger = logging.getLogger(__name__)
FIGURES_DIR = CFG.paths.figures_dir


def _savefig(fig, name):
    Path(FIGURES_DIR).mkdir(parents=True, exist_ok=True)
    path = f"{FIGURES_DIR}/{name}"
    fig.savefig(path, dpi=CFG.viz.dpi, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved %s", path)


def fig1_rho_bar_chart(cell_results):
    tested = [c for c in cell_results if c.status == "TESTED"]
    if not tested:
        logger.warning("fig1: no tested cells")
        return
    labels = [f"{c.encoder}\n{c.benchmark}\n{c.model_size}" for c in tested]
    rhos = [c.result.rho for c in tested]
    sigs = [c.result.significant for c in tested]
    fig, ax = plt.subplots(figsize=CFG.viz.fig1_size)
    bars = ax.bar(labels, rhos, color=["#1f77b4" if s else "#aec7e8" for s in sigs])
    for bar, sig, rho in zip(bars, sigs, rhos):
        if sig:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                    CFG.viz.significance_marker, ha="center", fontsize=CFG.viz.significance_fontsize)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Spearman ρ")
    ax.set_title("Spearman ρ per cell (* = p < 0.05)")
    _savefig(fig, "fig1_rho_bar_chart.png")


def fig2_scatter_panels(sim_matrices, pass_matrices, cell_results):
    tested = [c for c in cell_results if c.status == "TESTED"]
    if not tested:
        return
    n = len(tested)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5), squeeze=False)
    conditions = CFG.source_conditions
    colors = CFG.viz.condition_colors
    for ax, cell in zip(axes[0], tested):
        sv = cell.sim_vec
        pv = cell.pass_vec
        mask = ~np.isnan(pv)
        sim_ranks = np.argsort(np.argsort(sv[mask]))
        pass_ranks = np.argsort(np.argsort(pv[mask]))
        for idx, (sr, pr) in enumerate(zip(sim_ranks, pass_ranks)):
            cond_idx = np.where(mask)[0][idx]
            ax.scatter(sr, pr, color=colors[cond_idx], s=100, zorder=5)
            ax.annotate(conditions[cond_idx][:2], (sr, pr), textcoords="offset points",
                        xytext=(5, 5), fontsize=8)
        r = cell.result
        ax.set_title(f"{cell.encoder}/{cell.benchmark}\nρ={r.rho:.3f} p={r.pvalue:.4f}")
        ax.set_xlabel("Embedding sim rank")
        ax.set_ylabel("pass@1 rank")
    fig.tight_layout()
    _savefig(fig, "fig2_scatter_panels.png")


def fig3_null_distribution(cell_results):
    tested = [c for c in cell_results if c.status == "TESTED" and c.result.can_test]
    if not tested:
        return
    # most significant cell
    cell = min(tested, key=lambda c: c.result.pvalue)
    r = cell.result
    fig, ax = plt.subplots(figsize=CFG.viz.fig3_size)
    ax.hist(r.null_distribution, bins=50, color="#aec7e8", edgecolor="white", label="Null distribution")
    ax.axvline(r.rho, color="red", linewidth=2, label=f"Observed ρ={r.rho:.3f}\np={r.pvalue:.4f}")
    ax.set_xlabel("Spearman ρ")
    ax.set_ylabel("Count")
    ax.set_title(f"Null distribution — {cell.encoder}/{cell.benchmark}")
    ax.legend()
    _savefig(fig, "fig3_null_distribution.png")


def fig4_rank_heatmap(sim_matrices, pass_matrices):
    conditions = [c[:2].upper() for c in CFG.source_conditions]
    encoders = list(sim_matrices.keys())
    data = []
    row_labels = []
    for enc in encoders:
        mat = sim_matrices[enc]
        for j, bm in enumerate(CFG.benchmarks):
            col = mat[:, j]
            data.append(np.argsort(np.argsort(col)))
            row_labels.append(f"sim/{enc}/{bm}")
    for model_size, pass_mat in pass_matrices.items():
        for j, bm in enumerate(CFG.benchmarks):
            col = pass_mat[:, j]
            if np.all(np.isnan(col)):
                continue
            data.append(np.argsort(np.argsort(np.nan_to_num(col, nan=-1))))
            row_labels.append(f"pass/{model_size}/{bm}")
    if not data:
        return
    fig, ax = plt.subplots(figsize=CFG.viz.fig4_size)
    sns.heatmap(np.array(data), annot=True, fmt="d", xticklabels=conditions,
                yticklabels=row_labels, cmap="Blues", ax=ax)
    ax.set_title("Condition rank comparison (embedding vs performance)")
    _savefig(fig, "fig4_rank_heatmap.png")


def fig5_dual_encoder(cell_results):
    tested = [c for c in cell_results if c.status == "TESTED"]
    benchmarks = sorted(set(c.benchmark for c in tested))
    if not benchmarks:
        return
    fig, ax = plt.subplots(figsize=CFG.viz.fig5_size)
    for bm in benchmarks:
        cells_bm = {c.encoder: c for c in tested if c.benchmark == bm}
        if "codebert" in cells_bm and "minilm" in cells_bm:
            ax.scatter(cells_bm["codebert"].result.rho,
                       cells_bm["minilm"].result.rho,
                       label=bm, s=120)
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.axvline(0, color="gray", linewidth=0.8)
    ax.set_xlabel("CodeBERT ρ")
    ax.set_ylabel("MiniLM ρ")
    ax.set_title("Dual-encoder concordance")
    ax.legend()
    _savefig(fig, "fig5_dual_encoder.png")


def save_all_figures(sim_matrices, pass_matrices, cell_results):
    Path(FIGURES_DIR).mkdir(parents=True, exist_ok=True)
    fig1_rho_bar_chart(cell_results)
    fig2_scatter_panels(sim_matrices, pass_matrices, cell_results)
    fig3_null_distribution(cell_results)
    fig4_rank_heatmap(sim_matrices, pass_matrices)
    fig5_dual_encoder(cell_results)
