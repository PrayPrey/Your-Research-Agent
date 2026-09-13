import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from config import CONFIG

def plot_per_model_bar(correlations: dict[str, tuple[float, float]], mean_r: float, std_r: float, out_path: str) -> None:
    models = list(correlations.keys())
    rs = [correlations[m][0] for m in models]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(models, rs, color="steelblue", alpha=0.8)
    ax.axhline(mean_r, color="red", linestyle="--", label=f"mean={mean_r:.3f}")
    ax.fill_between([-0.5, len(models)-0.5], mean_r-std_r, mean_r+std_r, alpha=0.2, color="red")
    ax.axhline(CONFIG.mean_r_threshold, color="green", linestyle=":", label=f"threshold={CONFIG.mean_r_threshold}")
    ax.set_ylabel("Partial r (LOC-controlled)")
    ax.set_xlabel("Model")
    ax.set_title("SA-Correctness Correlation by Model")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_correlation_heatmap(df: pd.DataFrame, metrics: list[str], models: list[str], correlations_by_metric: dict, out_path: str) -> None:
    data = np.zeros((len(metrics), len(models)))
    for i, metric in enumerate(metrics):
        for j, model in enumerate(models):
            if model in correlations_by_metric.get(metric, {}):
                data[i, j] = correlations_by_metric[metric][model][0]
    fig, ax = plt.subplots(figsize=(8, 4))
    im = ax.imshow(data, cmap="RdYlGn", aspect="auto", vmin=-1, vmax=1)
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(models)
    ax.set_yticks(range(len(metrics)))
    ax.set_yticklabels(metrics)
    for i in range(len(metrics)):
        for j in range(len(models)):
            ax.text(j, i, f"{data[i,j]:.2f}", ha="center", va="center", fontsize=10)
    plt.colorbar(im, ax=ax, label="Partial r")
    ax.set_title("SA Metric vs Model Correlation Matrix")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def generate_all_figures(df: pd.DataFrame, correlations_pylint: dict, correlations_radon: dict) -> None:
    os.makedirs(CONFIG.figures_dir, exist_ok=True)
    models = list(correlations_pylint.keys())
    mean_r, std_r, _ = np.mean([r for r,p in correlations_pylint.values()]), np.std([r for r,p in correlations_pylint.values()]), 0
    plot_per_model_bar(correlations_pylint, mean_r, std_r, f"{CONFIG.figures_dir}/per_model_correlation.png")
    correlations_by_metric = {"pylint_score": correlations_pylint, "radon_cc": correlations_radon}
    plot_correlation_heatmap(df, ["pylint_score", "radon_cc"], models, correlations_by_metric, f"{CONFIG.figures_dir}/correlation_heatmap.png")
    print(f"Figures saved to {CONFIG.figures_dir}/")
