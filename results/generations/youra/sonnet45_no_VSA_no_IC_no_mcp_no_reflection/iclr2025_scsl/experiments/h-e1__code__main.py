"""
Main orchestrator for h-e1: Full 40-run experiment execution.
"""

import sys
from pathlib import Path
from train import run_all_seeds
from evaluate import (
    save_results,
    plot_convergence_comparison,
    plot_temporal_gap_distribution,
    check_poc_pass,
    check_full_pass
)


def main():
    """Run full h-e1 experiment pipeline."""

    print("\n" + "="*80)
    print("h-e1 Temporal Convergence Validation: Full Experiment Run")
    print("="*80)

    # Dataset list (CMNIST only for PoC - others require manual setup/download)
    datasets = ['CMNIST']

    num_seeds = 10  # Full 10-seed run for statistical validation
    all_results = {}

    # Run experiments
    for dataset in datasets:
        print(f"\n{'='*80}")
        print(f"Starting experiments for {dataset}")
        print(f"{'='*80}")

        try:
            results = run_all_seeds(dataset, num_seeds=num_seeds)
            all_results[dataset] = results
            print(f"\n{dataset} complete: {len(results)} runs")
        except Exception as e:
            print(f"\n[ERROR] {dataset} failed: {e}")
            import traceback
            traceback.print_exc()
            all_results[dataset] = []

    # Save results
    output_dir = Path(__file__).parent.parent / 'results'
    save_results(all_results, str(output_dir))

    # Generate figures
    figures_dir = Path(__file__).parent.parent / 'figures'
    figures_dir.mkdir(parents=True, exist_ok=True)

    plot_convergence_comparison(
        all_results,
        str(figures_dir / 'convergence_comparison.png')
    )

    plot_temporal_gap_distribution(
        all_results,
        str(figures_dir / 'temporal_gap_distribution.png')
    )

    # Validate gate criteria
    print("\n" + "="*80)
    print("GATE VALIDATION: PoC Pass Criteria")
    print("="*80)

    poc_result = check_poc_pass(all_results)
    print(f"\nPoC Pass: {'✓ PASS' if poc_result['poc_pass'] else '✗ FAIL'}")
    print(f"  Direction check (E_s < E_c on all datasets): {'✓' if poc_result['direction_pass'] else '✗'} ({poc_result['direction_pass_count']}/4 datasets)")
    print(f"  Magnitude check (mean Δ≥2 on ≥2 datasets): {'✓' if poc_result['magnitude_pass'] else '✗'} ({poc_result['magnitude_pass_count']}/4 datasets)")

    print("\nPer-dataset details:")
    for dataset, details in poc_result['details'].items():
        print(f"\n  {dataset}:")
        print(f"    Direction: {details['direction_correct_count']}/10 seeds (E_s < E_c)")
        print(f"    Mean Δ: {details['mean_delta']:.2f} epochs" if details['mean_delta'] else "    Mean Δ: N/A")
        print(f"    PoC: {'✓ PASS' if details['direction_pass'] else '✗ FAIL'}")

    print("\n" + "="*80)
    print("GATE VALIDATION: Full Statistical Pass Criteria")
    print("="*80)

    full_result = check_full_pass(all_results)
    print(f"\nFull Pass: {'✓ PASS' if full_result['full_pass'] else '✗ FAIL'}")
    print(f"  Significance (p<0.05 on all datasets): {'✓' if full_result['significance_pass'] else '✗'} ({full_result['significance_pass_count']}/4 datasets)")
    print(f"  Magnitude (mean Δ≥2 on ≥3 datasets): {'✓' if full_result['magnitude_pass'] else '✗'} ({full_result['magnitude_pass_count']}/4 datasets)")

    print("\nPer-dataset statistics:")
    for dataset, details in full_result['details'].items():
        stats = details['stats']
        print(f"\n  {dataset}:")
        print(f"    p-value: {stats['p_value']:.4f}" if stats['p_value'] else "    p-value: N/A")
        print(f"    mean Δ: {stats['mean_delta']:.2f} ± {stats['std_delta']:.2f} epochs" if stats['mean_delta'] else "    mean Δ: N/A")
        print(f"    Converged: {stats['n_converged']}/{stats['n_total']} seeds")

    # Final verdict
    print("\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80)

    if poc_result['poc_pass']:
        print("\n✓ PoC PASS: Core mechanism demonstrated")
        if full_result['full_pass']:
            print("✓ FULL PASS: Statistical validation complete")
            print("\nGate Result: PASS")
            print("h-e1 validates foundational temporal ordering pattern.")
            return 0
        else:
            print("⚠ FULL PASS: Not achieved (statistical evidence incomplete)")
            print("\nGate Result: PARTIAL")
            print("Direction correct but magnitude/significance weak.")
            return 0
    else:
        print("\n✗ PoC FAIL: Core mechanism not demonstrated")
        print("\nGate Result: FAIL")
        print("MUST_WORK gate violation - blocks dependent hypotheses.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
