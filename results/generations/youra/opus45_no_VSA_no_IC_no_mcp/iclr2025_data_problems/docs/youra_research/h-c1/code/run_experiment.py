"""Main entrypoint for H-C1 experiment."""

import os
import sys
import json

# Setup paths
CODE_DIR = os.path.dirname(__file__)
sys.path.insert(0, CODE_DIR)

from run_comparison import run_comparison_experiment
from analysis import compute_ensemble_mean, paired_ttest, gate_check, cohens_d
from figures import plot_ensemble_comparison, plot_per_benchmark_breakdown, plot_improvement_waterfall
from h_c1_config import SEEDS, CKPT_ROOT, IMPROVEMENT_THRESHOLD, EVAL_CONFIG, SIGNIFICANCE_ALPHA


def main():
    """Orchestrate: run experiment -> analysis -> figures -> output."""
    print("=" * 60)
    print("H-C1: CPDR vs RedPajama Defaults Comparison")
    print("=" * 60)

    # Run experiment
    raw = run_comparison_experiment(SEEDS, CKPT_ROOT)

    if not raw["per_seed"]:
        print("ERROR: No seeds completed successfully")
        return {"error": "no_seeds_completed"}

    tasks = EVAL_CONFIG["tasks"]

    # Compute ensemble scores per seed
    cpdr_per_seed = [compute_ensemble_mean(s["cpdr"], tasks) for s in raw["per_seed"]]
    rp_per_seed = [compute_ensemble_mean(s["redpajama"], tasks) for s in raw["per_seed"]]

    cpdr_mean = sum(cpdr_per_seed) / len(cpdr_per_seed)
    rp_mean = sum(rp_per_seed) / len(rp_per_seed)

    # Statistical tests
    ttest = paired_ttest(cpdr_per_seed, rp_per_seed)
    gate = gate_check(cpdr_mean, rp_mean, IMPROVEMENT_THRESHOLD)
    effect_size = cohens_d(cpdr_per_seed, rp_per_seed)

    # Compile output
    output = {
        "raw": raw,
        "cpdr_per_seed": cpdr_per_seed,
        "rp_per_seed": rp_per_seed,
        "cpdr_mean": cpdr_mean,
        "rp_mean": rp_mean,
        "ttest": ttest,
        "gate": gate,
        "cohens_d": effect_size,
        "significance": ttest["p_value"] < SIGNIFICANCE_ALPHA if ttest["p_value"] == ttest["p_value"] else False,
    }

    # Save results
    output_dir = os.path.join(CODE_DIR, "output")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "results.json"), "w") as f:
        json.dump(output, f, indent=2)

    # Generate figures
    figures_dir = os.path.join(CODE_DIR, "figures")
    plot_ensemble_comparison(output, os.path.join(figures_dir, "gate_ensemble_comparison.png"))
    plot_per_benchmark_breakdown(raw, tasks, os.path.join(figures_dir, "per_benchmark_breakdown.png"))
    plot_improvement_waterfall(raw, tasks, os.path.join(figures_dir, "improvement_waterfall.png"))

    # Print summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"CPDR mean:     {cpdr_mean:.4f}")
    print(f"RP mean:       {rp_mean:.4f}")
    print(f"Improvement:   {gate['improvement']:.4f} ({gate['improvement']*100:.2f}%)")
    print(f"Gate (>1%):    {'PASS' if gate['passed'] else 'FAIL'}")
    print(f"t-test p:      {ttest['p_value']:.4f}")
    print(f"Cohen's d:     {effect_size:.4f}")
    print("=" * 60)

    return output


if __name__ == "__main__":
    main()
