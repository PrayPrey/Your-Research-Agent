"""
visualize.py — H-E1: 5 required figures for validation report.
"""
import os
from typing import Any

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ModelResult = Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
FIGURES_DIR: str = "h-e1/figures"
SENSITIVITY_THRESHOLDS: list[float] = [0.75, 0.80, 0.85, 0.90]


def _ensure_figures_dir() -> None:
    os.makedirs(FIGURES_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Fig 1: OR Comparison Bar Chart
# ---------------------------------------------------------------------------

def plot_or_comparison(metrics: dict) -> None:
    """Fig 1: Bar chart OR (proposed) vs null OR=1.0 with 95% CI error bars."""
    _ensure_figures_dir()
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["Null (OR=1.0)", "Proposed Model"]
    ors = [1.0, metrics["OR"]]
    colors = ["#aaaaaa", "#2196F3"]
    bars = ax.bar(labels, ors, color=colors, width=0.4)
    # Error bars only for proposed model
    err_lo = metrics["OR"] - metrics["CI_lo"]
    err_hi = metrics["CI_hi"] - metrics["OR"]
    ax.errorbar(
        1, metrics["OR"],
        yerr=[[err_lo], [err_hi]],
        fmt="none", color="black", capsize=5, linewidth=2,
    )
    ax.axhline(1.0, color="red", linestyle="--", linewidth=1, label="OR=1.0 (null)")
    ax.set_ylabel("Odds Ratio (OR)")
    ax.set_title("Fig 1: OR Comparison — Proposed vs Null")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig1_or_comparison.png"), dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Fig 2: Forest Plot
# ---------------------------------------------------------------------------

def plot_forest(results: dict[str, Any]) -> None:
    """Fig 2: Forest plot of β₄ across model specs with 95% CI."""
    _ensure_figures_dir()
    model_names = list(results.keys())
    betas = []
    ci_los = []
    ci_his = []
    for name, res in results.items():
        try:
            b = float(res.params[2])  # type: ignore[arg-type]
            conf = np.array(res.conf_int())
            lo = float(conf[2, 0])
            hi = float(conf[2, 1])
        except Exception:
            b, lo, hi = 0.0, 0.0, 0.0
        betas.append(b)
        ci_los.append(b - lo)
        ci_his.append(hi - b)

    fig, ax = plt.subplots(figsize=(7, 4))
    y_pos = range(len(model_names))
    ax.errorbar(
        betas, list(y_pos),
        xerr=[ci_los, ci_his],
        fmt="o", color="#2196F3", capsize=5, linewidth=1.5,
    )
    ax.axvline(0.0, color="red", linestyle="--", linewidth=1, label="β₄=0 (null)")
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(model_names)
    ax.set_xlabel("β₄ coefficient (log-OR scale)")
    ax.set_title("Fig 2: Forest Plot — β₄ Across Model Specifications")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig2_forest_plot.png"), dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Fig 3: AIFS Distribution Violin
# ---------------------------------------------------------------------------

def plot_aifs_distribution(df_pairs: pd.DataFrame) -> None:
    """Fig 3: Violin plot of delta_aifs by split."""
    _ensure_figures_dir()
    fig, ax = plt.subplots(figsize=(6, 4))
    split_labels = {0: "Base (naive)", 1: "Online (deployed)"}
    data_by_split = [
        df_pairs.loc[df_pairs["split"] == s, "delta_aifs"].values
        for s in [0, 1]
    ]
    parts = ax.violinplot(data_by_split, positions=[0, 1], showmedians=True)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([split_labels[0], split_labels[1]])
    ax.set_ylabel("Δ AIFS Score (chosen − rejected)")
    ax.set_title("Fig 3: AIFS Score Distribution by Annotator Condition")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig3_aifs_distribution.png"), dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Fig 4: Cluster Size Histogram
# ---------------------------------------------------------------------------

def plot_cluster_histogram(df_pairs: pd.DataFrame) -> None:
    """Fig 4: Histogram of semantic cluster sizes (pairs per cluster_id)."""
    _ensure_figures_dir()
    cluster_sizes = df_pairs.groupby("cluster_id").size().tolist()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(cluster_sizes, bins=50, color="#4CAF50", edgecolor="white")
    ax.set_xlabel("Pairs per Cluster")
    ax.set_ylabel("Number of Clusters")
    ax.set_title("Fig 4: Semantic Cluster Size Distribution")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig4_cluster_histogram.png"), dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Fig 5: OR Sensitivity Across Cosine Thresholds
# ---------------------------------------------------------------------------

def plot_or_sensitivity(
    df_base: pd.DataFrame,
    df_online: pd.DataFrame,
    thresholds: list[float] = SENSITIVITY_THRESHOLDS,
) -> None:
    """Fig 5: OR estimates across cosine thresholds [0.75, 0.80, 0.85, 0.90]."""
    from data_prep import cluster_prompts, build_pairs_df, validate_clusters
    from experiment import fit_proposed_model

    _ensure_figures_dir()
    ors = []
    ci_los = []
    ci_his = []

    base_prompts = df_base["prompt"].tolist() if "prompt" in df_base.columns else df_base["chosen"].tolist()
    online_prompts = df_online["prompt"].tolist() if "prompt" in df_online.columns else df_online["chosen"].tolist()
    all_prompts = base_prompts + online_prompts

    for thresh in thresholds:
        try:
            cids = cluster_prompts(all_prompts, threshold=thresh)
            df_p = build_pairs_df(df_base, df_online, cids)
            validate_clusters(df_p)
            res = fit_proposed_model(df_p)
            b = float(res.params[2])  # type: ignore[arg-type]
            conf = np.array(res.conf_int())
            lo = float(np.exp(conf[2, 0]))
            hi = float(np.exp(conf[2, 1]))
            ors.append(float(np.exp(b)))
            ci_los.append(float(np.exp(b)) - lo)
            ci_his.append(hi - float(np.exp(b)))
        except Exception as e:
            ors.append(float("nan"))
            ci_los.append(0.0)
            ci_his.append(0.0)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.errorbar(
        thresholds, ors,
        yerr=[ci_los, ci_his],
        fmt="o-", color="#2196F3", capsize=5, linewidth=1.5,
    )
    ax.axhline(1.0, color="red", linestyle="--", linewidth=1, label="OR=1.0 (null)")
    ax.axhline(1.10, color="orange", linestyle=":", linewidth=1, label="OR=1.10 (gate)")
    ax.set_xlabel("Cosine Similarity Threshold")
    ax.set_ylabel("Odds Ratio (OR)")
    ax.set_title("Fig 5: OR Sensitivity Across Clustering Thresholds")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig5_or_sensitivity.png"), dpi=150)
    plt.close(fig)
