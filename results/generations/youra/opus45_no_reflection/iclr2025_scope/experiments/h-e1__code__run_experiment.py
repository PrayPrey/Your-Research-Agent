#!/usr/bin/env python3
"""H-E1 Experiment Runner - Main entry point"""
import os
import sys
import json
import traceback

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

def main():
    from config import ExperimentConfig
    from train import main as train_main
    from evaluate import generate_all_figures, check_gate_criteria

    print("="*60)
    print("H-E1 EXPERIMENT: Unified Phi-Mamba Framework")
    print("="*60)

    try:
        results = train_main()

        results_path = os.path.join(CODE_DIR, "outputs", "results.json")
        figures_dir = os.path.join(CODE_DIR, "..", "figures")

        gate_results = generate_all_figures(results_path, figures_dir)

        experiment_results = {
            "hypothesis_id": "h-e1",
            "objective": "Both matrix-level and token-level objectives can be implemented in unified Phi-Mamba framework",
            "mohawk_metrics": {
                "initial_loss": results["mohawk"]["initial_loss"],
                "final_loss": results["mohawk"]["final_loss"],
                "converged": results["mohawk"]["converged"],
                "nan_count": results["mohawk"]["nan_count"],
                "inf_count": results["mohawk"]["inf_count"],
            },
            "cab_metrics": {
                "initial_loss": results["cab"]["initial_loss"],
                "final_loss": results["cab"]["final_loss"],
                "converged": results["cab"]["converged"],
                "nan_count": results["cab"]["nan_count"],
                "inf_count": results["cab"]["inf_count"],
            },
            "gate_verdict": "PASS" if gate_results["overall_pass"] else "FAIL",
            "gate_type": "MUST_WORK",
            "mohawk_gate_details": gate_results["mohawk_gate"],
            "cab_gate_details": gate_results["cab_gate"],
        }

        output_path = os.path.join(CODE_DIR, "..", "experiment_results.json")
        with open(output_path, "w") as f:
            json.dump(experiment_results, f, indent=2)

        print("\n" + "="*60)
        print("EXPERIMENT COMPLETE")
        print("="*60)
        print(f"Gate Verdict: {experiment_results['gate_verdict']}")
        print(f"Results saved to: {output_path}")

        return 0 if gate_results["overall_pass"] else 1

    except Exception as e:
        print(f"EXPERIMENT FAILED: {e}")
        traceback.print_exc()

        error_results = {
            "hypothesis_id": "h-e1",
            "gate_verdict": "FAIL",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        output_path = os.path.join(CODE_DIR, "..", "experiment_results.json")
        with open(output_path, "w") as f:
            json.dump(error_results, f, indent=2)

        return 1


if __name__ == "__main__":
    sys.exit(main())
