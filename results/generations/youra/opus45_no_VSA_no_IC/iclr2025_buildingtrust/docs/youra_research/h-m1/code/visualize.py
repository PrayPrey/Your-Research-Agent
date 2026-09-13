"""H-M1 Visualization - Gate comparison and divergence plots."""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

def plot_gate_comparison(r_tqa_mmlu: float, r_mmlu_internal_mean: float, out_path: str, gate_pass: bool = False) -> None:
    """REQUIRED. Bar chart: 2 bars [r_tqa_mmlu, r_mmlu_internal_mean]."""
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

    labels = ["r(TQA, MMLU)", "r(MMLU internal)"]
    values = [r_tqa_mmlu, r_mmlu_internal_mean]
    colors = ["steelblue", "coral"]

    bars = ax.bar(labels, values, color=colors, edgecolor="black", linewidth=1.2)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center", va="bottom", fontsize=12, fontweight="bold")

    ax.set_ylabel("Spearman r", fontsize=12)
    ax.set_ylim(0, 1.0)

    status = "PASS" if gate_pass else "FAIL"
    ax.set_title(f"H-M1 Gate Comparison (Gate: {status})", fontsize=14, fontweight="bold")

    ax.axhline(y=r_mmlu_internal_mean, color="coral", linestyle="--", alpha=0.5, linewidth=1)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path)
    plt.close()
    print(f"Saved gate comparison figure: {out_path}")

def plot_scatter_divergent(scores_df: pd.DataFrame, divergent_df: pd.DataFrame, out_path: str) -> None:
    """Scatter mmlu (x) vs truthfulqa (y), divergent points highlighted red."""
    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)

    non_divergent = scores_df[~scores_df["model"].isin(divergent_df["model"])]
    ax.scatter(non_divergent["mmlu"], non_divergent["truthfulqa"],
               c="steelblue", alpha=0.6, s=50, label="Normal", edgecolors="white", linewidth=0.5)

    if len(divergent_df) > 0:
        ax.scatter(divergent_df["mmlu"], divergent_df["truthfulqa"],
                   c="red", alpha=0.8, s=80, label="Divergent", edgecolors="black", linewidth=1)

        for _, row in divergent_df.iterrows():
            ax.annotate(row["model"][:15], (row["mmlu"], row["truthfulqa"]),
                        fontsize=7, alpha=0.7, xytext=(5, 5), textcoords="offset points")

    ax.set_xlabel("MMLU Score", fontsize=12)
    ax.set_ylabel("TruthfulQA Score", fontsize=12)
    ax.set_title("TruthfulQA vs MMLU: Divergent Profile Models", fontsize=14, fontweight="bold")
    ax.legend(loc="lower right")

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path)
    plt.close()
    print(f"Saved scatter figure: {out_path}")

def plot_correlation_heatmap(scores_df: pd.DataFrame, out_path: str, max_subjects: int = 10) -> None:
    """Heatmap of corr matrix over [truthfulqa, mmlu, mmlu_subject_1..S]."""
    from scipy.stats import spearmanr

    cols = ["truthfulqa", "mmlu"]
    mmlu_subjects = [c for c in scores_df.columns if c.startswith("mmlu_")][:max_subjects]
    cols.extend(mmlu_subjects)

    corr_matrix = np.zeros((len(cols), len(cols)))
    for i, c1 in enumerate(cols):
        for j, c2 in enumerate(cols):
            r, _ = spearmanr(scores_df[c1], scores_df[c2])
            corr_matrix[i, j] = r

    fig, ax = plt.subplots(figsize=(12, 10), dpi=150)

    im = ax.imshow(corr_matrix, cmap="RdBu_r", vmin=-1, vmax=1)

    short_labels = [c.replace("mmlu_", "").replace("_", " ")[:12] for c in cols]
    ax.set_xticks(range(len(cols)))
    ax.set_yticks(range(len(cols)))
    ax.set_xticklabels(short_labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(short_labels, fontsize=8)

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Spearman r", fontsize=10)

    ax.set_title("Correlation Matrix: TruthfulQA, MMLU, and Subjects", fontsize=12, fontweight="bold")

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path)
    plt.close()
    print(f"Saved heatmap figure: {out_path}")
