#!/usr/bin/env python3
"""Main entrypoint: H-M2 Deduplication Stringency Experiment."""
import os
import sys
import json
import argparse
from config import ScaledExperimentConfig, DEDUP_LEVELS
from run_sweep import run_full_sweep
from analyze import load_sweep_results, aggregate_results, check_non_monotonicity, generate_analysis_summary, print_analysis
from figures import generate_all_figures

def main():
    parser = argparse.ArgumentParser(description="H-M2: Deduplication Stringency Dose-Response Experiment")
    parser.add_argument("--base-dir", default=".", help="Base directory for outputs")
    parser.add_argument("--analysis-only", action="store_true", help="Only run analysis on existing results")
    parser.add_argument("--total-tokens", type=int, default=50_000_000, help="Tokens per config (default: 50M)")
    parser.add_argument("--num-samples", type=int, default=50000, help="Number of documents to sample")
    parser.add_argument("--eval-limit", type=int, default=500, help="Eval samples per benchmark")
    args = parser.parse_args()

    base_dir = args.base_dir
    results_path = os.path.join(base_dir, "results", "sweep_results.json")
    figures_dir = os.path.join(base_dir, "figures")

    if args.analysis_only:
        if not os.path.exists(results_path):
            print(f"ERROR: Results file not found: {results_path}")
            sys.exit(1)
        results = load_sweep_results(results_path)
    else:
        cfg = ScaledExperimentConfig(
            total_tokens=args.total_tokens,
            num_samples=args.num_samples,
            eval_limit=args.eval_limit
        )

        print("="*60)
        print("H-M2: Deduplication Stringency Dose-Response Experiment")
        print("="*60)
        print(f"Config: {cfg.total_tokens/1e6:.0f}M tokens, {cfg.num_samples} docs, {len(cfg.seeds)} seeds")
        print(f"Dedup levels: {[l.level for l in DEDUP_LEVELS]}")
        print("="*60)

        results = run_full_sweep(cfg, base_dir)

    # Analysis
    print("\n" + "="*60)
    print("Running analysis...")
    print("="*60)

    analysis = generate_analysis_summary(results)
    print_analysis(analysis)

    # Save analysis
    analysis_path = os.path.join(base_dir, "results", "analysis.json")
    # Convert numpy types for JSON
    def convert_numpy(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert_numpy(v) for v in obj]
        return obj

    import numpy as np
    with open(analysis_path, "w") as f:
        json.dump(convert_numpy(analysis), f, indent=2)
    print(f"\nSaved analysis to {analysis_path}")

    # Figures
    print("\n" + "="*60)
    print("Generating figures...")
    print("="*60)

    dedup_stats_path = os.path.join(base_dir, "results", "dedup_stats.json")
    dedup_stats = {}
    if os.path.exists(dedup_stats_path):
        with open(dedup_stats_path) as f:
            dedup_stats = json.load(f)

    generate_all_figures(results, analysis["aggregated"], dedup_stats, figures_dir)

    # Final verdict
    print("\n" + "="*60)
    print("EXPERIMENT VERDICT")
    print("="*60)

    nm = analysis["non_monotonicity"]
    if analysis["hypothesis_supported"]:
        print("HYPOTHESIS SUPPORTED: Non-monotonic relationship confirmed")
        print(f"  Best intermediate ({nm['best_intermediate_level']}): {nm['best_intermediate_score']:.4f}")
        print(f"  Strictest ({nm['strictest_level']}): {nm['strictest_score']:.4f}")
        print(f"  Delta: {nm['delta']:.4f} ({nm['delta']*100:.2f}%)")
        verdict = "SUPPORTED"
    else:
        print("HYPOTHESIS NOT SUPPORTED: Monotonic or insufficient effect")
        print(f"  Delta: {nm.get('delta', 0):.4f}")
        verdict = "NOT_SUPPORTED"

    # Write final verdict
    verdict_path = os.path.join(base_dir, "results", "verdict.json")
    with open(verdict_path, "w") as f:
        json.dump({
            "hypothesis_id": "h-m2",
            "gate": "SHOULD_WORK",
            "verdict": verdict,
            "supported": analysis["hypothesis_supported"],
            "non_monotonic": nm.get("non_monotonic", False),
            "best_intermediate_level": nm.get("best_intermediate_level"),
            "best_score": nm.get("best_intermediate_score"),
            "strictest_score": nm.get("strictest_score"),
            "delta": nm.get("delta", 0)
        }, f, indent=2)

    print(f"\nSaved verdict to {verdict_path}")
    print("\nEXPERIMENT COMPLETE")

if __name__ == "__main__":
    main()
