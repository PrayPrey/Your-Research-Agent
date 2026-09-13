"""Visualization: 4 figures for H-E1 analysis pipeline."""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
from sklearn.metrics import roc_curve, auc

from config import VIZ_CONFIG, GATE_THRESHOLDS


def _setup_style():
    """Apply visualization style."""
    sns.set_palette(VIZ_CONFIG["color_palette"])
    plt.rcParams.update({"figure.dpi": VIZ_CONFIG["dpi"]})


def _save_figure(fig, name: str, save_dir: str):
    """Save figure to save_dir in all configured formats."""
    os.makedirs(save_dir, exist_ok=True)
    for fmt in VIZ_CONFIG["save_formats"]:
        path = os.path.join(save_dir, f"{name}.{fmt}")
        fig.savefig(path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
        print(f"  -> Saved: {path}")
    plt.close(fig)


def plot_gate_metrics(results_all_pairs: list[dict], save_dir: str) -> None:
    """Figure 1: Bar chart β₁ value and AUROC vs thresholds per model pair."""
    _setup_style()
    fig, axes = plt.subplots(1, 2, figsize=VIZ_CONFIG["figsize"])

    pair_ids = [r["pair_id"] for r in results_all_pairs]
    beta1_vals = [r["beta1"] for r in results_all_pairs]
    auroc_vals = [r["auroc_mmlu"] for r in results_all_pairs]

    # Beta1 chart
    colors_b1 = ["green" if v < GATE_THRESHOLDS["beta1_max"] else "red" for v in beta1_vals]
    axes[0].bar(pair_ids, beta1_vals, color=colors_b1)
    axes[0].axhline(y=GATE_THRESHOLDS["beta1_max"], color="black", linestyle="--", label="Gate threshold (0)")
    axes[0].set_title("β₁ Coefficient (margin → flip)")
    axes[0].set_ylabel("β₁")
    axes[0].legend()

    # AUROC chart
    colors_auroc = ["green" if v >= GATE_THRESHOLDS["auroc_min"] else "red" for v in auroc_vals]
    axes[1].bar(pair_ids, auroc_vals, color=colors_auroc)
    axes[1].axhline(y=GATE_THRESHOLDS["auroc_min"], color="black", linestyle="--", label=f"Gate threshold ({GATE_THRESHOLDS['auroc_min']})")
    axes[1].set_ylim(0, 1.0)
    axes[1].set_title("AUROC (MMLU)")
    axes[1].set_ylabel("AUROC")
    axes[1].legend()

    fig.suptitle("H-E1 Gate Metrics: Confidence Margin Predicts Argmax Flip", fontsize=13)
    plt.tight_layout()
    _save_figure(fig, "fig1_gate_metrics", save_dir)


def plot_quintile_flip_rates(
    margin_z: np.ndarray,
    flip: np.ndarray,
    pair_id: str,
    save_dir: str,
) -> None:
    """Figure 2: 5-bin bar chart P(flip | margin quintile)."""
    _setup_style()
    fig, ax = plt.subplots(figsize=VIZ_CONFIG["figsize"])

    n_q = VIZ_CONFIG["n_quintiles"]
    quintile_bounds = np.percentile(margin_z, np.linspace(0, 100, n_q + 1))
    flip_rates = []
    labels = []

    for i in range(n_q):
        lo, hi = quintile_bounds[i], quintile_bounds[i + 1]
        mask = (margin_z >= lo) & (margin_z <= hi)
        rate = float(np.mean(flip[mask])) if mask.sum() > 0 else 0.0
        flip_rates.append(rate)
        labels.append(f"Q{i+1}")

    palette = sns.color_palette(VIZ_CONFIG["color_palette"], n_q)
    ax.bar(labels, flip_rates, color=palette)
    ax.set_xlabel("Confidence Margin Quintile (Q1=low → Q5=high)")
    ax.set_ylabel("P(argmax flip)")
    ax.set_title(f"Flip Rate by Margin Quintile — {pair_id}")
    ax.set_ylim(0, max(flip_rates) * 1.2 + 0.01)

    plt.tight_layout()
    _save_figure(fig, f"fig2_quintile_flip_{pair_id}", save_dir)


def plot_roc_curves(
    results_all_pairs: list[dict],
    cross_benchmark_results: dict,
    save_dir: str,
) -> None:
    """Figure 3: Per model pair + cross-benchmark ROC curves."""
    _setup_style()
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    palette = sns.color_palette(VIZ_CONFIG["color_palette"], len(results_all_pairs))

    # Left: MMLU ROC curves
    for i, r in enumerate(results_all_pairs):
        lr_model = r.get("lr_model")
        margin_z = r.get("margin_z")
        flip = r.get("flip")
        kl_div = r.get("kl_div")
        if lr_model is None or margin_z is None:
            continue
        X = np.column_stack([margin_z, kl_div])
        probs = lr_model.predict_proba(X)[:, 1]
        fpr, tpr, _ = roc_curve(flip, probs)
        roc_auc_val = auc(fpr, tpr)
        axes[0].plot(fpr, tpr, color=palette[i], label=f"{r['pair_id']} (AUC={roc_auc_val:.3f})")

    axes[0].plot([0, 1], [0, 1], "k--", alpha=0.5)
    axes[0].set_xlabel("FPR")
    axes[0].set_ylabel("TPR")
    axes[0].set_title("ROC Curves — MMLU (primary)")
    axes[0].legend(loc="lower right", fontsize=8)

    # Right: cross-benchmark AUROC comparison
    if cross_benchmark_results:
        ds_names = list(next(iter(cross_benchmark_results.values()), {}).keys())
        pair_ids = list(cross_benchmark_results.keys())
        x = np.arange(len(pair_ids))
        width = 0.35

        for j, ds_name in enumerate(ds_names[:2]):
            vals = [cross_benchmark_results[pid].get(ds_name, 0.5) for pid in pair_ids]
            axes[1].bar(x + j * width, vals, width, label=ds_name)

        axes[1].axhline(y=GATE_THRESHOLDS["auroc_min"], color="red", linestyle="--", label="Gate (0.75)")
        axes[1].set_xticks(x + width / 2)
        axes[1].set_xticklabels(pair_ids, rotation=15)
        axes[1].set_ylabel("AUROC")
        axes[1].set_ylim(0, 1)
        axes[1].set_title("Cross-Benchmark AUROC")
        axes[1].legend()

    fig.suptitle("H-E1 ROC Analysis", fontsize=13)
    plt.tight_layout()
    _save_figure(fig, "fig3_roc_curves", save_dir)


def plot_margin_distribution(
    margin_z: np.ndarray,
    flip: np.ndarray,
    pair_id: str,
    save_dir: str,
) -> None:
    """Figure 4: Box plots of margin distribution for flipped vs non-flipped."""
    _setup_style()
    fig, ax = plt.subplots(figsize=VIZ_CONFIG["figsize"])

    data_flip = margin_z[flip == 1]
    data_noflip = margin_z[flip == 0]

    ax.boxplot(
        [data_noflip, data_flip],
        labels=["No Flip (0)", "Flip (1)"],
        patch_artist=True,
        boxprops=dict(facecolor="lightblue", color="blue"),
    )
    ax.set_ylabel("z-scored Confidence Margin")
    ax.set_title(f"Margin Distribution by Flip Status — {pair_id}")
    ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)

    plt.tight_layout()
    _save_figure(fig, f"fig4_margin_dist_{pair_id}", save_dir)


def save_all_figures(
    results_all_pairs: list[dict],
    figures_dir: str,
) -> None:
    """Call all plot functions and save to figures_dir."""
    print(f"\nGenerating figures to: {figures_dir}")
    os.makedirs(figures_dir, exist_ok=True)

    # Figure 1: Gate metrics
    plot_gate_metrics(results_all_pairs, figures_dir)

    # Per-pair figures
    for r in results_all_pairs:
        margin_z = r.get("margin_z")
        flip = r.get("flip")
        if margin_z is None or flip is None:
            continue
        # Figure 2: Quintile flip rates
        plot_quintile_flip_rates(margin_z, flip, r["pair_id"], figures_dir)
        # Figure 4: Margin distribution
        plot_margin_distribution(margin_z, flip, r["pair_id"], figures_dir)

    # Figure 3: ROC curves (aggregated)
    cross_benchmark_results = {r["pair_id"]: r.get("cross_benchmark", {}) for r in results_all_pairs}
    plot_roc_curves(results_all_pairs, cross_benchmark_results, figures_dir)

    print(f"All figures saved to: {figures_dir}")
