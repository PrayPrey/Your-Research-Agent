#!/usr/bin/env python3
"""Plot the four-axis MLR-Bench hallucination diagnostic for the paper body.

The figure summarizes the all-judge intersection counts for all four
fact-based hallucination categories in the MLR-Bench hallucination taxonomy.

Input layout:
  MLRbench_hallucination_analysis/
    <method>/<model>/per_type_prevalence_<model>.csv

Each CSV must contain:
  type, inter_n
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
        "MLRbench_hallucination_analysis/plot_hallucination_taxonomy_intersection.py"
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
    "Faked Experimental Results": "Faked Experimental Results",
    "Hallucinated Methodology": "Hallucinated Methodology",
    "Nonexistent Citations": "Incorrect Citations",
    "Mathematical Errors": "Mathematical Errors",
}


def load_intersection_counts(path: Path) -> dict[str, int]:
    required = {"type", "inter_n"}
    counts: dict[str, int] = {}

    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        missing = required.difference(reader.fieldnames or [])
        if missing:
            missing_cols = ", ".join(sorted(missing))
            raise ValueError(f"{path} is missing required columns: {missing_cols}")

        for row in reader:
            hallucination_type = row["type"].strip()
            counts[hallucination_type] = int(float(row["inter_n"]))

    return counts


def discover_data(input_dir: Path) -> dict[str, dict[str, dict[str, int]]]:
    """Return data[model][method][hallucination_type] = inter_n."""
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

    data: dict[str, dict[str, dict[str, int]]] = {}
    for (model, method), (_, path) in sorted(selected_paths.items()):
        if model not in MODEL_ORDER or method not in METHOD_ORDER:
            continue
        data.setdefault(model, {})[method] = load_intersection_counts(path)

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


def style_axis(ax: plt.Axes) -> None:
    ax.set_ylim(0, 10)
    ax.set_yticks(range(0, 11, 2))
    ax.grid(axis="y", color="#D6DEE8", linestyle="-", linewidth=0.65, alpha=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=0, pad=7, labelsize=9)
    ax.tick_params(axis="y", labelsize=8, colors="#394B59")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#A8B3C1")
    ax.spines["bottom"].set_color("#A8B3C1")


def annotate_bar(ax: plt.Axes, x: float, value: int) -> None:
    ax.text(
        x,
        value + 0.25,
        str(value),
        ha="center",
        va="bottom",
        fontsize=8,
        fontweight="bold",
        color="#23313F",
    )


def plot_hallucination_taxonomy(
    data: dict[str, dict[str, dict[str, int]]], output_dir: Path, formats: list[str]
) -> list[Path]:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titleweight": "bold",
            "axes.titlesize": 10,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )

    fig, axes_grid = plt.subplots(2, 2, figsize=(8.4, 6.15), sharey=True)
    axes = list(axes_grid.ravel())
    bar_width = 0.22
    x_centers = list(range(len(MODEL_ORDER)))
    offsets = {
        "YouRA": -bar_width,
        "MLRbench": 0.0,
        "AI_Scientist_V2": bar_width,
    }

    for panel_idx, (ax, hallucination_type) in enumerate(zip(axes, TARGET_TYPES), start=1):
        for method in METHOD_ORDER:
            xs = [center + offsets[method] for center in x_centers]
            values = [data[model][method].get(hallucination_type, 0) for model in MODEL_ORDER]
            bars = ax.bar(
                xs,
                values,
                width=bar_width * 0.92,
                color=METHOD_COLORS[method],
                edgecolor="white",
                linewidth=0.9,
                label=METHOD_LABELS[method],
                zorder=3,
            )
            for bar, value in zip(bars, values):
                annotate_bar(ax, bar.get_x() + bar.get_width() / 2, value)

        ax.set_title(f"{chr(64 + panel_idx)}. {TYPE_LABELS[hallucination_type]}", pad=10)
        ax.set_xticks(x_centers)
        ax.set_xticklabels([MODEL_LABELS[model] for model in MODEL_ORDER])
        style_axis(ax)

    axes[0].set_ylabel("All-judge intersection count (out of 10)", fontsize=9, color="#23313F")
    axes[2].set_ylabel("All-judge intersection count (out of 10)", fontsize=9, color="#23313F")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.04),
        ncol=3,
        frameon=False,
        fontsize=9,
        handlelength=1.4,
        columnspacing=1.8,
    )
    fig.subplots_adjust(left=0.085, right=0.99, top=0.89, bottom=0.08, wspace=0.13, hspace=0.4)

    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for fmt in formats:
        out_path = output_dir / f"hallucination_taxonomy_intersection.{fmt}"
        fig.savefig(out_path, bbox_inches="tight", dpi=300 if fmt.lower() == "png" else None)
        written.append(out_path)

    plt.close(fig)
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot all four MLR-Bench hallucination intersection counts for the paper body."
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
    written = plot_hallucination_taxonomy(data, args.output_dir, args.formats)
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
