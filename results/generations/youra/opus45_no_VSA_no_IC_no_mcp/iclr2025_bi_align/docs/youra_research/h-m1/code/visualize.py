"""Visualization for reward distribution."""
import matplotlib.pyplot as plt
import numpy as np


def plot_reward_distribution(rewards_chosen: list, rewards_rejected: list, out_path: str) -> None:
    """Plot reward distribution histogram."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(rewards_chosen, bins=50, alpha=0.6, label="Chosen", color="green")
    ax.hist(rewards_rejected, bins=50, alpha=0.6, label="Rejected", color="red")

    ax.axvline(np.mean(rewards_chosen), color="darkgreen", linestyle="--", label=f"Chosen mean: {np.mean(rewards_chosen):.3f}")
    ax.axvline(np.mean(rewards_rejected), color="darkred", linestyle="--", label=f"Rejected mean: {np.mean(rewards_rejected):.3f}")

    ax.set_xlabel("Reward Score")
    ax.set_ylabel("Count")
    ax.set_title("Reward Model Distribution: Chosen vs Rejected")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved distribution plot to {out_path}")
