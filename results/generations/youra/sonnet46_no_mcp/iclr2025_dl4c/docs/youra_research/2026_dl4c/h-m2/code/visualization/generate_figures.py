import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import linregress

COLORS = {
    "curriculum": "blue",
    "uniform": "orange",
    "easy_only": "green",
    "hard_only": "red",
}

CONDITIONS = ["curriculum", "uniform", "easy_only", "hard_only"]


def plot_scatter_density_vs_gain(
    all_densities: np.ndarray,
    all_gains: np.ndarray,
    condition_labels: list,
    pearson_r: float,
    output_path: str,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 7))
    for cond in CONDITIONS:
        mask = [l == cond for l in condition_labels]
        if not any(mask):
            continue
        x = all_densities[mask]
        y = all_gains[mask]
        ax.scatter(x, y, color=COLORS[cond], label=cond, alpha=0.7, s=60)

    if len(all_densities) >= 2 and np.std(all_densities) > 1e-9:
        slope, intercept, _, _, _ = linregress(all_densities, all_gains)
        x_line = np.linspace(all_densities.min(), all_densities.max(), 100)
        ax.plot(x_line, slope * x_line + intercept, "k--", linewidth=1.5)

    ax.set_xlabel("Reward Density (window mean)", fontsize=12)
    ax.set_ylabel("Pass@1 Gain (next 500 steps)", fontsize=12)
    ax.set_title(f"Reward Density vs Pass@1 Gain (Pearson r={pearson_r:.4f})", fontsize=13)
    ax.legend()
    ax.annotate(f"r = {pearson_r:.4f}", xy=(0.05, 0.92), xycoords="axes fraction", fontsize=11)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_entropy_timeseries(data: dict, output_path: str) -> None:
    from analysis.compute_entropy import add_entropy_column

    fig, ax = plt.subplots(figsize=(10, 7))
    for cond in CONDITIONS:
        if cond not in data:
            continue
        df = add_entropy_column(data[cond]["density"])
        ax.plot(df["step"], df["entropy"], color=COLORS[cond], label=cond, marker="o", markersize=4)

    ax.axvline(x=2500, color="gray", linestyle="--", linewidth=1, label="step 2500")
    ax.set_xlabel("Training Step", fontsize=12)
    ax.set_ylabel("Reward Entropy H(p)", fontsize=12)
    ax.set_title("Reward Entropy over Training Steps", fontsize=13)
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_entropy_density_comparison(data: dict, output_path: str) -> None:
    from analysis.compute_entropy import add_entropy_column

    conds = [c for c in CONDITIONS if c in data]
    early_densities = []
    early_entropies = []

    for cond in conds:
        df = add_entropy_column(data[cond]["density"])
        early = df[df["step"] <= 2500]
        early_densities.append(early["reward_density"].mean() if len(early) > 0 else 0.0)
        early_entropies.append(early["entropy"].mean() if len(early) > 0 else 0.0)

    x = np.arange(len(conds))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 7))
    bars1 = ax.bar(x - width / 2, early_densities, width, label="Reward Density",
                   color=[COLORS[c] for c in conds], alpha=0.7)
    bars2 = ax.bar(x + width / 2, early_entropies, width, label="Entropy H(p)",
                   color=[COLORS[c] for c in conds], alpha=0.4, hatch="//")

    ax.set_xlabel("Condition", fontsize=12)
    ax.set_ylabel("Mean Value (steps 0-2500)", fontsize=12)
    ax.set_title("Early-Phase Reward Density vs Entropy by Condition", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(conds)
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_per_condition_scatter(data: dict, output_path: str) -> None:
    from analysis.compute_gains import compute_pass1_gains

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes_flat = axes.flatten()

    for i, cond in enumerate(CONDITIONS):
        ax = axes_flat[i]
        if cond not in data:
            ax.set_title(f"{cond} (no data)")
            continue

        density_df = data[cond]["density"].sort_values("step").reset_index(drop=True)
        pass1_df = data[cond]["pass1"].sort_values("step").reset_index(drop=True)

        n_ckpts = min(len(density_df), len(pass1_df))
        n_intervals = min(n_ckpts - 1, 9)

        if n_intervals < 2:
            ax.set_title(f"{cond} (insufficient data)")
            continue

        densities = density_df["reward_density"].values[:n_intervals]
        gains = np.diff(pass1_df["pass1"].values[:n_intervals + 1])

        ax.scatter(densities, gains, color=COLORS[cond], s=60, alpha=0.8)

        if n_intervals >= 2 and np.std(densities) > 1e-9:
            try:
                slope, intercept, r, _, _ = linregress(densities, gains)
                x_line = np.linspace(densities.min(), densities.max(), 50)
                ax.plot(x_line, slope * x_line + intercept, "k--", linewidth=1)
                ax.set_title(f"{cond} (r={r:.3f})", fontsize=11)
            except Exception:
                ax.set_title(cond, fontsize=11)

        ax.set_xlabel("Reward Density")
        ax.set_ylabel("Pass@1 Gain")

    plt.suptitle("Per-Condition: Reward Density vs Pass@1 Gain", fontsize=13)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_pass1_gain_timeseries(data: dict, output_path: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 7))

    for cond in CONDITIONS:
        if cond not in data:
            continue
        pass1_df = data[cond]["pass1"].sort_values("step").reset_index(drop=True)
        if len(pass1_df) < 2:
            continue
        steps = pass1_df["step"].values[1:]
        gains = np.diff(pass1_df["pass1"].values)
        ax.plot(steps, gains, color=COLORS[cond], label=cond, marker="o", markersize=4)

    ax.axhline(y=0, color="gray", linestyle="--", linewidth=1)
    ax.set_xlabel("Training Step (end of interval)", fontsize=12)
    ax.set_ylabel("Pass@1 Gain", fontsize=12)
    ax.set_title("Pass@1 Gain per 500-Step Interval", fontsize=13)
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def generate_all_figures(
    data: dict,
    all_densities: np.ndarray,
    all_gains: np.ndarray,
    condition_labels: list,
    pearson_r: float,
    figures_dir: str,
) -> None:
    os.makedirs(figures_dir, exist_ok=True)

    plot_scatter_density_vs_gain(
        all_densities, all_gains, condition_labels, pearson_r,
        os.path.join(figures_dir, "scatter_density_vs_gain.png")
    )
    plot_entropy_timeseries(
        data,
        os.path.join(figures_dir, "entropy_timeseries.png")
    )
    plot_entropy_density_comparison(
        data,
        os.path.join(figures_dir, "entropy_density_comparison.png")
    )
    plot_per_condition_scatter(
        data,
        os.path.join(figures_dir, "per_condition_scatter.png")
    )
    plot_pass1_gain_timeseries(
        data,
        os.path.join(figures_dir, "pass1_gain_timeseries.png")
    )
    print(f"All 5 figures saved to {figures_dir}")
