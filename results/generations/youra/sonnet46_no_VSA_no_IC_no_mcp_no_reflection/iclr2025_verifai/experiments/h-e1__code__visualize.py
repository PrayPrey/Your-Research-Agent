import os
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


CATS = ["execution", "static_analysis", "type_checking", "smt_solving"]
CAT_LABELS = ["Execution", "Static Analysis", "Type Checking", "SMT Solving"]


def _ensure_dir(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def plot_activation_rates(stats: dict, out: str = "figures/activation_rates.png") -> None:
    _ensure_dir(out)
    rates = stats["activation_rates"]
    values = [rates.get(c, 0.0) for c in CATS]
    colors = ["green" if v >= 0.10 else "red" for v in values]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(CAT_LABELS, values, color=colors, alpha=0.8)
    ax.axhline(0.10, color="black", linestyle="--", linewidth=1.5, label="10% threshold")
    ax.set_ylabel("Activation Rate")
    ax.set_title("Verifier Activation Rates (H-E1 Gate Check)")
    ax.set_ylim(0, 1)
    ax.legend()
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01, f"{val:.1%}", ha="center", va="bottom", fontsize=10)
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"✓ Saved {out}")


def plot_overlap_matrix(stats: dict, out: str = "figures/overlap_matrix.png") -> None:
    _ensure_dir(out)
    n = len(CATS)
    matrix = np.zeros((n, n))
    rates = stats["activation_rates"]
    overlap = stats["pairwise_overlap"]

    for i, a in enumerate(CATS):
        matrix[i, i] = rates.get(a, 0.0)
        for j, b in enumerate(CATS):
            if i != j:
                key = f"{a}_{b}" if f"{a}_{b}" in overlap else f"{b}_{a}"
                matrix[i, j] = overlap.get(key, 0.0)

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(matrix, vmin=0, vmax=1, cmap="Blues")
    plt.colorbar(im, ax=ax, label="Overlap fraction")
    ax.set_xticks(range(n)); ax.set_xticklabels(CAT_LABELS, rotation=30, ha="right", fontsize=9)
    ax.set_yticks(range(n)); ax.set_yticklabels(CAT_LABELS, fontsize=9)
    ax.set_title("Pairwise Activation Overlap (fraction of all problems)")
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{matrix[i,j]:.2f}", ha="center", va="center", fontsize=8,
                    color="white" if matrix[i,j] > 0.5 else "black")
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"✓ Saved {out}")


def plot_by_source(stats: dict, out: str = "figures/activation_by_source.png") -> None:
    _ensure_dir(out)
    per_src = stats.get("per_source", {})
    he = [per_src.get("humaneval", {}).get(c, 0.0) for c in CATS]
    mb = [per_src.get("mbpp", {}).get(c, 0.0) for c in CATS]

    x = np.arange(len(CATS))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width/2, he, width, label="HumanEval", color="steelblue", alpha=0.8)
    ax.bar(x + width/2, mb, width, label="MBPP", color="darkorange", alpha=0.8)
    ax.axhline(0.10, color="black", linestyle="--", linewidth=1.2, label="10% threshold")
    ax.set_xticks(x); ax.set_xticklabels(CAT_LABELS, rotation=15, ha="right")
    ax.set_ylabel("Activation Rate")
    ax.set_title("Activation Rate by Dataset Source")
    ax.set_ylim(0, 1)
    ax.legend()
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"✓ Saved {out}")


def plot_signal_length(results: dict, out: str = "figures/signal_length_dist.png") -> None:
    _ensure_dir(out)
    lengths = {cat: [] for cat in CATS}
    for pid, cat_results in results.items():
        for cat in CATS:
            r = cat_results.get(cat)
            if r and r.activated and r.signal:
                lengths[cat].append(len(r.signal))

    data = [lengths[c] for c in CATS]
    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot(data, labels=CAT_LABELS, patch_artist=True)
    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_ylabel("Signal Length (chars)")
    ax.set_title("Signal Length Distribution (activated problems only)")
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"✓ Saved {out}")


def plot_smt_pilot(pilot: dict, out: str = "figures/smt_pilot.png") -> None:
    _ensure_dir(out)
    outcomes = [r["outcome"] for r in pilot.get("pilot_results", [])]
    counts = {}
    for o in outcomes:
        counts[o] = counts.get(o, 0) + 1

    labels = list(counts.keys())
    values = [counts[l] for l in labels]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(labels, values, color=["green" if l == "sat" else "gray" for l in labels], alpha=0.8)
    ax.set_ylabel("Count")
    ax.set_title(f"SMT Pilot Results (n={pilot.get('total', 20)}, sat_rate={pilot.get('sat_rate', 0):.1%})")
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"✓ Saved {out}")
