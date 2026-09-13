#!/usr/bin/env python3
"""Plot hallucination prevalence by method, type, and model.

Input layout:
  MLRbench_hallucination_analysis/
    <method>/<model>/per_type_prevalence_<model>.csv

Legacy one-level inputs are also accepted:
  MLRbench_hallucination_analysis/
    <method>/per_type_prevalence_<model>.csv

If both layouts contain the same method/model pair, the nested
<method>/<model>/ path is preferred.

Each CSV must contain:
  type, union_pct, inter_pct

The script writes two figures per model: one for union_pct and one for
inter_pct. Each figure is a single grouped bar chart containing all
hallucination types and methods.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing plotting dependency. Run with: "
        "uv run --with matplotlib python MLRbench_hallucination_analysis/plot_hallucination_prevalence.py"
    ) from exc


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = HERE / "plots"
CSV_RE = re.compile(r"per_type_prevalence_(?P<model>.+)\.csv$")

METHOD_LABELS = {
    "MLRbench": "MLRBench",
    "YouRA": "YouRA",
    "AI_Scientist_V2": "AI Scientist V2",
}

METHOD_ORDER = ["YouRA", "MLRbench", "AI_Scientist_V2"]

TYPE_ORDER = [
    "Nonexistent Citations",
    "Hallucinated Methodology",
    "Mathematical Errors",
    "Faked Experimental Results",
]

MODEL_LABELS = {
    "sonnet46": "Sonnet 4.6",
    "sonnet45": "Sonnet 4.5",
    "opus45": "Opus 4.5",
}

MODEL_ORDER = ["sonnet46", "sonnet45", "opus45"]

METHOD_COLORS = {
    "YouRA": "#4C78A8",
    "MLRbench": "#54A24B",
    "AI_Scientist_V2": "#E45756",
}

TYPE_LABELS = {
    "Nonexistent Citations": "Nonexistent\nCitations",
    "Hallucinated Methodology": "Hallucinated\nMethodology",
    "Mathematical Errors": "Mathematical\nErrors",
    "Faked Experimental Results": "Faked Experimental\nResults",
}


def pretty_method(method: str) -> str:
    return METHOD_LABELS.get(method, method.replace("_", " "))


def pretty_model(model: str) -> str:
    return MODEL_LABELS.get(model, model.replace("_", " "))


def load_csv(path: Path) -> dict[str, dict[str, float]]:
    required = {"type", "union_pct", "inter_pct"}
    rows: dict[str, dict[str, float]] = {}

    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        missing = required.difference(reader.fieldnames or [])
        if missing:
            missing_cols = ", ".join(sorted(missing))
            raise ValueError(f"{path} is missing required columns: {missing_cols}")

        for row in reader:
            hallucination_type = row["type"].strip()
            rows[hallucination_type] = {
                "union_pct": float(row["union_pct"]),
                "inter_pct": float(row["inter_pct"]),
            }

    return rows


def discover_data(input_dir: Path) -> tuple[dict[str, dict[str, dict[str, dict[str, float]]]], list[str]]:
    data: dict[str, dict[str, dict[str, dict[str, float]]]] = defaultdict(dict)
    methods: set[str] = set()
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

    for (model, method), (_, path) in sorted(selected_paths.items()):
        methods.add(method)
        data[model][method] = load_csv(path)

    if not data:
        raise FileNotFoundError(f"No per_type_prevalence_*.csv files found under {input_dir}")

    ordered_methods = sorted(
        methods,
        key=lambda name: (
            METHOD_ORDER.index(name) if name in METHOD_ORDER else len(METHOD_ORDER),
            pretty_method(name),
        ),
    )
    return dict(data), ordered_methods


def available_types(model_data: dict[str, dict[str, dict[str, float]]]) -> list[str]:
    found_types = {hallucination_type for method_rows in model_data.values() for hallucination_type in method_rows}
    ordered = [hallucination_type for hallucination_type in TYPE_ORDER if hallucination_type in found_types]
    ordered.extend(sorted(found_types.difference(ordered)))
    return ordered


def annotate_bars(ax: plt.Axes, bars) -> None:
    for bar in bars:
        height = bar.get_height()
        if not np.isfinite(height):
            continue
        ax.annotate(
            f"{height:.0f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=7,
        )


def metric_label(metric: str) -> str:
    return {"union_pct": "Union", "inter_pct": "Intersection"}[metric]


def metric_slug(metric: str) -> str:
    return {"union_pct": "union", "inter_pct": "intersection"}[metric]


def type_label(hallucination_type: str) -> str:
    return TYPE_LABELS.get(hallucination_type, hallucination_type.replace(" ", "\n"))


def plot_model_metric(
    model: str,
    model_data: dict[str, dict[str, dict[str, float]]],
    methods: list[str],
    metric: str,
    output_dir: Path,
    formats: list[str],
) -> list[Path]:
    hallucination_types = available_types(model_data)
    if not hallucination_types:
        raise ValueError(f"No hallucination types found for model {model}")

    fig, ax = plt.subplots(figsize=(13.5, 5.8))

    group_centers = np.arange(len(hallucination_types))
    n_bars_per_group = len(methods)
    bar_width = 0.2
    offsets = (np.arange(n_bars_per_group) - (n_bars_per_group - 1) / 2.0) * bar_width

    for method_idx, method in enumerate(methods):
        color = METHOD_COLORS.get(method, "#9D755D")
        values = [
            model_data.get(method, {}).get(hallucination_type, {}).get(metric, np.nan)
            for hallucination_type in hallucination_types
        ]
        bars = ax.bar(
            group_centers + offsets[method_idx],
            values,
            width=bar_width,
            color=color,
            edgecolor="black",
            linewidth=0.45,
            label=pretty_method(method),
        )
        annotate_bars(ax, bars)

    ax.set_title(
        f"MLRBench Hallucination Prevalence ({metric_label(metric)}) - {pretty_model(model)}",
        fontsize=14,
        fontweight="bold",
        pad=16,
    )
    ax.set_ylabel("Hallucination prevalence (%)", fontsize=10)
    ax.set_xticks(group_centers)
    ax.set_xticklabels([type_label(hallucination_type) for hallucination_type in hallucination_types], fontsize=9)
    ax.set_ylim(0, 112)
    ax.grid(axis="y", linestyle=":", alpha=0.45)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=0)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles,
        labels,
        loc="upper center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, -0.12),
        fontsize=9,
    )
    fig.subplots_adjust(left=0.07, right=0.99, top=0.88, bottom=0.24)

    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for fmt in formats:
        out_path = output_dir / f"hallucination_prevalence_{model}_{metric_slug(metric)}.{fmt}"
        fig.savefig(out_path, bbox_inches="tight", dpi=220 if fmt.lower() == "png" else None)
        written.append(out_path)

    plt.close(fig)
    return written


def plot_model(
    model: str,
    model_data: dict[str, dict[str, dict[str, float]]],
    methods: list[str],
    output_dir: Path,
    formats: list[str],
) -> list[Path]:
    written: list[Path] = []
    for metric in ["union_pct", "inter_pct"]:
        written.extend(plot_model_metric(model, model_data, methods, metric, output_dir, formats))
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create model-wise hallucination prevalence plots from per_type_prevalence CSVs."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=HERE,
        help=(
            "Directory containing method/model subdirectories with "
            "per_type_prevalence_<model>.csv files. Legacy one-level method "
            "subdirectories are also accepted."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where figures will be written.",
    )
    parser.add_argument(
        "--models",
        nargs="*",
        help="Optional model suffixes to plot, for example: sonnet46 sonnet45 opus45.",
    )
    parser.add_argument(
        "--formats",
        nargs="+",
        default=["png", "pdf"],
        choices=["png", "pdf", "svg"],
        help="Output figure formats.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data, methods = discover_data(args.input_dir)

    selected_models = args.models or sorted(
        data,
        key=lambda name: (
            MODEL_ORDER.index(name) if name in MODEL_ORDER else len(MODEL_ORDER),
            pretty_model(name),
        ),
    )
    missing = [model for model in selected_models if model not in data]
    if missing:
        available = ", ".join(sorted(data))
        raise ValueError(f"Requested models not found: {', '.join(missing)}. Available models: {available}")

    all_written: list[Path] = []
    for model in selected_models:
        written = plot_model(model, data[model], methods, args.output_dir, args.formats)
        all_written.extend(written)

    for path in all_written:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
