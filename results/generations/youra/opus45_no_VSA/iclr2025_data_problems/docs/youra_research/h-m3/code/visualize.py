import os
import matplotlib.pyplot as plt
import numpy as np


def plot_ai_bar_with_ci(ai: float, ci: tuple, out_dir: str) -> str:
    """Plot Amplification Index with 95% CI error bars."""
    os.makedirs(out_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 5))

    ci_lower, ci_upper = ci
    error_lower = ai - ci_lower
    error_upper = ci_upper - ai

    ax.bar(["Perplexity vs Random"], [ai], color="#4a90d9", edgecolor="black")
    ax.errorbar(["Perplexity vs Random"], [ai],
                yerr=[[error_lower], [error_upper]],
                fmt="none", color="black", capsize=5)

    ax.axhline(y=0, color="red", linestyle="--", linewidth=1, label="AI=0")
    ax.set_ylabel("Amplification Index")
    ax.set_title("H-M3: Amplification Index (AI)")
    ax.legend()

    # Annotate
    ax.text(0, ai + 0.02, f"AI={ai:.4f}\n95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]",
            ha="center", fontsize=9)

    path = os.path.join(out_dir, "ai_bar_chart.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

    print(f"Saved: {path}")
    return path


def plot_delta_boxplot(deltas: dict, out_dir: str) -> str:
    """Box plot of per-seed deltas by strategy."""
    os.makedirs(out_dir, exist_ok=True)

    ppl_deltas = [v for k, v in deltas.items() if "perplexity" in k]
    rand_deltas = [v for k, v in deltas.items() if "random" in k]

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.boxplot([ppl_deltas, rand_deltas], labels=["Perplexity", "Random"])
    ax.set_ylabel("Delta (Acc_contaminated - Acc_clean)")
    ax.set_title("H-M3: Per-Seed Deltas by Strategy")
    ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.5)

    path = os.path.join(out_dir, "delta_boxplot.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

    print(f"Saved: {path}")
    return path
