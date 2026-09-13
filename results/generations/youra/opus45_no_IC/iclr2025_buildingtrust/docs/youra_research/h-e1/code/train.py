"""Main entry point: run inference, compute ECE, perform ANOVA, generate figures."""

import os
import json
import random
import numpy as np
import torch
import matplotlib.pyplot as plt
from tqdm import tqdm

from config import (
    SEED, CLUSTER_NAMES, RESULTS_JSON, VALIDATION_MD, FIGURES_DIR,
    N_BOOTSTRAP, ALPHA, ECE_RANGE_TARGET
)
from data import load_truthfulqa_mc, assign_clusters, validate_cluster_sizes
from model import load_model_and_tokenizer, predict
from metrics import (
    compute_cluster_eces, bootstrap_cluster_ece, run_anova,
    bonferroni_pairwise, confidence_interval
)


def set_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def run_inference(dataset, model, tokenizer, device):
    """Run inference on all questions."""
    records = []
    for example in tqdm(dataset, desc="Running inference"):
        question = example["question"]
        choices = example["mc1_targets"]["choices"]
        labels = example["mc1_targets"]["labels"]
        correct_idx = labels.index(1)
        cluster_id = example["cluster_id"]

        record = predict(question, choices, correct_idx, model, tokenizer, device, cluster_id)
        records.append(record)

    return records


def aggregate_by_cluster(records):
    """Group records by cluster_id."""
    by_cluster = {}
    for r in records:
        cid = r["cluster_id"]
        if cid not in by_cluster:
            by_cluster[cid] = []
        by_cluster[cid].append(r)
    return by_cluster


def plot_cluster_ece_bar(cluster_eces, cis, path):
    """Bar chart of per-cluster ECE with error bars."""
    cluster_ids = sorted(cluster_eces.keys())
    eces = [cluster_eces[cid] for cid in cluster_ids]
    lowers = [cluster_eces[cid] - cis[cid][0] for cid in cluster_ids]
    uppers = [cis[cid][1] - cluster_eces[cid] for cid in cluster_ids]
    labels = [CLUSTER_NAMES.get(cid, f"Cluster {cid}") for cid in cluster_ids]

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(cluster_ids))
    ax.bar(x, eces, yerr=[lowers, uppers], capsize=5, color="steelblue", edgecolor="black")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("ECE")
    ax.set_title("Per-Cluster Expected Calibration Error (95% CI)")
    ax.set_ylim(0, max(eces) * 1.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_reliability_diagrams(records_by_cluster, path_dir):
    """Reliability diagrams (calibration curves) per cluster."""
    n_bins = 10
    for cid, records in records_by_cluster.items():
        confs = np.array([r["confidence"] for r in records])
        accs = np.array([float(r["correct"]) for r in records])

        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_accs = []
        bin_confs = []

        for i in range(n_bins):
            in_bin = (confs > bin_boundaries[i]) & (confs <= bin_boundaries[i + 1])
            if in_bin.sum() > 0:
                bin_accs.append(accs[in_bin].mean())
                bin_confs.append(confs[in_bin].mean())
            else:
                bin_accs.append(np.nan)
                bin_confs.append((bin_boundaries[i] + bin_boundaries[i + 1]) / 2)

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.plot([0, 1], [0, 1], "k--", label="Perfect calibration")
        ax.bar(np.array(bin_confs), bin_accs, width=0.08, alpha=0.7, label="Model")
        ax.set_xlabel("Confidence")
        ax.set_ylabel("Accuracy")
        ax.set_title(f"Reliability Diagram: {CLUSTER_NAMES.get(cid, f'Cluster {cid}')}")
        ax.legend()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        plt.tight_layout()
        plt.savefig(os.path.join(path_dir, f"reliability_cluster_{cid}.png"), dpi=150)
        plt.close()


def plot_confidence_histograms(records_by_cluster, path_dir):
    """Confidence histograms per cluster."""
    for cid, records in records_by_cluster.items():
        confs = [r["confidence"] for r in records]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(confs, bins=20, edgecolor="black", alpha=0.7, color="steelblue")
        ax.set_xlabel("Confidence")
        ax.set_ylabel("Count")
        ax.set_title(f"Confidence Distribution: {CLUSTER_NAMES.get(cid, f'Cluster {cid}')}")
        ax.set_xlim(0, 1)
        plt.tight_layout()
        plt.savefig(os.path.join(path_dir, f"confidence_hist_cluster_{cid}.png"), dpi=150)
        plt.close()


def save_results_json(results, path):
    """Save results to JSON."""
    with open(path, "w") as f:
        json.dump(results, f, indent=2)


def save_validation_md(gate_pass, results, path):
    """Generate validation report."""
    content = f"""# Phase 4 Validation Report: H-E1

**Hypothesis:** Category-dependent calibration variation exists in LLMs on TruthfulQA
**Date:** {results.get('date', 'N/A')}
**Status:** {'PASS' if gate_pass else 'FAIL'}

---

## Gate Evaluation

| Metric | Value | Target | Result |
|--------|-------|--------|--------|
| ANOVA p-value | {results['anova_p']:.6f} | < 0.05 | {'✓ PASS' if results['anova_p'] < ALPHA else '✗ FAIL'} |
| ANOVA F-statistic | {results['anova_f']:.4f} | - | - |
| ECE Range | {results['ece_range']:.4f} | > 0.05 | {'✓' if results['ece_range'] > ECE_RANGE_TARGET else '✗'} |

**Gate Verdict:** {'**PASS** - Significant variation detected' if gate_pass else '**FAIL** - No significant variation'}

---

## Per-Cluster ECE Results

| Cluster | ECE | 95% CI | N |
|---------|-----|--------|---|
"""
    for cid in sorted(results['cluster_eces'].keys()):
        ece = results['cluster_eces'][cid]
        ci = results['cluster_cis'][cid]
        n = results['cluster_sizes'][cid]
        name = CLUSTER_NAMES.get(int(cid), f"Cluster {cid}")
        content += f"| {name} | {ece:.4f} | [{ci[0]:.4f}, {ci[1]:.4f}] | {n} |\n"

    content += f"""
---

## Statistical Summary

- **Total Questions:** {results['total_questions']}
- **Global Accuracy:** {results['global_accuracy']:.2%}
- **Global ECE:** {results['global_ece']:.4f}
- **Min Cluster ECE:** {min(results['cluster_eces'].values()):.4f}
- **Max Cluster ECE:** {max(results['cluster_eces'].values()):.4f}

---

## Figures Generated

- `figures/cluster_ece_bar.png` - Per-cluster ECE with 95% CI
- `figures/reliability_cluster_*.png` - Reliability diagrams
- `figures/confidence_hist_cluster_*.png` - Confidence histograms

---

## Next Steps

{'Proceed to Phase 4.5 for hypothesis synthesis.' if gate_pass else 'ABANDON subsequent hypotheses - no category structure to exploit.'}
"""

    with open(path, "w") as f:
        f.write(content)


def main():
    set_seed()

    print("Loading dataset...")
    dataset = load_truthfulqa_mc()
    dataset = assign_clusters(dataset)
    cluster_sizes = validate_cluster_sizes(dataset)
    print(f"Cluster sizes: {cluster_sizes}")

    print("Loading model...")
    model, tokenizer = load_model_and_tokenizer()
    device = next(model.parameters()).device

    print("Running inference...")
    records = run_inference(dataset, model, tokenizer, device)

    print("Aggregating by cluster...")
    records_by_cluster = aggregate_by_cluster(records)

    print("Computing cluster ECEs...")
    cluster_eces = compute_cluster_eces(records_by_cluster)
    print(f"Cluster ECEs: {cluster_eces}")

    print("Bootstrap resampling...")
    bootstrap_samples = {}
    cluster_cis = {}
    for cid, recs in records_by_cluster.items():
        confs = [r["confidence"] for r in recs]
        accs = [float(r["correct"]) for r in recs]
        bootstrap_samples[cid] = bootstrap_cluster_ece(confs, accs, N_BOOTSTRAP)
        cluster_cis[cid] = confidence_interval(bootstrap_samples[cid])

    print("Running ANOVA...")
    f_stat, p_value = run_anova(bootstrap_samples)
    print(f"ANOVA F={f_stat:.4f}, p={p_value:.6f}")

    pairwise = bonferroni_pairwise(bootstrap_samples)

    global_accuracy = sum(r["correct"] for r in records) / len(records)
    global_ece = sum(cluster_eces[cid] * len(records_by_cluster[cid]) for cid in cluster_eces) / len(records)
    ece_values = list(cluster_eces.values())
    ece_range = max(ece_values) - min(ece_values)

    gate_pass = p_value < ALPHA

    results = {
        "date": "2026-08-10",
        "hypothesis": "h-e1",
        "total_questions": len(records),
        "cluster_sizes": {str(k): v for k, v in cluster_sizes.items()},
        "cluster_eces": {str(k): v for k, v in cluster_eces.items()},
        "cluster_cis": {str(k): list(v) for k, v in cluster_cis.items()},
        "global_accuracy": global_accuracy,
        "global_ece": global_ece,
        "anova_f": f_stat,
        "anova_p": p_value,
        "ece_range": ece_range,
        "gate_pass": gate_pass,
        "pairwise_bonferroni": {f"{a}-{b}": p for (a, b), p in pairwise.items()},
    }

    os.makedirs(FIGURES_DIR, exist_ok=True)

    print("Generating figures...")
    plot_cluster_ece_bar(cluster_eces, cluster_cis, os.path.join(FIGURES_DIR, "cluster_ece_bar.png"))
    plot_reliability_diagrams(records_by_cluster, FIGURES_DIR)
    plot_confidence_histograms(records_by_cluster, FIGURES_DIR)

    print("Saving results...")
    save_results_json(results, RESULTS_JSON)
    save_validation_md(gate_pass, results, VALIDATION_MD)

    print(f"\n{'='*50}")
    print(f"GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")
    print(f"ANOVA p-value: {p_value:.6f} (threshold: {ALPHA})")
    print(f"ECE Range: {ece_range:.4f}")
    print(f"{'='*50}")

    return results


if __name__ == "__main__":
    main()
