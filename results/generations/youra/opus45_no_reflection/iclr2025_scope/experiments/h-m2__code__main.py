"""Main orchestration for H-M2 Hidden State Drift Analysis."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import AnalysisConfig, validate_config
from analysis import run_full_analysis, save_results
from visualize import generate_all_figures


def main():
    print("=" * 60)
    print("H-M2: Hidden State Drift Analysis")
    print("Token-level (CAB) vs Matrix-level (MOHAWK) Distillation")
    print("=" * 60)

    config = AnalysisConfig()
    validate_config(config)
    print(f"Config: {config.num_samples} samples, lengths {config.target_lengths}")
    print(f"Middle layers: {config.middle_layers}")

    print("\nRunning full analysis...")
    results = run_full_analysis(config)

    print("\nSaving results...")
    save_results(results, config)

    print("\nGenerating figures...")
    generate_all_figures(results, config)

    print("\n" + "=" * 60)
    print("GATE RESULT")
    print("=" * 60)

    gate = results.get("gate", {})
    print(f"Variants run: {results.get('variants_run', [])}")

    if "mohawk" in results and results["mohawk"]:
        mohawk_slope = results["mohawk"]["slope"]["slope"]
        print(f"MOHAWK drift slope: {mohawk_slope:.6e}")

    if results.get("cab") and results["cab"]:
        cab_slope = results["cab"]["slope"]["slope"]
        print(f"CAB drift slope: {cab_slope:.6e}")
        print(f"Drift ratio (max/min): {gate.get('cab_drift_ratio', 'N/A'):.3f}")

    verdict = "PASS" if gate.get("pass") else "FAIL"
    print(f"\nGate condition: cab_slope < mohawk_slope AND ratio < 2.0")
    print(f"Gate verdict: {verdict}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
