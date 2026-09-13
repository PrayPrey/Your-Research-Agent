#!/usr/bin/env python3
"""H-E1 Experiment: Heavy-Tailed Exponent Computation for ViT Models."""
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG
from collect_models import fetch_vit_model_ids
from measure import run_measurement
from analyze import aggregate_statistics
from visualize import generate_all_figures


def main():
    print("=" * 60)
    print("H-E1: Heavy-Tailed Exponent Computation for ViT Models")
    print("=" * 60)
    start_time = time.time()

    print(f"\n[1/4] Fetching {CONFIG.n_models_fetch} ViT model IDs...")
    model_ids = fetch_vit_model_ids(CONFIG.n_models_fetch)
    print(f"Fetched {len(model_ids)} models")

    print(f"\n[2/4] Computing alpha for up to {CONFIG.n_models_target} models...")
    results = run_measurement(model_ids[:CONFIG.n_models_target + 50])
    print(f"Successfully measured {len(results)} models")

    if len(results) < CONFIG.n_models_target:
        print(f"WARNING: Only {len(results)} models (target: {CONFIG.n_models_target})")

    print("\n[3/4] Computing aggregate statistics...")
    aggregate = aggregate_statistics(results)
    print(f"  Mean α: {aggregate['mean_alpha']:.4f}")
    print(f"  Median α: {aggregate['median_alpha']:.4f}")
    print(f"  σ(α): {aggregate['sigma_alpha']:.4f}")
    print(f"  Range: [{aggregate['range'][0]:.2f}, {aggregate['range'][1]:.2f}]")

    failed_models = [mid for mid in model_ids[:len(results) + 50]
                     if mid not in [r["model_id"] for r in results]]

    output = {
        "per_model": results,
        "aggregate": aggregate,
        "failed_models": failed_models[:50],
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "n_models_target": CONFIG.n_models_target,
            "sigma_gate_threshold": CONFIG.sigma_gate_threshold,
            "runtime_seconds": time.time() - start_time
        }
    }

    results_path = os.path.join(os.path.dirname(__file__), CONFIG.results_path)
    with open(results_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved results to {results_path}")

    print("\n[4/4] Generating figures...")
    figures_dir = os.path.join(os.path.dirname(__file__), "..", "figures")
    generate_all_figures(results, aggregate, figures_dir)

    print("\n" + "=" * 60)
    print("GATE RESULT")
    print("=" * 60)
    print(f"σ(α) = {aggregate['sigma_alpha']:.4f}")
    print(f"Threshold = {CONFIG.sigma_gate_threshold}")
    if aggregate["gate_passed"]:
        print("GATE: PASS ✓")
    else:
        print("GATE: FAIL ✗")
    print(f"\nTotal runtime: {time.time() - start_time:.1f}s")

    return aggregate["gate_passed"]


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
