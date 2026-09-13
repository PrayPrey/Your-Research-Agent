"""
H-M3: Visualization module
- Gate metrics bar chart
- Overlap distribution histograms
- Venue-year heatmap
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats


def plot_gate_metrics(metrics: dict, out_path: str) -> None:
    """Bar chart: mean citing vs random overlap, 95% CI error bars,
    annotated p-value + Cohen's d. Saves to h-m3/figures/gate_metrics.png."""
    fig, ax = plt.subplots(figsize=(8, 6))

    groups = ["Citation Pairs", "Random Pairs"]
    means = [metrics["mean_citing_overlap"], metrics["mean_random_overlap"]]

    n_citing = metrics["n_citing_pairs"]
    n_random = metrics["n_random_pairs"]

    std_citing = metrics.get("std_citing", 0.1)
    std_random = metrics.get("std_random", 0.1)

    se_citing = std_citing / np.sqrt(n_citing) if n_citing > 0 else 0
    se_random = std_random / np.sqrt(n_random) if n_random > 0 else 0
    ci_95 = [1.96 * se_citing, 1.96 * se_random]

    colors = ["#4C72B0", "#DD8452"]
    bars = ax.bar(groups, means, yerr=ci_95, capsize=5, color=colors, edgecolor="black")

    ax.set_ylabel("Mean Jaccard Overlap", fontsize=12)
    ax.set_title("Citation vs Random Paper Pairs: Dataset Overlap", fontsize=14)

    p_val = metrics["p_value"]
    cohens_d = metrics["cohens_d"]
    p_str = f"p < 0.001" if p_val < 0.001 else f"p = {p_val:.4f}"

    annotation = f"Mann-Whitney U: {p_str}\nCohen's d = {cohens_d:.3f}"
    ax.annotate(annotation, xy=(0.95, 0.95), xycoords="axes fraction",
                ha="right", va="top", fontsize=10,
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))

    for bar, mean in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{mean:.3f}", ha="center", va="bottom", fontsize=10)

    ax.set_ylim(0, max(means) * 1.3)

    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_overlap_distribution(citing_overlaps: list[float], random_overlaps: list[float], out_path: str) -> None:
    """Side-by-side histograms, citing vs random overlap distributions."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

    bins = np.linspace(0, 1, 21)

    axes[0].hist(citing_overlaps, bins=bins, color="#4C72B0", edgecolor="black", alpha=0.7)
    axes[0].set_title(f"Citation Pairs (n={len(citing_overlaps):,})", fontsize=12)
    axes[0].set_xlabel("Jaccard Overlap", fontsize=11)
    axes[0].set_ylabel("Count", fontsize=11)
    axes[0].axvline(np.mean(citing_overlaps), color="red", linestyle="--",
                    label=f"Mean={np.mean(citing_overlaps):.3f}")
    axes[0].legend()

    axes[1].hist(random_overlaps, bins=bins, color="#DD8452", edgecolor="black", alpha=0.7)
    axes[1].set_title(f"Random Pairs (n={len(random_overlaps):,})", fontsize=12)
    axes[1].set_xlabel("Jaccard Overlap", fontsize=11)
    axes[1].axvline(np.mean(random_overlaps), color="red", linestyle="--",
                    label=f"Mean={np.mean(random_overlaps):.3f}")
    axes[1].legend()

    plt.suptitle("Dataset Overlap Distribution: Citation vs Random Pairs", fontsize=14, y=1.02)
    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_venue_year_heatmap(papers_df: pd.DataFrame, citations_df: pd.DataFrame, out_path: str) -> None:
    """Heatmap of Cohen's d effect size per venue-year cell."""
    from overlap import jaccard_similarity, sample_random_pairs
    from collections import defaultdict

    paper_datasets = {}
    for _, row in papers_df.iterrows():
        ds = row["datasets"]
        if isinstance(ds, list):
            paper_datasets[row["paper_id"]] = set(ds)
        else:
            paper_datasets[row["paper_id"]] = set()

    papers_by_vy = defaultdict(list)
    for _, row in papers_df.iterrows():
        papers_by_vy[row["venue_year"]].append(row["paper_id"])

    effect_sizes = {}

    for vy in citations_df["venue_year"].unique():
        vy_citations = citations_df[citations_df["venue_year"] == vy]
        vy_paper_ids = papers_by_vy.get(vy, [])

        if len(vy_citations) < 10 or len(vy_paper_ids) < 10:
            continue

        citing_overlaps = []
        for _, row in vy_citations.iterrows():
            citing_ds = paper_datasets.get(row["citing_id"], set())
            cited_ds = paper_datasets.get(row["cited_id"], set())
            citing_overlaps.append(jaccard_similarity(citing_ds, cited_ds))

        random_pairs = sample_random_pairs(vy_paper_ids, len(vy_citations), seed=42)
        random_overlaps = []
        for p1, p2 in random_pairs:
            d1 = paper_datasets.get(p1, set())
            d2 = paper_datasets.get(p2, set())
            random_overlaps.append(jaccard_similarity(d1, d2))

        if len(citing_overlaps) > 0 and len(random_overlaps) > 0:
            mean_c = np.mean(citing_overlaps)
            mean_r = np.mean(random_overlaps)
            pooled_std = np.sqrt((np.var(citing_overlaps) + np.var(random_overlaps)) / 2)
            d = (mean_c - mean_r) / pooled_std if pooled_std > 0 else 0

            parts = vy.split("_")
            if len(parts) == 2:
                venue, year = parts
                try:
                    effect_sizes[(venue, int(float(year)))] = d
                except ValueError:
                    continue

    if not effect_sizes:
        print("WARNING: No venue-year data for heatmap")
        return

    venues = sorted(set(k[0] for k in effect_sizes.keys()))
    years = sorted(set(k[1] for k in effect_sizes.keys()))

    matrix = np.full((len(venues), len(years)), np.nan)
    for (venue, year), d in effect_sizes.items():
        i = venues.index(venue)
        j = years.index(year)
        matrix[i, j] = d

    fig, ax = plt.subplots(figsize=(10, 4))

    mask = np.isnan(matrix)
    sns.heatmap(matrix, annot=True, fmt=".2f", cmap="RdYlGn", center=0,
                xticklabels=years, yticklabels=venues, mask=mask, ax=ax,
                cbar_kws={"label": "Cohen's d"})

    ax.set_title("Effect Size by Venue-Year (Cohen's d)", fontsize=14)
    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel("Venue", fontsize=11)

    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def generate_all(
    metrics: dict, citing_overlaps: list[float], random_overlaps: list[float],
    papers_df: pd.DataFrame, citations_df: pd.DataFrame, out_dir: str = "figures/"
) -> list[str]:
    """Generate all required figures. Returns list of generated file paths."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    generated = []

    metrics_with_std = metrics.copy()
    metrics_with_std["std_citing"] = np.std(citing_overlaps) if citing_overlaps else 0.1
    metrics_with_std["std_random"] = np.std(random_overlaps) if random_overlaps else 0.1

    gate_path = os.path.join(out_dir, "gate_metrics.png")
    plot_gate_metrics(metrics_with_std, gate_path)
    generated.append(gate_path)

    dist_path = os.path.join(out_dir, "overlap_distribution.png")
    plot_overlap_distribution(citing_overlaps, random_overlaps, dist_path)
    generated.append(dist_path)

    heatmap_path = os.path.join(out_dir, "venue_year_heatmap.png")
    plot_venue_year_heatmap(papers_df, citations_df, heatmap_path)
    generated.append(heatmap_path)

    return generated


if __name__ == "__main__":
    test_metrics = {
        "mean_citing_overlap": 0.25,
        "mean_random_overlap": 0.10,
        "p_value": 0.001,
        "cohens_d": 0.45,
        "n_citing_pairs": 5000,
        "n_random_pairs": 5000,
    }
    plot_gate_metrics(test_metrics, "test_figures/gate_metrics.png")
    print("Test figure generated")
