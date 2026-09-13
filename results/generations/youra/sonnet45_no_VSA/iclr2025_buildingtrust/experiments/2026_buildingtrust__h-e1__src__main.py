"""Main orchestration script for H-E1 meta-analysis."""
import logging
import sys
from pathlib import Path

from config import get_default_config
from data_extraction import BenchmarkCorpusBuilder
from meta_analysis import BenchmarkMetaAnalysis
from visualization import MetaAnalysisVisualizer
from report import ValidationReportGenerator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/experiment.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Execute H-E1 meta-analysis pipeline."""
    logger.info("=" * 60)
    logger.info("H-E1: CV-Stability Meta-Analysis")
    logger.info("=" * 60)

    # Load configuration
    config = get_default_config()
    logger.info(f"Configuration loaded: {config.hypothesis_id}")

    # Create output directories
    Path("data").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)
    Path("figures").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    try:
        # Step 1: Data Extraction
        logger.info("\n[Step 1/5] Data Extraction")
        logger.info("-" * 40)
        corpus_builder = BenchmarkCorpusBuilder(
            min_models=config.statistics.min_models
        )
        benchmark_dict = corpus_builder.build_corpus()
        corpus_builder.save_extraction_log("data/extraction_log.txt")
        logger.info(f"✓ Loaded {len(benchmark_dict)} benchmarks")

        # Step 2: Meta-Analysis
        logger.info("\n[Step 2/5] Meta-Analysis")
        logger.info("-" * 40)
        analyzer = BenchmarkMetaAnalysis(
            min_models=config.statistics.min_models,
            min_shared_models=config.statistics.min_shared_models
        )
        results = analyzer.analyze(benchmark_dict)
        logger.info(f"✓ Analysis complete")

        # Step 3: Visualization
        logger.info("\n[Step 3/5] Visualization")
        logger.info("-" * 40)
        visualizer = MetaAnalysisVisualizer(
            output_dir=config.figures_dir,
            dpi=config.visualization.dpi
        )

        # Extract data for plots
        cv_df = results.cv_per_benchmark
        rho_df = results.mean_rho_per_benchmark
        merged = cv_df.merge(rho_df, on="benchmark_name")

        visualizer.plot_cv_vs_rho_scatter(
            cv_values=merged["cv"].tolist(),
            mean_rho_values=merged["mean_rho"].tolist(),
            benchmark_names=merged["benchmark_name"].tolist(),
            r=results.pearson_r,
            p=results.pearson_p,
            ci_lower=results.ci_lower,
            ci_upper=results.ci_upper
        )
        visualizer.plot_per_benchmark_bars(
            cv_values=merged["cv"].tolist(),
            mean_rho_values=merged["mean_rho"].tolist(),
            benchmark_names=merged["benchmark_name"].tolist()
        )
        visualizer.plot_pairwise_heatmap(results.pairwise_rho_matrix)
        visualizer.plot_gate_comparison(
            target_r=config.statistics.target_pearson_r,
            actual_r=results.pearson_r,
            target_p=config.statistics.target_p_value,
            actual_p=results.pearson_p
        )
        logger.info("✓ All figures generated")

        # Step 4: Report Generation
        logger.info("\n[Step 4/5] Report Generation")
        logger.info("-" * 40)
        report_gen = ValidationReportGenerator(
            hypothesis_id=config.hypothesis_id,
            output_dir=config.output_dir
        )
        report_gen.save_artifacts(results, benchmark_dict)

        # Generate validation report
        validation_md = report_gen.generate_validation_md(results)
        with open("04_validation.md", "w") as f:
            f.write(validation_md)
        logger.info("✓ Validation report saved to 04_validation.md")

        # Step 5: Gate Decision
        logger.info("\n[Step 5/5] Gate Decision")
        logger.info("-" * 40)
        logger.info(f"Hypothesis Test:")
        logger.info(f"  Pearson r: {results.pearson_r:.3f}")
        logger.info(f"  p-value: {results.pearson_p:.4f}")
        logger.info(f"  95% CI: [{results.ci_lower:.3f}, {results.ci_upper:.3f}]")
        logger.info(f"\nGate Criteria:")
        logger.info(f"  Target r < -0.5: {results.pearson_r < -0.5} {'✓' if results.pearson_r < -0.5 else '✗'}")
        logger.info(f"  Target p < 0.05: {results.pearson_p < 0.05} {'✓' if results.pearson_p < 0.05 else '✗'}")
        logger.info(f"\nMUST_WORK Gate: {'✅ PASSED' if results.gate_passed else '❌ FAILED'}")

        if results.gate_passed:
            logger.info("\n✓ Hypothesis H-E1 VALIDATED")
            logger.info("  → Proceed to mechanism hypotheses (H-M1, H-M2, H-C1)")
            return 0
        else:
            logger.warning("\n✗ Hypothesis H-E1 REJECTED")
            logger.warning("  → Route to Phase 0 for fundamental redesign")
            return 1

    except Exception as e:
        logger.error(f"\n✗ Pipeline failed: {e}", exc_info=True)
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
