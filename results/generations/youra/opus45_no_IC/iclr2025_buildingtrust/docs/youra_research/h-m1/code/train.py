"""H-M1: Pairwise KS tests on cluster confidence distributions."""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

import numpy as np
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

# Add h-e1 to path first for data/model imports
H_E1_PATH = str(Path(__file__).parent.parent.parent / "h-e1" / "code")
sys.path.insert(0, H_E1_PATH)

from data import load_truthfulqa_mc, assign_clusters, validate_cluster_sizes
from model import load_model_and_tokenizer, predict

# Now import h-e1 config constants we need
import config as he1_config

# Remove h-e1 from path, add current dir for local modules
sys.path.remove(H_E1_PATH)
sys.path.insert(0, str(Path(__file__).parent))

from ks_analysis import (
    extract_cluster_confidences, pairwise_ks_tests,
    evaluate_gate_condition, cluster_mean_std
)

# Constants from h-e1
SEED = he1_config.SEED
MODEL_ID = he1_config.MODEL_ID
CLUSTER_NAMES = he1_config.CLUSTER_NAMES

# H-M1 specific constants
ALPHA = 0.05
MIN_CLUSTER_SIZE = 100
MAJORITY_PAIRS_REQUIRED = 11
RESULTS_JSON = "outputs/results.json"
VALIDATION_MD = "../04_validation.md"
FIGURES_DIR = "figures/"

np.random.seed(SEED)
torch.manual_seed(SEED)


def run_inference(dataset, model, tokenizer, device):
    """Iterate dataset rows, call predict() per question."""
    records = []
    for ex in tqdm(dataset, desc="Inference"):
        choices = ex["mc1_targets"]["choices"]
        correct_idx = ex["mc1_targets"]["labels"].index(1)
        record = predict(
            ex["question"], choices, correct_idx,
            model, tokenizer, device, ex["cluster_id"]
        )
        records.append(record)
    return records


def plot_ks_heatmap(ks_results, cluster_ids, path):
    """7x7 symmetric p-value heatmap."""
    n = len(cluster_ids)
    pvalue_matrix = np.ones((n, n))
    np.fill_diagonal(pvalue_matrix, np.nan)

    for (c1, c2), res in ks_results.items():
        i, j = cluster_ids.index(c1), cluster_ids.index(c2)
        pvalue_matrix[i, j] = res["pvalue"]
        pvalue_matrix[j, i] = res["pvalue"]

    fig, ax = plt.subplots(figsize=(8, 6))
    mask = np.eye(n, dtype=bool)
    cmap = sns.diverging_palette(10, 133, as_cmap=True)
    sns.heatmap(
        pvalue_matrix, mask=mask, annot=True, fmt=".3f",
        xticklabels=[CLUSTER_NAMES.get(c, str(c))[:15] for c in cluster_ids],
        yticklabels=[CLUSTER_NAMES.get(c, str(c))[:15] for c in cluster_ids],
        cmap=cmap, center=0.05, vmin=0, vmax=0.3, ax=ax
    )
    ax.set_title("KS Test P-Values (p<0.05 = significant)")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_confidence_histograms(cluster_confidences, path):
    """Overlaid histograms for all clusters."""
    fig, ax = plt.subplots(figsize=(10, 6))
    for cid in sorted(cluster_confidences.keys()):
        ax.hist(
            cluster_confidences[cid], bins=20, alpha=0.5,
            label=f"{CLUSTER_NAMES.get(cid, str(cid))[:20]} (n={len(cluster_confidences[cid])})"
        )
    ax.set_xlabel("Confidence")
    ax.set_ylabel("Frequency")
    ax.set_title("Confidence Distribution by Cluster")
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_confidence_boxplot(cluster_confidences, path):
    """Box plot comparing clusters."""
    fig, ax = plt.subplots(figsize=(10, 6))
    data = [cluster_confidences[c] for c in sorted(cluster_confidences.keys())]
    labels = [CLUSTER_NAMES.get(c, str(c))[:15] for c in sorted(cluster_confidences.keys())]
    ax.boxplot(data, labels=labels)
    ax.set_ylabel("Confidence")
    ax.set_title("Confidence by Cluster")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_cdf_comparison(cluster_confidences, path):
    """Empirical CDF per cluster."""
    fig, ax = plt.subplots(figsize=(10, 6))
    for cid in sorted(cluster_confidences.keys()):
        vals = np.sort(cluster_confidences[cid])
        cdf = np.arange(1, len(vals) + 1) / len(vals)
        ax.step(vals, cdf, label=f"{CLUSTER_NAMES.get(cid, str(cid))[:20]}", where='post')
    ax.set_xlabel("Confidence")
    ax.set_ylabel("Cumulative Probability")
    ax.set_title("Empirical CDF by Cluster")
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def save_results_json(results, path):
    """Save structured results to JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    serializable = results.copy()
    if "ks_results" in serializable:
        serializable["ks_results"] = {
            f"{k[0]}-{k[1]}": v for k, v in serializable["ks_results"].items()
        }
    with open(path, "w") as f:
        json.dump(serializable, f, indent=2)


def save_validation_md(gate_pass, results, path):
    """Write 04_validation.md with gate decision, stats, figures."""
    sig_count = results["significant_count"]
    total = results["total_pairs"]
    cluster_stats = results["cluster_stats"]
    conf_range = cluster_stats.get("_range", 0)

    lines = [
        "# H-M1 Validation Report",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Hypothesis:** LLMs produce category-specific confidence distributions on TruthfulQA",
        f"**Gate Type:** MUST_WORK",
        "",
        "## Gate Decision",
        "",
        f"**Result:** {'PASS' if gate_pass else 'FAIL'}",
        f"- Significant KS pairs: {sig_count}/{total} (threshold: ≥{MAJORITY_PAIRS_REQUIRED})",
        f"- Confidence range across clusters: {conf_range:.4f} (secondary metric, target >0.1)",
        "",
        "## Per-Cluster Statistics",
        "",
        "| Cluster | Mean Conf | Std | N |",
        "|---------|-----------|-----|---|",
    ]
    for cid in sorted(c for c in cluster_stats.keys() if isinstance(c, int)):
        s = cluster_stats[cid]
        name = CLUSTER_NAMES.get(cid, str(cid))[:25]
        lines.append(f"| {name} | {s['mean']:.4f} | {s['std']:.4f} | {s['n']} |")

    lines.extend([
        "",
        "## KS Test Results (Significant Pairs)",
        "",
        "| Pair | D-Statistic | P-Value |",
        "|------|-------------|---------|",
    ])
    for (c1, c2), res in sorted(results["ks_results"].items()):
        if res["pvalue"] < ALPHA:
            lines.append(f"| {c1}-{c2} | {res['statistic']:.4f} | {res['pvalue']:.4e} |")

    lines.extend([
        "",
        "## Figures",
        "",
        "- ![KS Heatmap](code/figures/ks_heatmap.png)",
        "- ![Confidence Histograms](code/figures/confidence_histograms.png)",
        "- ![Confidence Boxplot](code/figures/confidence_boxplot.png)",
        "- ![CDF Comparison](code/figures/cdf_comparison.png)",
        "",
        "## Conclusion",
        "",
    ])
    if gate_pass:
        lines.append(f"GATE PASS: {sig_count}/{total} cluster pairs show significantly different confidence distributions (p < {ALPHA}). The mechanism hypothesis is validated — category membership produces distinct confidence patterns.")
    else:
        lines.append(f"GATE FAIL: Only {sig_count}/{total} pairs significant, below threshold of {MAJORITY_PAIRS_REQUIRED}. Consider alternative clustering strategy.")

    with open(path, "w") as f:
        f.write("\n".join(lines))


def main():
    print("=== H-M1: Category-Specific Confidence Distributions ===")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # Step 1-2: Load dataset with clusters
    print("\n[1/7] Loading TruthfulQA...")
    dataset = load_truthfulqa_mc()
    dataset = assign_clusters(dataset)
    cluster_sizes = validate_cluster_sizes(dataset, MIN_CLUSTER_SIZE)
    print(f"Cluster sizes: {cluster_sizes}")

    # Step 3: Load model
    print("\n[2/7] Loading model...")
    model, tokenizer = load_model_and_tokenizer(MODEL_ID)

    # Step 4: Run inference
    print("\n[3/7] Running inference...")
    records = run_inference(dataset, model, tokenizer, device)

    # Step 5: Extract cluster confidences
    print("\n[4/7] Extracting cluster confidences...")
    cluster_conf = extract_cluster_confidences(records)

    # Step 6: KS tests
    print("\n[5/7] Running pairwise KS tests...")
    ks_results = pairwise_ks_tests(cluster_conf)
    gate_pass, sig_count, total = evaluate_gate_condition(
        ks_results, ALPHA, MAJORITY_PAIRS_REQUIRED
    )
    print(f"Significant pairs: {sig_count}/{total} (gate threshold: {MAJORITY_PAIRS_REQUIRED})")
    print(f"Gate: {'PASS' if gate_pass else 'FAIL'}")

    # Step 7: Cluster stats
    stats = cluster_mean_std(cluster_conf)
    print(f"Confidence range: {stats['_range']:.4f}")

    # Step 8: Visualizations
    print("\n[6/7] Generating figures...")
    os.makedirs(FIGURES_DIR, exist_ok=True)
    cluster_ids = sorted(cluster_conf.keys())
    plot_ks_heatmap(ks_results, cluster_ids, os.path.join(FIGURES_DIR, "ks_heatmap.png"))
    plot_confidence_histograms(cluster_conf, os.path.join(FIGURES_DIR, "confidence_histograms.png"))
    plot_confidence_boxplot(cluster_conf, os.path.join(FIGURES_DIR, "confidence_boxplot.png"))
    plot_cdf_comparison(cluster_conf, os.path.join(FIGURES_DIR, "cdf_comparison.png"))

    # Step 9: Save results
    print("\n[7/7] Saving results...")
    results = {
        "gate_passed": gate_pass,
        "significant_count": sig_count,
        "total_pairs": total,
        "alpha": ALPHA,
        "ks_results": ks_results,
        "cluster_stats": stats,
    }
    save_results_json(results, RESULTS_JSON)
    save_validation_md(gate_pass, results, VALIDATION_MD)

    print(f"\n=== COMPLETE ===")
    print(f"Gate: {'PASS' if gate_pass else 'FAIL'}")
    print(f"Results: {RESULTS_JSON}")
    print(f"Validation: {VALIDATION_MD}")
    return gate_pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
