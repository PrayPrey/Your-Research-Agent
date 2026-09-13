"""Visualization for H-M2 hedging analysis."""
import matplotlib.pyplot as plt
from pathlib import Path


def plot_gate_metrics(hedging_rate: float, threshold: float, out_dir: str) -> None:
    """Bar chart: actual rate vs threshold line."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["Hedging Presence Rate"], [hedging_rate], color="steelblue")
    ax.axhline(y=threshold, color="red", linestyle="--", label=f"Threshold ({threshold:.0%})")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Rate")
    ax.set_title("H-M2: Hedging Presence Rate vs Gate Threshold")
    ax.legend()

    for i, v in enumerate([hedging_rate]):
        ax.text(i, v + 0.02, f"{v:.1%}", ha="center")

    plt.tight_layout()
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    plt.savefig(Path(out_dir) / "gate_metrics.png", dpi=150)
    plt.close()


def plot_marker_frequency(freq_dist: dict, out_dir: str) -> None:
    """Horizontal bar chart of marker frequencies."""
    if not freq_dist:
        return

    markers = list(freq_dist.keys())[:15]
    counts = [freq_dist[m] for m in markers]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(markers[::-1], counts[::-1], color="teal")
    ax.set_xlabel("Count")
    ax.set_title("H-M2: Hedging Marker Frequency (Top 15)")

    plt.tight_layout()
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    plt.savefig(Path(out_dir) / "marker_frequency.png", dpi=150)
    plt.close()


def plot_hedging_count_histogram(results: list[dict], out_dir: str) -> None:
    """Histogram of total_count per output."""
    counts = [r["total_count"] for r in results]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(counts, bins=range(max(counts) + 2), color="coral", edgecolor="black")
    ax.set_xlabel("Hedging Markers per Output")
    ax.set_ylabel("Frequency")
    ax.set_title("H-M2: Distribution of Hedging Marker Counts")

    plt.tight_layout()
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    plt.savefig(Path(out_dir) / "hedging_count_histogram.png", dpi=150)
    plt.close()


def generate_visualizations(metrics: dict, freq_dist: dict, results: list[dict], output_dir: Path) -> None:
    """Generate all visualization figures."""
    out_dir = str(output_dir)
    plot_gate_metrics(metrics["hedging_presence_rate"], metrics.get("threshold", 0.30), out_dir)
    plot_marker_frequency(freq_dist, out_dir)
    plot_hedging_count_histogram(results, out_dir)
