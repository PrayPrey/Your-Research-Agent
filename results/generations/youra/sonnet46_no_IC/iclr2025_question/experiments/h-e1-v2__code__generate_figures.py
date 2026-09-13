#!/usr/bin/env python3
"""Figures for h-e1-v2 Phase 4 report (D-7).

v2 delta vs h-e1: loops ALL 6 model x dataset cells (skipping any cell whose
cache CSV is not yet present) instead of the hardcoded llama2/triviaqa cell,
and replaces the v1 breach-band anchor chart with plot_anchor_v2_report
(FR-5.4): per-cell within-sweep final-layer AUROC bar + direction-consistency
marker vs V1_DIRECTION_RECORD -- descriptive only, no gate line, no reference
band, no tolerance import.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analysis import build_auroc_grid, corrected_auroc, degeneracy_screen
from constants import (AUROC_GATE, FIGURES_DIR, MODEL_IDS, N_LAYERS,
                       RESULTS_DIR, V1_DIRECTION_RECORD)
import visualize

SIGNALS = ["entropy", "maxprob", "adj_kl"]
DATASETS = ["triviaqa", "truthfulqa"]
CELLS = [(m, d) for m in MODEL_IDS for d in DATASETS]


def _cell_inputs(model_key, dataset_name):
    """Load finalized cache + meta + top1 for one cell; None if not swept yet."""
    cache = Path(f"{RESULTS_DIR}/cache_{model_key}_{dataset_name}.csv")
    meta_p = Path(f"{RESULTS_DIR}/meta_{model_key}_{dataset_name}.json")
    top1_p = Path(f"{RESULTS_DIR}/top1_agreement_{model_key}_{dataset_name}.npy")
    if not (cache.exists() and meta_p.exists() and top1_p.exists()):
        return None
    df = pd.read_csv(cache)
    if "selection" not in set(df["split"]):
        return None                      # mid-generation, not finalized
    return df, json.loads(meta_p.read_text()), np.load(top1_p)


def plot_anchor_v2_report(cells):
    """FR-5.4: cells = {'{m}/{d}': (final_auroc, direction_bool)}. Descriptive
    A2-v2 report -- no gate line, no reference band."""
    names = sorted(cells)
    aurocs = [cells[c][0] for c in names]
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(names, aurocs, color="#47a", width=0.6)
    ax.bar_label(bars, fmt="%.4f", fontsize=8)
    for x, c in enumerate(names):
        m, d = c.split("/")
        v1 = V1_DIRECTION_RECORD.get((m, d))
        consistent = cells[c][1] == v1
        ax.text(x, 0.02, "✓" if consistent else "✗",
                ha="center", fontsize=14,
                color="#2a7" if consistent else "#c33")
    ax.set_ylim(0, max(aurocs) * 1.15 if aurocs else 1)
    ax.set_ylabel("within-sweep final-layer (L32) entropy corrected AUROC")
    ax.set_title("A2-v2 anchor report: per-cell within-sweep final-layer AUROC\n"
                 "(marker = direction consistency vs v1 record, descriptive only)")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    out = Path(FIGURES_DIR) / "anchor_v2_report.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def main():
    figdir = Path(FIGURES_DIR)
    figdir.mkdir(parents=True, exist_ok=True)
    anchor_cells = {}

    for model_key, dataset_name in CELLS:
        loaded = _cell_inputs(model_key, dataset_name)
        if loaded is None:
            print(f"skip {model_key}/{dataset_name}: cache not finalized")
            continue
        df, meta, top1 = loaded
        sel = df[df["split"] == "selection"]
        entropy_grid = sel[[f"entropy_L{i}"
                            for i in range(1, N_LAYERS + 1)]].to_numpy()
        retained = degeneracy_screen(entropy_grid, top1, meta["vocab_size"])
        grid = build_auroc_grid(df, retained)
        final_auroc, direction = corrected_auroc(
            sel["label"].to_numpy(), sel["entropy_L32"].to_numpy())
        anchor_cells[f"{model_key}/{dataset_name}"] = (final_auroc, direction)

        # per-cell AUROC vs depth (renderer logic unchanged from v1)
        fig, ax = plt.subplots(figsize=(9, 5))
        layers = [l + 1 for l in retained]
        for j, sig in enumerate(SIGNALS):
            ax.plot(layers, grid[:, j], marker=".", label=sig)
        ax.axhline(final_auroc, color="gray", ls=":",
                   label=f"final-layer entropy (this sweep) {final_auroc:.4f}")
        ax.axhline(AUROC_GATE, color="k", ls="--",
                   label=f"existence gate {AUROC_GATE}")
        ax.set_xlabel("layer")
        ax.set_ylabel(f"corrected AUROC (selection split, n={len(sel)})")
        ax.set_title(f"h-e1-v2 {model_key}/{dataset_name}: "
                     f"corrected AUROC vs depth")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(figdir / f"auroc_vs_depth_{model_key}_{dataset_name}.png",
                    dpi=150)
        plt.close(fig)

    if anchor_cells:
        plot_anchor_v2_report(anchor_cells)

    # FR-5.6 entropy heatmap for the binding model (unchanged from v1)
    binding = _cell_inputs("llama2", "triviaqa")
    if binding is not None:
        visualize.plot_entropy_heatmap(binding[0], "llama2", "triviaqa")

    print("figures written:", sorted(f.name for f in figdir.glob("*.png")))


if __name__ == "__main__":
    main()
