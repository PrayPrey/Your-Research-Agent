#!/usr/bin/env python3
# run.py - h-e1 NTI EXISTENCE PoC orchestrator
import os
import sys
import json
import random
import numpy as np
import torch

# Add code dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG
from data import load_truthfulqa_mc1, build_prompts
from model import load_model, extract_all_scores
from evaluate import run_cv, check_gate
from visualize import (
    plot_gate_metrics,
    plot_entropy_heatmap,
    plot_nti_distribution,
    plot_roc_curves,
)


def set_seed(seed):
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def main():
    print("=" * 60)
    print("NTI EXISTENCE PoC - h-e1")
    print("=" * 60)

    # Setup
    set_seed(CONFIG["seed"])
    os.makedirs(CONFIG["figures_dir"], exist_ok=True)
    os.makedirs(CONFIG["outputs_dir"], exist_ok=True)

    # Step 1: Load data
    print("\n[1/5] Loading TruthfulQA MC1 dataset...")
    samples = load_truthfulqa_mc1()
    prompts, labels = build_prompts(samples)
    print(f"  Loaded {len(samples)} questions -> {len(prompts)} prompt-choice pairs")
    print(f"  Label distribution: {sum(labels)} correct, {len(labels) - sum(labels)} incorrect")

    # Step 2: Load model
    print("\n[2/5] Loading LLaMA-2-7B via TransformerLens...")
    model = load_model()
    print(f"  Model loaded on {CONFIG['device']} with dtype={CONFIG['dtype']}")

    # Step 3: Extract scores
    print("\n[3/5] Extracting NTI scores...")
    print(f"  Processing {len(prompts)} prompts in batches of {CONFIG['batch_size']}...")
    scores = extract_all_scores(model, prompts)
    print(f"  NTI scores shape: {scores['nti'].shape}")
    print(f"  Trajectory shape: {scores['trajectory'].shape}")

    # Step 4: Evaluate
    print("\n[4/5] Running 5-fold CV evaluation...")
    cv_results = run_cv(scores["nti"], labels)
    gate_passed = check_gate(cv_results)

    print(f"\n  Results:")
    print(f"    Fold AUROCs: {[f'{a:.4f}' for a in cv_results['fold_aurocs']]}")
    print(f"    Mean AUROC:  {cv_results['mean_auroc']:.4f}")
    print(f"    Min AUROC:   {cv_results['min_auroc']:.4f}")
    print(f"    Pass Rate:   {cv_results['pass_count']}/{CONFIG['n_folds']} ({cv_results['pass_rate']:.1%})")
    print(f"\n  Gate Status: {'PASS' if gate_passed else 'FAIL'}")

    # Step 5: Visualize
    print("\n[5/5] Generating figures...")
    fig_paths = []
    fig_paths.append(plot_gate_metrics(cv_results))
    fig_paths.append(plot_entropy_heatmap(scores["trajectory"]))
    fig_paths.append(plot_nti_distribution(scores["nti"], labels))
    fig_paths.append(plot_roc_curves(cv_results))
    for p in fig_paths:
        print(f"  Saved: {p}")

    # Save results
    results_path = os.path.join(CONFIG["outputs_dir"], "results.json")
    results = {
        "hypothesis_id": "h-e1",
        "gate_type": "MUST_WORK",
        "gate_passed": bool(gate_passed),
        "metrics": {
            "mean_auroc": float(cv_results["mean_auroc"]),
            "min_auroc": float(cv_results["min_auroc"]),
            "fold_aurocs": [float(a) for a in cv_results["fold_aurocs"]],
            "pass_rate": float(cv_results["pass_rate"]),
            "pass_count": cv_results["pass_count"],
        },
        "thresholds": {
            "auroc_threshold": CONFIG["auroc_threshold"],
            "min_fold_threshold": CONFIG["min_fold_threshold"],
            "min_pass_rate": CONFIG["min_pass_rate"],
        },
        "dataset": {
            "name": "TruthfulQA MC1",
            "n_samples": len(samples),
            "n_prompts": len(prompts),
        },
        "model": CONFIG["model_id"],
        "figures": fig_paths,
    }

    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved: {results_path}")

    print("\n" + "=" * 60)
    print(f"EXPERIMENT COMPLETE: Gate {'PASSED' if gate_passed else 'FAILED'}")
    print("=" * 60)

    return gate_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
