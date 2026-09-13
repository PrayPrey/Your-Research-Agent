"""Visualization for H-E1."""
import logging
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

logger = logging.getLogger(__name__)


def _ensure_dir(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def plot_delta_star_heatmap(
    X: np.ndarray,
    model_ids: list,
    category_labels: list,
    out_path: str = "h-e1/figures/delta_star_heatmap.png",
) -> None:
    _ensure_dir(out_path)
    fig, ax = plt.subplots(figsize=(max(8, len(category_labels) * 0.8), max(5, len(model_ids) * 0.5)))
    short_ids = [m.split("/")[-1] for m in model_ids]
    sns.heatmap(
        X,
        xticklabels=category_labels,
        yticklabels=short_ids,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn_r",
        vmin=0,
        vmax=1,
        ax=ax,
        cbar_kws={"label": "Δ* (robustness drop)"},
    )
    ax.set_title("Δ*-Vector Heatmap: Models × Attack Categories")
    ax.set_xlabel("Attack Category")
    ax.set_ylabel("Model")
    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    logger.info(f"Saved: {out_path}")


def plot_reliability_scatter(
    reliability_scores: dict,
    threshold: float = 0.7,
    out_path: str = "h-e1/figures/reliability_scatter.png",
) -> None:
    _ensure_dir(out_path)
    cats = list(reliability_scores.keys())
    scores = [reliability_scores[c] for c in cats]

    fig, ax = plt.subplots(figsize=(max(6, len(cats) * 0.6), 4))
    colors = ["green" if s >= threshold else "red" for s in scores]
    ax.bar(cats, scores, color=colors)
    ax.axhline(threshold, color="black", linestyle="--", label=f"threshold={threshold}")
    ax.set_ylim(0, 1)
    ax.set_xlabel("Attack Category")
    ax.set_ylabel("Split-half reliability (r)")
    ax.set_title("Split-half Reliability per Attack Category")
    ax.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    logger.info(f"Saved: {out_path}")


def plot_manova_eta(
    eta_per_category: dict,
    threshold: float = 0.15,
    out_path: str = "h-e1/figures/manova_eta.png",
) -> None:
    _ensure_dir(out_path)
    cats = list(eta_per_category.keys())
    etas = [eta_per_category[c] for c in cats]

    fig, ax = plt.subplots(figsize=(max(6, len(cats) * 0.6), 4))
    colors = ["steelblue" if e >= threshold else "salmon" for e in etas]
    ax.bar(cats, etas, color=colors)
    ax.axhline(threshold, color="black", linestyle="--", label=f"η²={threshold}")
    ax.set_xlabel("Attack Category")
    ax.set_ylabel("η² (effect size)")
    ax.set_title("Permutation MANOVA η² per Attack Category")
    ax.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    logger.info(f"Saved: {out_path}")


def plot_lomo_confusion(
    confusion_matrix: np.ndarray,
    class_names: list,
    out_path: str = "h-e1/figures/lomo_confusion.png",
) -> None:
    _ensure_dir(out_path)
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(
        confusion_matrix,
        xticklabels=class_names,
        yticklabels=class_names,
        annot=True,
        fmt="d",
        cmap="Blues",
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("LOMO Classifier Confusion Matrix")
    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    logger.info(f"Saved: {out_path}")


def plot_family_profiles(
    X: np.ndarray,
    family_labels: list,
    category_labels: list,
    out_path: str = "h-e1/figures/family_profiles.png",
) -> None:
    _ensure_dir(out_path)
    families = sorted(set(family_labels))
    family_arr = np.array(family_labels)

    fig, ax = plt.subplots(figsize=(max(6, len(category_labels) * 0.7), 4))
    colors = {"encoder": "royalblue", "decoder": "tomato", "enc_dec": "seagreen"}
    x = np.arange(len(category_labels))

    for fam in families:
        mask = family_arr == fam
        if not mask.any():
            continue
        mean_profile = X[mask].mean(axis=0)
        std_profile = X[mask].std(axis=0) if mask.sum() > 1 else np.zeros(len(category_labels))
        color = colors.get(fam, "gray")
        ax.plot(x, mean_profile, label=fam, color=color, marker="o")
        ax.fill_between(x, mean_profile - std_profile, mean_profile + std_profile,
                        alpha=0.2, color=color)

    ax.set_xticks(x)
    ax.set_xticklabels(category_labels, rotation=45, ha="right")
    ax.set_ylabel("Mean Δ*")
    ax.set_title("Δ*-Vector Profiles by Architecture Family")
    ax.legend()
    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    logger.info(f"Saved: {out_path}")


def generate_all_figures(
    X: np.ndarray,
    model_ids: list,
    family_labels: list,
    reliable_categories: list,
    stats_results: dict,
    figures_dir: str = "h-e1/figures",
) -> None:
    os.makedirs(figures_dir, exist_ok=True)

    plot_delta_star_heatmap(
        X, model_ids, reliable_categories,
        out_path=os.path.join(figures_dir, "delta_star_heatmap.png"),
    )

    plot_family_profiles(
        X, family_labels, reliable_categories,
        out_path=os.path.join(figures_dir, "family_profiles.png"),
    )

    # MANOVA eta plot
    manova = stats_results.get("permutation_manova", {})
    eta_list = manova.get("eta_per_category", [])
    if eta_list and len(eta_list) == len(reliable_categories):
        eta_dict = {cat: eta_list[j] for j, cat in enumerate(reliable_categories)}
        plot_manova_eta(eta_dict, out_path=os.path.join(figures_dir, "manova_eta.png"))

    # LOMO confusion matrix
    lomo = stats_results.get("lomo", {})
    cm = lomo.get("confusion_matrix", [])
    if cm:
        unique_fams = sorted(set(family_labels))
        plot_lomo_confusion(
            np.array(cm), unique_fams,
            out_path=os.path.join(figures_dir, "lomo_confusion.png"),
        )

    logger.info(f"All figures saved to {figures_dir}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    X = np.random.rand(9, 5)
    models = ["bert", "roberta", "electra", "albert", "gpt2", "opt125", "opt350", "t5", "bart"]
    families = ["encoder"] * 4 + ["decoder"] * 3 + ["enc_dec"] * 2
    cats = [f"C{i}" for i in range(1, 6)]
    plot_delta_star_heatmap(X, models, cats, "/tmp/test_heatmap.png")
    plot_family_profiles(X, families, cats, "/tmp/test_profiles.png")
    print("Figures generated to /tmp/")
