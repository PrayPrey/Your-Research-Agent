"""Main experiment runner for H-E1."""

import os
import sys
import time
import yaml
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict

from .llm_client import SpecificationGenerator
from .verifier import FramaCVerifier
from .feedback_parser import FeedbackExtractor
from .refinement_loop import IterativeRefinementLoop
from .dataset import DatasetManager
from .metrics import MetricsTracker
from .visualizer import Visualizer


class ExperimentRunner:
    """Orchestrate H-E1 experiment."""

    def __init__(self, config_path: str):
        """Load configuration."""
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Initialize components
        api_key = os.environ.get(self.config['llm']['api_key_env'])
        if not api_key:
            raise ValueError(f"API key not found: {self.config['llm']['api_key_env']}")

        self.generator = SpecificationGenerator(
            api_key=api_key,
            model=self.config['llm']['model']
        )

        self.verifier = FramaCVerifier(
            timeout_per_obligation=self.config['verifier']['wp']['timeout_per_vc'],
            provers=self.config['verifier']['wp']['solvers']
        )

        self.feedback_extractor = FeedbackExtractor()

        self.refinement_loop = IterativeRefinementLoop(
            generator=self.generator,
            verifier=self.verifier,
            feedback_extractor=self.feedback_extractor,
            max_iterations=self.config['refinement']['max_iterations'],
            no_improvement_threshold=self.config['refinement']['early_stopping']['no_improvement_threshold']
        )

        self.dataset_manager = DatasetManager(
            dataset_name=self.config['dataset']['primary']['identifier']
        )

        # Output directories
        self.output_dir = Path(self.config['experiment']['output_dir']) / "code" / "results"
        self.figures_dir = Path(self.config['evaluation']['figures']['output_dir'])

        self.metrics_tracker = MetricsTracker(self.output_dir)
        self.visualizer = Visualizer(self.figures_dir)

    def run(self):
        """Execute complete experiment."""
        print("=" * 80)
        print("H-E1: Verifier-Feedback-Driven Specification Synthesis")
        print("=" * 80)
        print()

        # Load benchmark
        print("Loading benchmark dataset...")
        programs = self.dataset_manager.load_benchmark(
            num_programs=self.config['dataset']['benchmark']['size'],
            seed=self.config['experiment']['seed']
        )
        print(f"Loaded {len(programs)} programs\n")

        # Process each program
        for i, program in enumerate(programs, 1):
            print(f"\n{'='*80}")
            print(f"Processing Program {i}/{len(programs)}: {program.id}")
            print(f"{'='*80}\n")

            start_time = time.time()

            with TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Run refinement loop
                history = self.refinement_loop.synthesize_specification(
                    c_code=program.c_code,
                    temp_dir=temp_path
                )

                runtime = time.time() - start_time

                # Estimate API calls and cost
                api_calls = history.total_iterations + 1  # +1 for initial generation
                cost_usd = api_calls * 0.03  # Rough estimate

                # Record metrics
                metrics = self.metrics_tracker.record_experiment(
                    program_id=program.id,
                    history=history,
                    api_calls=api_calls,
                    cost_usd=cost_usd,
                    runtime=runtime
                )

                # Print summary
                print(f"\nResults for {program.id}:")
                print(f"  - Initial discharge rate: {metrics.initial_discharge_rate:.1f}%")
                print(f"  - Final discharge rate: {metrics.final_discharge_rate:.1f}%")
                print(f"  - Iterations: {metrics.iterations_to_convergence}")
                print(f"  - Convergence: {metrics.convergence_reason.value}")
                print(f"  - Improvement: {metrics.improvement_achieved}")
                print(f"  - Runtime: {runtime:.1f}s")

        # Aggregate results
        print(f"\n{'='*80}")
        print("Experiment Complete - Generating Report")
        print(f"{'='*80}\n")

        agg = self.metrics_tracker.compute_aggregate_metrics()

        print("\nAggregate Metrics:")
        print(f"  - Mean final discharge rate: {agg['mean_final_discharge_rate']:.1f}%")
        print(f"  - Programs with improvement: {agg['programs_with_improvement']}/{len(programs)} ({agg['improvement_percentage']:.1f}%)")
        print(f"  - Mean iterations: {agg['mean_iterations']:.1f}")
        print(f"  - Total cost: ${agg['total_cost_usd']:.2f}")

        # Gate evaluation
        target_rate = self.config['evaluation']['primary_metrics'][0]['target']
        gate_passed = agg['mean_final_discharge_rate'] >= target_rate

        print(f"\nGate Evaluation:")
        print(f"  - Target discharge rate: {target_rate}%")
        print(f"  - Actual discharge rate: {agg['mean_final_discharge_rate']:.1f}%")
        print(f"  - Gate Status: {'✓ PASS' if gate_passed else '✗ FAIL'}")

        # Save results
        self.metrics_tracker.save_results()
        print(f"\nResults saved to {self.output_dir / '04_results.json'}")

        # Generate visualizations
        self.visualizer.generate_all_plots(self.metrics_tracker, target_rate)

        # Generate validation report
        self._generate_validation_report(agg, gate_passed)

        print(f"\n{'='*80}")
        print("Experiment Complete!")
        print(f"{'='*80}\n")

        return gate_passed

    def _generate_validation_report(self, agg: Dict, gate_passed: bool):
        """Generate 04_validation.md report."""
        report_path = Path(self.config['experiment']['output_dir']) / "04_validation.md"

        with open(report_path, 'w') as f:
            f.write("# Phase 4 Validation Report: H-E1\n\n")
            f.write("**Hypothesis:** LLMs can utilize structured verifier feedback to iteratively refine formal specifications\n\n")
            f.write("**Date:** " + time.strftime("%Y-%m-%d") + "\n\n")
            f.write("## Experiment Summary\n\n")

            f.write(f"- **Programs Tested:** {agg.get('total_programs', len(self.metrics_tracker.experiments))}\n")
            f.write(f"- **Mean Discharge Rate:** {agg['mean_final_discharge_rate']:.1f}%\n")
            f.write(f"- **Programs with Improvement:** {agg['programs_with_improvement']} ({agg['improvement_percentage']:.1f}%)\n")
            f.write(f"- **Mean Iterations:** {agg['mean_iterations']:.1f}\n")
            f.write(f"- **Total API Calls:** {agg['total_api_calls']}\n")
            f.write(f"- **Total Cost:** ${agg['total_cost_usd']:.2f}\n\n")

            f.write("## Gate Evaluation\n\n")
            f.write(f"**Gate Type:** MUST_WORK\n\n")
            f.write(f"**Target:** ≥50% proof discharge rate\n\n")
            f.write(f"**Actual:** {agg['mean_final_discharge_rate']:.1f}%\n\n")
            f.write(f"**Result:** {'✓ PASS' if gate_passed else '✗ FAIL'}\n\n")

            f.write("## Feedback Dimension Utilization\n\n")
            f.write(f"- **Witness (Dimension 1):** {agg['witness_dimension_usage']} programs\n")
            f.write(f"- **Structure (Dimension 2):** {agg['structure_dimension_usage']} programs\n")
            f.write(f"- **Dependency (Dimension 3):** {agg['dependency_dimension_usage']} programs\n\n")

            f.write("## Conclusion\n\n")
            if gate_passed:
                f.write("The hypothesis H-E1 is **VALIDATED**. LLMs successfully utilized structured verifier feedback ")
                f.write("to iteratively refine formal specifications, achieving the target proof discharge rate.\n")
            else:
                f.write("The hypothesis H-E1 is **NOT VALIDATED**. The mean proof discharge rate did not meet ")
                f.write("the minimum threshold of 50%.\n")

        print(f"Validation report saved to {report_path}")


def main():
    """Entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m src.main <config_path>")
        sys.exit(1)

    config_path = sys.argv[1]

    runner = ExperimentRunner(config_path)
    gate_passed = runner.run()

    sys.exit(0 if gate_passed else 1)


if __name__ == "__main__":
    main()
