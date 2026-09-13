"""Visualization for BCS analysis."""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import BCS_SD_TARGET, FIGURES_DIR
import os


def plot_bcs_histogram(bcs_values: list, save_path: str = None) -> None:
    """Plot BCS distribution histogram."""
    clean = [b for b in bcs_values if not np.isnan(b)]

    plt.figure(figsize=(10, 6))
    sns.histplot(clean, bins=50, kde=True)
    plt.xlim(-1, 1)
    plt.xlabel("BCS (Pearson Correlation)")
    plt.ylabel("Frequency")
    plt.title(f"BCS Distribution (n={len(clean)}, SD={np.std(clean):.3f})")
    plt.axvline(x=0, color="red", linestyle="--", alpha=0.5)

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {save_path}")
    plt.close()


def plot_gate_comparison(stats: dict, sd_target: float = BCS_SD_TARGET, save_path: str = None) -> None:
    """Plot target vs actual SD bar chart."""
    plt.figure(figsize=(8, 5))

    actual_sd = stats.get("std", 0)
    colors = ["green" if actual_sd > sd_target else "red", "gray"]

    plt.bar(["Actual SD", "Target SD"], [actual_sd, sd_target], color=colors)
    plt.ylabel("Standard Deviation")
    plt.title(f"Gate Check: SD > {sd_target}")
    plt.axhline(y=sd_target, color="red", linestyle="--", alpha=0.5)

    gate_status = "PASS" if actual_sd > sd_target else "FAIL"
    plt.text(0, actual_sd + 0.02, f"{actual_sd:.3f}", ha="center", fontsize=12)
    plt.text(0.5, max(actual_sd, sd_target) + 0.05, f"Gate: {gate_status}", ha="center", fontsize=14, fontweight="bold")

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {save_path}")
    plt.close()
