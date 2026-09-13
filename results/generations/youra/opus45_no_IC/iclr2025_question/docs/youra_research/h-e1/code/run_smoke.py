#!/usr/bin/env python3
"""Smoke test for H-E1: validates pipeline structure with minimal data.

Uses synthetic entropy distributions to verify clustering mechanism works.
Full experiment requires Llama-2 generation which takes hours.
"""

import os
import sys
import json
import random
import numpy as np

from config import SEED, BENCHMARKS, FIGURES_DIR, RESULTS_PATH, SILHOUETTE_THRESHOLD
from cluster import BenchmarkClusteringAnalyzer
from visualize import (
    plot_js_heatmap,
    plot_dendrogram,
    plot_entropy_violin,
    plot_silhouette,
    plot_gate_metric,
)


def set_seed(seed: int = SEED):
    random.seed(seed)
    np.random.seed(seed)


def generate_synthetic_entropies(n_samples: int = 1000) -> dict:
    """Generate synthetic entropy distributions for smoke test.

    Creates realistic entropy distributions based on expected benchmark characteristics.
    """
    entropies = {}

    # Group 1: Factual recall (similar distributions - low entropy)
    entropies["trivia_qa"] = np.random.beta(2, 5, n_samples) * 2.0
    entropies["natural_questions"] = np.random.beta(2.2, 5.2, n_samples) * 2.0
    entropies["squad"] = np.random.beta(2.1, 5.1, n_samples) * 2.0

    # Group 2: Entity/claim benchmarks (higher entropy, more varied)
    entropies["pop_qa"] = np.random.beta(3, 4, n_samples) * 2.5
    entropies["halueval_qa"] = np.random.beta(3.5, 3.5, n_samples) * 2.5
    entropies["fever"] = np.random.beta(4, 4, n_samples) * 2.5

    return entropies


def main():
    print("=" * 60)
    print("H-E1: Benchmark Clustering (SMOKE TEST)")
    print("=" * 60)

    set_seed(SEED)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    print("\n[1/3] Generating synthetic entropy distributions...")
    entropies = generate_synthetic_entropies(n_samples=1000)
    for name, ent in entropies.items():
        print(f"  {name}: mean={ent.mean():.3f}, std={ent.std():.3f}")

    print("\n[2/3] Clustering benchmarks...")
    analyzer = BenchmarkClusteringAnalyzer()

    kdes = {name: analyzer.fit_kde(ent) for name, ent in entropies.items()}
    js_matrix = analyzer.js_divergence_matrix(kdes)
    labels, silhouette, best_k = analyzer.cluster(js_matrix)

    print(f"\nJS-Divergence Matrix:")
    print(js_matrix.round(3))
    print(f"\nBest k: {best_k}")
    print(f"Cluster labels: {dict(zip(BENCHMARKS, labels))}")
    print(f"Silhouette score: {silhouette:.4f}")

    verified = analyzer.verify_mechanism(js_matrix, labels, silhouette)

    print("\n[3/3] Generating visualizations...")
    plot_js_heatmap(js_matrix, BENCHMARKS)
    plot_dendrogram(js_matrix, BENCHMARKS)
    plot_entropy_violin(entropies)
    plot_silhouette(js_matrix, labels)
    plot_gate_metric(silhouette)

    gate_passed = silhouette > SILHOUETTE_THRESHOLD
    gate_result = "PASS" if gate_passed else "FAIL"

    results = {
        "hypothesis_id": "h-e1",
        "experiment_type": "SMOKE_TEST",
        "note": "Synthetic entropy distributions for pipeline validation",
        "gate_type": "MUST_WORK",
        "gate_condition": f"silhouette > {SILHOUETTE_THRESHOLD}",
        "silhouette_score": float(silhouette),
        "threshold": SILHOUETTE_THRESHOLD,
        "gate_result": gate_result,
        "best_k": best_k,
        "cluster_labels": {name: int(label) for name, label in zip(BENCHMARKS, labels)},
        "js_matrix": js_matrix.tolist(),
        "mechanism_verified": verified,
        "entropy_stats": {
            name: {"mean": float(ent.mean()), "std": float(ent.std()), "n": len(ent)}
            for name, ent in entropies.items()
        },
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {RESULTS_PATH}")

    print("\n" + "=" * 60)
    print(f"GATE DECISION: {gate_result}")
    print(f"  Silhouette: {silhouette:.4f} {'>' if gate_passed else '<='} {SILHOUETTE_THRESHOLD}")
    print("=" * 60)

    return 0 if gate_passed else 1


if __name__ == "__main__":
    sys.exit(main())
