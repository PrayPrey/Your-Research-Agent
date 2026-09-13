"""Visualization for H-M1 citation analysis."""
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


class Visualizer:
    def __init__(self, output_dir: str = "../figures/"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_zscore_bar(self, foundation_results: dict) -> str:
        fig, ax = plt.subplots(figsize=(10, 6))
        names = []
        zscores = []
        for pid, data in foundation_results.items():
            short_name = data.get("title", pid)[:30]
            names.append(short_name)
            zscores.append(data["z_score"])
        colors = ["green" if z > 2.0 else "gray" for z in zscores]
        bars = ax.bar(names, zscores, color=colors)
        ax.axhline(y=2.0, color="red", linestyle="--", label="2σ threshold")
        ax.set_ylabel("Z-score")
        ax.set_title("Foundation Model Citation Z-scores (H-M1)")
        ax.legend()
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        path = self.output_dir / "zscore_bar.png"
        plt.savefig(path, dpi=150)
        plt.close()
        return str(path)

    def plot_citation_histogram(self, field_citations: list[int], foundation_results: dict) -> str:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(field_citations, bins=50, alpha=0.7, label="Field distribution")
        for pid, data in foundation_results.items():
            ax.axvline(x=data["citations"], color="red", linestyle="--", alpha=0.8)
            ax.annotate(data.get("title", pid)[:15], xy=(data["citations"], 0), rotation=90, fontsize=8)
        ax.set_xlabel("Citation Count")
        ax.set_ylabel("Frequency")
        ax.set_title("Citation Distribution with Foundation Papers Marked")
        ax.set_xlim(0, np.percentile(field_citations, 99))
        plt.tight_layout()
        path = self.output_dir / "citation_histogram.png"
        plt.savefig(path, dpi=150)
        plt.close()
        return str(path)

    def plot_percentile_table(self, foundation_results: dict) -> str:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.axis("off")
        data = []
        for pid, r in foundation_results.items():
            data.append([
                r.get("title", pid)[:40],
                r["citations"],
                f"{r['z_score']:.2f}",
                f"{r['percentile']:.1f}%",
                "✓" if r["exceeds_2sigma"] else "✗",
            ])
        table = ax.table(
            cellText=data,
            colLabels=["Paper", "Citations", "Z-score", "Percentile", ">2σ"],
            loc="center",
            cellLoc="left",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.5)
        plt.title("Foundation Paper Percentile Ranks")
        plt.tight_layout()
        path = self.output_dir / "percentile_table.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        return str(path)
