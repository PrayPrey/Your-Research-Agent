#!/usr/bin/env python3
"""Generate routing_levels_stack.png from routing_levels.csv.

Stacked vertical bar: x=backbone, y=event count, segments=redesign/reset/unclass.
Each segment is labeled with its count; the per-bar total is annotated on top.
Micro-repair is intentionally omitted (always 0 by design).
"""
import csv
import argparse
from pathlib import Path

import matplotlib.pyplot as plt

VSA = Path(__file__).resolve().parent
DEFAULT_CSV = VSA / "routing_levels.csv"
DEFAULT_OUT = VSA / "routing_levels_stack.png"

ORDER = ["Sonnet 4.5", "Opus 4.5", "Sonnet 4.6"]
LEVELS = [
    ("redesign", "#4C9F70"),   # green
    ("reset",    "#C44536"),   # red
    ("unclass",  "#9E9E9E"),   # gray
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a stacked routing-level plot from routing_levels.csv.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV,
        help="Input routing_levels.csv path. Defaults to analysis/VSA/routing_levels.csv.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUT,
        help="Output PNG path. Defaults to analysis/VSA/routing_levels_stack.png.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    csv_path = args.csv.expanduser().resolve()
    out_path = args.output.expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = {}
    with csv_path.open() as f:
        for r in csv.DictReader(f):
            if r["backbone"] == "Total":
                continue
            rows[r["backbone"]] = {k: int(r[k]) for k in ("redesign", "reset", "unclass")}

    x = list(range(len(ORDER)))
    totals = [sum(rows[b].values()) for b in ORDER]

    fig, ax = plt.subplots(figsize=(6.0, 4.2), dpi=150)
    bottoms = [0] * len(ORDER)
    for level, color in LEVELS:
        vals = [rows[b][level] for b in ORDER]
        bars = ax.bar(x, vals, bottom=bottoms, color=color, edgecolor="white",
                      linewidth=0.8, label=level)
        for i, bar in enumerate(bars):
            if vals[i] > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bottoms[i] + vals[i] / 2,
                        str(vals[i]),
                        ha="center", va="center",
                        color="white", fontsize=11, fontweight="bold")
        bottoms = [b + v for b, v in zip(bottoms, vals)]

    for i, t in enumerate(totals):
        ax.text(i, t + max(totals) * 0.02, f"n={t}", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color="black")

    ax.set_xticks(x)
    ax.set_xticklabels(ORDER, fontsize=11)
    ax.set_ylabel("Archive-producing routing events", fontsize=11)
    ax.set_ylim(0, max(totals) * 1.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left", frameon=False, fontsize=10)
    ax.grid(axis="y", alpha=0.25, linewidth=0.5)

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
