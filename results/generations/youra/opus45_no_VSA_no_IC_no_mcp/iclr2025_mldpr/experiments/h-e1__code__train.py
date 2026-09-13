"""Main pipeline: load data -> compute DNSI -> validate -> visualize."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import CONFIG, TARGET_BENCHMARKS
from data import load_data
from metrics import DNSIComputer, compute_raw_entropy, compute_improvement_rate, compute_time_since_last_sota, validate_dnsi
from evaluate import compute_success_rate, check_gate, summarize

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def generate_figures(results: dict, out_dir: str) -> None:
    """Generate all required visualizations."""
    os.makedirs(out_dir, exist_ok=True)

    dnsi_values = results.get("dnsi", {})
    raw_entropy = results.get("raw_entropy", {})
    summary = results.get("summary", {})

    # 1. Success rate vs threshold (gate metric)
    fig, ax = plt.subplots(figsize=(8, 6))
    rate = summary.get("success_rate", 0)
    threshold = CONFIG["success_rate_threshold"]
    colors = ["green" if rate > threshold else "red", "gray"]
    ax.bar(["Actual Rate", "Threshold"], [rate, threshold], color=colors)
    ax.axhline(y=threshold, color="black", linestyle="--", label=f"Threshold ({threshold})")
    ax.set_ylabel("Success Rate")
    ax.set_title("DNSI Computation Success Rate vs MUST_WORK Threshold")
    ax.set_ylim(0, 1)
    for i, v in enumerate([rate, threshold]):
        ax.text(i, v + 0.02, f"{v:.2%}", ha="center")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "gate_metric.png"), dpi=150)
    plt.close()

    # 2. DNSI distribution histogram
    valid_dnsi = [v for v in dnsi_values.values() if validate_dnsi(v)]
    if valid_dnsi:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(valid_dnsi, bins=10, edgecolor="black", alpha=0.7)
        ax.axvline(x=np.mean(valid_dnsi), color="red", linestyle="--", label=f"Mean: {np.mean(valid_dnsi):.3f}")
        ax.set_xlabel("DNSI Value")
        ax.set_ylabel("Count")
        ax.set_title("DNSI Distribution Across Benchmarks")
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, "dnsi_distribution.png"), dpi=150)
        plt.close()

    # 3. DNSI vs Raw Entropy scatter
    common_keys = set(dnsi_values.keys()) & set(raw_entropy.keys())
    valid_pairs = [(dnsi_values[k], raw_entropy[k]) for k in common_keys
                   if validate_dnsi(dnsi_values[k]) and raw_entropy[k] is not None]
    if valid_pairs:
        fig, ax = plt.subplots(figsize=(8, 6))
        dnsi_vals, entropy_vals = zip(*valid_pairs)
        ax.scatter(entropy_vals, dnsi_vals, s=100, alpha=0.7)
        for k in common_keys:
            if validate_dnsi(dnsi_values[k]) and raw_entropy[k] is not None:
                ax.annotate(k, (raw_entropy[k], dnsi_values[k]), fontsize=8)
        ax.set_xlabel("Raw Entropy")
        ax.set_ylabel("DNSI")
        ax.set_title("DNSI vs Raw Entropy Comparison")
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, "dnsi_vs_entropy.png"), dpi=150)
        plt.close()

    # 4. Benchmark coverage (SOTA entry counts)
    benchmark_info = results.get("benchmark_info", {})
    if benchmark_info:
        fig, ax = plt.subplots(figsize=(10, 6))
        names = list(benchmark_info.keys())
        counts = [benchmark_info[n].get("entry_count", 0) for n in names]
        colors = ["green" if c >= CONFIG["min_sota_entries"] else "red" for c in counts]
        bars = ax.bar(names, counts, color=colors)
        ax.axhline(y=CONFIG["min_sota_entries"], color="black", linestyle="--",
                   label=f"Min entries ({CONFIG['min_sota_entries']})")
        ax.set_ylabel("SOTA Entry Count")
        ax.set_title("Benchmark Coverage: SOTA Entry Counts")
        ax.legend()
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, "benchmark_coverage.png"), dpi=150)
        plt.close()

    print(f"[FIGURES] Saved to {out_dir}")


def run_pipeline() -> dict:
    """Main experiment pipeline."""
    print("=" * 60)
    print("[PIPELINE] Starting DNSI Computation Experiment (h-e1)")
    print("=" * 60)

    # Load data
    print("\n[STEP 1] Loading PapersWithCode data...")
    benchmark_data = load_data()

    if not benchmark_data:
        print("[PIPELINE] FAILED: No benchmark data loaded")
        return {"success": False, "error": "No benchmark data"}

    # Compute DNSI for each benchmark
    print("\n[STEP 2] Computing DNSI for matched benchmarks...")
    computer = DNSIComputer(window_months=CONFIG["window_months"])

    dnsi_results = {}
    raw_entropy_results = {}
    improvement_rate_results = {}
    tsls_results = {}

    for name, info in benchmark_data.items():
        print(f"\n[DNSI] Computing for {name}...")
        history = info["history"]
        difficulty = info["difficulty_proxy"]

        dnsi = computer.compute_dnsi(history, difficulty)
        dnsi_results[name] = dnsi

        raw_ent = compute_raw_entropy(history)
        raw_entropy_results[name] = raw_ent

        ir = compute_improvement_rate(history)
        improvement_rate_results[name] = ir

        tsls = compute_time_since_last_sota(history)
        tsls_results[name] = tsls

        if validate_dnsi(dnsi):
            print(f"[DNSI] SUCCESS: {name} = {dnsi:.4f}")
        else:
            reason = "insufficient data" if difficulty is None else f"computation returned None (difficulty={difficulty}, entries={len(history)})"
            print(f"[DNSI] FAILED: {name} - {reason}")

    # Evaluate results
    print("\n[STEP 3] Evaluating results...")
    results = {
        "dnsi": dnsi_results,
        "raw_entropy": raw_entropy_results,
        "improvement_rate": improvement_rate_results,
        "time_since_last_sota": tsls_results,
        "benchmark_info": benchmark_data,
    }

    results["summary"] = summarize(results)
    summary = results["summary"]

    print(f"\n[RESULTS] Summary:")
    print(f"  - Total benchmarks attempted: {summary['total_benchmarks']}")
    print(f"  - Valid DNSI computed: {summary['valid_count']}")
    print(f"  - Success rate: {summary['success_rate']:.2%}")
    print(f"  - Threshold: {summary['threshold']:.2%}")
    print(f"  - GATE PASSED: {summary['gate_passed']}")

    if summary.get("dnsi_mean"):
        print(f"  - DNSI mean: {summary['dnsi_mean']:.4f}")
        print(f"  - DNSI std: {summary['dnsi_std']:.4f}")
        print(f"  - DNSI range: [{summary['dnsi_min']:.4f}, {summary['dnsi_max']:.4f}]")

    # Generate figures
    print("\n[STEP 4] Generating figures...")
    figures_dir = os.path.join(os.path.dirname(__file__), "..", CONFIG["figures_dir"])
    generate_figures(results, figures_dir)

    # Final status
    print("\n" + "=" * 60)
    if summary["gate_passed"]:
        print("[GATE] MUST_WORK: PASSED")
        print(f"  DNSI computed successfully for {summary['valid_count']}/{summary['total_benchmarks']} benchmarks")
        print(f"  Success rate {summary['success_rate']:.2%} > {summary['threshold']:.2%} threshold")
    else:
        print("[GATE] MUST_WORK: FAILED")
        print(f"  Success rate {summary['success_rate']:.2%} <= {summary['threshold']:.2%} threshold")
    print("=" * 60)

    return results


if __name__ == "__main__":
    results = run_pipeline()
    print("\nEXPERIMENT COMPLETE")
