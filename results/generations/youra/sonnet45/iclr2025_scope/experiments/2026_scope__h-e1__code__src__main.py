"""Main experiment runner for low-rank analysis."""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .config import AnalysisConfig, load_config
from .data import PileDataModule
from .analyzer import LowRankAnalyzer
from .visualize import AnalysisVisualizer
from .metrics import MetricsComputer


class ExperimentRunner:
    """Orchestrate low-rank structure analysis experiment."""

    def __init__(self, config: AnalysisConfig):
        """Initialize experiment runner.

        Args:
            config: Analysis configuration
        """
        self.config = config
        self.model: Optional[AutoModelForCausalLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        self.analyzer: Optional[LowRankAnalyzer] = None
        self.dataloader = None
        self.visualizer = AnalysisVisualizer(config.output_dir)

        # Set random seed
        torch.manual_seed(config.random_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(config.random_seed)

    def setup_model(self) -> AutoModelForCausalLM:
        """Load LLaMA model with configuration.

        Returns:
            Loaded model
        """
        print(f"Loading model: {self.config.model_name}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            token=self.config.hf_token,
            use_fast=False,
        )

        # Set pad token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load model
        dtype = torch.float16 if self.config.use_fp16 else torch.float32
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            token=self.config.hf_token,
            torch_dtype=dtype,
            device_map="auto",
            low_cpu_mem_usage=True,
        )

        self.model.eval()
        print(f"Model loaded on device: {self.model.device}")

        return self.model

    def setup_data(self):
        """Prepare dataset and dataloader.

        Returns:
            Configured DataLoader
        """
        print(f"Setting up data pipeline (num_samples={self.config.num_samples})")

        data_module = PileDataModule(
            tokenizer=self.tokenizer,
            context_length=self.config.context_length,
            batch_size=self.config.batch_size,
        )

        data_module.setup(num_samples=self.config.num_samples)
        self.dataloader = data_module.get_dataloader()

        print("Data pipeline ready")
        return self.dataloader

    def run_analysis(self) -> Dict[str, Any]:
        """Execute full analysis pipeline.

        Returns:
            Results dictionary with layers data and regression statistics
        """
        print("\n" + "=" * 60)
        print("STARTING LOW-RANK STRUCTURE ANALYSIS")
        print("=" * 60 + "\n")

        # Setup
        if self.model is None:
            self.setup_model()
        if self.dataloader is None:
            self.setup_data()

        # Initialize analyzer
        self.analyzer = LowRankAnalyzer(
            model=self.model,
            target_layers=self.config.target_layers,
            variance_threshold=self.config.variance_threshold,
        )

        # Run analysis
        print(f"\nAnalyzing layers {list(self.config.target_layers)}")
        num_batches = self.config.num_samples // self.config.batch_size
        print(f"Processing {num_batches} batches...\n")

        layers_results = self.analyzer.analyze_layers(
            self.dataloader, num_samples=num_batches
        )

        # Compute regression for entropy
        print("\nComputing entropy regression...")
        layer_indices = sorted(layers_results.keys())
        entropies = [layers_results[idx]["operator_entropy"] for idx in layer_indices]

        regression_stats = MetricsComputer.entropy_regression(
            layer_indices, entropies
        )

        print(f"Regression: β={regression_stats['slope']:.4f}, p={regression_stats['p_value']:.4e}")

        # Generate visualizations
        print("\nGenerating visualizations...")
        self.visualizer.plot_rank_vs_depth(layers_results)
        self.visualizer.plot_entropy_regression(layers_results, regression_stats)

        # Plot singular values for middle layer
        mid_layer = layer_indices[len(layer_indices) // 2]
        self.visualizer.plot_singular_values(
            mid_layer, layers_results[mid_layer]["singular_values"]
        )

        # Sensitivity analysis
        print("Running sensitivity analysis...")
        thresholds = [0.90, 0.95, 0.99, 0.999]
        ranks_by_threshold = {}
        for threshold in thresholds:
            ranks = []
            for layer_idx in layer_indices:
                attn = layers_results[layer_idx]["singular_values"]
                rank = MetricsComputer.svd_effective_rank(attn.unsqueeze(0), threshold)
                ranks.append(rank)
            ranks_by_threshold[threshold] = ranks

        self.visualizer.plot_rank_sensitivity(thresholds, ranks_by_threshold)

        # Gate metrics
        max_rank = max(
            layers_results[idx]["effective_rank"] for idx in layer_indices
        )
        target_metrics = {"max_rank": 256, "entropy_slope": 0}
        actual_metrics = {
            "max_rank": max_rank,
            "entropy_slope": regression_stats["slope"],
        }
        self.visualizer.plot_gate_metrics(target_metrics, actual_metrics)

        print("Visualizations saved to:", self.config.output_dir)

        # Compile results
        results = {
            "layers": {
                idx: {
                    "effective_rank": layers_results[idx]["effective_rank"],
                    "operator_entropy": layers_results[idx]["operator_entropy"],
                }
                for idx in layer_indices
            },
            "regression": regression_stats,
            "max_rank": max_rank,
            "timestamp": datetime.now().isoformat(),
        }

        # Save results
        results_file = os.path.join(self.config.output_dir, "results.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"Results saved to: {results_file}")

        return results

    def validate_results(self, results: Dict[str, Any]) -> bool:
        """Check MUST_WORK gate criteria.

        Args:
            results: Analysis results

        Returns:
            True if both criteria pass
        """
        print("\n" + "=" * 60)
        print("VALIDATING GATE CRITERIA (MUST_WORK)")
        print("=" * 60 + "\n")

        # Criterion 1: r_eff < 256 for all layers
        layers_data = results["layers"]
        criterion1_pass = True
        for layer_idx in sorted(layers_data.keys()):
            rank = layers_data[layer_idx]["effective_rank"]
            status = "✓" if rank < 256 else "✗"
            print(f"Layer {layer_idx}: r_eff={rank:.2f} {status}")
            if rank >= 256:
                criterion1_pass = False

        print(f"\nCriterion 1 (r_eff < 256): {'PASS ✓' if criterion1_pass else 'FAIL ✗'}")

        # Criterion 2: β < 0 with p < 0.01
        regression = results["regression"]
        slope = regression["slope"]
        p_value = regression["p_value"]

        criterion2_pass = slope < 0 and p_value < 0.01

        print(f"Criterion 2 (β < 0, p < 0.01): β={slope:.4f}, p={p_value:.4e}")
        print(f"Criterion 2: {'PASS ✓' if criterion2_pass else 'FAIL ✗'}")

        # Overall gate
        gate_pass = criterion1_pass and criterion2_pass

        print("\n" + "=" * 60)
        print(f"GATE RESULT: {'PASS ✓✓✓' if gate_pass else 'FAIL ✗✗✗'}")
        print("=" * 60 + "\n")

        return gate_pass

    def generate_report(self, results: Dict[str, Any], gate_pass: bool) -> None:
        """Generate 04_validation.md report.

        Args:
            results: Analysis results
            gate_pass: Whether gate criteria passed
        """
        report_path = "04_validation.md"

        with open(report_path, "w") as f:
            f.write("# Validation Report: h-e1\n\n")
            f.write(f"**Date:** {results['timestamp']}\n")
            f.write(f"**Hypothesis:** Low-Rank Structure Existence (h-e1)\n")
            f.write(f"**Gate Type:** MUST_WORK\n")
            f.write(f"**Result:** {'PASS ✓' if gate_pass else 'FAIL ✗'}\n\n")

            f.write("---\n\n")
            f.write("## Summary\n\n")

            if gate_pass:
                f.write("✓ Deep Transformer layers (L≥20) exhibit low-rank structure with r_eff < 256\n")
                f.write("✓ Operator entropy decreases monotonically with layer depth (β < 0, p < 0.01)\n")
                f.write("\n**Conclusion:** Bounded-state compression assumption VALIDATED. Proceed to h-m1.\n")
            else:
                f.write("✗ Gate criteria NOT satisfied\n")
                f.write("\n**Conclusion:** ABORT SSM conversion approach. Low-rank assumption invalid.\n")

            f.write("\n---\n\n")
            f.write("## Detailed Results\n\n")

            f.write("### Effective Rank (per layer)\n\n")
            f.write("| Layer | Effective Rank | Status |\n")
            f.write("|-------|---------------|--------|\n")

            for layer_idx in sorted(results["layers"].keys()):
                rank = results["layers"][layer_idx]["effective_rank"]
                status = "✓ PASS" if rank < 256 else "✗ FAIL"
                f.write(f"| {layer_idx} | {rank:.2f} | {status} |\n")

            f.write(f"\n**Maximum rank:** {results['max_rank']:.2f}\n")
            f.write(f"**Threshold:** 256\n\n")

            f.write("### Operator Entropy Regression\n\n")
            reg = results["regression"]
            f.write(f"- **Slope (β):** {reg['slope']:.4f}\n")
            f.write(f"- **P-value:** {reg['p_value']:.4e}\n")
            f.write(f"- **R-squared:** {reg['r_squared']:.3f}\n")
            f.write(f"- **Status:** {'✓ PASS (β < 0, p < 0.01)' if reg['slope'] < 0 and reg['p_value'] < 0.01 else '✗ FAIL'}\n\n")

            f.write("### Visualizations\n\n")
            f.write("Generated figures:\n")
            f.write("- `figures/rank_vs_depth.png`\n")
            f.write("- `figures/entropy_regression.png`\n")
            f.write("- `figures/singular_values_layer_*.png`\n")
            f.write("- `figures/rank_sensitivity.png`\n")
            f.write("- `figures/gate_metrics.png`\n\n")

            f.write("---\n\n")
            f.write("*Generated by Phase 4 Experiment Runner*\n")

        print(f"\nValidation report saved: {report_path}")


def main():
    """Entry point for low-rank analysis experiment."""
    # Load configuration
    config = load_config()

    # Run experiment
    runner = ExperimentRunner(config)
    results = runner.run_analysis()

    # Validate and report
    gate_pass = runner.validate_results(results)
    runner.generate_report(results, gate_pass)

    return 0 if gate_pass else 1


if __name__ == "__main__":
    exit(main())
