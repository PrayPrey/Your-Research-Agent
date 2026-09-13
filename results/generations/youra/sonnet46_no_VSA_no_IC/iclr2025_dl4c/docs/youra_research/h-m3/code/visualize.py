import os
import matplotlib
matplotlib.use("Agg")  # headless — must be before pyplot import
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from config import H_M3Config


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
    gate_label = "PASS" if gate_metrics["primary_gate_pass"] else "FAIL"
    ax.set_title(f"H-M3: Zero-Gradient Fraction | Gate: {gate_label}")
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

    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "gate_comparison.png"), dpi=150)
    plt.close(fig)
    print(f"[viz] gate_comparison.png saved")


def plot_per_condition_curves(frac_var: list, frac_rnd: list, figures_dir: str) -> None:
    """Fig 3: two frac_zero_std lines over all logged steps (up to 200)."""
    steps = list(range(1, len(frac_var) + 1))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(steps, frac_var, label="variance-50", color="steelblue", linewidth=1.5)
    ax.plot(steps, frac_rnd, label="random-50", color="coral", linewidth=1.5)
    ax.axhline(0.0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Training Step")
    ax.set_ylabel("frac_reward_zero_std")
    ax.set_title("H-M3: frac_reward_zero_std Trajectory (Warm-Start, Up to 200 Steps)")
    ax.legend()
    ax.set_ylim(-0.05, 1.05)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "per_condition_curves.png"), dpi=150)
    plt.close(fig)
    print(f"[viz] per_condition_curves.png saved")


def plot_gap_trajectory_200(gap_by_step: dict, figures_dir: str) -> None:
    """Fig 2: line plot gap=frac_rnd-frac_var over all steps. Red fill if gap<0."""
    steps = sorted(gap_by_step.keys())
    gap_values = [gap_by_step[s] for s in steps]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(steps, gap_values, color="steelblue", linewidth=1.5, label="gap (random - variance)")
    ax.axhline(0.0, color="black", linestyle="--", linewidth=1.0)
    # Red fill where gap < 0
    ax.fill_between(
        steps, gap_values, 0,
        where=[g < 0 for g in gap_values],
        color="red", alpha=0.2, label="gap < 0 (variance-50 worse)"
    )
    # Green fill where gap >= 0
    ax.fill_between(
        steps, gap_values, 0,
        where=[g >= 0 for g in gap_values],
        color="green", alpha=0.15, label="gap >= 0 (variance-50 better)"
    )
    ax.set_xlabel("Training Step")
    ax.set_ylabel("Gap (frac_zero_std: random-50 − variance-50)")
    ax.set_title("Proxy Stability: Gap Trajectory Over Training Steps")
    ax.set_xlim(0, 200)
    ax.legend()
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "gap_trajectory_200.png"), dpi=150)
    plt.close(fig)
    print(f"[viz] gap_trajectory_200.png saved")


def plot_gap_retention_bar(
    gap_at_10: float,
    gap_at_20: float,
    gap_at_50: float,
    gap_retention: float,
    figures_dir: str,
) -> None:
    """Fig 4: bar chart at steps 10, 20, 50 annotated with P2 retention threshold."""
    target_steps = [10, 20, 50]
    gap_vals = [gap_at_10, gap_at_20, gap_at_50]

    fig, ax = plt.subplots(figsize=(6, 5))
    x = np.arange(len(target_steps))
    ax.bar(x, gap_vals, width=0.5, color="steelblue", label="gap at checkpoint")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Step {s}" for s in target_steps])
    ax.set_xlabel("Training Step")
    ax.set_ylabel("Gap (frac_zero_std: random-50 − variance-50)")
    ax.set_title(f"Gap at Checkpoints (P2 Retention Threshold: gap_50/gap_10 ≥ 0.5)")
    ax.axhline(0.0, color="black", linestyle="-", linewidth=0.8)

    # P2 threshold line: gap_10 * 0.5 (minimum gap_50 needed for retention >= 0.5)
    if gap_at_10 > 0:
        p2_line_y = gap_at_10 * 0.5
        ax.axhline(
            p2_line_y,
            color="orange", linestyle="--", linewidth=1.5,
            label=f"P2 threshold (gap_50/gap_10=0.5): {p2_line_y:.3f}"
        )

    # Annotate retention value
    ax.text(
        0.98, 0.05,
        f"gap_retention = {gap_retention:.3f}",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", edgecolor="gray")
    )
    ax.legend(fontsize=8)
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "gap_retention_bar.png"), dpi=150)
    plt.close(fig)
    print(f"[viz] gap_retention_bar.png saved")


def plot_reward_std_histogram(log_var: list, log_rnd: list, figures_dir: str) -> None:
    """Reward std at checkpoints 10, 20, 50 (kept from H-M2)."""
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
        print("[viz] reward_std not available in log_history — skipping")
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
    ax.set_title("H-M3: Mean Group Reward Std at Checkpoints")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Step {s}" for s in target_steps])
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, "reward_std_histograms.png"), dpi=150)
    plt.close(fig)
    print(f"[viz] reward_std_histograms.png saved")


def generate_all_figures(
    cfg: H_M3Config,
    gate_metrics: dict,
    gap_by_step: dict,
    gap_at_10: float,
    gap_at_20: float,
    gap_at_50: float,
    gap_retention: float,
    frac_var: list,
    frac_rnd: list,
    log_var: list,
    log_rnd: list,
) -> None:
    """Generate all H-M3 figures."""
    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)
    plot_gate_bar_chart(gate_metrics, cfg.figures_dir)
    plot_gap_trajectory_200(gap_by_step, cfg.figures_dir)
    plot_per_condition_curves(frac_var, frac_rnd, cfg.figures_dir)
    plot_gap_retention_bar(gap_at_10, gap_at_20, gap_at_50, gap_retention, cfg.figures_dir)
    plot_reward_std_histogram(log_var, log_rnd, cfg.figures_dir)
    print(f"[viz] All figures saved to {cfg.figures_dir}")
