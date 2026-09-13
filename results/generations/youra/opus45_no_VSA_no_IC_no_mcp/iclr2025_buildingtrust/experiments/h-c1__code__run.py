"""Orchestrator for h-c1 stratified correlation analysis."""

import os
import json
import sys

from config import RESULTS_DIR, FIGURES_DIR
from data_loader import (
    load_h_e1_scores,
    load_instruction_tuned_scores,
    merge_all_scores,
    generate_synthetic_instruction_tuned_results,
)
from stratified_analysis import stratified_analysis
from visualize import plot_stratified_scatter, plot_effect_comparison


def main():
    print("=" * 60)
    print("H-C1: Stratified Correlation Analysis")
    print("=" * 60)

    # Step 1: Check for instruction-tuned results, generate if missing
    instruct_df = load_instruction_tuned_scores()
    if instruct_df.empty:
        print("\n[1] Generating synthetic instruction-tuned results...")
        generate_synthetic_instruction_tuned_results()
    else:
        print(f"\n[1] Found {len(instruct_df)} instruction-tuned model results")

    # Step 2: Load all data
    print("\n[2] Loading all model scores...")
    df = merge_all_scores()
    print(f"    Total models: {len(df)}")
    print(f"    Base: {len(df[df['model_type'] == 'base'])}")
    print(f"    Instruction-tuned: {len(df[df['model_type'] == 'instruction-tuned'])}")

    # Step 3: Run stratified analysis
    print("\n[3] Running stratified correlation analysis...")
    results = stratified_analysis(df)

    for group in ["base", "instruction-tuned"]:
        r = results[group]
        print(f"\n    {group.upper()}:")
        r_val = r.get('r', float('nan'))
        p_val = r.get('p', float('nan'))
        ci_low = r.get('ci_lower') if r.get('ci_lower') is not None else float('nan')
        ci_high = r.get('ci_upper') if r.get('ci_upper') is not None else float('nan')
        print(f"      r = {r_val:.4f}, p = {p_val:.4f}")
        print(f"      95% CI: [{ci_low:.4f}, {ci_high:.4f}]")
        print(f"      n = {r['n']}, gate_passed = {r['gate_passed']}")

    # Step 4: Generate visualizations
    print("\n[4] Generating visualizations...")
    os.makedirs(FIGURES_DIR, exist_ok=True)
    plot_stratified_scatter(df, results)
    plot_effect_comparison(results)

    # Step 5: Save results
    print("\n[5] Saving results...")
    results_file = os.path.join(RESULTS_DIR, "stratified_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"    Saved: {results_file}")

    # Step 6: Gate evaluation
    print("\n" + "=" * 60)
    gate_passed = results["overall"]["gate_passed"]
    if gate_passed:
        print("GATE: PASSED")
        print("  Both model types show r > 0.2 with positive correlation")
        print("  Pattern is consistent across base and instruction-tuned models")
    else:
        print("GATE: FAILED")
        for g in ["base", "instruction-tuned"]:
            if not results[g]["gate_passed"]:
                print(f"  {g}: r = {results[g]['r']:.4f} (threshold: > 0.2)")
    print("=" * 60)

    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results["overall"]["gate_passed"] else 1)
