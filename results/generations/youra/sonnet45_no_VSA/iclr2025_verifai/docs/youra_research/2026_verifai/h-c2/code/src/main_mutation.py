import yaml
from pathlib import Path
import sys
from typing import List
import tempfile

from dataset_loader import ACSLByExampleLoader, Program
from spec_synthesizer import SpecificationSynthesizer
from mutation_operators import ArithmeticMutation, RelationalMutation, BooleanMutation, StatementMutation, BoundaryMutation
from mutant_generator import MutantGenerator
from mutation_tester import MutationTester, KillRateResult
from comparison_analyzer import ComparisonAnalyzer, ComparisonResult, GateDecision
from mutation_visualizer import MutationVisualizer
from validation_reporter import ValidationReporter

class MutationExperimentRunner:
    def __init__(self, config_path: str, hypothesis_folder: str):
        self.config_path = Path(config_path)
        self.hypothesis_folder = Path(hypothesis_folder)
        self.config = self._load_config()

    def _load_config(self):
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def run(self):
        print("=" * 80)
        print("H-C2 MUTATION TESTING EXPERIMENT")
        print("=" * 80)

        # Setup components
        print("\n[1/6] Setting up components...")
        dataset_loader, spec_synthesizer, mutant_generator, mutation_tester, \
        comparison_analyzer, visualizer, reporter = self._setup_components()

        # Load dataset
        print("\n[2/6] Loading dataset...")
        programs = self._load_dataset(dataset_loader)
        print(f"  Loaded {len(programs)} programs")

        # Synthesize specifications
        print("\n[3/6] Synthesizing specifications...")
        synthesized_specs = self._synthesize_specifications(spec_synthesizer, programs)
        print(f"  Synthesized {len(synthesized_specs)} specifications")

        # Run mutation testing
        print("\n[4/6] Running mutation testing...")
        synthesized_results, gold_results = self._run_mutation_testing(
            mutant_generator, mutation_tester, programs, synthesized_specs
        )
        print(f"  Tested {len(synthesized_results)} programs")

        # Analyze results
        print("\n[5/6] Analyzing results...")
        comparisons, gate_decision, stats = self._analyze_results(
            comparison_analyzer, synthesized_results, gold_results
        )

        # Generate outputs
        print("\n[6/6] Generating outputs...")
        self._generate_outputs(visualizer, reporter, gate_decision, comparisons, stats, programs)

        # Final summary
        print("\n" + "=" * 80)
        print(f"EXPERIMENT COMPLETE")
        print(f"Gate Result: {'PASSED' if gate_decision.gate_passed else 'FAILED'}")
        print(f"Synthesized Kill Rate: {gate_decision.mean_synthesized:.2f}%")
        print(f"Gold Kill Rate: {gate_decision.mean_gold:.2f}%")
        print(f"Relative Performance: {gate_decision.relative_performance:.2f}")
        print("=" * 80)

        return gate_decision

    def _setup_components(self):
        dataset_loader = ACSLByExampleLoader(
            repo_path=self.config['dataset'].get('repo_url', '')
        )

        spec_synthesizer = SpecificationSynthesizer(
            max_iterations=self.config['synthesis'].get('max_iterations', 10)
        )

        operators = [
            ArithmeticMutation(),
            RelationalMutation(),
            BooleanMutation(),
            StatementMutation(),
            BoundaryMutation()
        ]
        mutant_generator = MutantGenerator(operators)

        mutation_tester = MutationTester(
            timeout=self.config['verification'].get('timeout_seconds', 10)
        )

        comparison_analyzer = ComparisonAnalyzer(
            threshold=self.config['comparison'].get('gate_threshold', 0.70)
        )

        visualizer = MutationVisualizer(
            output_dir=str(self.hypothesis_folder / "figures")
        )

        reporter = ValidationReporter(
            hypothesis_folder=str(self.hypothesis_folder)
        )

        return dataset_loader, spec_synthesizer, mutant_generator, mutation_tester, \
               comparison_analyzer, visualizer, reporter

    def _load_dataset(self, dataset_loader: ACSLByExampleLoader) -> List[Program]:
        num_programs = self.config['dataset'].get('num_programs', 30)
        stratified = self.config['dataset'].get('stratified_sampling', True)

        programs = dataset_loader.load_programs(
            num_programs=num_programs,
            stratified=stratified
        )

        return programs

    def _synthesize_specifications(
        self,
        spec_synthesizer: SpecificationSynthesizer,
        programs: List[Program]
    ):
        synthesized_specs = []

        for i, program in enumerate(programs):
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{len(programs)}")

            spec = spec_synthesizer.synthesize_with_feedback(
                program.c_code,
                program.program_id
            )
            synthesized_specs.append(spec)

        return synthesized_specs

    def _run_mutation_testing(
        self,
        mutant_generator: MutantGenerator,
        mutation_tester: MutationTester,
        programs: List[Program],
        synthesized_specs
    ):
        synthesized_results = []
        gold_results = []

        for i, (program, synth_spec) in enumerate(zip(programs, synthesized_specs)):
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{len(programs)}")

            mutants = mutant_generator.generate_mutants(program.c_code)

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                synth_result = mutation_tester.compute_kill_rate(
                    program.program_id,
                    mutants,
                    synth_spec,
                    "synthesized",
                    temp_path / "synthesized"
                )
                synthesized_results.append(synth_result)

                gold_result = mutation_tester.compute_kill_rate(
                    program.program_id,
                    mutants,
                    program.gold_spec,
                    "gold",
                    temp_path / "gold"
                )
                gold_results.append(gold_result)

        return synthesized_results, gold_results

    def _analyze_results(
        self,
        comparison_analyzer: ComparisonAnalyzer,
        synthesized_results: List[KillRateResult],
        gold_results: List[KillRateResult]
    ):
        comparisons = comparison_analyzer.compare_specs(
            synthesized_results,
            gold_results
        )

        gate_decision = comparison_analyzer.compute_gate_decision(comparisons)

        stats = comparison_analyzer.generate_statistics(comparisons)

        return comparisons, gate_decision, stats

    def _generate_outputs(
        self,
        visualizer: MutationVisualizer,
        reporter: ValidationReporter,
        gate_decision: GateDecision,
        comparisons: List[ComparisonResult],
        stats: dict,
        programs: List[Program]
    ):
        # Generate figures
        visualizer.generate_all_figures(comparisons, programs)
        print("  Generated all figures")

        # Generate validation report
        report = reporter.generate_validation_report(gate_decision, comparisons, stats)

        report_path = self.hypothesis_folder / "04_validation.md"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"  Saved validation report to {report_path}")

        # Save checkpoint
        checkpoint_data = {
            "gate_decision": {
                "gate_passed": gate_decision.gate_passed,
                "mean_synthesized": gate_decision.mean_synthesized,
                "mean_gold": gate_decision.mean_gold,
                "threshold": gate_decision.threshold,
                "relative_performance": gate_decision.relative_performance
            },
            "statistics": stats
        }
        reporter.save_checkpoint(checkpoint_data, "final_results")
        print("  Saved checkpoint")

def main():
    hypothesis_folder = Path(__file__).parent.parent
    config_path = hypothesis_folder / "config" / "mutation_config.yaml"

    runner = MutationExperimentRunner(
        config_path=str(config_path),
        hypothesis_folder=str(hypothesis_folder)
    )

    gate_decision = runner.run()

    sys.exit(0 if gate_decision.gate_passed else 1)

if __name__ == "__main__":
    main()
