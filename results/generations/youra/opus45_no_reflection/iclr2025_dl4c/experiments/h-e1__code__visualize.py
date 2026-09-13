"""Visualization for EVAF H-E1."""

import os
import matplotlib.pyplot as plt


def plot_gate_metrics(metrics: dict, out_path: str) -> None:
    """Bar chart with 20-60% target zone highlighted."""
    fig, ax = plt.subplots(figsize=(10, 6))

    categories = ["Accept Rate", "Coverage"]
    values = [metrics["accept_rate"] * 100, metrics["coverage"] * 100]
    colors = ["#2ecc71" if 20 <= values[0] <= 60 else "#e74c3c", "#3498db"]

    bars = ax.bar(categories, values, color=colors, edgecolor="black", linewidth=1.2)

    ax.axhspan(20, 60, alpha=0.2, color="green", label="Target Zone (20-60%)")
    ax.axhline(y=20, color="green", linestyle="--", linewidth=1.5)
    ax.axhline(y=60, color="green", linestyle="--", linewidth=1.5)

    ax.set_ylabel("Percentage (%)", fontsize=12)
    ax.set_title("EVAF Gate Metrics (H-E1)", fontsize=14, fontweight="bold")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper right")

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=11, fontweight="bold")

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_accept_distribution(results: list[dict], out_path: str) -> None:
    """Histogram of acceptance status."""
    fig, ax = plt.subplots(figsize=(8, 6))

    accepted = sum(1 for r in results if r.get("accepted", False))
    rejected = len(results) - accepted

    ax.bar(["Accepted", "Rejected"], [accepted, rejected],
           color=["#2ecc71", "#e74c3c"], edgecolor="black")

    ax.set_ylabel("Number of Problems", fontsize=12)
    ax.set_title("EVAF Accept/Reject Distribution (H-E1)", fontsize=14, fontweight="bold")

    for i, v in enumerate([accepted, rejected]):
        ax.text(i, v + 1, str(v), ha="center", va="bottom", fontsize=11, fontweight="bold")

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_rejection_breakdown(metrics: dict, out_path: str) -> None:
    """Pie chart of rejection reasons."""
    fig, ax = plt.subplots(figsize=(8, 8))

    breakdown = metrics.get("rejection_breakdown", {})
    if not breakdown:
        ax.text(0.5, 0.5, "No rejections", ha="center", va="center", fontsize=14)
        ax.axis("off")
    else:
        labels = list(breakdown.keys())
        sizes = list(breakdown.values())
        colors = plt.cm.Set3(range(len(labels)))

        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct="%1.1f%%",
            colors=colors, startangle=90,
            textprops={"fontsize": 10}
        )
        ax.set_title("Rejection Reason Breakdown (H-E1)", fontsize=14, fontweight="bold")

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
