import os
import matplotlib
matplotlib.use("Agg")  # headless — must be before pyplot import
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from config import H_M2Config


def plot_gate_bar_chart(gate_metrics: dict, figures_dir: str) -> None:
    """Fig 1: grouped bar of mean_frac_zero_std at checkpoints 10, 20, 50."""
    checkpoints = [10, 20, 50]
    var_vals = [gate_metrics[f"checkpoint_{N}"]["mean_frac_var"] for N in checkpoints]
    rnd_vals = [gate_metrics[f"checkpoint_{N}"]["mean_frac_rnd"] for N in checkpoints]

    x = np.arange(len(checkpoints))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    bars1 = ax.bar(x - width/2, var_vals, width, label="variance-50", color="steelblue")
    bars2 = ax.bar(x + width/2, rnd_vals, width, label="random-50", color="coral")

    ax.set_xlabel("Training Checkpoint (steps)")
    ax.set_ylabel("mean frac_reward_zero_std")
    ax.set_title("H-M2: Zero-Gradient Group Fraction by Selection Strategy")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Step {N}" for N in checkpoints])
    ax.legend()
    ax.set_ylim(0, 1.05)

    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{bar.get_height():.3f}", ha="center", va="bottom", fontsize=9)
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{bar.get_height():.3f}", ha="center", va="bottom", fontsize=9)

    gate_label = "PASS" if gate_metrics["primary_gate_pass"] else "FAIL"
    ax.set_title(f"H-M2: Zero-Gradient Fraction | Gate: {gate_label}")

    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "gate_comparison.png"), dpi=150)
    plt.close(fig)
    print(f"[viz] gate_comparison.png saved")


def plot_learning_curves(frac_var: list, frac_rnd: list, figures_dir: str) -> None:
    """Fig 2: per-step line plot steps 1-50."""
    steps = list(range(1, len(frac_var) + 1))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(steps, frac_var, label="variance-50", color="steelblue", linewidth=1.5)
    ax.plot(steps, frac_rnd, label="random-50", color="coral", linewidth=1.5)
    ax.axhline(0.0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Training Step")
    ax.set_ylabel("frac_reward_zero_std")
    ax.set_title("H-M2: frac_reward_zero_std Trajectory (Steps 1-50)")
    ax.legend()
    ax.set_ylim(-0.05, 1.05)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "learning_curves.png"), dpi=150)
    plt.close(fig)
    print(f"[viz] learning_curves.png saved")


def plot_gap_trajectory(frac_var: list, frac_rnd: list, figures_dir: str) -> None:
    """Fig 3: gap = frac_rnd - frac_var per step."""
    steps = list(range(1, len(frac_var) + 1))
    gap = [r - v for r, v in zip(frac_rnd, frac_var)]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(steps, gap, color="green", linewidth=1.5, label="gap (random - variance)")
    ax.axhline(0.0, color="black", linestyle="--", linewidth=1.0, label="0.0 threshold")
    ax.axhline(0.05, color="orange", linestyle="--", linewidth=1.0, label="0.05 secondary gate")
    ax.fill_between(steps, 0, gap, where=[g > 0 for g in gap], alpha=0.2, color="green")
    ax.fill_between(steps, 0, gap, where=[g <= 0 for g in gap], alpha=0.2, color="red")
    ax.set_xlabel("Training Step")
    ax.set_ylabel("frac_zero_std gap (random-50 − variance-50)")
    ax.set_title("H-M2: Gap Trajectory")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "gap_trajectory.png"), dpi=150)
    plt.close(fig)
    print(f"[viz] gap_trajectory.png saved")


def plot_reward_std_histogram(log_var: list, log_rnd: list, figures_dir: str) -> None:
    """
    Fig 4: reward_std scalar at checkpoints 10, 20, 50.
    TRL logs mean reward_std (not raw per-group). Use available scalar.
    """
    def extract_reward_std(log_history, steps):
        vals = {}
        for entry in log_history:
            step = entry.get("step", None)
            if step in steps and "reward_std" in entry:
                vals[step] = entry["reward_std"]
        return vals

    target_steps = [10, 20, 50]
    std_var = extract_reward_std(log_var, target_steps)
    std_rnd = extract_reward_std(log_rnd, target_steps)

    if not std_var and not std_rnd:
        print("[viz] reward_std not available in log_history — skipping histogram")
        return

    x = np.arange(len(target_steps))
    width = 0.35
    var_vals = [std_var.get(s, 0.0) for s in target_steps]
    rnd_vals = [std_rnd.get(s, 0.0) for s in target_steps]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, var_vals, width, label="variance-50", color="steelblue")
    ax.bar(x + width/2, rnd_vals, width, label="random-50", color="coral")
    ax.set_xlabel("Training Step")
    ax.set_ylabel("mean reward_std")
    ax.set_title("H-M2: Mean Group Reward Std at Checkpoints")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Step {s}" for s in target_steps])
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "reward_std_histograms.png"), dpi=150)
    plt.close(fig)
    print(f"[viz] reward_std_histograms.png saved")


def generate_all_figures(
    cfg: H_M2Config,
    gate_metrics: dict,
    frac_var: list,
    frac_rnd: list,
    log_var: list,
    log_rnd: list,
) -> None:
    """Generate all 4 figures."""
    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)
    plot_gate_bar_chart(gate_metrics, cfg.figures_dir)
    plot_learning_curves(frac_var, frac_rnd, cfg.figures_dir)
    plot_gap_trajectory(frac_var, frac_rnd, cfg.figures_dir)
    plot_reward_std_histogram(log_var, log_rnd, cfg.figures_dir)
    print(f"[viz] All figures saved to {cfg.figures_dir}")
