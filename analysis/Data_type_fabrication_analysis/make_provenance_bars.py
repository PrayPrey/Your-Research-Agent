#!/usr/bin/env python3
"""Grouped bar chart of conservative real-data counts per backbone.

Reads the per-run data-type JSONs under data_type_analysis_results/
generations_{claude,codex}. A run counts as real-data-based only when BOTH
analyzers label it "Real" (the conservative, maximum-synthetic reading used
in the paper). Writes provenance_real_data_bars.pdf next to this script.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "data_type_analysis_results"
BACKBONES = [("sonnet45", "Sonnet 4.5"), ("opus45", "Opus 4.5"), ("sonnet46", "Sonnet 4.6")]
SYSTEMS = [("youra", "YouRA", "#0173B2"),
           ("ai_scientist_v2", "AI Scientist V2", "#DE8F05"),
           ("mlragent", "MLR-Agent", "#949494")]


def load(analyzer: str) -> dict[str, dict[tuple[str, str], str]]:
    out: dict[str, dict[tuple[str, str], str]] = defaultdict(dict)
    for f in sorted((RESULTS / analyzer).glob("*/*_data_type.json")):
        system, bb = f.parent.name.rsplit("_", 1)
        task = f.name.replace("_fabrication_analysis_data_type.json", "")
        with f.open(encoding="utf-8") as fh:
            out[system][(bb, task)] = json.load(fh)["data_type"]
    return out


def main() -> None:
    ca, co = load("generations_claude"), load("generations_codex")
    counts = {s: {bb: sum(1 for (b, t), v in ca[s].items()
                          if b == bb and v == "Real" and co[s][(b, t)] == "Real")
                  for bb, _ in BACKBONES}
              for s, _, _ in SYSTEMS}
    for s, _, _ in SYSTEMS:
        print(s, counts[s])

    fig, ax = plt.subplots(figsize=(5.4, 2.6))
    width = 0.26
    for i, (key, label, color) in enumerate(SYSTEMS):
        xs = [j + (i - 1) * width for j in range(len(BACKBONES))]
        ys = [counts[key][bb] for bb, _ in BACKBONES]
        bars = ax.bar(xs, ys, width, label=label, color=color)
        ax.bar_label(bars, fontsize=8, padding=1)
    ax.set_xticks(range(len(BACKBONES)))
    ax.set_xticklabels([name for _, name in BACKBONES], fontsize=9)
    ax.set_ylabel("Real-data runs (of 10)", fontsize=9)
    ax.set_ylim(0, 11)
    ax.set_yticks(range(0, 11, 2))
    ax.tick_params(axis="y", labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="lower center",
              bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout()
    for ext in ("png", "pdf"):
        out = HERE / f"provenance_real_data_bars.{ext}"
        fig.savefig(out, dpi=300, bbox_inches="tight")
        print(f"saved: {out}")


if __name__ == "__main__":
    main()
