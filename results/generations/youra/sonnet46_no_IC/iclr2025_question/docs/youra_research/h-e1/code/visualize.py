"""h-e1 visualization: 4 required figures (A-6, FR-5.2..5.6)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from constants import AUROC_GATE, FIGURES_DIR, H_E1_REFERENCES, N_LAYERS

SIGNALS = ["entropy", "maxprob", "adj_kl"]


def _fig_path(name):
    Path(FIGURES_DIR).mkdir(parents=True, exist_ok=True)
    return Path(FIGURES_DIR) / name


def plot_gate_bar_chart(gate_results: dict):
    """FR-5.2 mandatory: target (0.55) vs actual best intermediate AUROC per cell."""
    cells = sorted(gate_results)
    actual = [gate_results[c]["best_auroc"] for c in cells]
    x = np.arange(len(cells))
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(x, actual, color=["#2a7" if gate_results[c]["gate_pass"] else "#c33"
                                    for c in cells])
    ax.axhline(AUROC_GATE, color="k", ls="--", label=f"gate {AUROC_GATE}")
    ax.set_xticks(x, [f"{m}\n{d}" for m, d in (c.split("/") for c in cells)])
    ax.set_ylabel("best intermediate corrected AUROC (selection)")
    ax.set_ylim(0.4, max(0.75, max((a for a in actual if a == a), default=0.75) + 0.05))
    ax.bar_label(bars, fmt="%.3f")
    ax.legend()
    ax.set_title("h-e1 gate metrics: target vs actual")
    p = _fig_path("gate_metrics_bar.png")
    fig.tight_layout(); fig.savefig(p, dpi=150); plt.close(fig)
    return p


def plot_auroc_heatmap(auroc_grids: dict, retained_layers: dict):
    """FR-5.3: 6 panels (3 models x 2 datasets), layer x signal corrected AUROC."""
    cells = sorted(auroc_grids)
    fig, axes = plt.subplots(2, 3, figsize=(18, 7))
    for ax, cell in zip(axes.flat, cells):
        full = np.full((N_LAYERS, 3), np.nan)
        for i, l in enumerate(retained_layers[cell]):
            full[l] = auroc_grids[cell][i]
        im = ax.imshow(full.T, aspect="auto", vmin=0.5, vmax=0.75, cmap="viridis")
        ax.set_yticks(range(3), SIGNALS)
        ax.set_xlabel("layer")
        ax.set_title(cell)
    fig.colorbar(im, ax=axes.ravel().tolist(), label="corrected AUROC")
    fig.suptitle("h-e1 layer x signal corrected AUROC (selection split)")
    p = _fig_path("auroc_heatmap.png")
    fig.savefig(p, dpi=150); plt.close(fig)
    return p


def plot_auroc_vs_depth(auroc_grids: dict, retained_layers: dict):
    """FR-5.4: AUROC-vs-depth curves per signal + final-layer baseline + gate lines."""
    cells = sorted(auroc_grids)
    fig, axes = plt.subplots(2, 3, figsize=(18, 8), sharey=True)
    for ax, cell in zip(axes.flat, cells):
        layers = [l + 1 for l in retained_layers[cell]]
        for j, sig in enumerate(SIGNALS):
            ax.plot(layers, auroc_grids[cell][:, j], marker=".", label=sig)
        model_key, dataset = cell.split("/")
        ax.axhline(H_E1_REFERENCES[(model_key, dataset)], color="gray", ls=":",
                   label="h-e1 final-layer ref")
        ax.axhline(AUROC_GATE, color="k", ls="--", label=f"gate {AUROC_GATE}")
        ax.set_title(cell); ax.set_xlabel("layer")
    axes.flat[0].set_ylabel("corrected AUROC"); axes.flat[0].legend(fontsize=7)
    fig.suptitle("h-e1 corrected AUROC vs depth (selection split)")
    p = _fig_path("auroc_vs_depth.png")
    fig.tight_layout(); fig.savefig(p, dpi=150); plt.close(fig)
    return p


def plot_entropy_heatmap(cache_df, model_key: str = "llama2",
                         dataset_name: str = "triviaqa"):
    """FR-5.6 (Task A-7, no v1 counterpart): examples x layers entropy heatmap,
    selection split only, correct vs incorrect groups (mechanism intuition)."""
    sel = cache_df[cache_df["split"] == "selection"]
    if sel.empty:
        raise ValueError(
            f"plot_entropy_heatmap: no 'selection' rows in cache_df for "
            f"{model_key}/{dataset_name} -- run the sweep/finalization first")
    cols = [f"entropy_L{i}" for i in range(1, N_LAYERS + 1)]
    groups = [("correct (label=0)", sel[sel["label"] == 0][cols].to_numpy()),
              ("incorrect (label=1)", sel[sel["label"] == 1][cols].to_numpy())]
    vmin = min((np.nanmin(a) for _, a in groups if a.size), default=0.0)
    vmax = max((np.nanmax(a) for _, a in groups if a.size), default=1.0)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, (name, arr) in zip(axes, groups):
        if arr.size:
            im = ax.imshow(arr, aspect="auto", cmap="magma",
                           vmin=vmin, vmax=vmax)
            fig.colorbar(im, ax=ax, label="entropy (nats)")
        ax.set_title(f"{name}, n={len(arr)}")
        ax.set_xlabel("layer")
        ax.set_ylabel("example (selection split)")
    fig.suptitle(
        f"h-e1 per-layer logit-lens entropy: {model_key}/{dataset_name}")
    p = _fig_path(f"entropy_heatmap_{model_key}.png")
    fig.tight_layout(); fig.savefig(p, dpi=150); plt.close(fig)
    return p


def plot_degeneracy_report(retained_layers: dict):
    """FR-5.5: dropped vs retained layers per cell."""
    cells = sorted(retained_layers)
    fig, ax = plt.subplots(figsize=(10, 5))
    for y, cell in enumerate(cells):
        kept = set(retained_layers[cell])
        for l in range(N_LAYERS):
            ax.scatter(l + 1, y, marker="s", s=60,
                       color="#2a7" if l in kept else "#ccc")
    ax.set_yticks(range(len(cells)), cells)
    ax.set_xlabel("layer (green=retained, gray=dropped)")
    ax.set_title("h-e1 degeneracy screen")
    p = _fig_path("degeneracy_screen.png")
    fig.tight_layout(); fig.savefig(p, dpi=150); plt.close(fig)
    return p
