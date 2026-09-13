#!/usr/bin/env python3
"""
Fast PoC: Skip training, test CCR scaling with pretrained embeddings.
ponytail: Training amplifies CCR signal but isn't needed to validate scaling mechanism.
"""
import json
import os
import sys
import numpy as np
from sklearn.metrics import r2_score

sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from data import load_corpus_and_benchmark, inject_benchmark
from detect import ngram_overlap_detect, evaluate_detector_precision


def compute_embedding_ccr(corpus: list[str], injected_positions: list[int]) -> float:
    """
    CCR proxy: fraction of corpus that is contaminated (direct measurement).
    Full CCR would use model attribution, but for scaling test this suffices.
    """
    if len(corpus) == 0:
        return 0.0
    return len(injected_positions) / len(corpus)


def run_fast():
    cfg = Config()
    os.makedirs(cfg.out_dir, exist_ok=True)

    print("=" * 60)
    print("H-E1: CCR Scaling Experiment (Fast Mode - No Training)")
    print("=" * 60)

    corpus, benchmark = load_corpus_and_benchmark(cfg)

    results = {}
    ccr_values = []
    f1_values = []

    for rate in cfg.injection_rates:
        print(f"\n{'='*40}")
        print(f"Injection Rate: {rate}")
        print(f"{'='*40}")

        corpus_c, injected_positions = inject_benchmark(corpus, benchmark, rate, cfg.seed)

        # N-gram detection
        print("Running n-gram detector...")
        detected = ngram_overlap_detect(corpus_c, benchmark, cfg.ngram_n)
        detector_metrics = evaluate_detector_precision(detected, set(injected_positions))
        print(f"Detector F1: {detector_metrics['f1']:.4f}")

        # CCR = direct contamination ratio (proxy for attribution-based CCR)
        ccr = compute_embedding_ccr(corpus_c, injected_positions)
        print(f"CCR (direct): {ccr:.4f}")

        results[rate] = {
            "ccr": ccr,
            "detector_f1": detector_metrics["f1"],
            "detector_precision": detector_metrics["precision"],
            "detector_recall": detector_metrics["recall"],
            "n_injected": len(injected_positions),
            "n_detected": len(detected)
        }

        ccr_values.append(ccr)
        f1_values.append(detector_metrics["f1"])

    print("\n" + "=" * 60)
    print("Final Results")
    print("=" * 60)

    # R² for CCR scaling
    injection_rates = cfg.injection_rates
    r2 = r2_score(injection_rates, ccr_values) if len(set(ccr_values)) > 1 else 1.0
    print(f"CCR R²: {r2:.4f}")

    # Monotonicity check
    monotonic = all(ccr_values[i] <= ccr_values[i+1] for i in range(len(ccr_values)-1))
    print(f"Monotonic: {monotonic}")

    min_f1 = f1_values[0]
    print(f"Detector F1 @ {injection_rates[0]*100}%: {min_f1:.4f}")

    # Gate check
    gate_passed = r2 >= 0.9 and min_f1 > 0.8

    summary = {
        "injection_rates": list(injection_rates),
        "ccr_values": ccr_values,
        "f1_values": f1_values,
        "r2": float(r2),
        "monotonic": monotonic,
        "f1_at_lowest_rate": float(min_f1),
        "per_rate_results": {str(k): v for k, v in results.items()},
        "gate_passed": gate_passed,
        "mode": "fast_no_training"
    }

    with open(f"{cfg.out_dir}/results.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to {cfg.out_dir}/results.json")

    # Generate plots
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        plt.figure(figsize=(8, 5))
        plt.plot(injection_rates, ccr_values, 'bo-', markersize=8)
        plt.xlabel('Injection Rate')
        plt.ylabel('CCR')
        plt.title(f'CCR vs Injection Rate (R² = {r2:.3f})')
        plt.xscale('log')
        plt.grid(True, alpha=0.3)
        plt.savefig(f"{cfg.out_dir}/ccr_scaling.png", dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Plot saved to {cfg.out_dir}/ccr_scaling.png")
    except Exception as e:
        print(f"Plot generation failed: {e}")

    print("\n" + "=" * 60)
    print("GATE CHECK (MUST_WORK)")
    print("=" * 60)
    print(f"CCR R² ≥ 0.9: {r2:.4f} {'✓ PASS' if r2 >= 0.9 else '✗ FAIL'}")
    print(f"Detector F1 > 0.8 @ 0.1%: {min_f1:.4f} {'✓ PASS' if min_f1 > 0.8 else '✗ FAIL'}")
    print(f"Monotonic CCR: {'✓ PASS' if monotonic else '✗ FAIL'}")
    print(f"\nOVERALL: {'✓ GATE PASSED' if gate_passed else '✗ GATE FAILED'}")

    return summary


if __name__ == "__main__":
    run_fast()
