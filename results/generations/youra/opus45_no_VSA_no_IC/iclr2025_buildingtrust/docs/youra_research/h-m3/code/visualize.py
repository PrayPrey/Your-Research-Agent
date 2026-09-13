"""Visualization for H-M3."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd


def plot_gate_metrics(
    r_fs_tqa: float,
    r_fs_he: float,
    threshold: float,
    out_path: str,
) -> None:
    """Bar chart showing FactScore correlations vs threshold."""
    fig, ax = plt.subplots(figsize=(8, 5))

    metrics = ["r(FactScore, TruthfulQA)", "r(FactScore, HaluEval)"]
    values = [r_fs_tqa, r_fs_he]
    colors = ["#3498db", "#27ae60"]

    bars = ax.bar(metrics, values, color=colors, alpha=0.8, edgecolor="black")
    ax.axhline(y=threshold, color="red", linestyle="--", linewidth=2, label=f"Threshold = {threshold}")

    ax.set_ylabel("Spearman Correlation")
    ax.set_title("H-M3 Gate Metrics: FactScore Cross-Benchmark Correlations")
    ax.set_ylim(-0.2, 1)
    ax.legend()

    for bar, val in zip(bars, values):
        ax.annotate(f"{val:.3f}", xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha="center", va="bottom", fontsize=12, fontweight="bold")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_correlation_heatmap(
    df: pd.DataFrame,
    cols: list[str],
    out_path: str,
) -> None:
    """3x3 correlation heatmap."""
    corr = df[cols].corr(method="spearman")

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt=".3f", cmap="RdYlBu_r", center=0,
                vmin=-1, vmax=1, square=True, ax=ax)
    ax.set_title("FactScore/TruthfulQA/HaluEval Correlation Matrix")

    labels = [c.replace("_mc2", "").replace("_agg", "").replace("truthfulqa", "TruthfulQA")
              .replace("halueval", "HaluEval").replace("factscore", "FactScore") for c in cols]
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels, rotation=0)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_pca_biplot(
    df: pd.DataFrame,
    pca_result: dict,
    cols: list[str],
    out_path: str,
) -> None:
    """PCA biplot with benchmark loadings as vectors."""
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA

    X = StandardScaler().fit_transform(df[cols].dropna().values)
    pca = PCA(n_components=2)
    scores = pca.fit_transform(X)
    loadings = pca.components_.T

    fig, ax = plt.subplots(figsize=(8, 8))

    # Plot scores
    ax.scatter(scores[:, 0], scores[:, 1], alpha=0.6, s=50)

    # Plot loadings as vectors
    for i, col in enumerate(cols):
        ax.arrow(0, 0, loadings[i, 0] * 3, loadings[i, 1] * 3,
                 head_width=0.1, head_length=0.05, fc='red', ec='red')
        label = col.replace("_mc2", "").replace("_agg", "").replace("truthfulqa", "TQA")
        label = label.replace("halueval", "HE").replace("factscore", "FS")
        ax.annotate(label, (loadings[i, 0] * 3.3, loadings[i, 1] * 3.3), fontsize=12, color='red')

    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.axvline(x=0, color='k', linewidth=0.5)
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%})")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%})")
    ax.set_title("PCA Biplot: Benchmark Loadings")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_scatter_matrix(
    df: pd.DataFrame,
    cols: list[str],
    out_path: str,
) -> None:
    """Pairwise scatter matrix."""
    labels = {c: c.replace("_mc2", "").replace("_agg", "").replace("truthfulqa", "TruthfulQA")
              .replace("halueval", "HaluEval").replace("factscore", "FactScore") for c in cols}
    df_plot = df[cols].rename(columns=labels)

    fig = sns.pairplot(df_plot, diag_kind="kde", plot_kws={"alpha": 0.6})
    fig.fig.suptitle("Benchmark Score Distributions", y=1.02)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_cumulative_variance(
    pca_result: dict,
    out_path: str,
) -> None:
    """Cumulative explained variance plot."""
    cum_var = pca_result["cumulative_variance"]
    n_comp = len(cum_var)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(range(1, n_comp + 1), pca_result["explained_variance"], alpha=0.7, label="Individual")
    ax.step(range(1, n_comp + 1), cum_var, where="mid", color="red", linewidth=2, label="Cumulative")
    ax.axhline(y=0.8, color="green", linestyle="--", label="80% threshold")

    ax.set_xlabel("Principal Component")
    ax.set_ylabel("Explained Variance Ratio")
    ax.set_title("PCA: Variance Explained by Component")
    ax.set_xticks(range(1, n_comp + 1))
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
