#!/usr/bin/env python3
"""H-M1: Weight Matrices Encode Behavioral Information

Pipeline: load models -> predictions -> class-wise accuracy -> weight features -> gate comparison
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
import numpy as np
from datetime import datetime

from config import DATA_PATH, CIFAR_ROOT, N_CLASSES, RESULTS_PATH, FIGURES_DIR
from weight_features import build_weight_feature_matrix
from probe import train_test_split_indices, run_gate_comparison
from visualize import plot_gate_metric, plot_per_class_r2_comparison, plot_predicted_vs_actual

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'base'))
from model_zoo_loader import load_model_zoo_final_epoch, get_model_predictions_from_weights
from analysis import compute_class_wise_accuracy, stratified_baseline


def main():
    print("=" * 60)
    print("H-M1: Weight Matrices Encode Behavioral Information")
    print("=" * 60)

    print(f"\n[1/7] Loading model zoo from {DATA_PATH}...")
    model_entries = load_model_zoo_final_epoch(DATA_PATH)
    n_models = len(model_entries)
    print(f"      Loaded {n_models} models")

    print(f"\n[2/7] Running inference on CIFAR-10 test set...")
    predictions = get_model_predictions_from_weights(model_entries, CIFAR_ROOT, device='cuda', batch_size=256)
    print(f"      Got predictions for {len(predictions)} models")

    print(f"\n[3/7] Computing class-wise accuracy...")
    import torch
    import torchvision
    import torchvision.transforms as T
    transform = T.Compose([T.ToTensor(), T.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616))])
    testset = torchvision.datasets.CIFAR10(root=CIFAR_ROOT, train=False, download=False, transform=transform)
    ground_truth = np.array(testset.targets)

    class_wise_acc, overall_acc, model_ids = compute_class_wise_accuracy(predictions, ground_truth, N_CLASSES)
    print(f"      Class-wise accuracy shape: {class_wise_acc.shape}")
    print(f"      Overall accuracy range: [{overall_acc.min():.4f}, {overall_acc.max():.4f}]")

    print(f"\n[4/7] Extracting weight features (5 layers x 5 stats = 25 features)...")
    # Build map with string keys (model_ids from predictions are strings)
    model_id_to_entry = {str(e[0]): e for e in model_entries}
    # model_ids from compute_class_wise_accuracy are strings
    aligned_entries = [model_id_to_entry[mid] for mid in model_ids if mid in model_id_to_entry]
    if len(aligned_entries) != len(model_ids):
        print(f"      WARNING: Alignment mismatch {len(aligned_entries)} vs {len(model_ids)}")
        valid_ids = set(str(e[0]) for e in aligned_entries)
        mask = np.array([mid in valid_ids for mid in model_ids])
        class_wise_acc = class_wise_acc[mask]
        overall_acc = overall_acc[mask]
        model_ids = [mid for mid in model_ids if mid in valid_ids]

    weight_features, feature_ids = build_weight_feature_matrix(aligned_entries)
    print(f"      Weight features shape: {weight_features.shape}")

    print(f"\n[5/7] Computing stratified baseline...")
    baseline_pred, class_difficulty = stratified_baseline(class_wise_acc, overall_acc)
    print(f"      Class difficulty: {class_difficulty}")

    print(f"\n[6/7] Running gate comparison (80/20 split)...")
    train_idx, test_idx = train_test_split_indices(len(model_ids))
    print(f"      Train: {len(train_idx)}, Test: {len(test_idx)}")

    gate_result = run_gate_comparison(
        weight_features, class_wise_acc, overall_acc, baseline_pred, train_idx, test_idx
    )

    print(f"\n[GATE RESULT]")
    print(f"      Baseline Mean R²:  {gate_result['baseline_r2_mean']:.4f}")
    print(f"      Proposed Mean R²:  {gate_result['proposed_r2_mean']:.4f}")
    print(f"      Gate Pass:         {gate_result['gate_pass']}")

    print(f"\n[7/7] Generating visualizations...")
    figure_paths = []
    fig1 = plot_gate_metric(gate_result['baseline_r2_mean'], gate_result['proposed_r2_mean'])
    figure_paths.append(fig1)
    print(f"      Saved: {fig1}")

    fig2 = plot_per_class_r2_comparison(
        gate_result['baseline_r2_per_class'],
        gate_result['proposed_r2_per_class']
    )
    figure_paths.append(fig2)
    print(f"      Saved: {fig2}")

    fig3 = plot_predicted_vs_actual(class_wise_acc[test_idx], gate_result['proposed_pred'], class_idx=0)
    figure_paths.append(fig3)
    print(f"      Saved: {fig3}")

    results = {
        "hypothesis_id": "h-m1",
        "hypothesis_title": "Weight Matrices Encode Behavioral Information",
        "gate_type": "MUST_WORK",
        "timestamp": datetime.now().isoformat(),
        "n_models": n_models,
        "n_train": len(train_idx),
        "n_test": len(test_idx),
        "metrics": {
            "baseline_r2_mean": gate_result['baseline_r2_mean'],
            "proposed_r2_mean": gate_result['proposed_r2_mean'],
            "baseline_r2_per_class": gate_result['baseline_r2_per_class'],
            "proposed_r2_per_class": gate_result['proposed_r2_per_class'],
            "delta_r2": gate_result['proposed_r2_mean'] - gate_result['baseline_r2_mean'],
        },
        "gate_pass": gate_result['gate_pass'],
        "figures": figure_paths,
    }

    with open(RESULTS_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {RESULTS_PATH}")

    print("\n" + "=" * 60)
    if gate_result['gate_pass']:
        print("GATE PASSED: Weight features predict class-wise accuracy")
        print("             better than stratified baseline.")
    else:
        print("GATE FAILED: Weight features do NOT outperform baseline.")
    print("=" * 60)

    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results['gate_pass'] else 1)
