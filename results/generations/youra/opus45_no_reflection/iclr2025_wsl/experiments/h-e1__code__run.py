"""Main experiment script for H-E1 hypothesis validation.

Uses Small CNN Zoo (Zenodo DOI: 10.5281/zenodo.6620868) to validate
existence of behavioral information beyond overall accuracy.
"""

import os
import json
import numpy as np
import torch
import sys

sys.path.insert(0, os.path.dirname(__file__))

from config import (
    SEED, N_CLASSES, RESIDUAL_RATIO_THRESHOLD,
    DATA_PATH, CIFAR_ROOT, FIGURES_DIR, RESULTS_PATH
)
from model_zoo_loader import (
    load_model_zoo_final_epoch,
    get_model_predictions_from_weights
)
from analysis import (
    compute_class_wise_accuracy, stratified_baseline,
    variance_analysis, per_class_variance
)
from visualize import (
    plot_gate_metric, plot_accuracy_heatmap,
    plot_variance_decomposition, plot_per_class_variance,
    plot_model_clustering
)


def build_report(metrics: dict, figure_paths: list, threshold: float, n_models: int) -> dict:
    """Build final report with pass/fail determination."""
    residual_ratio = metrics["residual_ratio"]
    passed = residual_ratio > threshold

    return {
        "hypothesis_id": "h-e1",
        "hypothesis_title": "Behavioral Information Exists Beyond Accuracy",
        "gate_type": "MUST_WORK",
        "pass": passed,
        "threshold": threshold,
        "n_models": n_models,
        "metrics": metrics,
        "figures": figure_paths,
        "interpretation": (
            f"Residual variance ratio = {residual_ratio:.4f} "
            f"({'>' if passed else '<='} {threshold}). "
            f"{'PASS: Significant behavioral variance exists beyond stratified baseline.' if passed else 'FAIL: No significant behavioral variance detected.'}"
        )
    }


def main():
    """Main experiment pipeline."""
    print("=" * 60)
    print("H-E1: Behavioral Information Exists Beyond Accuracy")
    print("=" * 60)

    np.random.seed(SEED)
    torch.manual_seed(SEED)

    device = 'cpu'  # Force CPU to avoid cuDNN issues
    print(f"Device: {device}")

    print("\n[1/7] Loading model zoo final-epoch weights...")
    model_entries = load_model_zoo_final_epoch(DATA_PATH, max_models=None)
    print(f"  Loaded {len(model_entries)} models")

    print("\n[2/7] Running inference to get predictions...")
    predictions = get_model_predictions_from_weights(
        model_entries,
        CIFAR_ROOT,
        device=device,
        batch_size=256
    )

    if len(predictions) == 0:
        raise ValueError("No valid model predictions obtained")

    from torchvision.datasets import CIFAR10
    try:
        test_data = CIFAR10(root=CIFAR_ROOT, train=False, download=False)
    except RuntimeError:
        test_data = CIFAR10(root=CIFAR_ROOT, train=False, download=True)
    ground_truth = np.array(test_data.targets)

    print("\n[4/7] Computing class-wise accuracy...")
    class_wise_acc, overall_acc, model_ids = compute_class_wise_accuracy(
        predictions, ground_truth, N_CLASSES
    )
    print(f"  Models: {len(model_ids)}")
    print(f"  Overall accuracy range: [{overall_acc.min():.3f}, {overall_acc.max():.3f}]")
    print(f"  Mean overall accuracy: {overall_acc.mean():.3f}")

    print("\n[5/7] Computing stratified baseline...")
    baseline_pred, class_difficulty = stratified_baseline(class_wise_acc, overall_acc)
    print(f"  Class difficulty range: [{class_difficulty.min():.3f}, {class_difficulty.max():.3f}]")

    print("\n[6/7] Performing variance analysis...")
    metrics = variance_analysis(class_wise_acc, baseline_pred)
    per_class_var = per_class_variance(class_wise_acc)

    print(f"  Total variance: {metrics['total_variance']:.6f}")
    print(f"  Residual variance: {metrics['residual_variance']:.6f}")
    print(f"  Residual ratio: {metrics['residual_ratio']:.4f}")
    print(f"  R² of baseline: {metrics['r2_baseline']:.4f}")

    metrics["n_models"] = len(model_ids)
    metrics["class_difficulty"] = class_difficulty.tolist()
    metrics["per_class_variance"] = per_class_var.tolist()
    metrics["overall_acc_mean"] = float(overall_acc.mean())
    metrics["overall_acc_std"] = float(overall_acc.std())

    print("\n[7/7] Generating figures...")
    os.makedirs(FIGURES_DIR, exist_ok=True)
    figure_paths = []

    fig_path = plot_gate_metric(
        metrics["residual_ratio"],
        RESIDUAL_RATIO_THRESHOLD,
        os.path.join(FIGURES_DIR, "gate_metric.png")
    )
    figure_paths.append(fig_path)
    print(f"  Saved: {fig_path}")

    fig_path = plot_accuracy_heatmap(
        class_wise_acc,
        os.path.join(FIGURES_DIR, "accuracy_heatmap.png")
    )
    figure_paths.append(fig_path)
    print(f"  Saved: {fig_path}")

    fig_path = plot_variance_decomposition(
        metrics["residual_variance"],
        metrics["total_variance"],
        os.path.join(FIGURES_DIR, "variance_decomposition.png")
    )
    figure_paths.append(fig_path)
    print(f"  Saved: {fig_path}")

    fig_path = plot_per_class_variance(
        per_class_var,
        os.path.join(FIGURES_DIR, "per_class_variance.png")
    )
    figure_paths.append(fig_path)
    print(f"  Saved: {fig_path}")

    fig_path = plot_model_clustering(
        class_wise_acc,
        overall_acc,
        os.path.join(FIGURES_DIR, "model_clustering.png")
    )
    figure_paths.append(fig_path)
    print(f"  Saved: {fig_path}")

    report = build_report(metrics, figure_paths, RESIDUAL_RATIO_THRESHOLD, len(model_ids))

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"RESULT: {'PASS' if report['pass'] else 'FAIL'}")
    print(f"Residual Ratio: {metrics['residual_ratio']:.4f} (threshold: {RESIDUAL_RATIO_THRESHOLD})")
    print(f"Results saved to: {RESULTS_PATH}")
    print(f"{'=' * 60}")

    return report


if __name__ == "__main__":
    main()
