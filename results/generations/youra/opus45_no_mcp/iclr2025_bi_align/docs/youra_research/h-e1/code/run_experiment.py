#!/usr/bin/env python3
"""Main experiment runner for H-E1: Calibration Inversion Clustering."""

import json
import os
import sys
import torch
from datetime import datetime

from config import CONFIG
from data import load_all_tasks
from inference import load_model, run_inference_on_tasks
from calibration import build_calibration_vectors, compute_inversion_score, is_calibration_inverted
from clustering import evaluate_k_range, select_best_k, cluster_and_evaluate, fit_kmeans
from visualize import (
    plot_gate_metric,
    plot_calibration_histogram,
    plot_cluster_scatter,
    plot_cluster_profiles,
    plot_cross_model_agreement
)


def main():
    print("=" * 60)
    print("H-E1: Calibration Inversion Clustering Experiment")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Device: {CONFIG.device}")
    print(f"Models: {CONFIG.models}")
    print()

    os.makedirs(CONFIG.output_dir, exist_ok=True)
    os.makedirs(CONFIG.figures_dir, exist_ok=True)

    print("Step 1: Loading tasks...")
    tasks = load_all_tasks()
    task_ids = [t["task_id"] for t in tasks]
    print(f"Loaded {len(tasks)} tasks\n")

    print("Step 2: Running inference on all models...")
    results_by_model = {}

    for model_id in CONFIG.models:
        print(f"\n--- {model_id} ---")
        model, tokenizer = load_model(model_id)
        results = run_inference_on_tasks(model, tokenizer, tasks, CONFIG.batch_size)
        results_by_model[model_id] = results

        del model
        torch.cuda.empty_cache()
        print(f"Completed inference for {model_id}")

    print("\nStep 3: Building calibration vectors...")
    primary_model = CONFIG.models[CONFIG.primary_model_index]
    X = build_calibration_vectors(results_by_model[primary_model])
    print(f"Calibration vector shape: {X.shape}")

    print("\nStep 4: Evaluating clustering (k-sweep)...")
    silhouette_by_k = evaluate_k_range(X, CONFIG.k_range)
    best_k = select_best_k(silhouette_by_k)
    print(f"Best k: {best_k}")

    print("\nStep 5: Final clustering and gate check...")
    cluster_result = cluster_and_evaluate(X, best_k)
    silhouette_score = cluster_result["silhouette_score"]
    gate_passed = cluster_result["gate_passed"]

    print(f"\n{'='*60}")
    print(f"GATE CHECK: silhouette={silhouette_score:.4f} > {CONFIG.silhouette_gate} ?")
    print(f"RESULT: {'PASS' if gate_passed else 'FAIL'}")
    print(f"{'='*60}\n")

    print("Step 6: Cross-model clustering...")
    labels_by_model = {primary_model: cluster_result["cluster_labels"]}

    for model_id in CONFIG.models[1:]:
        Xi = build_calibration_vectors(results_by_model[model_id])
        kmeans = fit_kmeans(Xi, best_k, CONFIG.seed)
        labels_by_model[model_id] = kmeans.labels_

    print("Step 7: Generating figures...")
    plot_gate_metric(
        silhouette_score, CONFIG.silhouette_gate,
        os.path.join(CONFIG.figures_dir, "gate_metric.png")
    )
    plot_calibration_histogram(X, os.path.join(CONFIG.figures_dir, "calibration_histogram.png"))
    plot_cluster_scatter(X, cluster_result["cluster_labels"],
                         os.path.join(CONFIG.figures_dir, "cluster_scatter.png"))
    plot_cluster_profiles(X, cluster_result["cluster_labels"],
                          os.path.join(CONFIG.figures_dir, "cluster_profiles.png"))
    plot_cross_model_agreement(labels_by_model,
                               os.path.join(CONFIG.figures_dir, "cross_model_agreement.png"))
    print("Figures saved to:", CONFIG.figures_dir)

    print("\nStep 8: Building results...")
    per_task_results = []
    for i, task_id in enumerate(task_ids):
        task_result = results_by_model[primary_model][task_id]
        inversion = compute_inversion_score(
            task_result["correct_logprob_norm"],
            task_result["max_wrong_logprob_norm"]
        )
        per_task_results.append({
            "task_id": task_id,
            "correct_logprob_norm": task_result["correct_logprob_norm"],
            "max_wrong_logprob_norm": task_result["max_wrong_logprob_norm"],
            "inversion_score": inversion,
            "is_inverted": is_calibration_inverted(inversion),
            "cluster_label": int(cluster_result["cluster_labels"][i])
        })

    aggregate_results = {
        "silhouette_score": silhouette_score,
        "gate_passed": gate_passed,
        "best_k": best_k,
        "silhouette_by_k": silhouette_by_k,
        "cluster_centers": cluster_result["cluster_centers"].tolist(),
        "n_tasks_per_cluster": [
            int(sum(cluster_result["cluster_labels"] == c))
            for c in range(best_k)
        ],
        "n_inverted_tasks": sum(1 for r in per_task_results if r["is_inverted"]),
        "total_tasks": len(tasks),
        "models_evaluated": CONFIG.models,
        "timestamp": datetime.now().isoformat()
    }

    output = {
        "aggregate": aggregate_results,
        "per_task": per_task_results
    }

    with open(CONFIG.results_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Results saved to: {CONFIG.results_path}")

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print(f"End time: {datetime.now().isoformat()}")
    print(f"Gate result: {'PASS' if gate_passed else 'FAIL'}")
    print(f"Silhouette score: {silhouette_score:.4f}")
    print("=" * 60)

    return 0 if gate_passed else 1


if __name__ == "__main__":
    sys.exit(main())
