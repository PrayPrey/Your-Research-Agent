#!/usr/bin/env python3
"""End-to-end experiment runner for H-E1 dose-response curation study."""

import os
import sys
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SWEEP_CONFIGS
from sweep import run_sweep
from analysis import analyze, run_analysis
from analysis.figures import generate_figures


def main():
    parser = argparse.ArgumentParser(description="H-E1 Dose-Response Curation Experiment")
    parser.add_argument("--base-dir", default=".", help="Base directory for outputs")
    parser.add_argument("--skip-training", action="store_true", help="Skip training, run analysis only")
    parser.add_argument("--smoke-test", action="store_true", help="Run quick smoke test with reduced params")
    args = parser.parse_args()

    base_dir = os.path.abspath(args.base_dir)
    results_dir = os.path.join(base_dir, "results")
    fig_dir = os.path.join(base_dir, "figures")
    all_configs_path = os.path.join(results_dir, "all_configs.json")

    print("=" * 60)
    print("H-E1 Dose-Response Curation Experiment")
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Base directory: {base_dir}")
    print("=" * 60)

    if not args.skip_training:
        print("\n[Phase 1] Running 15-config sweep...")
        results = run_sweep(SWEEP_CONFIGS, base_dir)
        print(f"\nCompleted {len(results)} configs")
    else:
        print("\n[Phase 1] Skipping training, loading existing results...")
        with open(all_configs_path, "r") as f:
            results = json.load(f)

    print("\n[Phase 2] Running dose-response analysis...")
    analysis = analyze(results, fig_dir)

    analysis_path = os.path.join(results_dir, "analysis.json")
    with open(analysis_path, "w") as f:
        json.dump(analysis, f, indent=2)
    print(f"Analysis saved: {analysis_path}")

    print("\n[Phase 3] Generating figures...")
    figures = generate_figures(analysis, fig_dir)
    for fig in figures:
        print(f"  - {fig}")

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    perp = analysis["perplexity"]
    print(f"\nPerplexity Dimension:")
    print(f"  Best fit: degree {perp['fit']['degree']} (AIC={perp['fit']['aic']:.2f}, R²={perp['fit']['r2']:.3f})")
    print(f"  Peak detected: {perp['peak']}" if perp['peak'] else "  No interior peak")
    print(f"  Concave (hypothesis supported): {perp['is_concave']}")

    dedup = analysis["dedup"]
    print(f"\nDeduplication Dimension:")
    print(f"  Best fit: degree {dedup['fit']['degree']} (AIC={dedup['fit']['aic']:.2f}, R²={dedup['fit']['r2']:.3f})")
    print(f"  Peak detected: {dedup['peak']}" if dedup['peak'] else "  No interior peak")
    print(f"  Concave (hypothesis supported): {dedup['is_concave']}")

    hypothesis_supported = perp["is_concave"] or dedup["is_concave"]
    print(f"\n{'✓' if hypothesis_supported else '✗'} H-E1 EXISTENCE HYPOTHESIS: {'SUPPORTED' if hypothesis_supported else 'NOT SUPPORTED'}")
    print(f"  At least one parameter shows concave dose-response: {hypothesis_supported}")

    print(f"\nEnd time: {datetime.now().isoformat()}")
    print("=" * 60)

    return {
        "success": True,
        "hypothesis_supported": hypothesis_supported,
        "analysis": analysis,
        "figures": figures,
    }


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result["success"] else 1)
