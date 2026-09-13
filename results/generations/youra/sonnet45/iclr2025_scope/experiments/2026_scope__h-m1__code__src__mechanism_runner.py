"""Mechanism Experiment Runner for h-m1."""

import json
import os
from datetime import datetime
from typing import Dict, Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .config import load_mechanism_config
from .analyzer import LowRankAnalyzer
from .data import PileDataModule
from .stability import ContextStabilityTester
from .validator import MechanismValidator
from .visualize import AnalysisVisualizer


class MechanismExperimentRunner:
    """Runs mechanism validation experiment for h-m1."""

    def __init__(self, config=None):
        """Initialize experiment runner."""
        self.config = config or load_mechanism_config()
        self.analyzer = None
        self.stability_tester = None
        self.validator = None
        self.results_dir = "../results"
        os.makedirs(self.results_dir, exist_ok=True)

    def setup_base_analyzer(self) -> LowRankAnalyzer:
        """Set up base analyzer from h-e1."""
        print("Loading model and tokenizer...")
        model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            torch_dtype=torch.float16 if self.config.use_fp16 else torch.float32,
            device_map="auto",
            trust_remote_code=True,
            attn_implementation="eager"  # Required for output_attentions=True
        )

        analyzer = LowRankAnalyzer(
            model=model,
            target_layers=self.config.target_layers,
            variance_threshold=self.config.variance_threshold
        )

        print(f"✓ Analyzer initialized for layers {min(self.config.target_layers)}-{max(self.config.target_layers)}")
        return analyzer

    def run_base_analysis(self) -> Dict[str, Any]:
        """Run base SVD/entropy analysis."""
        print("\n" + "=" * 80)
        print("RUNNING BASE ANALYSIS")
        print("=" * 80)

        # Load tokenizer and data
        tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        data_module = PileDataModule(
            tokenizer=tokenizer,
            context_length=self.config.context_length,
            batch_size=self.config.batch_size
        )
        data_module.setup(num_samples=self.config.num_samples)
        dataloader = data_module.get_dataloader()

        # Run analysis
        results = self.analyzer.analyze_layers(dataloader, num_samples=self.config.num_samples)

        print(f"✓ Base analysis completed for {len(results)} layers")
        return results

    def run_stability_tests(self) -> Dict[str, Any]:
        """Run context stability tests."""
        print("\n" + "=" * 80)
        print("RUNNING STABILITY TESTS")
        print("=" * 80)

        # Create dataloader factory
        tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        def dataloader_factory(context_length: int):
            data_module = PileDataModule(
                tokenizer=tokenizer,
                context_length=context_length,
                batch_size=self.config.batch_size
            )
            data_module.setup(num_samples=self.config.samples_per_context)
            return data_module.get_dataloader()

        # Run stability tests
        stability_results = self.stability_tester.test_context_stability(
            dataloader_factory,
            num_samples_per_length=self.config.samples_per_context
        )

        print(f"✓ Stability tests completed for {len(self.config.context_lengths)} context lengths")
        return stability_results

    def validate_mechanism(
        self,
        base_results: Dict[str, Any],
        stability_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate mechanism hypothesis."""
        print("\n" + "=" * 80)
        print("VALIDATING MECHANISM")
        print("=" * 80)

        # Run validation checks
        is_activated, activation_details = self.validator.verify_mechanism_activated(base_results)
        compression_results = self.validator.verify_compression_mechanism(base_results)
        gate_results = self.validator.validate_gate_criteria(base_results, stability_results)

        validation = {
            'timestamp': datetime.now().isoformat(),
            'mechanism_activated': is_activated,
            'activation_details': activation_details,
            'compression_results': compression_results,
            'gate_results': gate_results
        }

        # Print report
        report = self.validator.generate_validation_report(gate_results)
        print("\n" + report)

        return validation

    def generate_report(self, validation_results: Dict[str, Any]) -> None:
        """Generate validation report and save results."""
        print("\n" + "=" * 80)
        print("GENERATING REPORT")
        print("=" * 80)

        # Save results to JSON
        results_file = os.path.join(self.results_dir, "mechanism_validation.json")
        with open(results_file, 'w') as f:
            json.dump(validation_results, f, indent=2, default=str)

        print(f"✓ Results saved to: {results_file}")

    def run(self):
        """Run complete mechanism validation experiment."""
        print("\n" + "=" * 80)
        print("MECHANISM VALIDATION EXPERIMENT (h-m1)")
        print("=" * 80)
        print(f"Model: {self.config.model_name}")
        print(f"Target layers: {min(self.config.target_layers)}-{max(self.config.target_layers)}")
        print(f"Context lengths: {self.config.context_lengths}")
        print(f"Samples: {self.config.num_samples} (base), {self.config.samples_per_context} (per context)")
        print("=" * 80)

        # Setup
        self.analyzer = self.setup_base_analyzer()
        self.stability_tester = ContextStabilityTester(
            analyzer=self.analyzer,
            context_lengths=self.config.context_lengths
        )
        self.validator = MechanismValidator(
            analyzer=self.analyzer,
            stability_tester=self.stability_tester
        )

        # Run experiment
        base_results = self.run_base_analysis()
        stability_results = self.run_stability_tests()
        validation = self.validate_mechanism(base_results, stability_results)
        self.generate_report(validation)

        # Return gate result
        gate_result = validation['gate_results']['gate_result']
        print(f"\n{'=' * 80}")
        print(f"FINAL GATE RESULT: {gate_result}")
        print(f"{'=' * 80}\n")

        return validation


def main():
    """Main entry point."""
    runner = MechanismExperimentRunner()
    results = runner.run()
    return results


if __name__ == "__main__":
    main()
