import os
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict
from config import CONFIG

def plot_interaction(df: pd.DataFrame, simple_effects: Dict, out_path: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    model_order = ["7B", "34B", "gpt4"]
    formats = ["raw", "structured"]
    colors = {"raw": "#e74c3c", "structured": "#3498db"}

    fig, ax = plt.subplots(figsize=(8, 6))

    for fmt in formats:
        means = []
        cis = []
        for model in model_order:
            subset = df[(df["model"] == model) & (df["format"] == fmt)]
            p = subset["passed"].mean()
            n = len(subset)
            se = (p * (1 - p) / n) ** 0.5
            means.append(p * 100)
            cis.append(1.96 * se * 100)

        ax.errorbar(
            model_order, means, yerr=cis,
            label=fmt.capitalize(), color=colors[fmt],
            marker="o", markersize=8, linewidth=2, capsize=4
        )

    ax.set_xlabel("Model Scale", fontsize=12)
    ax.set_ylabel("Repair Success Rate (%)", fontsize=12)
    ax.set_title("Format × Model Scale Interaction (h-c1)", fontsize=14)
    ax.legend(title="Error Format")
    ax.grid(True, alpha=0.3)

    effect_text = "\n".join([
        f"{m}: Δ={simple_effects[m]['effect']*100:.1f}% (d={simple_effects[m]['d']:.2f})"
        for m in model_order
    ])
    ax.text(0.98, 0.02, effect_text, transform=ax.transAxes,
            fontsize=9, verticalalignment="bottom", horizontalalignment="right",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved interaction plot: {out_path}")
