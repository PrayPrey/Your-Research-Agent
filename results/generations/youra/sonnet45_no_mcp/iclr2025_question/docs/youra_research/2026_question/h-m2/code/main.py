"""Main entry point for h-m2 error signature analysis experiment."""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG
from experiment.runner import ExperimentRunner


def main():
    """Run error signature analysis experiment."""
    print("\n" + "="*60)
    print("h-m2: Error Type Signature Analysis")
    print("="*60)
    print(f"Hypothesis: Knowledge gaps vs confident misconceptions")
    print(f"Datasets: NaturalQuestions (100) + TruthfulQA (100)")
    print(f"Model: {CONFIG['model_name']}")
    print(f"K samples: {CONFIG['k_samples']}")
    print(f"Temperature: {CONFIG['temperature']}")
    print("="*60 + "\n")

    # Initialize experiment runner
    runner = ExperimentRunner(CONFIG)

    # Run experiment
    results = runner.run_experiment()

    print("\n" + "="*60)
    print("EXPERIMENT COMPLETED")
    print("="*60)
    print(f"Gate Result: {'PASS' if results['gate_pass'] else 'FAIL'}")
    print(f"Results saved to: {CONFIG['output_dir']}/experiment_results.json")
    print(f"Figures saved to: {CONFIG['figures_dir']}/")
    print("="*60 + "\n")

    return results


if __name__ == "__main__":
    main()
