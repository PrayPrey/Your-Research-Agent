#!/usr/bin/env python3
"""H-E1: Error Class Independence Verification Experiment.

Measures Jaccard overlap between error classes fixed by:
1. Grammar constraints (syntax errors)
2. Static analysis (security/quality issues)
3. SMT-guided repair (specification violations)

Gate: MUST_WORK - All pairwise Jaccard < 0.30
"""

import json
import random
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import config
from data import load_humaneval_problems, load_verus_task_ids, generate_samples
from strategies import run_verification_strategies
from overlap import compute_jaccard_overlap, gate_check
from visualize import plot_jaccard_bar, plot_venn, plot_per_model_comparison


def main() -> int:
    """Run the H-E1 experiment and return exit code (0=pass, 1=fail)."""
    print("=" * 60)
    print("H-E1: Error Class Independence Verification")
    print("=" * 60)
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    random.seed(config.SEED)

    print("[1/6] Loading HumanEval problems...")
    problems = load_humaneval_problems()
    verus_ids = load_verus_task_ids()
    print(f"  Loaded {len(problems)} problems, {len(verus_ids)} with formal specs")

    print("\n[2/6] Generating samples per model...")
    all_samples = []
    samples_by_model = {}
    for model in config.MODELS:
        print(f"  Generating {config.N_SAMPLES} samples/problem for {model}...")
        model_samples = generate_samples(model, problems, config.N_SAMPLES)
        all_samples.extend(model_samples)
        samples_by_model[model] = model_samples
    print(f"  Total samples: {len(all_samples)}")

    print("\n[3/6] Running verification strategies...")
    pooled_sets = run_verification_strategies(all_samples, verus_ids)
    print(f"  Grammar improved: {len(pooled_sets['grammar'])} tasks")
    print(f"  Static improved: {len(pooled_sets['static'])} tasks")
    print(f"  SMT improved: {len(pooled_sets['smt'])} tasks")

    sets_by_model = {}
    for model, samples in samples_by_model.items():
        sets_by_model[model] = run_verification_strategies(samples, verus_ids)

    print("\n[4/6] Computing Jaccard overlap...")
    pooled_overlaps = compute_jaccard_overlap(pooled_sets)
    print(f"  grammar_vs_static: {pooled_overlaps['grammar_vs_static']:.4f}")
    print(f"  grammar_vs_smt: {pooled_overlaps['grammar_vs_smt']:.4f}")
    print(f"  static_vs_smt: {pooled_overlaps['static_vs_smt']:.4f}")
    print(f"  mean: {pooled_overlaps['mean']:.4f}")

    overlaps_by_model = {}
    for model, sets in sets_by_model.items():
        overlaps_by_model[model] = compute_jaccard_overlap(sets)

    print("\n[5/6] Gate check...")
    gate_passed = gate_check(pooled_overlaps, config.JACCARD_THRESHOLD)
    if gate_passed:
        print(f"  ✓ PASS - All pairwise Jaccard < {config.JACCARD_THRESHOLD}")
    else:
        print(f"  ✗ FAIL - Some pairwise Jaccard >= {config.JACCARD_THRESHOLD}")

    print("\n[6/6] Generating visualizations and saving results...")

    plot_jaccard_bar(
        pooled_overlaps,
        config.JACCARD_THRESHOLD,
        str(config.FIGURES_DIR / "jaccard_comparison.png")
    )
    print(f"  Saved: {config.FIGURES_DIR / 'jaccard_comparison.png'}")

    plot_venn(pooled_sets, str(config.FIGURES_DIR / "venn_overlap.png"))
    print(f"  Saved: {config.FIGURES_DIR / 'venn_overlap.png'}")

    plot_per_model_comparison(
        overlaps_by_model,
        str(config.FIGURES_DIR / "per_model_jaccard.png")
    )
    print(f"  Saved: {config.FIGURES_DIR / 'per_model_jaccard.png'}")

    results = {
        "hypothesis_id": "h-e1",
        "gate": "MUST_WORK",
        "gate_condition": f"Jaccard < {config.JACCARD_THRESHOLD} for all pairs",
        "gate_passed": gate_passed,
        "timestamp": datetime.now().isoformat(),
        "config": {
            "seed": config.SEED,
            "temperature": config.TEMPERATURE,
            "n_samples": config.N_SAMPLES,
            "models": config.MODELS,
            "jaccard_threshold": config.JACCARD_THRESHOLD,
        },
        "pooled_results": {
            "overlaps": pooled_overlaps,
            "set_sizes": {
                "grammar": len(pooled_sets["grammar"]),
                "static": len(pooled_sets["static"]),
                "smt": len(pooled_sets["smt"]),
            },
        },
        "per_model_results": {
            model: {
                "overlaps": overlaps_by_model[model],
                "set_sizes": {
                    "grammar": len(sets_by_model[model]["grammar"]),
                    "static": len(sets_by_model[model]["static"]),
                    "smt": len(sets_by_model[model]["smt"]),
                },
            }
            for model in config.MODELS
        },
    }

    results_path = config.RESULTS_DIR / "overlap_data.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Saved: {results_path}")

    csv_path = config.OUTPUTS_DIR / "results.csv"
    with open(csv_path, "w") as f:
        f.write("pair,jaccard,threshold,passed\n")
        for pair in ["grammar_vs_static", "grammar_vs_smt", "static_vs_smt"]:
            val = pooled_overlaps[pair]
            passed = "true" if val < config.JACCARD_THRESHOLD else "false"
            f.write(f"{pair},{val:.4f},{config.JACCARD_THRESHOLD},{passed}\n")
    print(f"  Saved: {csv_path}")

    print()
    print("=" * 60)
    print(f"H-E1 GATE RESULT: {'PASS' if gate_passed else 'FAIL'}")
    print("=" * 60)
    print(f"End time: {datetime.now().isoformat()}")

    return 0 if gate_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
