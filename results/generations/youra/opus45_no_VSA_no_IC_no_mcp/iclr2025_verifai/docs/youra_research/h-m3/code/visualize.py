import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict
from config import CONFIG

def _ensure_dir():
    os.makedirs(CONFIG["figures_dir_hm3"], exist_ok=True)

def plot_gate_metrics(df: pd.DataFrame) -> str:
    _ensure_dir()
    means = df.groupby("level")["success"].mean()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(means.index, means.values, color=["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4"])
    ax.set_xlabel("Fix Specificity Level")
    ax.set_ylabel("Success Rate")
    ax.set_title("Success Rate by Fix Level (Gate Metrics)")
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(["L0: None", "L1: Strategy", "L2: Pattern", "L3: Exact"])

    path = os.path.join(CONFIG["figures_dir_hm3"], "gate_metrics.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path

def plot_inverted_u_curve(df: pd.DataFrame, fit_result: Dict) -> str:
    _ensure_dir()
    means = df.groupby("level")["success"].mean()
    sems = df.groupby("level")["success"].sem()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(means.index, means.values, yerr=sems.values, fmt='o', markersize=10,
                capsize=5, color='#2c3e50', label='Observed')

    x_fit = np.linspace(0, 3, 100)
    y_fit = (fit_result["quad_coef"] * x_fit**2 +
             (means[1] - means[0] - fit_result["quad_coef"]) * x_fit + means[0])
    ax.plot(x_fit, y_fit, '--', color='#e74c3c', label='Quadratic Fit')

    ax.set_xlabel("Fix Specificity Level")
    ax.set_ylabel("Success Rate")
    ax.set_title(f"Inverted-U Pattern (quad_coef={fit_result['quad_coef']:.4f}, p={fit_result['quad_pval']:.4f})")
    ax.legend()
    ax.set_xticks([0, 1, 2, 3])

    path = os.path.join(CONFIG["figures_dir_hm3"], "inverted_u_curve.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path

def plot_model_heatmap(df: pd.DataFrame) -> str:
    _ensure_dir()
    pivot = df.pivot_table(values="success", index="model", columns="level", aggfunc="mean")

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="RdYlGn", ax=ax, vmin=0, vmax=1)
    ax.set_title("Success Rate by Model and Level")
    ax.set_xlabel("Fix Specificity Level")
    ax.set_ylabel("Model")

    path = os.path.join(CONFIG["figures_dir_hm3"], "model_heatmap.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path

def plot_error_type_breakdown(df: pd.DataFrame) -> str:
    _ensure_dir()
    pivot = df.pivot_table(values="success", index="error_type", columns="level", aggfunc="mean")

    fig, ax = plt.subplots(figsize=(10, 6))
    pivot.plot(kind="bar", ax=ax)
    ax.set_xlabel("Error Type")
    ax.set_ylabel("Success Rate")
    ax.set_title("Success Rate by Error Type and Level")
    ax.legend(title="Level", labels=["L0", "L1", "L2", "L3"])
    plt.xticks(rotation=45, ha='right')

    path = os.path.join(CONFIG["figures_dir_hm3"], "error_type_breakdown.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path

def plot_iterations_per_level(df: pd.DataFrame) -> str:
    _ensure_dir()
    passed_df = df[df["passed"] == True]

    fig, ax = plt.subplots(figsize=(8, 5))
    if len(passed_df) > 0:
        sns.boxplot(data=passed_df, x="level", y="attempts_used", ax=ax)
    ax.set_xlabel("Fix Specificity Level")
    ax.set_ylabel("Attempts Used (Passed Only)")
    ax.set_title("Repair Efficiency by Level")

    path = os.path.join(CONFIG["figures_dir_hm3"], "iterations_per_level.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path

def demo():
    import numpy as np
    np.random.seed(42)
    records = []
    for i in range(50):
        for level in [0, 1, 2, 3]:
            records.append({
                "error_id": f"e_{i}", "model": "m1", "benchmark": "b",
                "level": level, "rep": 0, "passed": np.random.random() < 0.5,
                "attempts_used": np.random.randint(1, 4), "error_type": "IndexError",
                "first_iter_success": False, "success": 1
            })
    df = pd.DataFrame(records)
    df["success"] = df["passed"].astype(int)

    fit_result = {"quad_coef": -0.05, "quad_pval": 0.01, "peak_level": 2}

    paths = [
        plot_gate_metrics(df),
        plot_inverted_u_curve(df, fit_result),
        plot_model_heatmap(df),
        plot_error_type_breakdown(df),
        plot_iterations_per_level(df)
    ]

    for p in paths:
        assert os.path.exists(p), f"File not found: {p}"
    print(f"visualize.py demo PASS (created {len(paths)} figures)")

if __name__ == "__main__":
    demo()
