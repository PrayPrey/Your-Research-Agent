"""Main execution script for H-E2 SAT profiling experiment."""

import logging
import json
from pathlib import Path
import sys
import os

# Add src to path - ensure we can import from src package
src_dir = Path(__file__).parent.absolute()
parent_dir = src_dir.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Change to src directory for consistent paths
os.chdir(src_dir)

from config import (
    ExperimentConfig,
    get_cnn_configs,
    get_transformer_configs,
    set_reproducibility,
    log_environment
)
from experiment.runner import ExperimentRunner
from evaluation.metrics import (
    compute_precision_recall,
    compute_confusion_matrix,
    evaluate_causality,
    compute_precision_recall_curve
)
from visualization.plotter import (
    plot_sat_vs_degradation,
    plot_precision_recall_curve,
    plot_jitter_validation,
    plot_architecture_sat_distribution,
    plot_confusion_matrix,
    plot_gate_metrics_comparison
)


def setup_logging(config: ExperimentConfig):
    """Configure logging."""
    logging.basicConfig(
        level=getattr(logging, config.output.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.output.hypothesis_folder / 'results' / 'experiment.log'),
            logging.StreamHandler()
        ]
    )


def main():
    """Main experiment execution."""
    # Initialize configuration
    config = ExperimentConfig()
    setup_logging(config)

    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("H-E2: GPU-normalized SAT Profiling Experiment")
    logger.info("=" * 80)

    # Setup reproducibility
    set_reproducibility(config.reproducibility)
    log_environment(config.reproducibility)

    # Initialize experiment runner
    results_dir = config.output.hypothesis_folder / "results"
    runner = ExperimentRunner(str(results_dir))

    # Get configurations (reduced for PoC)
    cnn_configs = get_cnn_configs()
    transformer_configs = get_transformer_configs()
    all_configs = cnn_configs + transformer_configs

    logger.info(f"Total configurations: {len(all_configs)}")
    logger.info(f"  - CNN configs: {len(cnn_configs)}")
    logger.info(f"  - Transformer configs: {len(transformer_configs)}")

    # Phase 1: Run natural workload experiments
    logger.info("\n" + "=" * 80)
    logger.info("Phase 1: Natural Workload Profiling")
    logger.info("=" * 80)

    natural_results = runner.run_natural_workload(all_configs)
    runner.save_results(natural_results, "profiling_results.json")

    logger.info(f"Completed {len(natural_results)} / {len(all_configs)} configurations")

    # Phase 2: Run synthetic jitter experiments
    logger.info("\n" + "=" * 80)
    logger.info("Phase 2: Synthetic Jitter Experiments")
    logger.info("=" * 80)

    # Use first CNN config as base for jitter experiments
    jitter_base_config = cnn_configs[0]
    jitter_results = runner.run_synthetic_jitter(
        jitter_base_config,
        config.jitter.delay_levels
    )

    jitter_data = {
        "base_config": jitter_base_config.model_name,
        "results": jitter_results
    }
    runner.save_results(jitter_data, "jitter_results.json")

    # Phase 3: Compute metrics
    logger.info("\n" + "=" * 80)
    logger.info("Phase 3: Metrics Evaluation")
    logger.info("=" * 80)

    # Extract SAT values and degradations
    SAT_values = [r["SAT"] for r in natural_results.values() if r is not None]
    degradations = [r["degradation"] for r in natural_results.values() if r is not None]
    architectures = [r["architecture"] for r in natural_results.values() if r is not None]

    if len(SAT_values) < 2:
        logger.error("Not enough valid results for evaluation")
        sys.exit(1)

    # Compute precision, recall, F1
    precision, recall, f1 = compute_precision_recall(
        SAT_values,
        degradations,
        threshold=config.analysis.sat_threshold
    )

    logger.info(f"Precision: {precision:.3f} (target: {config.analysis.precision_target:.3f})")
    logger.info(f"Recall: {recall:.3f} (target: {config.analysis.recall_target:.3f})")
    logger.info(f"F1-Score: {f1:.3f} (target: {config.analysis.f1_target:.3f})")

    # Compute confusion matrix
    cm = compute_confusion_matrix(SAT_values, degradations, threshold=config.analysis.sat_threshold)
    logger.info(f"Confusion Matrix:\n{cm}")

    # Evaluate causality
    if jitter_results and len(jitter_results) > 1:
        SAT_natural = jitter_results.get(0, SAT_values[0] if SAT_values else 1.0)
        causality_metrics = evaluate_causality(
            SAT_natural,
            jitter_results,
            gpu_util=50.0  # Placeholder
        )
        logger.info(f"Causality Metrics: {causality_metrics}")
    else:
        causality_metrics = {"causality_validated": False}

    # Gate validation
    logger.info("\n" + "=" * 80)
    logger.info("GATE VALIDATION (MUST_WORK)")
    logger.info("=" * 80)

    gate_passed = (
        precision >= config.analysis.precision_target and
        recall >= config.analysis.recall_target
    )

    logger.info(f"Gate Status: {'PASS' if gate_passed else 'FAIL'}")
    logger.info(f"  - Precision: {precision:.3f} >= {config.analysis.precision_target:.3f}: {precision >= config.analysis.precision_target}")
    logger.info(f"  - Recall: {recall:.3f} >= {config.analysis.recall_target:.3f}: {recall >= config.analysis.recall_target}")

    # Save metrics summary
    metrics_summary = {
        "gate_type": "MUST_WORK",
        "gate_passed": gate_passed,
        "metrics": {
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1)
        },
        "targets": {
            "precision": config.analysis.precision_target,
            "recall": config.analysis.recall_target,
            "f1": config.analysis.f1_target
        },
        "confusion_matrix": cm.tolist(),
        "causality": causality_metrics,
        "num_configs_evaluated": len(SAT_values)
    }

    runner.save_results(metrics_summary, "metrics_summary.json")

    # Phase 4: Generate visualizations
    logger.info("\n" + "=" * 80)
    logger.info("Phase 4: Visualization Generation")
    logger.info("=" * 80)

    figures_dir = config.output.hypothesis_folder / config.output.figures_subdir
    figures_dir.mkdir(parents=True, exist_ok=True)

    # 1. SAT vs Degradation scatter plot
    plot_sat_vs_degradation(
        SAT_values,
        degradations,
        architectures,
        str(figures_dir / "sat_vs_degradation.png")
    )
    logger.info("Generated: sat_vs_degradation.png")

    # 2. Precision-Recall curve
    thresholds, precisions, recalls = compute_precision_recall_curve(SAT_values, degradations)
    plot_precision_recall_curve(
        thresholds,
        precisions,
        recalls,
        str(figures_dir / "precision_recall_curve.png")
    )
    logger.info("Generated: precision_recall_curve.png")

    # 3. Jitter validation
    if jitter_results:
        plot_jitter_validation(
            {"Experiment": jitter_results},
            str(figures_dir / "jitter_validation.png")
        )
        logger.info("Generated: jitter_validation.png")

    # 4. Architecture SAT distribution
    plot_architecture_sat_distribution(
        natural_results,
        str(figures_dir / "architecture_sat_dist.png")
    )
    logger.info("Generated: architecture_sat_dist.png")

    # 5. Confusion matrix
    plot_confusion_matrix(
        cm,
        str(figures_dir / "confusion_matrix.png")
    )
    logger.info("Generated: confusion_matrix.png")

    # 6. Gate metrics comparison
    plot_gate_metrics_comparison(
        metrics_summary["metrics"],
        metrics_summary["targets"],
        str(figures_dir / "gate_metrics_comparison.png")
    )
    logger.info("Generated: gate_metrics_comparison.png")

    logger.info("\n" + "=" * 80)
    logger.info("Experiment Complete")
    logger.info("=" * 80)
    logger.info(f"Results saved to: {results_dir}")
    logger.info(f"Figures saved to: {figures_dir}")
    logger.info(f"Gate Status: {'PASS' if gate_passed else 'FAIL'}")

    return 0 if gate_passed else 1


if __name__ == "__main__":
    sys.exit(main())
