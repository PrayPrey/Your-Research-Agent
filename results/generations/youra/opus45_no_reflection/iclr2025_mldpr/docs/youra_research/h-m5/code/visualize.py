"""H-M5 Visualization: 4 required figures"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config import CONFIG


def plot_gate_metrics(result: dict, out_path: str) -> None:
    """Bar chart r_pre vs r_post with threshold lines."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))

    labels = ["Pre-2020\n(CV-NLP)", "Post-2021\n(CV-NLP)"]
    values = [result["r_pre"], result["r_post"]]
    colors = ["#2ecc71" if result["r_pre"] > 0.6 else "#e74c3c",
              "#2ecc71" if result["r_post"] < 0.4 else "#e74c3c"]

    bars = ax.bar(labels, values, color=colors, width=0.6, edgecolor="black")

    ax.axhline(y=0.6, color="green", linestyle="--", linewidth=2, label="r_pre threshold (0.6)")
    ax.axhline(y=0.4, color="red", linestyle="--", linewidth=2, label="r_post threshold (0.4)")

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center", va="bottom", fontsize=12, fontweight="bold")

    status = "PASS" if result["gate_pass"] else "FAIL"
    status_color = "green" if result["gate_pass"] else "red"
    ax.set_title(f"H-M5 Gate Metrics: {status}\n(Fisher z-test p = {result['p_value']:.4f})",
                 fontsize=14, fontweight="bold", color=status_color)

    ax.set_ylabel("Pearson Correlation (r)", fontsize=12)
    ax.set_ylim(-0.2, 1.0)
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_rolling_correlation(rolling: pd.Series, out_path: str) -> None:
    """Line plot of rolling CV-NLP correlation."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(rolling.index, rolling.values, color="#3498db", linewidth=2, label="6-month rolling r (CV-NLP)")

    ax.axvline(x=pd.Timestamp("2020-01-01"), color="orange", linestyle="--", linewidth=2, label="2020-01")
    ax.axvline(x=pd.Timestamp("2021-01-01"), color="red", linestyle="--", linewidth=2, label="2021-01")

    ax.axhline(y=0.6, color="green", linestyle=":", alpha=0.7, label="r=0.6 threshold")
    ax.axhline(y=0.4, color="red", linestyle=":", alpha=0.7, label="r=0.4 threshold")

    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Rolling Correlation", fontsize=12)
    ax.set_title("H-M5: Rolling 6-Month CV-NLP Gini Correlation", fontsize=14, fontweight="bold")
    ax.legend(loc="lower left")
    ax.grid(alpha=0.3)
    ax.set_ylim(-1, 1)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_gini_trajectories(gini_df: pd.DataFrame, out_path: str) -> None:
    """Multi-line plot showing monthly Gini for each modality."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6))

    colors = {"CV": "#e74c3c", "NLP": "#3498db", "Audio": "#2ecc71", "Tabular": "#9b59b6"}

    for col in gini_df.columns:
        ax.plot(gini_df.index, gini_df[col], color=colors.get(col, "gray"),
                linewidth=2, label=col, alpha=0.8)

    ax.axvline(x=pd.Timestamp("2020-01-01"), color="gray", linestyle="--", linewidth=1.5, alpha=0.7)
    ax.axvline(x=pd.Timestamp("2021-01-01"), color="gray", linestyle="--", linewidth=1.5, alpha=0.7)

    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Gini Coefficient", fontsize=12)
    ax.set_title("H-M5: Monthly Gini Coefficient by Modality", fontsize=14, fontweight="bold")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_correlation_heatmap(pre_matrix: pd.DataFrame, post_matrix: pd.DataFrame, out_path: str) -> None:
    """Two-panel heatmap (pre vs post) for all modality pairs."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax, matrix, title in zip(axes, [pre_matrix, post_matrix], ["Pre-2020", "Post-2021"]):
        im = ax.imshow(matrix.values, cmap="RdYlGn", vmin=-1, vmax=1)

        ax.set_xticks(range(len(matrix.columns)))
        ax.set_yticks(range(len(matrix.index)))
        ax.set_xticklabels(matrix.columns, fontsize=10)
        ax.set_yticklabels(matrix.index, fontsize=10)

        for i in range(len(matrix.index)):
            for j in range(len(matrix.columns)):
                val = matrix.iloc[i, j]
                if not np.isnan(val):
                    ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                            color="black" if abs(val) < 0.5 else "white", fontsize=10)

        ax.set_title(f"{title} Correlation Matrix", fontsize=12, fontweight="bold")

    fig.colorbar(im, ax=axes, orientation="vertical", fraction=0.02, pad=0.04, label="Pearson r")
    fig.suptitle("H-M5: Modality-Pair Correlations", fontsize=14, fontweight="bold", y=1.02)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")
