import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_bug_distribution(summary: dict, output_dir: str):
    """Required figure: bug-type distribution bar chart with 80% threshold line."""
    bug_types = ["type_error", "runtime_error", "logic_error"]
    fractions = [summary[t] for t in bug_types]
    colors = ["#e74c3c", "#f39c12", "#3498db"]
    labels = ["Type Error", "Runtime Error", "Logic Error"]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, fractions, color=colors, alpha=0.85, edgecolor="black", linewidth=0.7)

    # Annotate bars with counts and percentages
    counts = summary.get("counts", {})
    for bar, bug_type, frac in zip(bars, bug_types, fractions):
        count = counts.get(bug_type, 0)
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{frac:.1%}\n(n={count})", ha="center", va="bottom", fontsize=10)

    # 80% threshold line
    ax.axhline(0.80, color="red", linestyle="--", linewidth=1.5, label="80% threshold")

    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Fraction of Failures", fontsize=12)
    ax.set_title(f"H-M1: Bug-Type Distribution of GPT-4o-mini Failures\n"
                 f"(n={summary['n_failures']} failures / {summary['n_total']} problems, "
                 f"pass@1={summary['pass_rate']:.1%})", fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    mixed = summary.get("mixed_distribution", False)
    verdict = "PASS: Mixed distribution" if mixed else "FAIL: Single type dominates"
    ax.text(0.98, 0.97, verdict, transform=ax.transAxes,
            ha="right", va="top", fontsize=9,
            color="green" if mixed else "red",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="gray", alpha=0.8))

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "bug_distribution.png")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"✓ Saved: {path}")


def plot_stacked_bar(summary: dict, output_dir: str):
    """Stacked bar: HumanEval vs MBPP bug-type distributions."""
    bug_types = ["type_error", "runtime_error", "logic_error"]
    colors = ["#e74c3c", "#f39c12", "#3498db"]
    labels = ["Type Error", "Runtime Error", "Logic Error"]

    fig, ax = plt.subplots(figsize=(6, 5))
    sources = ["humaneval", "mbpp"]
    source_labels = ["HumanEval", "MBPP"]
    x = np.arange(len(sources))
    width = 0.5

    bottoms = np.zeros(len(sources))
    for bug_type, color, label in zip(bug_types, colors, labels):
        fracs = []
        for src in sources:
            src_data = summary.get(src, {})
            total = src_data.get("n_failures", 0)
            count = src_data.get("counts", {}).get(bug_type, 0)
            fracs.append(count / total if total else 0.0)
        ax.bar(x, fracs, width, bottom=bottoms, color=color, alpha=0.85,
               edgecolor="black", linewidth=0.5, label=label)
        bottoms += np.array(fracs)

    ax.set_xticks(x)
    ax.set_xticklabels(source_labels, fontsize=12)
    ax.set_ylabel("Fraction of Failures", fontsize=12)
    ax.set_ylim(0, 1.05)
    ax.set_title("Bug-Type Distribution by Dataset", fontsize=12)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    # Failure counts
    for i, src in enumerate(sources):
        n = summary.get(src, {}).get("n_failures", 0)
        ax.text(i, -0.06, f"n={n}", ha="center", va="top", fontsize=9, transform=ax.get_xaxis_transform())

    path = os.path.join(output_dir, "stacked_by_dataset.png")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"✓ Saved: {path}")


def plot_spot_check(spot_check_result: dict, output_dir: str):
    """Agreement matrix: auto classifier vs exception-only reference."""
    details = spot_check_result.get("details", [])
    if not details:
        return

    bug_types = ["type_error", "runtime_error", "logic_error"]
    matrix = {ref: {auto: 0 for auto in bug_types} for ref in bug_types}
    for d in details:
        ref = d["ref"]
        auto = d["auto"]
        if ref in matrix and auto in matrix[ref]:
            matrix[ref][auto] += 1

    data = np.array([[matrix[ref][auto] for auto in bug_types] for ref in bug_types])
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(data, cmap="Blues")
    ax.set_xticks(range(len(bug_types)))
    ax.set_yticks(range(len(bug_types)))
    tick_labels = ["Type\nError", "Runtime\nError", "Logic\nError"]
    ax.set_xticklabels(tick_labels, fontsize=10)
    ax.set_yticklabels(tick_labels, fontsize=10)
    ax.set_xlabel("Auto Label (Pyright-based)", fontsize=11)
    ax.set_ylabel("Reference Label (Exception-only)", fontsize=11)
    ax.set_title(f"Spot-Check Agreement: {spot_check_result['agreement_rate']:.1%} "
                 f"(n={spot_check_result['n_sampled']})", fontsize=11)

    for i in range(len(bug_types)):
        for j in range(len(bug_types)):
            ax.text(j, i, str(data[i, j]), ha="center", va="center", fontsize=12,
                    color="white" if data[i, j] > data.max() / 2 else "black")

    fig.colorbar(im, ax=ax)
    path = os.path.join(output_dir, "spot_check_agreement.png")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"✓ Saved: {path}")
