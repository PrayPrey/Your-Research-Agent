import logging
import os
from typing import Any, Dict, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import roc_curve

logger = logging.getLogger(__name__)

METHOD_LABELS = {
    "token_prob": "Token-Prob",
    "semantic_entropy": "SE",
    "kle": "KLE",
    "selfcheck_bertscore": "SC-BERT",
    "selfcheck_nli": "SC-NLI",
    "seps": "SEPs",
}
MODEL_LABELS = {"small": "8B", "large": "70B"}
DATASET_LABELS = {"trivia_qa": "TriviaQA", "natural_questions": "NQ"}


def plot_auroc_bar(auroc_results: Dict[str, Any], out_path: str) -> None:
    """FR8.1: Bar chart AUROC per method x scale x dataset with CI error bars."""
    methods = list(METHOD_LABELS.keys())
    model_keys = [k for k in ["small", "large"] if k in auroc_results]
    dataset_keys = list({ds for mk in model_keys for ds in auroc_results.get(mk, {}).keys()})

    fig, axes = plt.subplots(1, len(dataset_keys), figsize=(6 * len(dataset_keys), 5), sharey=True)
    if len(dataset_keys) == 1:
        axes = [axes]

    colors = sns.color_palette("Set2", len(model_keys))

    for ax_i, ds_name in enumerate(dataset_keys):
        ax = axes[ax_i]
        x = np.arange(len(methods))
        width = 0.35
        for m_i, model_key in enumerate(model_keys):
            aurocs = []
            ci_errs = []
            for method in methods:
                res = auroc_results.get(model_key, {}).get(ds_name, {}).get(method, {})
                a = res.get("auroc") if res else None
                ci_l = res.get("ci_low") if res else None
                ci_h = res.get("ci_high") if res else None
                aurocs.append(a if a is not None else 0.0)
                if a and ci_l and ci_h:
                    ci_errs.append([a - ci_l, ci_h - a])
                else:
                    ci_errs.append([0, 0])
            ci_errs_T = np.array(ci_errs).T  # [2, n_methods]
            offset = (m_i - len(model_keys) / 2 + 0.5) * width
            bars = ax.bar(
                x + offset,
                aurocs,
                width,
                label=MODEL_LABELS.get(model_key, model_key),
                color=colors[m_i],
                yerr=ci_errs_T,
                capsize=3,
                alpha=0.85,
            )
        ax.set_title(DATASET_LABELS.get(ds_name, ds_name))
        ax.set_xticks(x)
        ax.set_xticklabels([METHOD_LABELS.get(m, m) for m in methods], rotation=30, ha="right")
        ax.set_ylabel("AUROC")
        ax.set_ylim(0.4, 1.0)
        ax.axhline(0.5, linestyle="--", color="gray", alpha=0.5, label="Random")
        ax.legend()

    fig.suptitle("AUROC Comparison: UQ Methods × Scale × Dataset", fontsize=13)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_path}")


def plot_auroc_difference(auroc_results: Dict[str, Any], out_path: str) -> None:
    """FR8.2: AUROC_SE - AUROC_TP per scale per dataset with CI."""
    model_keys = [k for k in ["small", "large"] if k in auroc_results]
    dataset_keys = list({ds for mk in model_keys for ds in auroc_results.get(mk, {}).keys()})

    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(len(dataset_keys))
    width = 0.35
    colors = sns.color_palette("Set1", len(model_keys))

    for m_i, model_key in enumerate(model_keys):
        diffs, err_low, err_high = [], [], []
        for ds_name in dataset_keys:
            se_res = auroc_results.get(model_key, {}).get(ds_name, {}).get("semantic_entropy", {})
            tp_res = auroc_results.get(model_key, {}).get(ds_name, {}).get("token_prob", {})
            se_a = se_res.get("auroc") if se_res else None
            tp_a = tp_res.get("auroc") if tp_res else None
            if se_a and tp_a:
                diff = se_a - tp_a
                se_ci_l = se_res.get("ci_low", se_a)
                se_ci_h = se_res.get("ci_high", se_a)
                tp_ci_l = tp_res.get("ci_low", tp_a)
                tp_ci_h = tp_res.get("ci_high", tp_a)
                # Conservative CI propagation
                err_l = abs(diff) - abs((se_a - se_ci_l) + (tp_ci_h - tp_a))
                err_h = abs((se_ci_h - se_a) + (tp_a - tp_ci_l))
                diffs.append(diff)
                err_low.append(max(0, -err_l))
                err_high.append(max(0, err_h))
            else:
                diffs.append(0)
                err_low.append(0)
                err_high.append(0)

        offset = (m_i - len(model_keys) / 2 + 0.5) * width
        ax.bar(
            x + offset,
            diffs,
            width,
            label=MODEL_LABELS.get(model_key, model_key),
            color=colors[m_i],
            yerr=[err_low, err_high],
            capsize=4,
            alpha=0.85,
        )

    ax.axhline(0, linestyle="--", color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([DATASET_LABELS.get(d, d) for d in dataset_keys])
    ax.set_ylabel("AUROC_SE − AUROC_TP")
    ax.set_title("Semantic Entropy Advantage over Token-Probability")
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_path}")


def plot_roc_curves(
    uq_scores_all: Dict[str, Dict[str, Dict[str, np.ndarray]]],
    correctness_labels_all: Dict[str, np.ndarray],
    out_path: str,
    dataset_name: str = "trivia_qa",
) -> None:
    """FR8.3: ROC curves for SE vs TP at 8B and 70B."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    model_info = [("small", "8B"), ("large", "70B")]
    colors = {"semantic_entropy": "blue", "token_prob": "orange"}

    for ax, (model_key, label) in zip(axes, model_info):
        labels = correctness_labels_all.get(dataset_name)
        scores_dict = uq_scores_all.get(model_key, {}).get(dataset_name, {})
        if labels is None:
            continue
        for method, color in colors.items():
            scores = scores_dict.get(method)
            if scores is None:
                continue
            valid = ~np.isnan(scores)
            if valid.sum() < 10 or len(np.unique(labels[valid])) < 2:
                continue
            fpr, tpr, _ = roc_curve(labels[valid], -scores[valid])
            from sklearn.metrics import auc
            auroc_val = auc(fpr, tpr)
            ax.plot(
                fpr, tpr,
                color=color,
                label=f"{METHOD_LABELS.get(method, method)} (AUROC={auroc_val:.3f})",
                linewidth=1.8,
            )
        ax.plot([0, 1], [0, 1], "k--", linewidth=0.8, label="Random")
        ax.set_title(f"Llama-3-{label} on {DATASET_LABELS.get(dataset_name, dataset_name)}")
        ax.set_xlabel("FPR")
        ax.set_ylabel("TPR")
        ax.legend(fontsize=8)
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1.02])

    fig.suptitle("ROC Curves: SE vs Token-Probability", fontsize=13)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_path}")


def plot_bootstrap_distribution(
    uq_scores_all: Dict[str, Dict[str, Dict[str, np.ndarray]]],
    correctness_labels_all: Dict[str, np.ndarray],
    out_path: str,
    dataset_name: str = "trivia_qa",
    n_resamples: int = 1000,
) -> None:
    """FR8.4: Bootstrap AUROC histograms for SE vs TP per scale."""
    from evaluate import bootstrap_auroc_ci

    model_info = [("small", "8B"), ("large", "70B")]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    for ax, (model_key, label) in zip(axes, model_info):
        labels = correctness_labels_all.get(dataset_name)
        scores_dict = uq_scores_all.get(model_key, {}).get(dataset_name, {})
        if labels is None:
            continue
        for method, color in [("semantic_entropy", "blue"), ("token_prob", "orange")]:
            scores = scores_dict.get(method)
            if scores is None:
                continue
            valid = ~np.isnan(scores)
            if valid.sum() < 10:
                continue
            # Generate bootstrap distribution
            rng = np.random.default_rng(42)
            Q = valid.sum()
            boot = []
            labs = labels[valid]
            sc = scores[valid]
            for _ in range(n_resamples):
                idx = rng.integers(0, Q, size=Q)
                if len(np.unique(labs[idx])) < 2:
                    continue
                try:
                    from sklearn.metrics import roc_auc_score
                    boot.append(roc_auc_score(labs[idx], -sc[idx]))
                except Exception:
                    pass
            if boot:
                ax.hist(
                    boot, bins=40, alpha=0.6, color=color,
                    label=METHOD_LABELS.get(method, method), density=True
                )
        ax.set_title(f"Llama-3-{label} Bootstrap AUROC ({DATASET_LABELS.get(dataset_name, dataset_name)})")
        ax.set_xlabel("AUROC")
        ax.set_ylabel("Density")
        ax.legend()

    fig.suptitle("Bootstrap AUROC Distributions: SE vs Token-Probability", fontsize=12)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_path}")


def generate_all_figures(
    auroc_results: Dict,
    uq_scores_all: Dict,
    correctness_labels_all: Dict,
    figures_dir: str,
) -> None:
    """Generate all 4 required figures."""
    os.makedirs(figures_dir, exist_ok=True)
    plot_auroc_bar(auroc_results, os.path.join(figures_dir, "auroc_comparison_bar.png"))
    plot_auroc_difference(auroc_results, os.path.join(figures_dir, "auroc_difference.png"))
    plot_roc_curves(
        uq_scores_all, correctness_labels_all,
        os.path.join(figures_dir, "roc_curves.png"),
    )
    plot_bootstrap_distribution(
        uq_scores_all, correctness_labels_all,
        os.path.join(figures_dir, "bootstrap_distribution.png"),
    )
    logger.info(f"All figures saved to {figures_dir}")
