"""Main Ablation Runner - Entry point for H-M1 experiment"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../h-e1/code'))
from src.llm_client import SpecificationGenerator
from src.verifier import FramaCVerifier
from src.feedback_parser import FeedbackExtractor
from src.refinement_loop import IterativeRefinementLoop
from src.dataset import DatasetManager

from .ablation_experiment import AblationExperiment
from .statistical_analyzer import StatisticalAnalyzer
from .ablation_visualizer import AblationVisualizer
from .results_documentor import ResultsDocumentor
from .feedback_ablator import FeedbackCondition


class AblationRunner:
    """Orchestrate complete ablation study"""

    def __init__(self, hypothesis_folder: Path):
        self.hypothesis_folder = Path(hypothesis_folder)
        self.code_dir = self.hypothesis_folder / "code"
        self.results_dir = self.code_dir / "results"
        self.figures_dir = self.hypothesis_folder / "figures"
        self.temp_dir = self.code_dir / "temp"

        # Create directories
        for d in [self.results_dir, self.figures_dir, self.temp_dir]:
            d.mkdir(parents=True, exist_ok=True)

        print(f"Ablation Runner initialized")
        print(f"  Hypothesis: {self.hypothesis_folder.name}")
        print(f"  Results: {self.results_dir}")
        print(f"  Figures: {self.figures_dir}")

    def run(self):
        """Execute complete ablation study"""
        print("\n" + "="*70)
        print("H-M1 ABLATION STUDY - Information Gradient Validation")
        print("="*70)

        # Step 1: Setup components
        print("\n[1/5] Setting up components...")
        components = self._setup_components()

        # Step 2: Load benchmark
        print("\n[2/5] Loading benchmark dataset...")
        programs = self._load_benchmark(components['dataset_manager'])

        # Step 3: Run ablation study
        print(f"\n[3/5] Running ablation study ({len(programs)} programs × 4 conditions)...")
        ablation_results = self._run_ablation_study(components, programs)

        # Step 4: Analyze results
        print("\n[4/5] Analyzing results...")
        stats = self._analyze_results(ablation_results)

        # Step 5: Generate outputs
        print("\n[5/5] Generating outputs...")
        self._generate_outputs(ablation_results, stats)

        print("\n" + "="*70)
        print("ABLATION STUDY COMPLETE")
        print("="*70)

        gate_decision = stats['gate_decision']
        print(f"\nGate Status: {gate_decision.status}")
        print(f"Reason: {gate_decision.reason}")

        return gate_decision

    def _setup_components(self):
        """Initialize all required components"""
        # LLM client
        generator = SpecificationGenerator(
            model="claude-opus-4-5",
            temperature=0.7,
            max_tokens=2048
        )
        print("  ✓ LLM client initialized")

        # Verifier
        verifier = FramaCVerifier(
            timeout_per_obligation=10,
            provers=["alt-ergo", "z3"]
        )
        print("  ✓ Frama-C verifier initialized")

        # Feedback extractor
        feedback_extractor = FeedbackExtractor()
        print("  ✓ Feedback extractor initialized")

        # Base refinement loop (from h-e1)
        base_loop = IterativeRefinementLoop(
            generator=generator,
            verifier=verifier,
            feedback_extractor=feedback_extractor,
            max_iterations=10,
            no_improvement_threshold=3
        )
        print("  ✓ Base refinement loop initialized")

        # Dataset manager
        dataset_manager = DatasetManager(
            dataset_name="acsl-by-example",
            cache_dir=Path(".cache/datasets")
        )
        print("  ✓ Dataset manager initialized")

        return {
            'generator': generator,
            'verifier': verifier,
            'feedback_extractor': feedback_extractor,
            'base_loop': base_loop,
            'dataset_manager': dataset_manager
        }

    def _load_benchmark(self, dataset_manager):
        """Load benchmark programs"""
        # For now, use a subset of programs
        # In real implementation, would load from ACSL-by-Example
        programs = dataset_manager.load_programs()

        print(f"  ✓ Loaded {len(programs)} programs")
        return programs

    def _run_ablation_study(self, components, programs):
        """Execute ablation experiment"""
        ablation_experiment = AblationExperiment(
            base_refinement_loop=components['base_loop'],
            output_dir=self.results_dir / "trials"
        )

        ablation_results = ablation_experiment.run_full_ablation(
            programs=programs,
            temp_dir=self.temp_dir
        )

        # Save aggregate results
        aggregate_file = self.results_dir / "condition_aggregates.json"
        with aggregate_file.open('w') as f:
            json.dump({
                cond: {
                    'mean_rate': res.mean_rate,
                    'std_rate': res.std_rate,
                    'mean_iterations': res.mean_iterations,
                    'total_compute': res.total_compute
                }
                for cond, res in ablation_results.results_by_condition.items()
            }, f, indent=2)

        print(f"  ✓ Completed {len(ablation_results.raw_trials)} trials")
        return ablation_results

    def _analyze_results(self, ablation_results):
        """Perform statistical analysis"""
        analyzer = StatisticalAnalyzer(significance_level=0.05)

        # Extract condition means
        condition_means = {
            cond: res.mean_rate
            for cond, res in ablation_results.results_by_condition.items()
        }

        # Test 1: Monotonic ordering
        monotonic_test = analyzer.test_monotonic_ordering(condition_means)
        print(f"  ✓ Monotonic ordering test: {'PASS' if monotonic_test.passed else 'FAIL'}")

        # Test 2: Adjacent gaps
        gap_test = analyzer.test_adjacent_gaps(condition_means, threshold=10.0)
        print(f"  ✓ Adjacent gaps test: {'PASS' if gap_test.passed else 'FAIL'}")

        # Test 3: Regression
        regression = analyzer.run_regression(ablation_results)
        print(f"  ✓ Regression analysis: {'PASS' if regression.significant else 'FAIL'}")
        print(f"    β={regression.coefficient:.4f}, p={regression.p_value:.6f}, R²={regression.r_squared:.4f}")

        # Gate decision
        gate_decision = analyzer.make_gate_decision(monotonic_test, gap_test, regression)

        # Save statistical tests
        stats_file = self.results_dir / "statistical_tests.json"
        with stats_file.open('w') as f:
            json.dump({
                'monotonic_test': {
                    'passed': monotonic_test.passed,
                    'ordering': monotonic_test.ordering,
                    'violations': monotonic_test.violations
                },
                'gap_test': {
                    'passed': gap_test.passed,
                    'gaps': gap_test.gaps,
                    'failed_gaps': gap_test.failed_gaps
                },
                'regression': {
                    'coefficient': regression.coefficient,
                    'p_value': regression.p_value,
                    'r_squared': regression.r_squared,
                    'significant': regression.significant
                },
                'gate_decision': {
                    'status': gate_decision.status,
                    'passing_tests': gate_decision.passing_tests,
                    'failing_tests': gate_decision.failing_tests,
                    'reason': gate_decision.reason
                }
            }, f, indent=2)

        return {
            'monotonic_test': monotonic_test,
            'gap_test': gap_test,
            'regression': regression,
            'gate_decision': gate_decision
        }

    def _generate_outputs(self, ablation_results, stats):
        """Generate visualizations and documentation"""
        # Visualizations
        visualizer = AblationVisualizer(output_dir=self.figures_dir)
        visualizer.generate_all_figures(ablation_results, stats)

        # Validation report
        documentor = ResultsDocumentor(hypothesis_folder=self.hypothesis_folder)
        report = documentor.generate_validation_report(
            ablation_results=ablation_results,
            stats=stats,
            gate_decision=stats['gate_decision']
        )
        documentor.save_validation_report(report, "04_validation.md")

        print("  ✓ All outputs generated")


def main():
    """Entry point"""
    # Get hypothesis folder from environment or argument
    hypothesis_folder = os.getenv('HYPOTHESIS_FOLDER', 'docs/youra_research/h-m1')

    if len(sys.argv) > 1:
        hypothesis_folder = sys.argv[1]

    runner = AblationRunner(Path(hypothesis_folder))
    gate_decision = runner.run()

    # Exit code based on gate decision
    sys.exit(0 if gate_decision.status == "SATISFIED" else 1)


if __name__ == "__main__":
    main()
