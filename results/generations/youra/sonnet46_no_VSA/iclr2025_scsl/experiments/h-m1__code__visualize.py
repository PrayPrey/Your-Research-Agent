import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import config

V = config.VIZ


def _save(fig, name: str) -> None:
    path = os.path.join(config.FIGURES_DIR, name)
    fig.savefig(path, dpi=V["dpi"], bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_gate_metrics(results_per_seed: dict) -> None:
    """fig_gate_metrics.png — p_min(t*) and p_maj(t*) per seed with threshold lines."""
    seeds = sorted(results_per_seed.keys())
    p_mins = [results_per_seed[s][results_per_seed[s]["tstar"]]["p_min"] for s in seeds]
    p_majs = [results_per_seed[s][results_per_seed[s]["tstar"]]["p_maj"] for s in seeds]

    fig, ax = plt.subplots(figsize=(V["fig_width"], V["fig_height"]))
    x = np.arange(len(seeds))
    width = 0.35
    ax.bar(x - width / 2, p_mins, width, label="p_minority(t*)", color=V["minority_color"], alpha=0.8)
    ax.bar(x + width / 2, p_majs, width, label="p_majority(t*)", color=V["majority_color"], alpha=0.8)

    ax.axhline(config.GATE_P_MIN_LOW, color=V["gate_low_color"], linestyle=V["threshold_linestyle"],
               linewidth=V["threshold_linewidth"], label=f"Gate low ({config.GATE_P_MIN_LOW})")
    ax.axhline(config.GATE_P_MIN_HIGH, color=V["gate_high_color"], linestyle=V["threshold_linestyle"],
               linewidth=V["threshold_linewidth"], label=f"Gate high ({config.GATE_P_MIN_HIGH})")
    ax.axhline(config.GATE_P_MAJ, color=V["gate_maj_color"], linestyle=V["threshold_linestyle"],
               linewidth=V["threshold_linewidth"], label=f"Majority gate ({config.GATE_P_MAJ})")

    ax.set_xticks(x)
    ax.set_xticklabels([f"Seed {s}" for s in seeds])
    ax.set_ylabel("Confidence")
    ax.set_ylim(0, 1)
    ax.set_title("H-M1 Gate Metrics: Confidence at t* per Seed")
    ax.legend(loc="upper left")
    _save(fig, "fig_gate_metrics.png")


def plot_confidence_trajectory(results_per_seed: dict) -> None:
    """fig_confidence_trajectory.png — p_min(t) and p_maj(t) vs t per seed."""
    epochs = config.CHECKPOINT_EPOCHS

    fig, ax = plt.subplots(figsize=(V["fig_width"], V["fig_height"]))
    for i, seed in enumerate(sorted(results_per_seed.keys())):
        traj = results_per_seed[seed]
        p_mins = [traj[e]["p_min"] for e in epochs]
        p_majs = [traj[e]["p_maj"] for e in epochs]
        alpha = 0.5 + 0.1 * i
        ax.plot(epochs, p_mins, color=V["minority_color"], alpha=alpha, marker="o", linewidth=1.5,
                label=f"Minority s{seed}" if i == 0 else None)
        ax.plot(epochs, p_majs, color=V["majority_color"], alpha=alpha, marker="s", linewidth=1.5,
                label=f"Majority s{seed}" if i == 0 else None)

    # Show gate bands
    ax.axhspan(config.GATE_P_MIN_LOW, config.GATE_P_MIN_HIGH, alpha=0.1,
               color=V["gate_low_color"], label="Gate band [0.3, 0.7]")
    ax.axhline(config.GATE_P_MAJ, color=V["gate_maj_color"], linestyle=V["threshold_linestyle"],
               linewidth=V["threshold_linewidth"], label=f"Majority gate {config.GATE_P_MAJ}")

    ax.set_xlabel("Training Epoch")
    ax.set_ylabel("Mean Confidence")
    ax.set_title("H-M1 Confidence Trajectories: Minority vs Majority (5 seeds)")
    # Custom legend: just 2 group lines
    from matplotlib.lines import Line2D
    handles = [
        Line2D([0], [0], color=V["minority_color"], marker="o", label="Minority (G1+G2)"),
        Line2D([0], [0], color=V["majority_color"], marker="s", label="Majority (G0+G3)"),
        plt.axhspan(0, 0, alpha=0.1, color=V["gate_low_color"], label="Gate band"),
    ]
    ax.legend(handles=handles[:2])
    _save(fig, "fig_confidence_trajectory.png")


def plot_conf_distribution(results_per_seed: dict) -> None:
    """fig_conf_distribution.png — box plot of p_per_sample at t* for minority vs majority."""
    import torch
    minority_confs = []
    majority_confs = []

    for seed, traj in results_per_seed.items():
        tstar = traj["tstar"]
        p_ps = traj[tstar]["p_per_sample"]
        # Rebuild minority_mask — same shape as loader dataset
        # minority_mask stored per seed via the same indexing in main
        # Use per-seed p_per_sample if mask available; else approximate
        if "minority_mask" in traj:
            mask = traj["minority_mask"]
        else:
            # fallback: use stored boolean from aggregate (if set)
            continue
        minority_confs.extend(p_ps[mask].tolist())
        majority_confs.extend(p_ps[~mask].tolist())

    if not minority_confs:
        print("  Skipping distribution plot (no minority_mask stored)")
        return

    fig, ax = plt.subplots(figsize=(V["fig_width"], V["fig_height"]))
    bp = ax.boxplot(
        [minority_confs, majority_confs],
        labels=["Minority (G1+G2)", "Majority (G0+G3)"],
        patch_artist=True,
    )
    bp["boxes"][0].set_facecolor(V["minority_color"])
    bp["boxes"][0].set_alpha(0.7)
    bp["boxes"][1].set_facecolor(V["majority_color"])
    bp["boxes"][1].set_alpha(0.7)

    ax.axhline(config.GATE_P_MIN_LOW, color=V["gate_low_color"], linestyle=V["threshold_linestyle"],
               linewidth=V["threshold_linewidth"])
    ax.axhline(config.GATE_P_MIN_HIGH, color=V["gate_high_color"], linestyle=V["threshold_linestyle"],
               linewidth=V["threshold_linewidth"])
    ax.axhline(config.GATE_P_MAJ, color=V["gate_maj_color"], linestyle=V["threshold_linestyle"],
               linewidth=V["threshold_linewidth"])

    ax.set_ylabel("Confidence (softmax in true class)")
    ax.set_title("H-M1 Confidence Distribution at t* (across 5 seeds)")
    _save(fig, "fig_conf_distribution.png")


def plot_boundary_fraction(results_per_seed: dict) -> None:
    """fig_boundary_fraction.png — fraction of minority samples with p∈[0.3,0.7] at each epoch."""
    epochs = config.CHECKPOINT_EPOCHS

    fig, ax = plt.subplots(figsize=(V["fig_width"], V["fig_height"]))
    has_data = False
    for seed, traj in results_per_seed.items():
        if "minority_mask" not in traj:
            continue
        mask = traj["minority_mask"]
        fractions = []
        for epoch in epochs:
            p_ps = traj[epoch]["p_per_sample"]
            p_min_samples = p_ps[mask]
            in_boundary = ((p_min_samples >= config.GATE_P_MIN_LOW) &
                           (p_min_samples <= config.GATE_P_MIN_HIGH))
            fractions.append(in_boundary.float().mean().item())
        ax.plot(epochs, fractions, marker="o", label=f"Seed {seed}", alpha=0.7)
        has_data = True

    if not has_data:
        print("  Skipping boundary fraction plot (no minority_mask stored)")
        return

    ax.set_xlabel("Training Epoch")
    ax.set_ylabel("Fraction of Minority in [0.3, 0.7]")
    ax.set_ylim(0, 1)
    ax.set_title("H-M1 Boundary Fraction: Minority in Gate Band per Epoch")
    ax.legend()
    _save(fig, "fig_boundary_fraction.png")


def save_all_figures(results_per_seed: dict) -> None:
    """Generate all 4 required figures."""
    config.ensure_dirs()
    print("Generating figures...")
    plot_gate_metrics(results_per_seed)
    plot_confidence_trajectory(results_per_seed)
    plot_conf_distribution(results_per_seed)
    plot_boundary_fraction(results_per_seed)
