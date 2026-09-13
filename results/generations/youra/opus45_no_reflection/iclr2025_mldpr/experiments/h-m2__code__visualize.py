"""Visualization suite for H-M2."""
import matplotlib.pyplot as plt
from collections import Counter
from config import VizConfig, POST_2020_THRESHOLD, GPT3_RELEASE_YEAR


def plot_gate_metrics(results: dict, out_path: str) -> None:
    """Bar chart showing post-2020 ratio vs threshold."""
    cfg = VizConfig()
    fig, ax = plt.subplots(figsize=cfg.figsize, dpi=cfg.dpi)

    ratio = results["post_2020_ratio"]
    color = cfg.emergent_color if ratio > POST_2020_THRESHOLD else cfg.traditional_color

    ax.bar(["Post-2020 Ratio"], [ratio], color=color, alpha=0.8, width=0.5)
    ax.axhline(POST_2020_THRESHOLD, color=cfg.threshold_line_color, linestyle="--",
               linewidth=2, label=f"Threshold ({POST_2020_THRESHOLD:.0%})")

    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Ratio")
    ax.set_title(f"H-M2 Gate: Post-2020 Emergent Benchmark Ratio = {ratio:.1%}")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_creation_timeline(benchmarks: list[dict], out_path: str) -> None:
    """Histogram of benchmark creation dates by type."""
    cfg = VizConfig()
    fig, ax = plt.subplots(figsize=cfg.figsize, dpi=cfg.dpi)

    emergent_years = [b["year"] for b in benchmarks
                      if b["category"] == "emergent-capability" and b["year"] and 2000 <= b["year"] <= 2025]
    traditional_years = [b["year"] for b in benchmarks
                         if b["category"] == "traditional" and b["year"] and 2000 <= b["year"] <= 2025]

    bins = range(2000, 2027)
    ax.hist([traditional_years, emergent_years], bins=bins,
            label=["Traditional", "Emergent-Capability"],
            color=[cfg.traditional_color, cfg.emergent_color], alpha=0.7, stacked=True)

    ax.axvline(GPT3_RELEASE_YEAR, color=cfg.gpt3_marker_color, linestyle="--",
               linewidth=2, label="GPT-3 (2020)")

    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    ax.set_title("Benchmark Creation Timeline")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_cumulative_curve(benchmarks: list[dict], out_path: str) -> None:
    """Cumulative emergent-capability benchmarks over time."""
    cfg = VizConfig()
    fig, ax = plt.subplots(figsize=cfg.figsize, dpi=cfg.dpi)

    emergent = [b for b in benchmarks
                if b["category"] == "emergent-capability" and b["year"] and 2000 <= b["year"] <= 2025]
    years = sorted([b["year"] for b in emergent])

    cumulative = list(range(1, len(years) + 1))

    ax.plot(years, cumulative, color=cfg.emergent_color, linewidth=2, marker="o", markersize=3)
    ax.axvline(GPT3_RELEASE_YEAR, color=cfg.gpt3_marker_color, linestyle="--",
               linewidth=2, label="GPT-3 (2020)")

    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative Count")
    ax.set_title("Cumulative Emergent-Capability Benchmarks")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_type_distribution_by_year(benchmarks: list[dict], out_path: str) -> None:
    """Stacked bar chart of benchmark types per year."""
    cfg = VizConfig()
    fig, ax = plt.subplots(figsize=cfg.figsize, dpi=cfg.dpi)

    emergent_counter = Counter(b["year"] for b in benchmarks
                               if b["category"] == "emergent-capability" and b["year"] and 2015 <= b["year"] <= 2025)
    traditional_counter = Counter(b["year"] for b in benchmarks
                                  if b["category"] == "traditional" and b["year"] and 2015 <= b["year"] <= 2025)

    years = list(range(2015, 2026))
    emergent_counts = [emergent_counter.get(y, 0) for y in years]
    traditional_counts = [traditional_counter.get(y, 0) for y in years]

    ax.bar(years, traditional_counts, label="Traditional", color=cfg.traditional_color, alpha=0.7)
    ax.bar(years, emergent_counts, bottom=traditional_counts, label="Emergent-Capability",
           color=cfg.emergent_color, alpha=0.7)

    ax.axvline(GPT3_RELEASE_YEAR - 0.5, color=cfg.gpt3_marker_color, linestyle="--",
               linewidth=2, label="GPT-3 (2020)")

    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    ax.set_title("Benchmark Type Distribution by Year")
    ax.legend()
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=45)

    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")
