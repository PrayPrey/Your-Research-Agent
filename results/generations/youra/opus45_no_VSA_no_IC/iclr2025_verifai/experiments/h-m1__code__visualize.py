import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from config import CONFIG
import os

def plot_bar_chart(results: dict, threshold: float, out_path: str) -> None:
    metrics = list(results.keys())
    r_values = [abs(results[m]["r_partial"]) for m in metrics]
    plt.figure(figsize=(8, 5))
    plt.bar(metrics, r_values, color="steelblue")
    plt.axhline(y=threshold, color="red", linestyle="--", label=f"threshold={threshold}")
    plt.ylabel("|r_partial|")
    plt.title("SA Metrics Partial Correlation with Pass@1")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def plot_scatter(df: pd.DataFrame, metric: str, out_path: str) -> None:
    plt.figure(figsize=(8, 5))
    jitter = np.random.normal(0, 0.05, len(df))
    plt.scatter(df[metric], df["passed"] + jitter, alpha=0.5)
    plt.xlabel(metric)
    plt.ylabel("passed (jittered)")
    plt.title(f"{metric} vs Pass@1")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def plot_heatmap(df: pd.DataFrame, out_path: str) -> None:
    cols = ["pylint_score", "mypy_errors", "radon_cc", "loc", "passed"]
    corr = df[cols].corr()
    plt.figure(figsize=(8, 6))
    plt.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    plt.colorbar()
    plt.xticks(range(len(cols)), cols, rotation=45)
    plt.yticks(range(len(cols)), cols)
    for i in range(len(cols)):
        for j in range(len(cols)):
            plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center")
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def generate_all_figures(df: pd.DataFrame, results: dict) -> None:
    os.makedirs(CONFIG.figures_dir, exist_ok=True)
    plot_bar_chart(results, CONFIG.corr_threshold, f"{CONFIG.figures_dir}/bar_chart.png")
    for m in ["pylint_score", "mypy_errors", "radon_cc"]:
        plot_scatter(df, m, f"{CONFIG.figures_dir}/scatter_{m}.png")
    plot_heatmap(df, f"{CONFIG.figures_dir}/heatmap.png")
