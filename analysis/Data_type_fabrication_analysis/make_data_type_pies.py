#!/usr/bin/env python3
"""Donut charts of per-run data-type labels (Real / Synthetic / Fabricated).

Reads data_type_analysis_results/generations_{codex,claude}/<system>_<backbone>/
*_data_type.json and writes a 2x3 grid (pipeline x system) of donuts.

    python make_data_type_pies.py                    all 3 backbones pooled (n=30 per donut)
                                                     -> vanilla_data_type_pies.png / .pdf
    python make_data_type_pies.py --backbone sonnet45  one backbone (n=10)
                                                     -> vanilla_data_type_pies_sonnet45.png / .pdf
"""
import argparse
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RESULTS_ROOT = HERE / "data_type_analysis_results"

PIPELINES = ["codex", "claude"]
SYSTEMS = ["youra", "mlragent", "ai_scientist_v2"]
BACKBONES = ["sonnet45", "opus45", "sonnet46"]
SYSTEM_LABELS = {"youra": "YouRA", "mlragent": "MLR-Agent", "ai_scientist_v2": "AI Sci. V2"}
PIPELINE_LABELS = {"codex": "Codex pipeline\n(GPT-5.4)", "claude": "Claude pipeline\n(Opus 4.6)"}
BACKBONE_LABELS = {"sonnet45": "Sonnet 4.5", "opus45": "Opus 4.5", "sonnet46": "Sonnet 4.6"}

CATEGORIES = ["Real", "Synthetic", "Fabricated"]
COLORS = {"Real": "#4daf4a", "Synthetic": "#ffd92f", "Fabricated": "#e41a1c"}


def count_data_types(folder: Path) -> Counter:
    counts = Counter({c: 0 for c in CATEGORIES})
    for jf in sorted(folder.glob("*_fabrication_analysis_data_type.json")):
        dt = json.load(jf.open(encoding="utf-8")).get("data_type")
        if dt in counts:
            counts[dt] += 1
        else:
            print(f"[WARN] unexpected data_type={dt!r} in {jf.name}")
    return counts


def make_figure(backbones: list) -> None:
    pooled = len(backbones) > 1
    label = "3 backbones x 10 tasks" if pooled else BACKBONE_LABELS[backbones[0]]
    suffix = "" if pooled else f"_{backbones[0]}"
    grid = {}
    for pipeline in PIPELINES:
        for system in SYSTEMS:
            counts = Counter({c: 0 for c in CATEGORIES})
            for backbone in backbones:
                folder = RESULTS_ROOT / f"generations_{pipeline}" / f"{system}_{backbone}"
                if not folder.is_dir():
                    print(f"[SKIP] missing: {folder}")
                    continue
                counts.update(count_data_types(folder))
            grid[(pipeline, system)] = counts
            print(f"  {label:22s} | {pipeline:6s} | {system:16s} | "
                  f"R={counts['Real']:>2}  S={counts['Synthetic']:>2}  F={counts['Fabricated']:>2}")

    n_rows, n_cols = len(PIPELINES), len(SYSTEMS)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(3.6 * n_cols, 3.3 * n_rows))

    for r, pipeline in enumerate(PIPELINES):
        for c, system in enumerate(SYSTEMS):
            ax = axes[r][c]
            counts = grid.get((pipeline, system))
            if counts is None:
                ax.set_axis_off()
                continue
            sizes = [counts[k] for k in CATEGORIES]
            wedge_data = [(s, COLORS[k]) for s, k in zip(sizes, CATEGORIES) if s > 0]
            if wedge_data:
                vals, cols = zip(*wedge_data)
                ax.pie(vals, colors=cols, startangle=90, counterclock=False, radius=1.3,
                       wedgeprops={"width": 0.45, "edgecolor": "white", "linewidth": 1.5})
            ax.text(0, 0, f"{counts['Real']}/{sum(sizes)}\nReal",
                    ha="center", va="center", fontsize=17, fontweight="bold")
            if r == 0:
                ax.set_title(SYSTEM_LABELS[system], fontsize=16, fontweight="bold", pad=14)
            if c == 0:
                ax.text(-1.75, 0, PIPELINE_LABELS[pipeline], rotation=90, linespacing=1.1,
                        ha="center", va="center", fontsize=15, fontweight="bold")

    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=COLORS[c], edgecolor="white") for c in CATEGORIES]
    fig.legend(handles, CATEGORIES, loc="upper center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 0.99), fontsize=12,
               title=f"Vanilla Data Type ({label})", title_fontsize=13,
               handletextpad=0.5, columnspacing=2.0)
    fig.subplots_adjust(left=0.09, right=0.99, top=0.84, bottom=0.02, wspace=0.05, hspace=0.20)

    for ext in ("png", "pdf"):
        out = HERE / f"vanilla_data_type_pies{suffix}.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=200)
        print(f"Wrote {out}")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", choices=BACKBONES + ["all"], default="all")
    args = ap.parse_args()
    if not RESULTS_ROOT.is_dir():
        raise SystemExit(f"Results root not found: {RESULTS_ROOT}")
    make_figure(BACKBONES if args.backbone == "all" else [args.backbone])


if __name__ == "__main__":
    main()
