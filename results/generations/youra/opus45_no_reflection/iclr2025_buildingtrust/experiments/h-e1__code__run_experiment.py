"""H-E1: Main Experiment Runner - Factuality-Robustness Correlation Study"""

import json
import sys
import os
from datetime import datetime

from config import MODEL_IDS, SEED, RESULTS_PATH, ANALYSIS_PATH, FIGURES_DIR
from run_eval import run_all, save_results
from analyze import evaluate_hypothesis, save_analysis, print_analysis_summary
from visualize import generate_all_figures


def main():
    """Run complete H-E1 experiment pipeline."""
    print("=" * 70)
    print("H-E1: Factuality-Robustness Correlation Study")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Models: {len(MODEL_IDS)}")
    print(f"Seed: {SEED}")
    print()

    print("\n[Phase 1/3] Running Model Evaluations...")
    print("-" * 50)
    results = run_all(MODEL_IDS)
    save_results(results, RESULTS_PATH)

    print("\n[Phase 2/3] Analyzing Correlations...")
    print("-" * 50)
    analysis = evaluate_hypothesis(results)
    save_analysis(analysis, ANALYSIS_PATH)
    print_analysis_summary(analysis)

    print("\n[Phase 3/3] Generating Figures...")
    print("-" * 50)
    os.makedirs(FIGURES_DIR, exist_ok=True)
    figures = generate_all_figures(results, analysis, FIGURES_DIR)

    print("\n" + "=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)
    print(f"End time: {datetime.now().isoformat()}")
    print(f"\nOutputs:")
    print(f"  Results: {RESULTS_PATH}")
    print(f"  Analysis: {ANALYSIS_PATH}")
    print(f"  Figures: {FIGURES_DIR} ({len(figures)} files)")
    print(f"\nGate Result: {analysis['gate_result']}")
    print(f"Action: {analysis['gate_action']}")

    experiment_results = {
        "hypothesis_id": "h-e1",
        "completed_at": datetime.now().isoformat(),
        "n_models": analysis["n_models"],
        "pearson_r": analysis["pearson_r"],
        "p_value": analysis["p_value"],
        "ci_95": analysis["ci_95"],
        "partial_r": analysis["partial_r"],
        "gate_result": analysis["gate_result"],
        "gate_action": analysis["gate_action"]
    }

    with open("results/experiment_results.json", "w") as f:
        json.dump(experiment_results, f, indent=2)

    return 0 if analysis["gate_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
