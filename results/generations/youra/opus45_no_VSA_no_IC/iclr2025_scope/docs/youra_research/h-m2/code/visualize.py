"""Visualization for h-m2 sensitivity analysis."""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config import MODELS, Paths


def plot_sensitivity_vs_scale(
    sensitivities_df: pd.DataFrame,
    fit_result: dict | None = None,
    output_png: str | None = None,
) -> None:
    """Plot sensitivity vs log10(N) with error bars."""
    paths = Paths()
    output_png = output_png or paths.sensitivity_plot_png
    os.makedirs(os.path.dirname(output_png) or ".", exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {"squad_v2": "steelblue", "hotpotqa": "darkorange"}
    markers = {"squad_v2": "o", "hotpotqa": "s"}

    for dataset in sensitivities_df["dataset"].unique():
        ds_df = sensitivities_df[sensitivities_df["dataset"] == dataset]
        agg = ds_df.groupby("model").agg({"sensitivity": ["mean", "std"]}).reset_index()
        agg.columns = ["model", "mean", "std"]
        agg["N"] = agg["model"].map(MODELS)
        agg["log_N"] = np.log10(agg["N"])

        ax.errorbar(
            agg["log_N"],
            agg["mean"],
            yerr=agg["std"],
            fmt=markers.get(dataset, "o"),
            color=colors.get(dataset, "gray"),
            capsize=5,
            capthick=2,
            markersize=10,
            label=dataset,
        )

        if fit_result and dataset in fit_result.get("power_law_fit", {}):
            fit = fit_result["power_law_fit"][dataset]
            x_line = np.linspace(agg["log_N"].min() - 0.1, agg["log_N"].max() + 0.1, 50)
            y_line = fit["a"] * (10 ** x_line) ** fit["gamma"]
            ax.plot(
                x_line,
                y_line,
                "--",
                color=colors.get(dataset, "gray"),
                alpha=0.7,
                label=f"{dataset} fit (γ={fit['gamma']:.2f})",
            )

    ax.set_xlabel("log₁₀(N) - Model Parameters", fontsize=12)
    ax.set_ylabel("Rank Sensitivity |∂F1/∂log(r)|", fontsize=12)
    ax.set_title("Rank Sensitivity vs Model Scale (h-m2)", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_png, dpi=150)
    plt.close()
    print(f"Sensitivity plot saved: {output_png}")


def plot_rank_curves(
    combined_df: pd.DataFrame,
    output_png: str | None = None,
) -> None:
    """Plot F1 vs rank overlay for all models."""
    paths = Paths()
    output_png = output_png or paths.rank_curves_png
    os.makedirs(os.path.dirname(output_png) or ".", exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    datasets = combined_df["dataset"].unique()
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(MODELS)))

    for idx, dataset in enumerate(datasets):
        ax = axes[idx] if len(datasets) > 1 else axes
        ds_df = combined_df[combined_df["dataset"] == dataset]

        for i, model in enumerate(sorted(MODELS.keys(), key=lambda m: MODELS[m])):
            model_df = ds_df[ds_df["model"] == model]
            agg = model_df.groupby("rank").agg({"f1_score": ["mean", "std"]}).reset_index()
            agg.columns = ["rank", "mean", "std"]

            ax.errorbar(
                np.log2(agg["rank"]),
                agg["mean"],
                yerr=agg["std"],
                fmt="o-",
                color=colors[i],
                capsize=3,
                markersize=6,
                label=model,
            )

        ax.set_xlabel("log₂(rank)", fontsize=11)
        ax.set_ylabel("F1 Score", fontsize=11)
        ax.set_title(f"F1 vs Rank: {dataset}", fontsize=12)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_png, dpi=150)
    plt.close()
    print(f"Rank curves plot saved: {output_png}")


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Generate h-m2 visualizations")
    parser.add_argument("--sensitivities-csv", default="results/h-m2_sensitivities.csv")
    parser.add_argument("--combined-csv", default="results/h-m2_combined.csv")
    parser.add_argument("--phase-transition-json", default="results/h-m2_phase_transition.json")
    parser.add_argument("--figures-dir", default="figures")
    args = parser.parse_args()

    os.makedirs(args.figures_dir, exist_ok=True)

    sens_df = pd.read_csv(args.sensitivities_csv)

    fit_result = None
    if os.path.exists(args.phase_transition_json):
        with open(args.phase_transition_json) as f:
            fit_result = json.load(f)

    plot_sensitivity_vs_scale(
        sens_df,
        fit_result,
        os.path.join(args.figures_dir, "h-m2_sensitivity_vs_scale.png"),
    )

    if os.path.exists(args.combined_csv):
        combined_df = pd.read_csv(args.combined_csv)
        plot_rank_curves(combined_df, os.path.join(args.figures_dir, "h-m2_rank_curves.png"))
