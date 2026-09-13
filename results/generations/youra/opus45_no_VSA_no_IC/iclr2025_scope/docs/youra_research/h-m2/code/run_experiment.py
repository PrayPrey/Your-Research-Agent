"""Full experiment pipeline for h-m2 hypothesis.

This script runs the complete experiment:
1. HotpotQA sweep (72 runs) - SKIP if results exist
2. Combine SQuAD-v2 (from h-e1) + HotpotQA results
3. Compute rank sensitivities for all (model, dataset, seed)
4. Run phase transition analysis
5. Generate visualizations
"""
import os
import json
import argparse

from config import Paths


def run_full_experiment(
    skip_training: bool = False,
    data_cache_dir: str | None = None,
) -> dict:
    """Run full h-m2 experiment pipeline."""
    from main import run_hotpotqa_sweep, build_combined_dataset
    from sensitivity import compute_all_sensitivities
    from analyze_sensitivity import run_full_analysis
    from visualize import plot_sensitivity_vs_scale, plot_rank_curves

    paths = Paths()
    os.makedirs("results", exist_ok=True)
    os.makedirs("figures", exist_ok=True)

    print("=" * 60)
    print("h-m2: Rank Sensitivity Phase Transition Experiment")
    print("=" * 60)

    if not skip_training:
        print("\n[1/5] Running HotpotQA sweep (72 runs)...")
        run_hotpotqa_sweep(data_cache_dir=data_cache_dir)
    else:
        print("\n[1/5] Skipping training (--skip-training)")

    print("\n[2/5] Combining SQuAD-v2 + HotpotQA results...")
    combined_df = build_combined_dataset()

    print("\n[3/5] Computing rank sensitivities...")
    sens_df = compute_all_sensitivities(combined_df, paths.sensitivities_csv)
    print(f"Computed {len(sens_df)} sensitivity values")

    print("\n[4/5] Running phase transition analysis...")
    results = run_full_analysis(paths.sensitivities_csv, paths.phase_transition_json)

    print("\n[5/5] Generating visualizations...")
    plot_sensitivity_vs_scale(sens_df, results, paths.sensitivity_plot_png)
    plot_rank_curves(combined_df, paths.rank_curves_png)

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)

    print("\n=== Phase Transition Results ===")
    if "phase_transition_combined" in results:
        pt = results["phase_transition_combined"]
        print(f"Sensitivity Ratio (12B/1B): {pt['ratio']:.3f}")
        print(f"95% CI: [{pt['ci_low']:.3f}, {pt['ci_high']:.3f}]")
        print(f"p-value: {pt['p_value']:.4f}")
        print(f"PASS: {pt['pass']}")

    print(f"\nOverall Pass: {results.get('overall_pass', 'N/A')}")

    with open("results/h-m2_experiment_results.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run h-m2 experiment")
    parser.add_argument("--skip-training", action="store_true",
                        help="Skip training, use existing results")
    parser.add_argument("--data-cache", default=None,
                        help="Data cache directory")
    args = parser.parse_args()

    run_full_experiment(
        skip_training=args.skip_training,
        data_cache_dir=args.data_cache,
    )
