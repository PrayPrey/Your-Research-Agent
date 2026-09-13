# H-M4 Visualization: Benchmark dominance figures

import os
import pandas as pd
import matplotlib.pyplot as plt
from config import (
    OUTPUT_DIR, FIGURE_SIZE, DPI, COLORS,
    PER_BENCHMARK_COLORS, FIGURE_FILES, TRADITIONAL_BENCHMARKS
)


def ensure_output_dir():
    """Create output directory if needed."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def plot_gate_metrics(gate_result: dict, out_path: str = None) -> None:
    """Bar chart: traditional vs emergent share."""
    ensure_output_dir()

    fig, axes = plt.subplots(1, 2, figsize=FIGURE_SIZE)

    # Share comparison
    shares = [gate_result["traditional_share"], gate_result["emergent_share"]]
    labels = ["Traditional", "Emergent"]
    colors = [COLORS["traditional"], COLORS["emergent"]]

    axes[0].bar(labels, shares, color=colors)
    axes[0].set_ylabel("Share of Total Papers")
    axes[0].set_title("Benchmark Category Share")
    axes[0].axhline(y=0.5, color="black", linestyle="--", alpha=0.5, label="50% threshold")
    axes[0].legend()

    for i, v in enumerate(shares):
        axes[0].text(i, v + 0.01, f"{v*100:.1f}%", ha="center")

    # Paper count comparison
    counts = [gate_result["traditional_papers"], gate_result["emergent_papers"]]
    axes[1].bar(labels, counts, color=colors)
    axes[1].set_ylabel("Total Paper Count")
    axes[1].set_title("Benchmark Paper Counts")

    for i, v in enumerate(counts):
        axes[1].text(i, v + 1000, f"{v:,}", ha="center")

    plt.tight_layout()
    out_path = out_path or os.path.join(OUTPUT_DIR, FIGURE_FILES["gate_metrics"])
    plt.savefig(out_path, dpi=DPI)
    plt.close()
    print(f"Saved: {out_path}")


def plot_share_timeseries(df: pd.DataFrame, out_path: str = None) -> None:
    """Pie chart showing paper distribution."""
    ensure_output_dir()

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    # Aggregate by category
    category_counts = df.groupby("category")["paper_count"].sum()

    colors_map = {
        "traditional": COLORS["traditional"],
        "emergent": COLORS["emergent"],
        "other": "#888888",
    }
    colors = [colors_map.get(c, "#888888") for c in category_counts.index]

    wedges, texts, autotexts = ax.pie(
        category_counts.values,
        labels=category_counts.index,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
    )

    ax.set_title("Paper Distribution by Benchmark Category")

    plt.tight_layout()
    out_path = out_path or os.path.join(OUTPUT_DIR, FIGURE_FILES["share_timeseries"])
    plt.savefig(out_path, dpi=DPI)
    plt.close()
    print(f"Saved: {out_path}")


def plot_stacked_area(df: pd.DataFrame, out_path: str = None) -> None:
    """Bar chart: top benchmarks by paper count."""
    ensure_output_dir()

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    # Get top 15 benchmarks by paper count
    top = df.nlargest(15, "paper_count")[["dataset_name", "paper_count", "category"]]

    colors = [COLORS.get(c, "#888888") for c in top["category"]]
    bars = ax.barh(top["dataset_name"], top["paper_count"], color=colors)

    ax.set_xlabel("Paper Count")
    ax.set_title("Top 15 Benchmarks by Paper Count")
    ax.invert_yaxis()

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS["traditional"], label="Traditional"),
        Patch(facecolor=COLORS["emergent"], label="Emergent"),
        Patch(facecolor="#888888", label="Other"),
    ]
    ax.legend(handles=legend_elements, loc="lower right")

    plt.tight_layout()
    out_path = out_path or os.path.join(OUTPUT_DIR, FIGURE_FILES["stacked_area"])
    plt.savefig(out_path, dpi=DPI)
    plt.close()
    print(f"Saved: {out_path}")


def plot_per_benchmark(per_benchmark: dict, out_path: str = None) -> None:
    """Per-traditional-benchmark bar chart."""
    ensure_output_dir()

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    benchmarks = list(per_benchmark.keys())
    counts = list(per_benchmark.values())
    colors = [PER_BENCHMARK_COLORS.get(b, "#333333") for b in benchmarks]

    ax.bar(benchmarks, counts, color=colors)
    ax.set_xlabel("Benchmark")
    ax.set_ylabel("Total Paper Count")
    ax.set_title("Traditional Benchmarks: Paper Counts")

    for i, v in enumerate(counts):
        ax.text(i, v + 100, f"{v:,}", ha="center")

    plt.tight_layout()
    out_path = out_path or os.path.join(OUTPUT_DIR, FIGURE_FILES["per_benchmark"])
    plt.savefig(out_path, dpi=DPI)
    plt.close()
    print(f"Saved: {out_path}")
