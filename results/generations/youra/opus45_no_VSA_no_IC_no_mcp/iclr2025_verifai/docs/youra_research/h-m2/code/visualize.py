import matplotlib.pyplot as plt
import numpy as np
import os
from config import CONFIG

def plot_gate_comparison(results: dict, out_path: str = None) -> None:
    """Side-by-side bar chart of Structured vs Scrambled success rates with 95% CI."""
    fig, ax = plt.subplots(figsize=(8, 6))

    conditions = ["Structured", "Scrambled"]
    rates = [results["structured_rate"] * 100, results["scrambled_rate"] * 100]
    ci_lower, ci_upper = results["ci_95"]

    # Error bars: CI is on the delta, approximate for individual bars
    # Use bootstrap SE as rough error estimate
    se = (ci_upper - ci_lower) / 3.92 * 100  # 95% CI = 3.92 SEs
    errors = [se, se]

    bars = ax.bar(conditions, rates, yerr=errors, capsize=5, color=["#2ecc71", "#e74c3c"])
    ax.set_ylabel("Repair Success Rate (%)")
    ax.set_title(f"Structure vs Scrambled Format\n(n={results['n_samples']}, p={results['p_value']:.4f})")
    ax.set_ylim(0, 100)

    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f"{rate:.1f}%", ha="center", fontsize=12)

    plt.tight_layout()
    out_path = out_path or os.path.join(CONFIG["figures_dir"], "gate_comparison.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")

def plot_discordant_pairs(results: dict, out_path: str = None) -> None:
    """Bar chart of discordant pair analysis."""
    fig, ax = plt.subplots(figsize=(6, 5))

    categories = ["Structured Wins\n(Structured=pass, Scrambled=fail)",
                  "Scrambled Wins\n(Structured=fail, Scrambled=pass)"]
    counts = [results["discordant_structured_wins"], results["discordant_scrambled_wins"]]

    bars = ax.bar(categories, counts, color=["#2ecc71", "#e74c3c"])
    ax.set_ylabel("Number of Samples")
    ax.set_title("Discordant Pair Analysis")

    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                str(count), ha="center", fontsize=12)

    plt.tight_layout()
    out_path = out_path or os.path.join(CONFIG["figures_dir"], "discordant_pairs.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")
