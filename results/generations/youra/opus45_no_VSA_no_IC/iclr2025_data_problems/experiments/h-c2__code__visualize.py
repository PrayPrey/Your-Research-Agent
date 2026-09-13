"""Visualization for h-c2."""
import os
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np


def plot_profile_heatmap(profiles: Dict[str, Dict[str, float]], out_path: str) -> None:
    """3x3 heatmap: models x modes."""
    models = list(profiles.keys())
    modes = list(profiles[models[0]].keys())
    data = np.array([[profiles[m][mode] for mode in modes] for m in models])

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(data, cmap="RdBu_r", aspect="auto")
    ax.set_xticks(range(len(modes)))
    ax.set_xticklabels(modes)
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels(models)
    for i in range(len(models)):
        for j in range(len(modes)):
            ax.text(j, i, f"{data[i, j]:.3f}", ha="center", va="center", fontsize=10)
    plt.colorbar(im, ax=ax, label="Mean Influence Score")
    ax.set_title("Mode Profile Heatmap")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_correlation_bars(correlations: Dict[Tuple[str, str], dict], threshold: float, out_path: str) -> None:
    """Bar chart of r per model pair with threshold line."""
    pairs = list(correlations.keys())
    rs = [correlations[p]["r"] for p in pairs]
    labels = [f"{p[0]}-{p[1]}" for p in pairs]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["green" if r > threshold else "red" for r in rs]
    ax.bar(labels, rs, color=colors, edgecolor="black")
    ax.axhline(y=threshold, color="orange", linestyle="--", label=f"r={threshold}")
    ax.set_ylabel("Pearson r")
    ax.set_title("Cross-Model Profile Correlations")
    ax.legend()
    ax.set_ylim(0, 1.05)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_profile_radar(profiles: Dict[str, Dict[str, float]], out_path: str) -> None:
    """Radar chart per model."""
    models = list(profiles.keys())
    modes = list(profiles[models[0]].keys())
    angles = np.linspace(0, 2 * np.pi, len(modes), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    for m in models:
        vals = [profiles[m][mode] for mode in modes] + [profiles[m][modes[0]]]
        ax.plot(angles, vals, label=m, linewidth=2)
        ax.fill(angles, vals, alpha=0.1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(modes)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1))
    ax.set_title("Mode Profiles Radar")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_bootstrap_ci(correlations: Dict[Tuple[str, str], dict], out_path: str) -> None:
    """Error bar plot with bootstrap CIs."""
    pairs = list(correlations.keys())
    rs = [correlations[p]["r"] for p in pairs]
    cis = [correlations[p].get("ci", (correlations[p]["r"], correlations[p]["r"])) for p in pairs]
    labels = [f"{p[0]}-{p[1]}" for p in pairs]

    fig, ax = plt.subplots(figsize=(8, 5))
    yerr = [[rs[i] - cis[i][0] for i in range(len(rs))], [cis[i][1] - rs[i] for i in range(len(rs))]]
    ax.errorbar(labels, rs, yerr=yerr, fmt="o", capsize=5, markersize=8)
    ax.axhline(y=0.7, color="orange", linestyle="--", label="r=0.7")
    ax.set_ylabel("Pearson r")
    ax.set_title("Correlations with 95% CI")
    ax.legend()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
