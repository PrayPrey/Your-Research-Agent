import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import ExperimentConfig


def _t_star_from_analysis(analysis_result: dict) -> float:
    return analysis_result.get("t_star_mean", None) if analysis_result else None


def plot_delta_curve(
    results_df: pd.DataFrame,
    dataset: str,
    out_path: str,
    analysis_result: dict = None,
) -> None:
    epochs = sorted(results_df["epoch"].unique())
    delta_pivot = results_df.pivot_table(index="epoch", columns="seed", values="delta")
    delta_mean = delta_pivot.mean(axis=1).values
    delta_std = delta_pivot.std(axis=1).values

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(epochs, delta_mean, color="steelblue", label="mean delta(t)", linewidth=2)
    ax.fill_between(
        epochs,
        delta_mean - delta_std,
        delta_mean + delta_std,
        alpha=0.3,
        color="steelblue",
        label="±1 std",
    )
    ax.fill_between(
        epochs,
        np.maximum(delta_mean, 0),
        0,
        where=(delta_mean > 0),
        alpha=0.15,
        color="green",
        label="delta > 0 (positive gap)",
    )
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    if analysis_result and analysis_result.get("t_star_mean"):
        ax.axvline(
            analysis_result["t_star_mean"],
            color="red",
            linestyle="--",
            linewidth=1.5,
            label=f"t* ≈ {analysis_result['t_star_mean']:.0f}",
        )
    ax.set_xlabel("Training Epoch")
    ax.set_ylabel("delta(t) = spurious_acc - core_acc")
    ax.set_title(f"Temporal Feature Gap delta(t) — {dataset}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_seed_overlay(
    results_df: pd.DataFrame,
    dataset: str,
    out_path: str,
) -> None:
    seeds = sorted(results_df["seed"].unique())
    fig, ax = plt.subplots(figsize=(10, 5))
    cmap = plt.cm.get_cmap("tab10", len(seeds))
    for i, seed in enumerate(seeds):
        df_s = results_df[results_df["seed"] == seed].sort_values("epoch")
        ax.plot(df_s["epoch"], df_s["delta"], color=cmap(i), alpha=0.8,
                label=f"seed {seed}", linewidth=1.5)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Training Epoch")
    ax.set_ylabel("delta(t)")
    ax.set_title(f"Per-Seed delta(t) Overlay — {dataset}")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_probe_trajectories(
    results_df: pd.DataFrame,
    dataset: str,
    out_path: str,
) -> None:
    epochs = sorted(results_df["epoch"].unique())
    spur_pivot = results_df.pivot_table(index="epoch", columns="seed", values="spurious_acc")
    core_pivot = results_df.pivot_table(index="epoch", columns="seed", values="core_acc")
    spur_mean = spur_pivot.mean(axis=1).values
    core_mean = core_pivot.mean(axis=1).values

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(epochs, spur_mean, color="red", label="spurious_acc (mean)", linewidth=2)
    ax.plot(epochs, core_mean, color="blue", label="core_acc (mean)", linewidth=2)
    ax.fill_between(epochs, core_mean, spur_mean,
                    where=(np.array(spur_mean) > np.array(core_mean)),
                    alpha=0.15, color="orange", label="delta > 0 region")
    ax.set_xlabel("Training Epoch")
    ax.set_ylabel("Probe Accuracy")
    ax.set_title(f"Spurious vs Core Probe Trajectories — {dataset}")
    ax.legend()
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {out_path}")


def generate_all_figures(
    results_df: pd.DataFrame,
    cfg: ExperimentConfig,
    analysis_result: dict = None,
    figures_dir: str = None,
) -> None:
    if figures_dir is None:
        # Default: sibling to results_dir
        base = os.path.dirname(cfg.results_dir)
        figures_dir = os.path.join(base, "figures")
    os.makedirs(figures_dir, exist_ok=True)

    dataset = cfg.train.dataset

    plot_delta_curve(
        results_df, dataset,
        os.path.join(figures_dir, f"delta_curve_{dataset}.png"),
        analysis_result=analysis_result,
    )
    plot_seed_overlay(
        results_df, dataset,
        os.path.join(figures_dir, f"seed_overlay_{dataset}.png"),
    )
    plot_probe_trajectories(
        results_df, dataset,
        os.path.join(figures_dir, f"probe_trajectories_{dataset}.png"),
    )
    print(f"All figures saved to {figures_dir}")
