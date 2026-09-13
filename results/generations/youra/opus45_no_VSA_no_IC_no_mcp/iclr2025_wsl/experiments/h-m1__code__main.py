#!/usr/bin/env python3
"""
h-m1: Training Dynamics Analysis for DWS vs NFT
Validates MECHANISM hypothesis: Architecture encodes different inductive biases
"""
import json
import os
import sys

import torch

from config import Config
from run_seeds import run_all_seeds
from metrics import check_success_criteria
from visualize import (
    plot_gradient_heatmap,
    plot_locality_evolution,
    plot_attention_entropy_curve,
    plot_layerwise_update_boxplot,
    plot_gate_metrics,
)


def aggregate_stats(results: dict, model_type: str) -> dict:
    """Aggregate stats across seeds for a model type."""
    all_runs = results.get(model_type, [])
    if not all_runs:
        return {}

    # Use first seed as representative (for visualization)
    first = all_runs[0]
    agg = {
        "grad_norms": first.get("grad_norms", {}),
        "weight_updates": first.get("weight_updates", {}),
        "attention_entropy": first.get("attention_entropy", []),
        "accuracies": [r.get("accuracy", 0) for r in all_runs],
        "mean_accuracy": sum(r.get("accuracy", 0) for r in all_runs) / len(all_runs),
    }
    return agg


def main():
    print("="*60)
    print("h-m1: Training Dynamics Analysis")
    print("="*60)

    cfg = Config()

    # Check device
    if not torch.cuda.is_available():
        print("WARNING: CUDA not available, using CPU (will be slow)")
        cfg.device = "cpu"

    # Run experiments across all seeds
    print("\nRunning experiments...")
    results = run_all_seeds(cfg)

    # Aggregate stats
    dws_stats = aggregate_stats(results, "dws")
    nft_stats = aggregate_stats(results, "nft")
    mlp_stats = aggregate_stats(results, "mlp")

    # Check success criteria
    print("\n" + "="*60)
    print("Evaluating Success Criteria")
    print("="*60)
    success_results = check_success_criteria(dws_stats, nft_stats, cfg)

    for key, value in success_results.items():
        print(f"  {key}: {value}")

    # Generate visualizations
    print("\nGenerating figures...")
    fig_dir = cfg.fig_dir
    os.makedirs(fig_dir, exist_ok=True)

    plot_gradient_heatmap(
        dws_stats.get("grad_norms", {}),
        nft_stats.get("grad_norms", {}),
        os.path.join(fig_dir, "gradient_heatmap.png")
    )
    plot_locality_evolution(
        dws_stats.get("weight_updates", {}),
        os.path.join(fig_dir, "locality_evolution.png")
    )
    plot_attention_entropy_curve(
        nft_stats.get("attention_entropy", []),
        os.path.join(fig_dir, "attention_entropy.png")
    )
    plot_layerwise_update_boxplot(
        dws_stats.get("weight_updates", {}),
        nft_stats.get("weight_updates", {}),
        os.path.join(fig_dir, "layerwise_updates.png")
    )
    plot_gate_metrics(results, success_results, os.path.join(fig_dir, "gate_metrics.png"))

    print(f"Figures saved to {fig_dir}/")

    # Save results
    output = {
        "hypothesis": "h-m1",
        "type": "MECHANISM",
        "gate": "MUST_WORK",
        "success_criteria": success_results,
        "model_accuracies": {
            "mlp": mlp_stats.get("mean_accuracy", 0),
            "dws": dws_stats.get("mean_accuracy", 0),
            "nft": nft_stats.get("mean_accuracy", 0),
        },
        "config": {
            "epochs": cfg.epochs,
            "lr": cfg.lr,
            "seeds": cfg.seeds,
            "wasserstein_threshold": cfg.wasserstein_threshold,
        },
        "pass": success_results.get("all_criteria_pass", False),
    }

    # Convert numpy bools to Python bools for JSON
    def convert_types(obj):
        import numpy as np
        if isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_types(v) for v in obj]
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        return obj

    output = convert_types(output)
    os.makedirs(os.path.dirname(cfg.results_path), exist_ok=True)
    with open(cfg.results_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {cfg.results_path}")

    # Final verdict
    print("\n" + "="*60)
    if output["pass"]:
        print("RESULT: PASS - MECHANISM hypothesis validated")
    else:
        print("RESULT: FAIL - MECHANISM hypothesis not validated")
    print("="*60)

    return 0 if output["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
