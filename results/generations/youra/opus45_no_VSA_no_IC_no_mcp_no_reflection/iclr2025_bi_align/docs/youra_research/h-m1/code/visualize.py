"""H-M1 Visualization: Training plots."""
import json
from pathlib import Path
import matplotlib.pyplot as plt


def plot_reward_trajectory(history: list[dict], out_dir: Path):
    """Plot reward components and KL over training steps."""
    out_dir.mkdir(parents=True, exist_ok=True)

    steps = [h["step"] for h in history]
    rewards = [h["reward/mean"] for h in history]
    helpfulness = [h["reward/helpfulness"] for h in history]
    controllability = [h["reward/controllability"] for h in history]
    kls = [h["objective/kl"] for h in history]

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Combined reward
    axes[0, 0].plot(steps, rewards, 'b-', linewidth=2)
    axes[0, 0].set_xlabel("Step")
    axes[0, 0].set_ylabel("Combined Reward")
    axes[0, 0].set_title("Combined Reward Trajectory")
    axes[0, 0].grid(True, alpha=0.3)

    # Helpfulness
    axes[0, 1].plot(steps, helpfulness, 'g-', linewidth=2)
    axes[0, 1].set_xlabel("Step")
    axes[0, 1].set_ylabel("R_helpfulness")
    axes[0, 1].set_title("Helpfulness Reward")
    axes[0, 1].grid(True, alpha=0.3)

    # Controllability
    axes[1, 0].plot(steps, controllability, 'r-', linewidth=2)
    axes[1, 0].set_xlabel("Step")
    axes[1, 0].set_ylabel("R_IFEval")
    axes[1, 0].set_title("Controllability Reward (IFEval)")
    axes[1, 0].grid(True, alpha=0.3)

    # KL divergence
    axes[1, 1].plot(steps, kls, 'm-', linewidth=2)
    axes[1, 1].axhline(y=5.0, color='r', linestyle='--', label='Threshold (5.0)')
    axes[1, 1].set_xlabel("Step")
    axes[1, 1].set_ylabel("KL Divergence")
    axes[1, 1].set_title("KL Divergence from Reference")
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_dir / "reward_trajectory.png", dpi=150)
    plt.close()

    print(f"Saved reward_trajectory.png to {out_dir}")


def plot_component_comparison(history: list[dict], out_dir: Path):
    """Plot helpfulness vs controllability on same axes."""
    out_dir.mkdir(parents=True, exist_ok=True)

    steps = [h["step"] for h in history]
    helpfulness = [h["reward/helpfulness"] for h in history]
    controllability = [h["reward/controllability"] for h in history]

    plt.figure(figsize=(10, 6))
    plt.plot(steps, helpfulness, 'g-', linewidth=2, label='Helpfulness')
    plt.plot(steps, controllability, 'r-', linewidth=2, label='Controllability')
    plt.xlabel("Step")
    plt.ylabel("Reward Component")
    plt.title("Reward Components Over Training")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig(out_dir / "component_comparison.png", dpi=150)
    plt.close()

    print(f"Saved component_comparison.png to {out_dir}")


def plot_reward_hacking(train_rewards: list[float], eval_metrics: list[float],
                        correlation: float, out_dir: Path):
    """Scatter plot of training reward vs eval metric."""
    out_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 8))
    plt.scatter(train_rewards, eval_metrics, s=100, alpha=0.7)
    plt.xlabel("Training Reward")
    plt.ylabel("Eval IFEval Accuracy")
    plt.title(f"Reward Hacking Check (r={correlation:.3f})")
    plt.grid(True, alpha=0.3)

    # Add regression line
    if len(train_rewards) > 1:
        import numpy as np
        z = np.polyfit(train_rewards, eval_metrics, 1)
        p = np.poly1d(z)
        x_line = [min(train_rewards), max(train_rewards)]
        plt.plot(x_line, [p(x) for x in x_line], 'r--', linewidth=2)

    plt.savefig(out_dir / "reward_hacking.png", dpi=150)
    plt.close()

    print(f"Saved reward_hacking.png to {out_dir}")


if __name__ == "__main__":
    import sys

    history_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("outputs/training_history.json")
    out_dir = history_path.parent.parent / "figures"

    with open(history_path) as f:
        history = json.load(f)

    plot_reward_trajectory(history, out_dir)
    plot_component_comparison(history, out_dir)
