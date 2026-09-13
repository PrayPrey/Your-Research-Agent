"""Visualization: stratified scatter plots and effect size comparison."""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config import FIGURES_DIR


def plot_stratified_scatter(df: pd.DataFrame, results: dict, out_path: str = None):
    """Two-panel scatter plot: base vs instruction-tuned."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "stratified_scatter.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax, model_type in zip(axes, ["base", "instruction-tuned"]):
        subset = df[df["model_type"] == model_type]
        r_info = results.get(model_type, {})

        ax.scatter(
            subset["truthfulqa_mc1"],
            subset["advglue_avg"],
            c="steelblue" if model_type == "base" else "darkorange",
            s=60,
            alpha=0.7,
            edgecolors="white",
            linewidth=0.5,
        )

        # Fit line
        if len(subset) >= 2:
            x = subset["truthfulqa_mc1"].values
            y = subset["advglue_avg"].values
            coef = np.polyfit(x, y, 1)
            x_line = np.linspace(x.min(), x.max(), 50)
            y_line = np.polyval(coef, x_line)
            ax.plot(x_line, y_line, "--", color="gray", alpha=0.8)

        r_val = r_info.get("r", np.nan)
        p_val = r_info.get("p", np.nan)
        n_val = r_info.get("n", 0)

        title = f"{model_type.replace('-', ' ').title()} (n={n_val})"
        if not np.isnan(r_val):
            title += f"\nr={r_val:.3f}, p={p_val:.4f}"
        ax.set_title(title)
        ax.set_xlabel("TruthfulQA MC1")
        ax.set_ylabel("AdvGLUE Average")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_effect_comparison(results: dict, out_path: str = None):
    """Bar chart comparing r values between groups."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "effect_comparison.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    groups = ["base", "instruction-tuned"]
    rs = [results[g].get("r", 0) or 0 for g in groups]
    ci_lows = [results[g].get("ci_lower") for g in groups]
    ci_highs = [results[g].get("ci_upper") for g in groups]

    fig, ax = plt.subplots(figsize=(6, 5))
    x = np.arange(len(groups))
    colors = ["steelblue", "darkorange"]

    ax.bar(x, rs, color=colors, alpha=0.8, edgecolor="black", linewidth=0.5)

    # Only add error bars if CI is valid
    for i, r in enumerate(rs):
        if ci_lows[i] is not None and ci_highs[i] is not None:
            if not (np.isnan(ci_lows[i]) or np.isnan(ci_highs[i])):
                err_low = max(0, r - ci_lows[i])
                err_high = max(0, ci_highs[i] - r)
                ax.errorbar(x[i], r, yerr=[[err_low], [err_high]], fmt="none", color="black", capsize=5)

    ax.axhline(0.2, color="red", linestyle="--", linewidth=1, label="Threshold (r=0.2)")
    ax.axhline(0, color="gray", linestyle="-", linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels([g.replace("-", " ").title() for g in groups])
    ax.set_ylabel("Partial Correlation (r)")
    ax.set_title("Effect Size by Model Type")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    from data_loader import merge_all_scores
    from stratified_analysis import stratified_analysis

    df = merge_all_scores()
    results = stratified_analysis(df)
    plot_stratified_scatter(df, results)
    plot_effect_comparison(results)
