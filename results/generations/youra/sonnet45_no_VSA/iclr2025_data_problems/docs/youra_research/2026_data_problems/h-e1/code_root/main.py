"""Main experiment orchestrator for H-E1."""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from config import ExperimentConfig, validate_config
from src.coupling_extractor import CouplingMetricsExtractor
from src.data_loader import CodeNetLoader
from src.variance_analyzer import VarianceAnalyzer
from src.visualizer import ResultVisualizer


def setup_logging(config: ExperimentConfig) -> logging.Logger:
    """Configure logging."""
    config.log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(config.log_path),
            logging.StreamHandler(sys.stdout),
        ],
    )

    return logging.getLogger(__name__)


def save_results(
    config: ExperimentConfig,
    metrics: list,
    per_problem_cv: dict,
    gate_status: dict,
    statistics: dict,
) -> None:
    """Save results to JSON files."""
    # Save metrics
    metrics_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "config": {
                "dataset_name": config.dataset_name,
                "num_problems": config.num_problems,
                "cv_threshold": config.cv_threshold,
                "extraction_rate_threshold": config.extraction_rate_threshold,
            },
        },
        "submissions": [
            {
                "problem_id": m.problem_id,
                "submission_id": m.submission_id,
                "coupling_score": m.coupling_score,
                "fan_in": m.fan_in,
                "fan_out": m.fan_out,
                "centrality": m.centrality,
            }
            for m in metrics
        ],
    }

    config.results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config.results_path, "w") as f:
        json.dump(metrics_data, f, indent=2)

    # Save CV analysis
    cv_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
        },
        "gate_validation": {
            "average_cv": statistics["cv"]["average"],
            "cv_threshold": config.cv_threshold,
            "gate_passed": gate_status["cv_passed"] and gate_status["extraction_passed"],
            "cv_passed": gate_status["cv_passed"],
            "extraction_passed": gate_status["extraction_passed"],
        },
        "per_problem_cv": [
            {
                "problem_id": pid,
                "cv": cv,
            }
            for pid, cv in per_problem_cv.items()
        ],
        "statistics": statistics,
    }

    with open(config.cv_analysis_path, "w") as f:
        json.dump(cv_data, f, indent=2)


def main():
    """Execute full experiment pipeline."""
    # Initialize configuration
    config = ExperimentConfig()
    validate_config(config)

    # Setup logging
    logger = setup_logging(config)
    logger.info("="*80)
    logger.info("Starting H-E1 Static Coupling Metrics Extraction Experiment")
    logger.info("="*80)

    # Phase 1: Data Loading
    logger.info("\n" + "="*80)
    logger.info("Phase 1: Data Loading")
    logger.info("="*80)

    loader = CodeNetLoader(cache_dir=config.cache_path)
    problems_dict, stats = loader.prepare_dataset()

    logger.info(f"\nDataset loaded:")
    logger.info(f"  - Problems: {stats['total_problems']}")
    logger.info(f"  - Submissions: {stats['total_submissions']}")
    logger.info(f"  - Parse failures: {stats['parse_failures']}")

    # Phase 2: Metrics Extraction
    logger.info("\n" + "="*80)
    logger.info("Phase 2: Metrics Extraction")
    logger.info("="*80)

    extractor = CouplingMetricsExtractor()
    all_metrics = []
    extraction_failures = 0

    total_subs = sum(len(subs) for subs in problems_dict.values())
    processed = 0

    for problem_id, submissions in problems_dict.items():
        for sub in submissions:
            # Single-file assumption (most CodeNet submissions are single file)
            code_files = {"main.py": sub.get("code", "")}
            submission_id = sub.get("id", f"sub_{processed}")

            metrics = extractor.analyze_submission(problem_id, submission_id, code_files)

            if metrics is None:
                extraction_failures += 1
            else:
                all_metrics.append(metrics)

            processed += 1

            # Log progress
            if processed % config.log_progress_interval == 0:
                pct = (processed / total_subs) * 100
                logger.info(f"  Progress: {processed}/{total_subs} ({pct:.1f}%)")

    extraction_rate = 1.0 - (extraction_failures / total_subs) if total_subs > 0 else 0.0

    logger.info(f"\nExtraction complete:")
    logger.info(f"  - Successful: {len(all_metrics)}")
    logger.info(f"  - Failed: {extraction_failures}")
    logger.info(f"  - Extraction rate: {extraction_rate:.2%}")

    # Phase 3: Variance Analysis
    logger.info("\n" + "="*80)
    logger.info("Phase 3: Variance Analysis")
    logger.info("="*80)

    analyzer = VarianceAnalyzer()
    per_problem_cv = analyzer.analyze_per_problem_variance(all_metrics)
    average_cv = analyzer.compute_average_cv(per_problem_cv)
    gate_status = analyzer.validate_gate(average_cv, extraction_rate)
    statistics = analyzer.get_statistics(all_metrics, per_problem_cv)

    logger.info(f"\nVariance analysis:")
    logger.info(f"  - Average CV: {average_cv:.3f}")
    logger.info(f"  - CV range: [{statistics['cv']['min']:.3f}, {statistics['cv']['max']:.3f}]")
    logger.info(f"  - Problems with CV > 0.3: {sum(1 for cv in per_problem_cv.values() if cv > 0.3)}/{len(per_problem_cv)}")

    # Phase 4: Visualization
    logger.info("\n" + "="*80)
    logger.info("Phase 4: Visualization")
    logger.info("="*80)

    visualizer = ResultVisualizer(output_dir=config.figures_dir)
    figures = visualizer.generate_all_figures(
        all_metrics, per_problem_cv, average_cv, extraction_rate
    )

    logger.info(f"\nGenerated figures:")
    for name, path in figures.items():
        logger.info(f"  - {name}: {path}")

    # Phase 5: Save Results
    logger.info("\n" + "="*80)
    logger.info("Phase 5: Save Results")
    logger.info("="*80)

    save_results(config, all_metrics, per_problem_cv, gate_status, statistics)

    logger.info(f"\nResults saved:")
    logger.info(f"  - Metrics: {config.results_path}")
    logger.info(f"  - CV analysis: {config.cv_analysis_path}")

    # Phase 6: Gate Validation
    logger.info("\n" + "="*80)
    logger.info("Phase 6: Gate Validation")
    logger.info("="*80)

    cv_passed = gate_status["cv_passed"]
    extraction_passed = gate_status["extraction_passed"]
    overall_passed = cv_passed and extraction_passed

    logger.info(f"\nGate validation results:")
    logger.info(f"  - CV > 0.3: {'PASS' if cv_passed else 'FAIL'} (actual: {average_cv:.3f})")
    logger.info(f"  - Extraction > 95%: {'PASS' if extraction_passed else 'FAIL'} (actual: {extraction_rate:.2%})")
    logger.info(f"  - Overall: {'PASS' if overall_passed else 'FAIL'}")

    logger.info("\n" + "="*80)
    if overall_passed:
        logger.info("✓ EXPERIMENT COMPLETE - GATE PASSED")
    else:
        logger.info("✗ EXPERIMENT COMPLETE - GATE FAILED")
    logger.info("="*80)

    return 0 if overall_passed else 1


if __name__ == "__main__":
    sys.exit(main())
