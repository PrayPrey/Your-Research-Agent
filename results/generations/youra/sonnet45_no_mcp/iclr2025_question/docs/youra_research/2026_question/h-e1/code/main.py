"""Main entry point for h-e1 experiment."""

import sys
import os
import json
from datetime import datetime

# Add code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG
from data.loader import NQDataLoader
from models.generator import MistralGenerator
from methods.uncertainty import SemanticEntropyEstimator, EnsembleBaseline
from experiment.runner import ExperimentRunner
from experiment.visualizer import Visualizer


def main():
    """Run the full experiment."""
    print("=" * 60)
    print("H-E1: Semantic Entropy vs Ensemble Baseline")
    print("=" * 60)
    print()

    # Set GPU device
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
        print("Warning: CUDA_VISIBLE_DEVICES not set. Using default GPU.")

    # Initialize components
    print("Initializing components...")

    # Data loader
    data_loader = NQDataLoader(
        split=CONFIG['split'],
        num_samples=CONFIG['num_samples'],
        seed=CONFIG['seed']
    )

    # Generator
    generator = MistralGenerator(
        model_name=CONFIG['model_name'],
        device=CONFIG['device']
    )

    # Uncertainty estimators
    semantic_estimator = SemanticEntropyEstimator(
        embedding_model=CONFIG['embedding_model'],
        similarity_threshold=CONFIG['clustering_threshold']
    )

    ensemble_estimator = EnsembleBaseline()

    # Experiment runner
    runner = ExperimentRunner(
        data_loader=data_loader,
        generator=generator,
        semantic_estimator=semantic_estimator,
        ensemble_estimator=ensemble_estimator
    )

    print("Components initialized")
    print()

    # Run experiment
    results = runner.run_experiment()

    # Save results
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)

    results_file = os.path.join(output_dir, 'results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_file}")

    # Also save to hypothesis root for Phase 4 workflow
    root_results_file = os.path.join(os.path.dirname(__file__), '..', 'experiment_results.json')
    with open(root_results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {root_results_file}")

    # Generate visualizations
    figures_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')
    visualizer = Visualizer(output_dir=figures_dir)

    print("\nGenerating visualizations...")
    visualizer.plot_auroc_comparison(results)
    visualizer.plot_roc_curves(
        results['y_true'],
        results['semantic_scores'],
        results['ensemble_scores']
    )
    print("Visualizations complete")

    # Print final summary
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Gate Status: {'PASS ✅' if results['gate_pass'] else 'FAIL ❌'}")
    print("=" * 60)

    # Exit with code based on gate result
    return 0 if results['gate_pass'] else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
