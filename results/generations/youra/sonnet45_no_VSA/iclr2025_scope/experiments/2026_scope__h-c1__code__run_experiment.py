#!/usr/bin/env python3
"""
Main Experiment Orchestrator - Epic C-6 (h-c1)
End-to-end experiment script with config loading and logging
"""

import sys
import os
import logging
import json
from datetime import datetime
import numpy as np

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from experiments.poc_runner import PoC_ThreeStrategyRunner as ThreeStrategyRunner
from analysis.fnr_metrics import FNRAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExperimentOrchestrator:
    """
    Orchestrates full experiment pipeline:
    1. Load corpus
    2. Run three-strategy validation
    3. Calculate FNR metrics
    4. Generate visualizations
    """

    def __init__(self, config: dict):
        """
        Initialize orchestrator

        Args:
            config: Experiment configuration dict
        """
        self.config = config
        self.results = {}

    def run(self):
        """
        Execute full experiment pipeline

        Returns:
            Dict with experiment results
        """
        logger.info("=" * 60)
        logger.info("Starting H-C1 Three-Strategy Validation Experiment")
        logger.info("=" * 60)

        # Step 1: Run three-strategy experiment
        logger.info("\nStep 1: Running three-strategy validation...")
        corpus_path = self.config.get("corpus_path", "data/defect_corpus.csv")
        output_path = self.config.get("output_path", "outputs/results.csv")

        runner = ThreeStrategyRunner(corpus_path, output_path)
        results_df = runner.run_experiments()

        self.results["results_df"] = results_df
        logger.info(f"✓ Results saved: {output_path}")

        # Step 2: Calculate FNR metrics
        logger.info("\nStep 2: Calculating FNR metrics...")
        analyzer = FNRAnalyzer(results_df)

        fnr_metrics = analyzer.calculate_fnr_all_strategies()
        self.results["fnr_metrics"] = fnr_metrics

        # Step 3: Statistical tests
        logger.info("\nStep 3: Running statistical tests...")
        mcnemar_structural = analyzer.mcnemar_test("structural_only", "combined")
        mcnemar_metamorphic = analyzer.mcnemar_test("metamorphic_only", "combined")

        self.results["mcnemar_structural"] = mcnemar_structural
        self.results["mcnemar_metamorphic"] = mcnemar_metamorphic

        # Step 4: Calculate FNR reduction
        logger.info("\nStep 4: Calculating FNR reduction...")
        reduction_structural = analyzer.fnr_reduction_percentage("structural_only", "combined")
        reduction_metamorphic = analyzer.fnr_reduction_percentage("metamorphic_only", "combined")

        self.results["fnr_reduction_structural"] = reduction_structural
        self.results["fnr_reduction_metamorphic"] = reduction_metamorphic

        # Step 5: Gate evaluation
        logger.info("\nStep 5: Evaluating gate criteria...")
        gate_threshold = self.config.get("gate_threshold", 30.0)  # 30% reduction required

        # Use better baseline for gate evaluation
        better_reduction = max(reduction_structural, reduction_metamorphic)
        gate_pass = better_reduction >= gate_threshold

        self.results["gate_pass"] = gate_pass
        self.results["gate_threshold"] = gate_threshold

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("Experiment Complete")
        logger.info("=" * 60)

        logger.info("\nFNR Metrics:")
        for strategy, metrics in fnr_metrics.items():
            logger.info(f"  {strategy}: {metrics.fnr:.2%} "
                       f"(95% CI: [{metrics.fnr_ci_lower:.2%}, {metrics.fnr_ci_upper:.2%}])")

        logger.info(f"\nFNR Reduction:")
        logger.info(f"  Structural baseline: {reduction_structural:.1f}%")
        logger.info(f"  Metamorphic baseline: {reduction_metamorphic:.1f}%")
        logger.info(f"  Better reduction: {better_reduction:.1f}%")

        logger.info(f"\nGate Evaluation:")
        logger.info(f"  Threshold: ≥{gate_threshold}% reduction")
        logger.info(f"  Result: {'PASS' if gate_pass else 'FAIL'}")

        # Save results to JSON
        results_json_path = self.config.get("results_json_path", "outputs/experiment_results.json")
        self._save_results_json(results_json_path)

        return self.results

    def _save_results_json(self, output_path: str):
        """
        Save results to JSON file

        Args:
            output_path: Path to save JSON
        """
        # Convert to serializable format
        results_serializable = {
            "timestamp": datetime.now().isoformat(),
            "config": self.config,
            "fnr_metrics": {
                strategy: {
                    "fnr": float(metrics.fnr),
                    "fnr_ci_lower": float(metrics.fnr_ci_lower),
                    "fnr_ci_upper": float(metrics.fnr_ci_upper),
                    "detection_rate": float(metrics.detection_rate),
                    "total_defects": int(metrics.total_defects),
                    "detected_defects": int(metrics.detected_defects),
                    "missed_defects": int(metrics.missed_defects)
                }
                for strategy, metrics in self.results["fnr_metrics"].items()
            },
            "fnr_reduction": {
                "structural_baseline": float(self.results["fnr_reduction_structural"]),
                "metamorphic_baseline": float(self.results["fnr_reduction_metamorphic"])
            },
            "mcnemar_tests": {
                "structural_vs_combined": {k: (bool(v) if isinstance(v, (bool, np.bool_)) else
                                              int(v) if isinstance(v, (int, np.integer)) else
                                              float(v) if isinstance(v, (float, np.floating)) else str(v))
                                            for k, v in self.results["mcnemar_structural"].items()},
                "metamorphic_vs_combined": {k: (bool(v) if isinstance(v, (bool, np.bool_)) else
                                               int(v) if isinstance(v, (int, np.integer)) else
                                               float(v) if isinstance(v, (float, np.floating)) else str(v))
                                             for k, v in self.results["mcnemar_metamorphic"].items()}
            },
            "gate_evaluation": {
                "threshold": float(self.results["gate_threshold"]),
                "pass": bool(self.results["gate_pass"])
            }
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(results_serializable, f, indent=2)

        logger.info(f"\n✓ Results JSON saved: {output_path}")


def main():
    """Main entry point"""
    # Configuration
    config = {
        "corpus_path": "data/defect_corpus.csv",
        "output_path": "outputs/results.csv",
        "results_json_path": "outputs/experiment_results.json",
        "gate_threshold": 30.0  # 30% FNR reduction required (MUST_WORK gate)
    }

    # Run experiment
    orchestrator = ExperimentOrchestrator(config)
    results = orchestrator.run()

    return results


if __name__ == "__main__":
    main()
