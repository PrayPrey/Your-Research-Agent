"""H-E1: Main orchestration script."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import OUTPUT_DIR, FIGURES_DIR
from extract import build_dataset
from cluster import run_kmeans, evaluate
from visualize import plot_cluster_task_bar, plot_tsne


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(base_dir, "results")
    figures_dir = os.path.join(base_dir, "figures")
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    print("=" * 60)
    print("H-E1: Task-Correlated Structure in BERT Hidden States")
    print("=" * 60)

    print("\n[1/4] Building dataset...")
    embeddings, task_labels, task_names = build_dataset()

    print("\n[2/4] Running KMeans clustering...")
    cluster_ids = run_kmeans(embeddings)

    print("\n[3/4] Evaluating clusters...")
    metrics = evaluate(cluster_ids, task_labels)

    print("\nMetrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")

    print("\n[4/4] Generating visualizations...")
    plot_cluster_task_bar(
        cluster_ids, task_labels, task_names,
        os.path.join(figures_dir, "cluster_composition.png")
    )
    plot_tsne(
        embeddings, task_labels, task_names,
        os.path.join(figures_dir, "tsne.png")
    )

    metrics_path = os.path.join(results_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nSaved: {metrics_path}")

    print("\n" + "=" * 60)
    random_baseline = 1.0 / len(task_names)
    gate_passed = metrics["purity"] > random_baseline

    print(f"GATE CHECK: purity ({metrics['purity']:.4f}) > random baseline ({random_baseline:.4f})")
    print(f"GATE RESULT: {'PASS' if gate_passed else 'FAIL'}")
    print("=" * 60)

    return metrics, gate_passed


if __name__ == "__main__":
    metrics, gate_passed = main()
    sys.exit(0 if gate_passed else 1)
