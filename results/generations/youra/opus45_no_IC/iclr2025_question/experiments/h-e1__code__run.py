#!/usr/bin/env python3
"""Pipeline orchestration for H-E1 Benchmark Clustering Experiment.

Gate: silhouette > 0.5 (MUST_WORK)
"""

import os
import sys
import json
import random
import numpy as np
import torch

from config import SEED, BENCHMARKS, FIGURES_DIR, RESULTS_PATH, SILHOUETTE_THRESHOLD
from data import load_all_benchmarks
from generate import ResponseGenerator
from entropy import SemanticEntropyComputer
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
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def main():
    print("=" * 60)
    print("H-E1: Benchmark Clustering Experiment")
    print("=" * 60)

    set_seed(SEED)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    print("\n[1/5] Loading benchmarks...")
    benchmarks = load_all_benchmarks()
    total_queries = sum(len(v) for v in benchmarks.values())
    print(f"Loaded {total_queries} queries across {len(benchmarks)} benchmarks")

    print("\n[2/5] Generating responses...")
    generator = ResponseGenerator()
    all_responses = {}
    for name, queries in benchmarks.items():
        print(f"  {name}...")
        all_responses[name] = generator.generate_for_benchmark(queries)

    print("\n[3/5] Computing semantic entropy...")
    entropy_computer = SemanticEntropyComputer()
    entropies = {}
    for name, responses in all_responses.items():
        print(f"  {name}...")
        entropies[name] = entropy_computer.compute_for_benchmark(responses)

    print("\n[4/5] Clustering benchmarks...")
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

    print("\n[5/5] Generating visualizations...")
    plot_js_heatmap(js_matrix, BENCHMARKS)
    plot_dendrogram(js_matrix, BENCHMARKS)
    plot_entropy_violin(entropies)
    plot_silhouette(js_matrix, labels)
    plot_gate_metric(silhouette)

    gate_passed = silhouette > SILHOUETTE_THRESHOLD
    gate_result = "PASS" if gate_passed else "FAIL"

    results = {
        "hypothesis_id": "h-e1",
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
