# visualize.py - h-m1 MECHANISM: Null vs Full model comparison plots
import os
import numpy as np
import matplotlib.pyplot as plt
from config import CONFIG


def plot_gate_metrics(cv_results, save_path=None):
    """Bar chart comparing null vs full AUROC per fold with gain threshold."""
    save_path = save_path or os.path.join(CONFIG["figures_dir"], "gate_metrics.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    n_folds = cv_results["n_folds"]
    fold_results = cv_results["fold_results"]

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(n_folds + 1)
    width = 0.35

    null_aurocs = [r["auroc_null"] for r in fold_results] + [cv_results["mean_auroc_null"]]
    full_aurocs = [r["auroc_full"] for r in fold_results] + [cv_results["mean_auroc_full"]]

    ax.bar(x - width/2, null_aurocs, width, label="Null (H_L)", color="gray", alpha=0.7)
    ax.bar(x + width/2, full_aurocs, width, label="Full (H_L+NTI+CMI)", color="blue", alpha=0.7)

    labels = [f"Fold {i+1}" for i in range(n_folds)] + ["Mean"]
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("AUROC")
    ax.set_title(f"AUROC Comparison: Null vs Full Model\nMean Gain: {cv_results['mean_auroc_gain']:.4f}")
    ax.legend()
    ax.set_ylim(0.4, 0.8)

    # Add gain threshold line
    gain_thresh = CONFIG["auroc_gain_threshold"]
    ax.axhline(y=cv_results["mean_auroc_null"] + gain_thresh, color="orange",
               linestyle="--", label=f"Target (+{gain_thresh})")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path


def plot_lrt_pvalue(cv_results, save_path=None):
    """Plot LRT p-values per fold with significance threshold."""
    save_path = save_path or os.path.join(CONFIG["figures_dir"], "lrt_pvalue.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fold_results = cv_results["fold_results"]
    n_folds = len(fold_results)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left: p-values per fold
    p_values = [r["p_value"] for r in fold_results]
    x = range(n_folds)
    colors = ["green" if p < CONFIG["lrt_pvalue_threshold"] else "red" for p in p_values]

    ax1.bar(x, p_values, color=colors, alpha=0.7, edgecolor="black")
    ax1.axhline(y=CONFIG["lrt_pvalue_threshold"], color="orange", linestyle="--",
                label=f"α = {CONFIG['lrt_pvalue_threshold']}")
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"Fold {i+1}" for i in range(n_folds)])
    ax1.set_ylabel("p-value")
    ax1.set_title("LRT p-value per Fold")
    ax1.legend()
    ax1.set_yscale("log")

    # Right: G statistic per fold
    G_values = [r["G"] for r in fold_results]
    ax2.bar(x, G_values, color="blue", alpha=0.7, edgecolor="black")
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"Fold {i+1}" for i in range(n_folds)])
    ax2.set_ylabel("LRT G statistic")
    ax2.set_title(f"LRT G Statistic (df={CONFIG['lrt_df']})")

    plt.suptitle(f"Combined p-value (Fisher): {cv_results['combined_p_value']:.4e}")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path


def plot_roc_overlay(cv_results, save_path=None):
    """ROC curves: null vs full model overlay."""
    save_path = save_path or os.path.join(CONFIG["figures_dir"], "roc_overlay.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))

    fold_results = cv_results["fold_results"]
    for i, r in enumerate(fold_results):
        fpr_null, tpr_null = r["roc_null"]
        fpr_full, tpr_full = r["roc_full"]
        ax.plot(fpr_null, tpr_null, color="gray", alpha=0.3)
        ax.plot(fpr_full, tpr_full, color="blue", alpha=0.3)

    # Legend entries
    ax.plot([], [], color="gray", alpha=0.7, label=f"Null (mean={cv_results['mean_auroc_null']:.3f})")
    ax.plot([], [], color="blue", alpha=0.7, label=f"Full (mean={cv_results['mean_auroc_full']:.3f})")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Random")

    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(f"ROC Overlay: Null vs Full Model\nGain: {cv_results['mean_auroc_gain']:.4f}")
    ax.legend(loc="lower right")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path


def plot_fold_auroc_bars(cv_results, save_path=None):
    """AUROC gain per fold bar chart."""
    save_path = save_path or os.path.join(CONFIG["figures_dir"], "fold_auroc_bars.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fold_results = cv_results["fold_results"]
    n_folds = len(fold_results)

    gains = [r["auroc_gain"] for r in fold_results]
    x = range(n_folds)

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["green" if g >= CONFIG["auroc_gain_threshold"] else "orange" for g in gains]

    ax.bar(x, gains, color=colors, alpha=0.7, edgecolor="black")
    ax.axhline(y=CONFIG["auroc_gain_threshold"], color="red", linestyle="--",
               label=f"Threshold ({CONFIG['auroc_gain_threshold']})")
    ax.axhline(y=cv_results["mean_auroc_gain"], color="blue", linestyle="-",
               label=f"Mean ({cv_results['mean_auroc_gain']:.4f})")

    ax.set_xticks(x)
    ax.set_xticklabels([f"Fold {i+1}" for i in range(n_folds)])
    ax.set_ylabel("AUROC Gain (Full - Null)")
    ax.set_title("AUROC Gain per Fold")
    ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path


def plot_coefficients(cv_results, save_path=None):
    """Feature coefficients from full model."""
    save_path = save_path or os.path.join(CONFIG["figures_dir"], "coefficients.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fold_results = cv_results["fold_results"]
    all_coefs = np.array([r["coef_full"] for r in fold_results])
    mean_coefs = all_coefs.mean(axis=0)
    std_coefs = all_coefs.std(axis=0)

    features = ["H_L", "NTI", "CMI"]
    x = range(len(features))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x, mean_coefs, yerr=std_coefs, color="blue", alpha=0.7, capsize=5)
    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(features)
    ax.set_ylabel("Coefficient")
    ax.set_title("Logistic Regression Coefficients (Full Model)")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path


def plot_nti_cmi_scatter(nti, cmi, labels, save_path=None):
    """Scatter plot of NTI vs CMI colored by label."""
    save_path = save_path or os.path.join(CONFIG["figures_dir"], "nti_cmi_scatter.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))

    correct_mask = labels == 1
    ax.scatter(nti[correct_mask], cmi[correct_mask], c="green", alpha=0.4, s=10, label="Correct")
    ax.scatter(nti[~correct_mask], cmi[~correct_mask], c="red", alpha=0.4, s=10, label="Incorrect")

    ax.set_xlabel("NTI")
    ax.set_ylabel("CMI")
    ax.set_title("NTI vs CMI Feature Space")
    ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path
