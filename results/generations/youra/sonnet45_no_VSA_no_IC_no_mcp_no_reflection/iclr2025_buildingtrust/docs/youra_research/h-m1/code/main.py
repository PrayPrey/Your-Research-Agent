#!/usr/bin/env python3
import json
import numpy as np
from pathlib import Path
from config import ExperimentConfig
from data_loader import H_E1_DataLoader
from clustering import WardClusterer
from metrics import find_optimal_k
from bootstrap import BootstrapClusterValidator
from visualizations import plot_dendrogram, plot_silhouette_vs_k, plot_consistency_matrix


def evaluate_gate(silhouette_scores, mean_consistency, optimal_k):
    max_silhouette = max(silhouette_scores.values())
    if (max_silhouette > 0.5
        and mean_consistency >= 80.0
        and 2 <= optimal_k <= 5):
        return "PASS"
    else:
        return "FAIL"


def main():
    config = ExperimentConfig()
    base_dir = Path(__file__).parent.parent

    loader = H_E1_DataLoader(base_dir / config.data.h_e1_results_path)

    print("1. Loading h-e1 correlation matrix...")
    corr_matrix, benchmark_names = loader.load_correlation_matrix()
    dist_matrix = loader.compute_distance_matrix(corr_matrix)

    if config.data.cache_distance_matrix:
        cache_path = base_dir / config.data.distance_matrix_path
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(cache_path, dist_matrix)

    print("2. Ward linkage clustering...")
    clusterer = WardClusterer(dist_matrix)
    linkage_matrix = clusterer.fit(method=config.clustering.linkage_method)
    cophenetic_corr = clusterer.compute_cophenetic()
    print(f"   Cophenetic correlation: {cophenetic_corr:.3f}")

    print("3. Silhouette evaluation...")
    optimal_k, silhouette_scores = find_optimal_k(
        dist_matrix,
        linkage_matrix,
        config.clustering.k_range
    )
    print(f"   Optimal k: {optimal_k}")
    for k, score in silhouette_scores.items():
        print(f"   k={k}: silhouette={score:.3f}")

    cluster_labels = {k: clusterer.get_clusters(k) for k in config.clustering.k_range}

    print("4. Bootstrap validation (1000 iterations)...")
    benchmark_data = loader.load_benchmark_scores()
    validator = BootstrapClusterValidator(
        benchmark_data,
        optimal_k,
        n_iterations=config.bootstrap.n_iterations,
        random_seed=config.bootstrap.random_seed
    )
    consistency_matrix = validator.run_bootstrap()
    _, mean_consistency = validator.compute_consistency_matrix(consistency_matrix)
    print(f"   Mean bootstrap consistency: {mean_consistency:.1f}%")

    print("5. Gate decision...")
    gate_result = evaluate_gate(silhouette_scores, mean_consistency, optimal_k)
    print(f"   Gate: {gate_result}")

    results_dir = base_dir / config.results_dir
    results_dir.mkdir(parents=True, exist_ok=True)

    clustering_results = {
        "linkage_matrix": linkage_matrix.tolist(),
        "cluster_assignments": {f"k={k}": labels.tolist() for k, labels in cluster_labels.items()},
        "silhouette_scores": silhouette_scores,
        "optimal_k": optimal_k,
        "cophenetic_correlation": cophenetic_corr
    }
    with open(results_dir / "clustering_results.json", "w") as f:
        json.dump(clustering_results, f, indent=2)

    bootstrap_results = {
        "consistency_matrix": consistency_matrix.tolist(),
        "mean_consistency": mean_consistency,
        "gate_threshold": config.metrics.consistency_threshold,
        "gate_pass": bool(mean_consistency >= config.metrics.consistency_threshold),
        "n_iterations": config.bootstrap.n_iterations,
        "random_seed": config.bootstrap.random_seed
    }
    with open(results_dir / "bootstrap_consistency.json", "w") as f:
        json.dump(bootstrap_results, f, indent=2)

    gate_decision = {
        "gate_result": gate_result,
        "optimal_k": int(optimal_k),
        "max_silhouette": float(max(silhouette_scores.values())),
        "mean_consistency": float(mean_consistency),
        "cophenetic_correlation": float(cophenetic_corr),
        "criteria": {
            "silhouette > 0.5": bool(max(silhouette_scores.values()) > 0.5),
            "consistency >= 80%": bool(mean_consistency >= 80.0),
            "2 <= k <= 5": bool(2 <= optimal_k <= 5)
        }
    }
    with open(results_dir / "gate_decision.json", "w") as f:
        json.dump(gate_decision, f, indent=2)

    print("6. Generating visualizations...")
    figures_dir = base_dir / config.viz.figures_dir
    figures_dir.mkdir(parents=True, exist_ok=True)

    plot_dendrogram(linkage_matrix, config.viz.dendrogram_labels, optimal_k, figures_dir / "dendrogram.png")
    plot_silhouette_vs_k(silhouette_scores, figures_dir / "silhouette_vs_k.png")
    plot_consistency_matrix(consistency_matrix, config.viz.dendrogram_labels, figures_dir / "consistency_matrix.png")

    print(f"\nCompleted. Gate: {gate_result}")
    print(f"Results saved to {results_dir}")
    print(f"Figures saved to {figures_dir}")


if __name__ == "__main__":
    main()
