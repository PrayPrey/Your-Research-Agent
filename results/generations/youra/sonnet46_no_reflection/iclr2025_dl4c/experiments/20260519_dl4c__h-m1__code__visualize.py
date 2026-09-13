import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")


def plot_kl_curves(grpo_kl_log: list, dpo_kl_log: list, output_path: str) -> None:
    """Figure 1: KL divergence vs training step for GRPO and DPO."""
    fig, ax = plt.subplots(figsize=(8, 5))
    if grpo_kl_log:
        steps = [e["step"] for e in grpo_kl_log]
        kls = [e["kl_divergence"] for e in grpo_kl_log]
        ax.plot(steps, kls, label="GRPO", marker="o", markersize=4)
    if dpo_kl_log:
        steps = [e["step"] for e in dpo_kl_log]
        kls = [e["kl_divergence"] for e in dpo_kl_log]
        ax.plot(steps, kls, label="DPO", marker="s", markersize=4)
    ax.set_xlabel("Training Step")
    ax.set_ylabel("KL Divergence")
    ax.set_title("KL Divergence vs Training Step")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_edit_per_kl(grpo_per_kl: list, dpo_per_kl: list, output_path: str) -> None:
    """Figure 2: Semantic-edit-per-KL bar chart for GRPO vs DPO."""
    fig, ax = plt.subplots(figsize=(6, 5))
    means = [
        float(np.mean(grpo_per_kl)) if grpo_per_kl else 0.0,
        float(np.mean(dpo_per_kl)) if dpo_per_kl else 0.0,
    ]
    stds = [
        float(np.std(grpo_per_kl)) if grpo_per_kl else 0.0,
        float(np.std(dpo_per_kl)) if dpo_per_kl else 0.0,
    ]
    ax.bar(["GRPO", "DPO"], means, yerr=stds, capsize=5, color=["steelblue", "coral"])
    ax.set_ylabel("Semantic Edit Distance / KL")
    ax.set_title("Semantic Edit per KL Divergence")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_bootstrap_ci(ci_result: dict, output_path: str) -> None:
    """Figure 3: Bootstrap CI for GRPO-DPO differential."""
    fig, ax = plt.subplots(figsize=(6, 4))
    mean = ci_result.get("mean", 0)
    lower = ci_result.get("lower", 0)
    upper = ci_result.get("upper", 0)
    ax.errorbar([0], [mean], yerr=[[mean - lower], [upper - mean]],
                fmt="o", capsize=8, color="steelblue", markersize=8)
    ax.axhline(0, color="red", linestyle="--", alpha=0.7, label="H0: diff=0")
    ax.set_xlim(-0.5, 0.5)
    ax.set_xticks([])
    ax.set_ylabel("GRPO - DPO (Semantic Edit / KL)")
    ax.set_title(f"Bootstrap 95% CI: [{lower:.3f}, {upper:.3f}]")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_pass_rates(grpo_pass_rate: float, dpo_pass_rate: float, output_path: str) -> None:
    """Figure 4: Pass@1 rates for GRPO vs DPO."""
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.bar(["GRPO", "DPO"], [grpo_pass_rate, dpo_pass_rate], color=["steelblue", "coral"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Pass@1")
    ax.set_title("HumanEval+ Pass@1")
    ax.grid(True, axis="y", alpha=0.3)
    for i, v in enumerate([grpo_pass_rate, dpo_pass_rate]):
        ax.text(i, v + 0.01, f"{v:.3f}", ha="center", va="bottom")
    fig.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def generate_all_figures(results: dict, grpo_kl_log: list, dpo_kl_log: list, figures_dir: str) -> list:
    """Generate all 4 figures. Returns list of file paths."""
    os.makedirs(figures_dir, exist_ok=True)
    paths = []

    p1 = os.path.join(figures_dir, "fig1_kl_curves.png")
    plot_kl_curves(grpo_kl_log, dpo_kl_log, p1)
    paths.append(p1)

    p2 = os.path.join(figures_dir, "fig2_edit_per_kl.png")
    plot_edit_per_kl(results.get("grpo_edit_per_kl", []), results.get("dpo_edit_per_kl", []), p2)
    paths.append(p2)

    p3 = os.path.join(figures_dir, "fig3_bootstrap_ci.png")
    plot_bootstrap_ci(results.get("bootstrap_ci", {}), p3)
    paths.append(p3)

    p4 = os.path.join(figures_dir, "fig4_pass_rates.png")
    plot_pass_rates(results.get("grpo_pass_rate", 0), results.get("dpo_pass_rate", 0), p4)
    paths.append(p4)

    print(f"Figures saved to {figures_dir}: {[os.path.basename(p) for p in paths]}")
    return paths
