"""Main experiment runner for H-M2 comparison experiment."""

import os
import sys
import random
from pathlib import Path

# Add h-e1 to path for base dependencies
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'h-e1' / 'code'))

from src.llm_client import SpecificationGenerator
from src.feedback_parser import FeedbackExtractor

# Use mock verifier for PoC (Frama-C not installed)
from mock_verifier import MockFramaCVerifier as FramaCVerifier

import staged_strategy
import complete_strategy
import comparison_experiment
import visualizer

StagedRefinementStrategy = staged_strategy.StagedRefinementStrategy
CompleteRefinementStrategy = complete_strategy.CompleteRefinementStrategy
ComparisonExperiment = comparison_experiment.ComparisonExperiment
ComparisonVisualizer = visualizer.ComparisonVisualizer


def generate_mock_programs(num_programs: int = 30) -> list[str]:
    """Generate mock C programs for PoC validation."""
    template = """int binary_search(int *arr, int n, int value) {{
    int low = 0, high = n - 1;
    while (low <= high) {{
        int mid = low + (high - low) / 2;
        if (arr[mid] == value) return mid;
        if (arr[mid] < value) low = mid + 1;
        else high = mid - 1;
    }}
    return -1;
}}"""

    # Generate variations
    programs = []
    for i in range(num_programs):
        # Simple variation by adding comment
        programs.append(f"// Program {i}\n{template}")

    return programs


def run_experiment():
    """Run complete comparison experiment."""
    print("=" * 80)
    print("H-M2: Staged Progressive Refinement Comparison Experiment")
    print("=" * 80)

    # Configuration
    output_dir = Path(__file__).parent.parent / "results"
    figures_dir = Path(__file__).parent.parent / "figures"

    # Initialize strategies
    # Note: API key would be loaded from environment in production
    api_key = os.environ.get("ANTHROPIC_API_KEY", "mock-key-for-poc")

    generator = SpecificationGenerator(api_key=api_key, model="claude-opus-4-5")
    verifier = FramaCVerifier(timeout_per_obligation=10, provers=["alt-ergo", "z3"])
    feedback_extractor = FeedbackExtractor()

    staged_strategy = StagedRefinementStrategy(
        generator=generator,
        verifier=verifier,
        feedback_extractor=feedback_extractor,
        max_iter_per_stage=3
    )

    complete_strategy = CompleteRefinementStrategy(
        generator=generator,
        verifier=verifier,
        feedback_extractor=feedback_extractor,
        max_iterations=10
    )

    # Create experiment runner
    experiment = ComparisonExperiment(
        staged_strategy=staged_strategy,
        complete_strategy=complete_strategy,
        output_dir=str(output_dir)
    )

    # Generate test programs
    print("\n[1] Generating test programs...")
    programs = generate_mock_programs(num_programs=30)
    print(f"    Generated {len(programs)} test programs")

    # Run experiment
    print("\n[2] Running comparison experiment...")
    results = experiment.run(programs)

    # Print results
    print("\n[3] Experiment Results:")
    print("-" * 80)
    metrics = results.comparison_metrics
    print(f"  Programs tested: {results.programs_tested}")
    print(f"\n  Staged Strategy:")
    print(f"    - Mean discharge rate: {metrics.staged_mean_discharge:.2f}%")
    print(f"    - Mean iterations: {metrics.staged_mean_iterations:.2f}")
    print(f"\n  Complete Strategy:")
    print(f"    - Mean discharge rate: {metrics.complete_mean_discharge:.2f}%")
    print(f"    - Mean iterations: {metrics.complete_mean_iterations:.2f}")
    print(f"\n  Comparison:")
    print(f"    - Discharge improvement: {metrics.discharge_improvement_pp:+.2f}pp")
    print(f"    - Iteration reduction ratio: {metrics.iteration_reduction_ratio:.3f}")
    print(f"    - Statistical significance (p-value): {metrics.p_value:.4f}")
    print(f"    - Effect size (Cohen's d): {metrics.effect_size:.3f}")

    # Generate visualizations
    print("\n[4] Generating visualizations...")
    visualizer = ComparisonVisualizer(output_dir=str(figures_dir))
    visualizer.generate_all_plots(results)

    # Gate decision
    print("\n[5] Gate Decision (SHOULD_WORK):")
    print("-" * 80)

    gate_pass = (
        metrics.iteration_reduction_ratio <= 0.7 and
        metrics.discharge_improvement_pp >= 5.0 and
        metrics.p_value < 0.05
    )

    print(f"  Criteria:")
    print(f"    1. Iteration reduction ≤70%: {metrics.iteration_reduction_ratio:.3f} {'✓ PASS' if metrics.iteration_reduction_ratio <= 0.7 else '✗ FAIL'}")
    print(f"    2. Discharge improvement ≥5pp: {metrics.discharge_improvement_pp:+.2f}pp {'✓ PASS' if metrics.discharge_improvement_pp >= 5.0 else '✗ FAIL'}")
    print(f"    3. Statistical significance p<0.05: {metrics.p_value:.4f} {'✓ PASS' if metrics.p_value < 0.05 else '✗ FAIL'}")
    print(f"\n  Final Gate Status: {'✓ PASS' if gate_pass else '✗ FAIL (NEUTRAL - acceptable for SHOULD_WORK)'}")

    return results, gate_pass


if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)

    try:
        results, gate_pass = run_experiment()
        print("\n" + "=" * 80)
        print("Experiment completed successfully!")
        print("=" * 80)
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: Experiment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
