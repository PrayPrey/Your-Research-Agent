#!/usr/bin/env python3
"""Plot intersection and union counts for the MLR-Bench hallucination taxonomy.

The figure uses a 2 x 4 small-multiple layout:
  row 1: all-judge intersection counts
  row 2: any-judge union counts

Columns correspond to the four fact-based hallucination categories used by
MLR-Bench.

Input layout:
  MLRbench_hallucination_analysis/
    <method>/<model>/per_type_prevalence_<model>.csv

Each CSV must contain:
  type, inter_n, union_n
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing plotting dependency. Run with: "
        "uv run --with matplotlib python "
        "MLRbench_hallucination_analysis/plot_hallucination_taxonomy_bounds.py"
    ) from exc


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = HERE / "plots"
CSV_RE = re.compile(r"per_type_prevalence_(?P<model>.+)\.csv$")

METHOD_ORDER = ["YouRA", "MLRbench", "AI_Scientist_V2"]
METHOD_LABELS = {
    "YouRA": "YouRA",
    "MLRbench": "MLR-Agent",
    "AI_Scientist_V2": "AI Scientist V2",
}
METHOD_COLORS = {
    "YouRA": "#2F6FBA",
    "MLRbench": "#5B7F55",
    "AI_Scientist_V2": "#D95F59",
}

MODEL_ORDER = ["sonnet45", "opus45", "sonnet46"]
MODEL_LABELS = {
    "sonnet45": "Sonnet 4.5",
    "opus45": "Opus 4.5",
    "sonnet46": "Sonnet 4.6",
}

TARGET_TYPES = [
    "Faked Experimental Results",
    "Hallucinated Methodology",
    "Nonexistent Citations",
    "Mathematical Errors",
]
TYPE_LABELS = {
    "Faked Experimental Results": "Faked\nExperimental Results",
    "Hallucinated Methodology": "Hallucinated\nMethodology",
    "Nonexistent Citations": "Incorrect\nCitations",
    "Mathematical Errors": "Mathematical\nErrors",
}

METRICS = [
    ("inter_n", "Intersection", "all 4 judges"),
    ("union_n", "Union", "any judge"),
]


def load_counts(path: Path) -> dict[str, dict[str, int]]:
    required = {"type", "inter_n", "union_n"}
    counts: dict[str, dict[str, int]] = {}

    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        missing = required.difference(reader.fieldnames or [])
        if missing:
            missing_cols = ", ".join(sorted(missing))
            raise ValueError(f"{path} is missing required columns: {missing_cols}")

        for row in reader:
            hallucination_type = row["type"].strip()
            counts[hallucination_type] = {
                "inter_n": int(float(row["inter_n"])),
                "union_n": int(float(row["union_n"])),
            }

    return counts


def discover_data(input_dir: Path) -> dict[str, dict[str, dict[str, dict[str, int]]]]:
    """Return data[model][method][hallucination_type][metric] = count."""
    selected_paths: dict[tuple[str, str], tuple[int, Path]] = {}

    for path in sorted(input_dir.rglob("per_type_prevalence_*.csv")):
        rel_parts = path.relative_to(input_dir).parts
        if len(rel_parts) < 2:
            continue

        method = rel_parts[0]
        if method.startswith(".") or method == "plots":
            continue

        match = CSV_RE.match(path.name)
        if not match:
            continue

        model = match.group("model")
        is_nested_model_path = len(rel_parts) >= 3 and rel_parts[-2] == model
        rank = 0 if is_nested_model_path else 1
        key = (model, method)
        previous = selected_paths.get(key)
        if previous is None or rank < previous[0]:
            selected_paths[key] = (rank, path)

    data: dict[str, dict[str, dict[str, dict[str, int]]]] = {}
    for (model, method), (_, path) in sorted(selected_paths.items()):
        if model not in MODEL_ORDER or method not in METHOD_ORDER:
            continue
        data.setdefault(model, {})[method] = load_counts(path)

    missing_pairs = [
        f"{METHOD_LABELS[method]} / {MODEL_LABELS[model]}"
        for model in MODEL_ORDER
        for method in METHOD_ORDER
        if method not in data.get(model, {})
    ]
    if missing_pairs:
        missing_text = "; ".join(missing_pairs)
        raise FileNotFoundError(f"Missing prevalence CSVs for: {missing_text}")

    return data


def style_axis(ax: plt.Axes, *, show_xticklabels: bool) -> None:
    ax.set_ylim(0, 10.8)
    ax.set_yticks(range(0, 11, 2))
    ax.grid(axis="y", color="#D8E1EA", linestyle="-", linewidth=0.6, alpha=0.85)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=0, pad=6, labelsize=7)
    ax.tick_params(axis="y", labelsize=7, colors="#394B59")
    if not show_xticklabels:
        ax.set_xticklabels([])
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#AAB7C4")
    ax.spines["bottom"].set_color("#AAB7C4")


def annotate_bar(ax: plt.Axes, x: float, value: int) -> None:
    ax.text(
        x,
        value + 0.16,
        str(value),
        ha="center",
        va="bottom",
        fontsize=6,
        fontweight="bold",
        color="#23313F",
    )


def plot_hallucination_bounds(
    data: dict[str, dict[str, dict[str, dict[str, int]]]], output_dir: Path, formats: list[str]
) -> list[Path]:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titleweight": "bold",
            "axes.titlesize": 9,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )

    fig, axes = plt.subplots(2, 4, figsize=(12.2, 5.7), sharey=True)
    bar_width = 0.22
    x_centers = list(range(len(MODEL_ORDER)))
    offsets = {
        "YouRA": -bar_width,
        "MLRbench": 0.0,
        "AI_Scientist_V2": bar_width,
    }

    for row_idx, (metric, row_title, row_subtitle) in enumerate(METRICS):
        for col_idx, hallucination_type in enumerate(TARGET_TYPES):
            ax = axes[row_idx][col_idx]
            for method in METHOD_ORDER:
                xs = [center + offsets[method] for center in x_centers]
                values = [
                    data[model][method].get(hallucination_type, {}).get(metric, 0)
                    for model in MODEL_ORDER
                ]
                bars = ax.bar(
                    xs,
                    values,
                    width=bar_width * 0.92,
                    color=METHOD_COLORS[method],
                    edgecolor="white",
                    linewidth=0.7,
                    label=METHOD_LABELS[method],
                    zorder=3,
                )
                for bar, value in zip(bars, values):
                    annotate_bar(ax, bar.get_x() + bar.get_width() / 2, value)

            if row_idx == 0:
                ax.set_title(TYPE_LABELS[hallucination_type], pad=9)
            ax.set_xticks(x_centers)
            ax.set_xticklabels([MODEL_LABELS[model] for model in MODEL_ORDER])
            style_axis(ax, show_xticklabels=True)

        axes[row_idx][0].set_ylabel("Count out of 10", fontsize=8, color="#23313F")

    handles, labels = axes[0][0].get_legend_handles_labels()
    legend = fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.035),
        ncol=3,
        frameon=True,
        fontsize=10,
        handlelength=1.8,
        handleheight=1.0,
        handletextpad=0.65,
        columnspacing=2.2,
        borderpad=0.45,
        labelspacing=0.5,
    )
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_edgecolor("#B8C2CC")
    legend.get_frame().set_linewidth(0.8)
    legend.get_frame().set_alpha(0.98)
    fig.text(
        0.027,
        0.635,
        "Intersection\nall 4 judges",
        rotation=90,
        ha="center",
        va="center",
        fontsize=9,
        fontweight="bold",
        color="#23313F",
        bbox={
            "boxstyle": "round,pad=0.36",
            "facecolor": "#EAF2FB",
            "edgecolor": "#B8CBE3",
            "linewidth": 0.8,
        },
    )
    fig.text(
        0.027,
        0.255,
        "Union\nany judge",
        rotation=90,
        ha="center",
        va="center",
        fontsize=9,
        fontweight="bold",
        color="#23313F",
        bbox={
            "boxstyle": "round,pad=0.36",
            "facecolor": "#F2F6ED",
            "edgecolor": "#C8D8BD",
            "linewidth": 0.8,
        },
    )
    fig.subplots_adjust(left=0.105, right=0.995, top=0.86, bottom=0.09, wspace=0.13, hspace=0.25)

    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for fmt in formats:
        out_path = output_dir / f"hallucination_taxonomy_bounds.{fmt}"
        fig.savefig(out_path, bbox_inches="tight", dpi=300 if fmt.lower() == "png" else None)
        written.append(out_path)

    plt.close(fig)
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot intersection and union counts for the four MLR-Bench hallucination categories."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=HERE,
        help="Directory containing hallucination analysis CSVs.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to write the figure files.",
    )
    parser.add_argument(
        "--formats",
        nargs="+",
        default=["png", "pdf"],
        help="Output formats supported by matplotlib.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = discover_data(args.input_dir)
    written = plot_hallucination_bounds(data, args.output_dir, args.formats)
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
