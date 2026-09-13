"""Main orchestrator for H-M3: Within-cluster threshold transfer."""

import os
import sys
import json
import numpy as np
from datetime import datetime

H_M3_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H_M3_PATH)

from config import (
    SEED, BENCHMARKS, WITHIN_CLUSTER_PAIRS, SAMPLE_SIZE,
    OUTPUTS_DIR, FIGURES_DIR, DEGRADATION_THRESHOLD, CI_UPPER_THRESHOLD
)
from data import load_benchmark, split_calib_eval
from transfer import run_all_transfers
from stats import aggregate_results, check_gate
from visualize import plot_degradation_bar, plot_transfer_heatmap

H_M1_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "h-m1", "code")
sys.path.insert(0, H_M1_PATH)

from entropy_pipeline import get_or_compute_benchmark_entropy

from response_generator import ResponseGenerator
from entailment_clusterer import EntailmentClusterer


def main():
    np.random.seed(SEED)
    print("="*60)
    print("H-M3: Within-Cluster Threshold Transfer Experiment")
    print("="*60)

    print("\n[1/5] Loading models...")
    generator = ResponseGenerator()
    clusterer = EntailmentClusterer()

    print("\n[2/5] Loading and processing benchmarks...")
    entropy_cache = {}

    for bench in BENCHMARKS:
        print(f"\n--- {bench} ---")
        items = load_benchmark(bench, SAMPLE_SIZE)
        print(f"Loaded {len(items)} items")

        calib_items, eval_items = split_calib_eval(items)
        print(f"Split: {len(calib_items)} calib, {len(eval_items)} eval")

        calib_e, calib_l, eval_e, eval_l = get_or_compute_benchmark_entropy(
            bench, calib_items, eval_items, generator, clusterer
        )
        entropy_cache[bench] = (calib_e, calib_l, eval_e, eval_l)

        correct_rate = calib_l.mean()
        print(f"Correctness rate: {correct_rate:.2%}")
        print(f"Mean entropy: {calib_e.mean():.3f} (calib), {eval_e.mean():.3f} (eval)")

    print("\n[3/5] Running within-cluster transfers...")
    transfer_results = run_all_transfers(WITHIN_CLUSTER_PAIRS, entropy_cache)

    print("\nTransfer results:")
    for r in transfer_results:
        status = "✓" if r["degradation"] <= DEGRADATION_THRESHOLD else "✗"
        print(f"  {status} {r['source']} → {r['target']}: "
              f"AUROC {r['source_auroc']:.3f} → {r['target_auroc']:.3f} "
              f"(deg={r['degradation']:+.4f})")

    print("\n[4/5] Aggregating results...")
    agg = aggregate_results(transfer_results)
    gate_pass = check_gate(agg)

    print(f"\nAggregate Statistics:")
    print(f"  Mean degradation: {agg['mean_degradation']:.4f} (threshold: {DEGRADATION_THRESHOLD})")
    print(f"  Std degradation:  {agg['std_degradation']:.4f}")
    print(f"  95% CI: [{agg['ci_lower']:.4f}, {agg['ci_upper']:.4f}] (upper threshold: {CI_UPPER_THRESHOLD})")
    print(f"  Min/Max: {agg['min_degradation']:.4f} / {agg['max_degradation']:.4f}")
    print(f"\nGate Result: {'PASS' if gate_pass else 'FAIL'}")

    print("\n[5/5] Generating visualizations...")
    plot_degradation_bar(transfer_results)
    plot_transfer_heatmap(transfer_results, BENCHMARKS)

    results = {
        "hypothesis": "H-M3",
        "statement": "Within-cluster benchmark pairs show successful threshold transfer (AUROC degradation ≤ 0.08)",
        "timestamp": datetime.now().isoformat(),
        "gate": {
            "type": "SHOULD_WORK",
            "pass_condition": f"Mean degradation ≤ {DEGRADATION_THRESHOLD} AND CI upper < {CI_UPPER_THRESHOLD}",
            "result": "PASS" if gate_pass else "FAIL",
            "satisfied": gate_pass
        },
        "aggregate": agg,
        "transfers": transfer_results,
        "benchmarks": BENCHMARKS,
        "sample_size": SAMPLE_SIZE
    }

    results_path = os.path.join(OUTPUTS_DIR, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_path}")

    print("\n" + "="*60)
    print(f"H-M3 EXPERIMENT COMPLETE: {'PASS' if gate_pass else 'FAIL'}")
    print("="*60)

    return results


if __name__ == "__main__":
    main()
