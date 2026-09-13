"""Evaluation, metrics, figures for H-E1."""
import json
import os
import re
import string
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, roc_curve


def normalize_answer(s: str) -> str:
    """TriviaQA standard EM normalization."""
    s = s.lower()
    s = re.sub(r'\b(a|an|the)\b', ' ', s)
    s = ''.join(c for c in s if c not in string.punctuation)
    s = ' '.join(s.split())
    return s


def em_correctness(predictions: list, references: list) -> list:
    """Binary EM correctness: 1 if prediction matches any alias."""
    labels = []
    for pred, refs in zip(predictions, references):
        norm_pred = normalize_answer(str(pred))
        match = any(normalize_answer(str(r)) == norm_pred for r in refs)
        labels.append(int(match))
    return labels


def bootstrap_auroc(y_true: np.ndarray, y_score: np.ndarray,
                    n_bootstrap: int = 1000, seed: int = 42) -> tuple:
    """Stratified bootstrap AUROC. Returns (mean_auroc, [ci_low, ci_high])."""
    rng = np.random.default_rng(seed)
    aurocs = []
    pos_idx = np.where(y_true == 1)[0]
    neg_idx = np.where(y_true == 0)[0]

    if len(pos_idx) == 0 or len(neg_idx) == 0:
        # degenerate: return point estimate
        try:
            pt = roc_auc_score(y_true, y_score)
        except Exception:
            pt = 0.5
        return pt, np.array([pt, pt])

    for _ in range(n_bootstrap):
        boot_pos = rng.choice(pos_idx, size=len(pos_idx), replace=True)
        boot_neg = rng.choice(neg_idx, size=len(neg_idx), replace=True)
        idx = np.concatenate([boot_pos, boot_neg])
        try:
            aurocs.append(roc_auc_score(y_true[idx], y_score[idx]))
        except Exception:
            aurocs.append(0.5)

    aurocs = np.array(aurocs)
    return float(np.mean(aurocs)), np.percentile(aurocs, [2.5, 97.5])


def verify_mechanism(te_scores: list, se_scores: list,
                     correctness: list, avg_clusters: float) -> tuple:
    """Run mechanism assertions. Returns (passed, diagnostics_dict)."""
    y_true = np.array(correctness)
    te_arr = np.array(te_scores)
    se_arr = np.array(se_scores)

    try:
        gap = (roc_auc_score(y_true, -se_arr) - roc_auc_score(y_true, -te_arr))
    except Exception:
        gap = 0.0

    checks = {
        "avg_clusters_gt_1.5": avg_clusters > 1.5,
        "mean_te_nonzero": float(np.mean(te_arr)) > 0.0,
        "two_classes_present": len(set(correctness)) == 2,
        "gap_sane": abs(gap) < 0.30,
    }
    passed = all(checks.values())
    diagnostics = {**checks, "gap": float(gap), "avg_clusters": avg_clusters, "all_passed": passed}
    return passed, diagnostics


def save_results(te_scores, se_scores, correctness, auroc_te, auroc_se,
                 te_ci, se_ci, avg_clusters, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    gap = auroc_se - auroc_te
    results = {
        "n_questions": len(te_scores),
        "auroc_te": float(auroc_te),
        "auroc_se": float(auroc_se),
        "gap": float(gap),
        "te_ci": [float(te_ci[0]), float(te_ci[1])],
        "se_ci": [float(se_ci[0]), float(se_ci[1])],
        "avg_clusters": float(avg_clusters),
        "correctness_rate": float(np.mean(correctness)),
        "gate_pass": gap >= 0.05,
        "gate_extend": 0.03 <= gap < 0.05,
        "gate_fail": gap < 0.03,
    }
    with open(os.path.join(out_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=2)
    np.save(os.path.join(out_dir, "te_scores.npy"), np.array(te_scores))
    np.save(os.path.join(out_dir, "se_scores.npy"), np.array(se_scores))
    np.save(os.path.join(out_dir, "correctness.npy"), np.array(correctness))
    print(f"Results saved to {out_dir}")


def plot_figures(te_scores, se_scores, correctness, auroc_te, auroc_se,
                 te_ci, se_ci, bootstrap_te, bootstrap_se, figures_dir: str) -> None:
    os.makedirs(figures_dir, exist_ok=True)
    y_true = np.array(correctness)
    te_arr = np.array(te_scores)
    se_arr = np.array(se_scores)
    gap = auroc_se - auroc_te

    # Fig 1: Bar chart AUROC comparison with CI
    fig, ax = plt.subplots(figsize=(6, 5))
    methods = ["Token Entropy", "Semantic Entropy"]
    aurocs = [auroc_te, auroc_se]
    cis = [te_ci, se_ci]
    yerr = [[a - ci[0] for a, ci in zip(aurocs, cis)],
            [ci[1] - a for a, ci in zip(aurocs, cis)]]
    colors = ["#4C9BE8", "#E8834C"]
    bars = ax.bar(methods, aurocs, color=colors, yerr=yerr, capsize=8, width=0.5)
    ax.axhline(0.5, color="gray", linestyle="--", linewidth=1, label="Random")
    ax.set_ylim(0.3, 0.8)
    ax.set_ylabel("AUROC")
    ax.set_title(f"H-E1: SE vs TE AUROC (N={len(te_scores)})\nGap={gap:.4f}")
    ax.annotate(f"Gap={gap:.4f}", xy=(0.5, (auroc_te + auroc_se) / 2),
                xycoords=("axes fraction", "data"), ha="center", fontsize=11,
                color="green" if gap >= 0.05 else "red")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig1_auroc_bar.png"), dpi=150)
    plt.close()

    # Fig 2: ROC curves
    fig, ax = plt.subplots(figsize=(6, 5))
    fpr_te, tpr_te, _ = roc_curve(y_true, -te_arr)
    fpr_se, tpr_se, _ = roc_curve(y_true, -se_arr)
    ax.plot(fpr_te, tpr_te, label=f"TE (AUROC={auroc_te:.4f})", color="#4C9BE8")
    ax.plot(fpr_se, tpr_se, label=f"SE (AUROC={auroc_se:.4f})", color="#E8834C")
    ax.plot([0, 1], [0, 1], "k--", linewidth=0.8)
    ax.set_xlabel("FPR"); ax.set_ylabel("TPR")
    ax.set_title("ROC Curves: SE vs TE")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig2_roc_curves.png"), dpi=150)
    plt.close()

    # Fig 3: Uncertainty distribution violin
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    for ax_i, (scores, name) in enumerate([(te_arr, "TE"), (se_arr, "SE")]):
        correct = scores[y_true == 1]
        incorrect = scores[y_true == 0]
        axes[ax_i].violinplot([correct.tolist(), incorrect.tolist()],
                              positions=[0, 1], showmedians=True)
        axes[ax_i].set_xticks([0, 1])
        axes[ax_i].set_xticklabels(["Correct", "Incorrect"])
        axes[ax_i].set_title(f"{name} Score Distribution")
        axes[ax_i].set_ylabel("Uncertainty Score")
    plt.suptitle("Uncertainty Score by Correctness")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig3_violin_distributions.png"), dpi=150)
    plt.close()

    # Fig 4: Bootstrap AUROC histograms
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(bootstrap_te, bins=40, alpha=0.6, label="TE bootstrap", color="#4C9BE8")
    ax.hist(bootstrap_se, bins=40, alpha=0.6, label="SE bootstrap", color="#E8834C")
    ax.axvline(auroc_te, color="#4C9BE8", linestyle="--")
    ax.axvline(auroc_se, color="#E8834C", linestyle="--")
    ax.set_xlabel("AUROC"); ax.set_ylabel("Count")
    ax.set_title("Bootstrap AUROC Distribution")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig4_bootstrap_hist.png"), dpi=150)
    plt.close()

    print(f"Figures saved to {figures_dir}")
