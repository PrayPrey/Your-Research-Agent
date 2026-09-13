#!/usr/bin/env python3
"""H-M3 Pipeline: Linear Fusion of Entropy + Consistency."""
import json
import os

import config
from load_results import load_h_m2_results
from fusion import LinearFusionScorer, train_test_split_idx, grid_search_weights
from stats import evaluate_variants, bootstrap_ci_improvement
from visualize import (
    plot_gate_metrics,
    plot_roc_overlay,
    plot_weight_heatmap,
    plot_entropy_vs_consistency,
)


def run(h_m2_results_path: str = None) -> dict:
    """Full H-M3 pipeline. Returns results dict."""
    path = h_m2_results_path or config.H_M2_RESULTS_PATH

    print(f"Loading h-m2 results from: {path}")
    data = load_h_m2_results(path)
    entropy = data["entropy"]
    consistency = data["consistency"]
    correct = data["correct"]
    n = data["n"]
    print(f"Loaded {n} questions")

    # Split
    val_idx, test_idx = train_test_split_idx(n, config.VAL_FRACTION, config.SEED)
    print(f"Split: {len(val_idx)} val, {len(test_idx)} test")

    # Grid search on val set
    print("Running grid search on validation set...")
    best_alpha, best_beta, val_auroc, auroc_grid = grid_search_weights(
        entropy[val_idx], consistency[val_idx], correct[val_idx],
        config.ALPHA_RANGE, config.BETA_RANGE
    )
    print(f"Best weights: α={best_alpha}, β={best_beta} (val AUROC={val_auroc:.4f})")

    # Evaluate variants on test set
    print("Evaluating variants on test set...")
    variants = evaluate_variants(
        entropy[test_idx], consistency[test_idx], correct[test_idx],
        {
            "entropy_only": (1.0, 0.0),
            "consistency_only": (0.0, 1.0),
            "equal": (0.5, 0.5),
            "optimal": (best_alpha, best_beta),
        }
    )

    for name, v in variants.items():
        print(f"  {name}: AUROC={v['auroc']:.4f}")

    # Determine best single metric
    best_single_name = (
        "entropy_only" if variants["entropy_only"]["auroc"] >= variants["consistency_only"]["auroc"]
        else "consistency_only"
    )

    # Bootstrap CI for improvement
    print("Computing bootstrap CI...")
    ci = bootstrap_ci_improvement(
        correct[test_idx],
        variants["optimal"]["scores"],
        variants[best_single_name]["scores"],
        config.N_BOOTSTRAP,
        config.SEED,
    )
    print(f"Improvement vs {best_single_name}: {ci['improvement']:.4f} (95% CI: [{ci['ci_low']:.4f}, {ci['ci_high']:.4f}])")

    # Gate check
    gate_pass = variants["optimal"]["auroc"] > max(
        variants["entropy_only"]["auroc"],
        variants["consistency_only"]["auroc"]
    )
    print(f"Gate PASS: {gate_pass}")

    # Visualizations
    os.makedirs(config.FIGURES_DIR, exist_ok=True)

    print("Generating figures...")
    plot_gate_metrics(
        variants["entropy_only"]["auroc"],
        variants["consistency_only"]["auroc"],
        variants["optimal"]["auroc"],
        os.path.join(config.FIGURES_DIR, "gate_metrics.png")
    )

    plot_roc_overlay(
        correct[test_idx],
        variants["entropy_only"]["scores"],
        variants["consistency_only"]["scores"],
        variants["optimal"]["scores"],
        os.path.join(config.FIGURES_DIR, "roc_overlay.png")
    )

    # Full grid for heatmap (recompute on full test set for visualization)
    _, _, _, full_auroc_grid = grid_search_weights(
        entropy[test_idx], consistency[test_idx], correct[test_idx],
        config.ALPHA_RANGE, config.BETA_RANGE
    )
    plot_weight_heatmap(
        config.ALPHA_RANGE,
        config.BETA_RANGE,
        full_auroc_grid,
        os.path.join(config.FIGURES_DIR, "weight_heatmap.png")
    )

    plot_entropy_vs_consistency(
        entropy, consistency, correct,
        os.path.join(config.FIGURES_DIR, "entropy_vs_consistency.png")
    )

    # Results JSON
    results = {
        "hypothesis": "h-m3",
        "description": "Linear Fusion of Entropy and Consistency",
        "n_questions": n,
        "n_val": len(val_idx),
        "n_test": len(test_idx),
        "best_alpha": best_alpha,
        "best_beta": best_beta,
        "val_auroc": val_auroc,
        "variants": {k: v["auroc"] for k, v in variants.items()},
        "best_single_metric": best_single_name,
        "bootstrap_ci": ci,
        "gate_pass": gate_pass,
    }

    os.makedirs(os.path.dirname(config.OUTPUT_PATH), exist_ok=True)
    with open(config.OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {config.OUTPUT_PATH}")

    return results


def main():
    results = run()
    print("\n" + "="*50)
    print("H-M3 SUMMARY")
    print("="*50)
    print(f"Combined AUROC: {results['variants']['optimal']:.4f}")
    print(f"Best single:    {results['variants'][results['best_single_metric']]:.4f} ({results['best_single_metric']})")
    print(f"Improvement:    {results['bootstrap_ci']['improvement']:.4f}")
    print(f"Gate PASS:      {results['gate_pass']}")
    print("="*50)


if __name__ == "__main__":
    main()
