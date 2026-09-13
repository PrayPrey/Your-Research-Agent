from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_curve
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def _save(fig: plt.Figure, figures_dir: Path, name_key: str) -> None:
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)
    path = figures_dir / config.FIGURE_NAMES[name_key]
    fig.savefig(path, dpi=config.FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)


def plot_auc_comparison_bar(
    delta_result: dict,
    auc_threshold: float,
    figures_dir: Path,
) -> None:
    """fig1: LOO-AUC composite vs MMLU-only with CI error bars."""
    auc_c = delta_result["auc_composite"]
    auc_b = delta_result["auc_baseline"]
    ci_lo, ci_hi = delta_result["delta_auc_ci"]
    delta = delta_result["delta_auc"]

    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(
        ["Composite\n(ECE+TruthfulQA+Brier)", "Baseline\n(MMLU only)"],
        [auc_c, auc_b],
        color=["steelblue", "salmon"],
        alpha=config.BAR_ALPHA,
        capsize=config.BAR_CAPSIZE,
    )
    # CI error bar on delta shown via text annotation
    ax.axhline(auc_threshold, color="red", linestyle="--", label=f"AUC threshold ({auc_threshold})")
    ax.set_ylabel("LOO-AUC")
    ax.set_title(f"LOO-AUC Comparison\nΔAUC={delta:.3f} (95% CI [{ci_lo:.3f}, {ci_hi:.3f}])")
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.annotate(
        f"ΔR²={delta:.3f}",
        xy=(0.5, max(auc_c, auc_b) + 0.03),
        xycoords=("axes fraction", "data"),
        ha="center", fontsize=10, color="darkgreen",
    )
    _save(fig, figures_dir, "gate_metrics_comparison")


def plot_partial_rho_comparison(
    partial_result: dict,
    hm1_partial_rho: float,
    figures_dir: Path,
) -> None:
    """fig3: partial rho(ECE, AdvGLUE|MMLU) and ANLI vs H-M1 reference."""
    labels = ["ρ(ECE,AdvGLUE|MMLU)", "ρ(ECE,ANLI|MMLU)", "H-M1 ref\nρ(ECE,TruthfulQA|MMLU)"]
    rhos = [
        partial_result["rho_partial_advglue"],
        partial_result["rho_partial_anli"],
        hm1_partial_rho,
    ]
    ci_lows = [
        abs(partial_result["rho_partial_advglue"] - partial_result["bca_ci_low"]),
        abs(partial_result["rho_partial_anli"] - partial_result["anli_bca_ci_low"]),
        0,
    ]
    ci_highs = [
        abs(partial_result["bca_ci_high"] - partial_result["rho_partial_advglue"]),
        abs(partial_result["anli_bca_ci_high"] - partial_result["rho_partial_anli"]),
        0,
    ]

    fig, ax = plt.subplots(figsize=(7, 5))
    colors = ["steelblue", "darkorange", "gray"]
    for i, (label, rho, cl, ch, col) in enumerate(
        zip(labels, rhos, ci_lows, ci_highs, colors)
    ):
        ax.barh(
            i, rho,
            xerr=[[cl], [ch]],
            capsize=4, color=col, alpha=0.8,
        )
    ax.axvline(0, color="black", linewidth=0.8)
    ax.axvline(config.PARTIAL_RHO_THRESHOLD, color="red", linestyle="--",
               label=f"Threshold |ρ|≥{config.PARTIAL_RHO_THRESHOLD}")
    ax.axvline(-config.PARTIAL_RHO_THRESHOLD, color="red", linestyle="--")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_xlabel("Partial Spearman ρ")
    ax.set_title("Partial Correlation Comparison (BCa 95% CI)")
    ax.legend()
    _save(fig, figures_dir, "partial_correlation_comparison")


def plot_roc_curves(
    composite_auc: dict,
    baseline_auc: dict,
    figures_dir: Path,
) -> None:
    """fig2: ROC curve overlay for composite vs MMLU-only."""
    fig, ax = plt.subplots(figsize=(6, 6))
    for result, label, color in [
        (composite_auc, "Composite", "steelblue"),
        (baseline_auc, "MMLU-only", "salmon"),
    ]:
        fpr, tpr, _ = roc_curve(result["y_true"], result["y_proba"])
        ax.plot(
            fpr, tpr,
            color=color, linewidth=config.ROC_LINEWIDTH,
            label=f"{label} (AUC={result['auc']:.3f})",
        )
    ax.plot([0, 1], [0, 1], config.ROC_DIAGONAL_STYLE, color="gray", linewidth=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves: Composite vs MMLU-only")
    ax.legend(loc="lower right")
    _save(fig, figures_dir, "roc_curves_comparison")


def plot_advglue_distribution(
    df: pd.DataFrame,
    q75_threshold: float,
    figures_dir: Path,
) -> None:
    """fig4: histogram of AdvGLUE_drop with top-quartile threshold line."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(df["AdvGLUE_drop"], bins=15, color="steelblue", alpha=0.7, edgecolor="white")
    ax.axvline(
        q75_threshold, color="red", linestyle="--",
        label=f"75th pct (top-quartile threshold={q75_threshold:.3f})"
    )
    ax.set_xlabel("AdvGLUE Drop")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of AdvGLUE Drop (N=30)")
    ax.legend()
    _save(fig, figures_dir, "advglue_drop_distribution")


def plot_feature_importance(
    df: pd.DataFrame,
    composite_cols: list[str],
    target_col: str,
    seed: int,
    figures_dir: Path,
) -> None:
    """fig5: standardized LOO logistic regression coefficients with variability."""
    loo = LeaveOneOut()
    X = df[composite_cols].values
    y = df[target_col].values.astype(int)
    coefs: list[np.ndarray] = []
    for train_idx, _ in loo.split(X):
        scaler = StandardScaler().fit(X[train_idx])
        X_tr_s = scaler.transform(X[train_idx])
        clf = LogisticRegression(
            C=config.LR_C, max_iter=config.LR_MAX_ITER, random_state=seed
        )
        clf.fit(X_tr_s, y[train_idx])
        coefs.append(clf.coef_[0])

    coef_arr = np.array(coefs)  # (N, F)
    means = coef_arr.mean(axis=0)
    stds = coef_arr.std(axis=0)

    fig, ax = plt.subplots(figsize=(6, 4))
    x_pos = np.arange(len(composite_cols))
    ax.bar(x_pos, means, yerr=stds, capsize=5, color="steelblue", alpha=0.8)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(composite_cols, rotation=15)
    ax.set_ylabel("Standardized Coefficient (mean ± std across LOO folds)")
    ax.set_title("LOO Logistic Regression Feature Importance")
    _save(fig, figures_dir, "feature_importance")


def plot_composite_scatter(
    df: pd.DataFrame,
    figures_dir: Path,
) -> None:
    """fig6: composite epistemic score (PC1 proxy) vs AdvGLUE_drop scatter."""
    X = df[config.COMPOSITE_COLS].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    pca = PCA(n_components=1)
    pc1 = pca.fit_transform(X_scaled)[:, 0]

    fig, ax = plt.subplots(figsize=(6, 5))
    families = df["family"].unique() if "family" in df.columns else ["unknown"]
    cmap = plt.cm.get_cmap("tab10", len(families))
    family_col = df["family"] if "family" in df.columns else pd.Series(["unknown"] * len(df))
    for i, fam in enumerate(families):
        mask = family_col == fam
        ax.scatter(
            pc1[mask], df["AdvGLUE_drop"].values[mask],
            color=cmap(i), label=fam,
            alpha=config.SCATTER_ALPHA, s=config.SCATTER_SIZE,
        )
    ax.set_xlabel("Epistemic Composite Score (PC1 of ECE+TruthfulQA+Brier)")
    ax.set_ylabel("AdvGLUE Drop")
    ax.set_title("Epistemic Composite vs Adversarial Robustness")
    ax.legend(fontsize=7, loc="best")
    _save(fig, figures_dir, "epistemic_vs_adversarial_scatter")
