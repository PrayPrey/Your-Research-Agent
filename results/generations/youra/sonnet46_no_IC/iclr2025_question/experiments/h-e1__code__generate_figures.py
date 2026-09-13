#!/usr/bin/env python3
"""LLM-generated figures for h-e1 Phase 4 report.

Grounded ONLY in data that exists: the finalized llama2/triviaqa cell
(donor-reused, split assigned) plus its meta/top1 artifacts. The other 5
cells were never swept (A2 anchor halt), so no figures are fabricated for them.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analysis import build_auroc_grid, degeneracy_screen
from constants import AUROC_GATE, BASELINE_TOLERANCE, FIGURES_DIR, N_LAYERS, RESULTS_DIR
import visualize

SIGNALS = ["entropy", "maxprob", "adj_kl"]
CELL = ("llama2", "triviaqa")
REF = 0.5186
OBS_SEL, OBS_FULL = 0.5928, 0.5739


def main():
    figdir = Path(FIGURES_DIR)
    figdir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(f"{RESULTS_DIR}/cache_llama2_triviaqa.csv")
    meta = json.loads(Path(f"{RESULTS_DIR}/meta_llama2_triviaqa.json").read_text())
    top1 = np.load(f"{RESULTS_DIR}/top1_agreement_llama2_triviaqa.npy")
    sel = df[df["split"] == "selection"]
    entropy_grid = sel[[f"entropy_L{i}" for i in range(1, N_LAYERS + 1)]].to_numpy()
    retained = degeneracy_screen(entropy_grid, top1, meta["vocab_size"])
    grid = build_auroc_grid(df, retained)

    # 1. AUROC vs depth (headline: the binding cell)
    fig, ax = plt.subplots(figsize=(9, 5))
    layers = [l + 1 for l in retained]
    for j, sig in enumerate(SIGNALS):
        ax.plot(layers, grid[:, j], marker=".", label=sig)
    ax.axhline(OBS_SEL, color="gray", ls=":",
               label=f"final-layer entropy (this sweep) {OBS_SEL:.4f}")
    ax.axhline(AUROC_GATE, color="k", ls="--", label=f"existence gate {AUROC_GATE}")
    ax.set_xlabel("layer")
    ax.set_ylabel("corrected AUROC (selection split, n=500)")
    ax.set_title("h-e1 llama2/triviaqa: corrected AUROC vs depth")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(figdir / "auroc_vs_depth_llama2_triviaqa.png", dpi=150)
    plt.close(fig)

    # 2. Anchor check visual (the gate that fired)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.axhspan(REF - BASELINE_TOLERANCE, REF + BASELINE_TOLERANCE,
               color="#2a7", alpha=0.2, label=f"reference ±{BASELINE_TOLERANCE}")
    ax.axhline(REF, color="#2a7", ls="-", label=f"v1 reference {REF}")
    bars = ax.bar(["selection split\n(n=500)", "full set\n(n=1000)"],
                  [OBS_SEL, OBS_FULL], color=["#c33", "#c33"], width=0.5)
    ax.bar_label(bars, fmt="%.4f")
    ax.set_ylim(0.45, 0.65)
    ax.set_ylabel("final-layer entropy corrected AUROC")
    ax.set_title("A2 anchor check FAILED: llama2/triviaqa\n"
                 "(reference provenance = different protocol; see 04_validation.md)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(figdir / "anchor_check_llama2_triviaqa.png", dpi=150)
    plt.close(fig)

    # 3. Degeneracy screen map (single measured cell)
    fig, ax = plt.subplots(figsize=(9, 2.4))
    kept = set(retained)
    for l in range(N_LAYERS):
        ax.scatter(l + 1, 0, marker="s", s=90,
                   color="#2a7" if l in kept else "#ccc")
    ax.set_yticks([0], ["llama2/triviaqa"])
    ax.set_xlabel("layer (green=retained, gray=dropped)")
    ax.set_title(f"h-e1 degeneracy screen: {len(retained)}/32 layers retained")
    fig.tight_layout()
    fig.savefig(figdir / "degeneracy_screen_llama2_triviaqa.png", dpi=150)
    plt.close(fig)

    # 4. Entropy heatmap (FR-5.6, uses the implemented plot_entropy_heatmap)
    p = visualize.plot_entropy_heatmap(df, "llama2", "triviaqa")

    print("figures written:", sorted(f.name for f in figdir.glob("*.png")))


if __name__ == "__main__":
    main()
