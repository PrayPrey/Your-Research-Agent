#!/usr/bin/env python3
"""h-m2: Low-entropy subset AUROC evaluation.

Tests: On low-entropy subset (H_L < 25th percentile), NTI achieves AUROC > 0.55
with 95% CI lower bound > 0.50.

Gate: SHOULD_WORK
"""
import os
import sys
import json
import numpy as np
from sklearn.metrics import roc_auc_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from config import CONFIG


def load_or_build_features(cache_path: str, h_e1_code_dir: str) -> dict:
    """Load cached features or regenerate from h-e1 code."""
    if os.path.exists(cache_path):
        print(f"Loading cached features from {cache_path}")
        data = np.load(cache_path)
        return {"h_l": data["h_l"], "nti": data["nti"], "labels": data["labels"]}

    print(f"Cache not found. Regenerating features from h-e1 code...")
    original_dir = os.getcwd()
    original_path = sys.path.copy()

    try:
        os.chdir(h_e1_code_dir)
        sys.path.insert(0, h_e1_code_dir)

        from data import load_truthfulqa_mc1, build_prompts
        from model import load_model, extract_all_scores

        samples = load_truthfulqa_mc1()
        prompts, labels = build_prompts(samples)
        print(f"Loaded {len(prompts)} prompts")

        model = load_model()
        scores = extract_all_scores(model, prompts)

        h_l = scores["baseline_entropy"]
        nti = scores["nti"]

        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        np.savez(cache_path, h_l=h_l, nti=nti, labels=labels)
        print(f"Saved features to {cache_path}")

        return {"h_l": h_l, "nti": nti, "labels": labels}
    finally:
        os.chdir(original_dir)
        sys.path = original_path


def filter_low_entropy(h_l, labels, nti, percentile=25):
    """Filter to low-entropy subset (H_L < percentile)."""
    threshold = np.percentile(h_l, percentile)
    mask = h_l < threshold
    return h_l[mask], labels[mask], nti[mask], mask, threshold


def bootstrap_auroc_ci(y_true, y_score, n_bootstrap=1000, ci=0.95, seed=42):
    """Compute AUROC with bootstrap confidence interval."""
    rng = np.random.default_rng(seed)
    auroc = roc_auc_score(y_true, y_score)

    n = len(y_true)
    boot_aurocs = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, n)
        y_b, s_b = y_true[idx], y_score[idx]
        if len(np.unique(y_b)) < 2:
            continue
        boot_aurocs.append(roc_auc_score(y_b, s_b))

    alpha = (1 - ci) / 2
    ci_lower, ci_upper = np.percentile(boot_aurocs, [alpha * 100, (1 - alpha) * 100])
    return {"auroc": auroc, "ci_lower": ci_lower, "ci_upper": ci_upper, "n_bootstrap": len(boot_aurocs)}


def check_gate(result, auroc_threshold=0.55, ci_lb_threshold=0.50):
    """Check gate conditions: AUROC > 0.55 AND CI_LB > 0.50."""
    return result["auroc"] > auroc_threshold and result["ci_lower"] > ci_lb_threshold


def plot_auroc_comparison(subset_result, out_path):
    """Bar chart: AUROC with CI vs thresholds."""
    fig, ax = plt.subplots(figsize=(6, 5))

    auroc = subset_result["auroc"]
    ci_lo = subset_result["ci_lower"]
    ci_hi = subset_result["ci_upper"]

    ax.bar(["NTI (low-entropy)"], [auroc], yerr=[[auroc - ci_lo], [ci_hi - auroc]],
           capsize=8, color="steelblue", alpha=0.8)
    ax.axhline(y=0.55, color="green", linestyle="--", label="Target (0.55)")
    ax.axhline(y=0.50, color="red", linestyle=":", label="Chance (0.50)")

    ax.set_ylabel("AUROC")
    ax.set_title("h-m2: NTI on Low-Entropy Subset")
    ax.set_ylim(0.40, 0.70)
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def plot_entropy_histogram(h_l, threshold, out_path):
    """Histogram of H_L with 25th percentile cutoff."""
    fig, ax = plt.subplots(figsize=(7, 4))

    ax.hist(h_l, bins=50, alpha=0.7, color="steelblue", edgecolor="black")
    ax.axvline(x=threshold, color="red", linestyle="--", linewidth=2,
               label=f"25th percentile ({threshold:.2f})")

    n_low = np.sum(h_l < threshold)
    ax.set_xlabel("H_L (output entropy)")
    ax.set_ylabel("Count")
    ax.set_title(f"Entropy Distribution (low-entropy: {n_low}/{len(h_l)} samples)")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def plot_roc_subset(y_true, y_score, auroc, out_path):
    """ROC curve for low-entropy subset."""
    from sklearn.metrics import roc_curve

    fpr, tpr, _ = roc_curve(y_true, y_score)

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(fpr, tpr, color="steelblue", linewidth=2, label=f"ROC (AUROC={auroc:.4f})")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.5)

    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve (Low-Entropy Subset)")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def main():
    np.random.seed(CONFIG["seed"])
    os.makedirs(CONFIG["outputs_dir"], exist_ok=True)
    os.makedirs(CONFIG["figures_dir"], exist_ok=True)

    print("=" * 60)
    print("h-m2: Low-Entropy Subset AUROC Evaluation")
    print("=" * 60)

    feats = load_or_build_features(CONFIG["feature_cache"], CONFIG["h_e1_code_dir"])
    h_l, labels, nti = feats["h_l"], feats["labels"], feats["nti"]
    print(f"Total samples: {len(h_l)}")

    h_l_sub, labels_sub, nti_sub, mask, threshold = filter_low_entropy(
        h_l, labels, nti, CONFIG["entropy_percentile"]
    )
    print(f"Low-entropy subset: {len(h_l_sub)} samples (H_L < {threshold:.4f})")

    result = bootstrap_auroc_ci(
        labels_sub, nti_sub,
        n_bootstrap=CONFIG["n_bootstrap"],
        ci=CONFIG["confidence_level"],
        seed=CONFIG["seed"]
    )
    print(f"AUROC: {result['auroc']:.4f}")
    print(f"95% CI: [{result['ci_lower']:.4f}, {result['ci_upper']:.4f}]")

    gate_passed = check_gate(result, CONFIG["auroc_threshold"], CONFIG["ci_lb_threshold"])
    print(f"Gate: {'PASS' if gate_passed else 'FAIL'}")

    fig1 = plot_auroc_comparison(result, os.path.join(CONFIG["figures_dir"], "auroc_comparison.png"))
    fig2 = plot_entropy_histogram(h_l, threshold, os.path.join(CONFIG["figures_dir"], "entropy_histogram.png"))
    fig3 = plot_roc_subset(labels_sub, nti_sub, result["auroc"], os.path.join(CONFIG["figures_dir"], "roc_curve_subset.png"))

    output = {
        "hypothesis_id": "h-m2",
        "gate_type": "SHOULD_WORK",
        "total_samples": int(len(h_l)),
        "subset_samples": int(len(h_l_sub)),
        "entropy_threshold": float(threshold),
        "auroc": float(result["auroc"]),
        "ci_lower": float(result["ci_lower"]),
        "ci_upper": float(result["ci_upper"]),
        "n_bootstrap": result["n_bootstrap"],
        "gate_passed": gate_passed,
        "figures": [fig1, fig2, fig3],
    }

    results_path = os.path.join(CONFIG["outputs_dir"], "results.json")
    with open(results_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Results saved to {results_path}")

    print("=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    return gate_passed


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
