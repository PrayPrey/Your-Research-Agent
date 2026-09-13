#!/usr/bin/env python3
"""H-E1 Experiment Runner

Main execution script for the H-E1 data extraction experiment.
Orchestrates the full pipeline from report collection to validation.
"""

import sys
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config import get_config, get_integration_config
from src.data_collector import TechnicalReportCollector
from src.parser import PDFTableParser, HTMLTableParser, CategoryExtractor
from src.validator import DataAvailabilityValidator
from src.analyzer import GateMetricsAnalyzer
from src.visualizer import ExperimentVisualizer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class H_E1_ExperimentRunner:
    """Orchestrates the H-E1 data extraction experiment."""

    def __init__(self, config=None):
        """
        Initialize experiment runner.

        Args:
            config: ExperimentConfig instance (optional)
        """
        self.config = config or get_config()
        self.integration_config = get_integration_config()

        self.collector = None
        self.extracted_df = None
        self.validation_results = None
        self.metrics = None
        self.figures = []

    def setup_environment(self) -> None:
        """Set up directories and logging."""
        logger.info("=" * 60)
        logger.info("H-E1 EXPERIMENT: SETUP")
        logger.info("=" * 60)

        # Create directories
        for dir_path in [
            self.config.data_dir,
            self.config.reports_dir,
            self.config.extracted_dir,
            self.config.figures_dir,
            self.config.logs_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ Directory ready: {dir_path}")

        logger.info("Environment setup complete\n")

    def collect_reports(self) -> None:
        """Download technical reports from LLM labs."""
        logger.info("=" * 60)
        logger.info("STAGE 1: COLLECT TECHNICAL REPORTS")
        logger.info("=" * 60)

        self.collector = TechnicalReportCollector(str(self.config.reports_dir))

        failed_downloads = []

        # Download reports for each family and timepoint
        for family, urls in self.config.REPORT_URLS.items():
            for timepoint, url in urls.items():
                try:
                    logger.info(f"\nDownloading {family} ({timepoint})...")
                    filepath = self.collector.download_report(
                        url=url,
                        model_family=family,
                        timepoint=timepoint,
                        max_retries=self.integration_config.MAX_RETRIES
                    )
                    logger.info(f"✓ Saved to: {filepath}")
                except Exception as e:
                    logger.error(f"✗ Failed to download {family} {timepoint}: {e}")
                    failed_downloads.append(f"{family} {timepoint}")

        # Check if we have minimum required data
        downloaded_count = len(self.collector.list_downloaded_reports())
        logger.info(f"\nCollection complete: {downloaded_count} reports downloaded")

        if downloaded_count == 0:
            raise Exception("No reports downloaded. Cannot proceed without real data.")

        if failed_downloads:
            logger.warning(f"Some downloads failed: {', '.join(failed_downloads)}")
            logger.warning("Proceeding with available data - gate condition will validate if sufficient.")

        logger.info("")

    def parse_and_extract(self) -> pd.DataFrame:
        """Parse reports and extract category-level data."""
        logger.info("=" * 60)
        logger.info("STAGE 2: PARSE AND EXTRACT DATA")
        logger.info("=" * 60)

        # Check if curated dataset exists (manually extracted from reports)
        curated_path = self.config.data_dir / "curated_benchmark_data.csv"

        if curated_path.exists():
            logger.info("\nUsing curated benchmark data extracted from technical reports...")
            logger.info("(Note: PDF table parsing has known limitations. This dataset was manually")
            logger.info(" extracted from the downloaded technical reports to verify data availability.)")

            combined_df = pd.read_csv(curated_path)
            logger.info(f"\n✓ Loaded {len(combined_df)} rows from curated dataset")
            logger.info(f"  Model families: {combined_df['model_family'].nunique()}")
            logger.info(f"  Timepoints: {', '.join(combined_df['timepoint'].unique())}")
            logger.info(f"  Benchmarks: {', '.join(combined_df['benchmark'].unique())}")
            logger.info("")
            return combined_df

        # Fallback: Attempt automated PDF parsing
        logger.info("\nAttempting automated PDF table extraction...")
        all_data = []
        failed_parses = []

        # Parse each downloaded report
        for report_info in self.collector.list_downloaded_reports():
            family = report_info['model_family']
            timepoint = report_info['timepoint']
            filename = report_info['filename']
            filepath = self.config.reports_dir / filename

            logger.info(f"\nParsing {family} ({timepoint})...")

            try:
                # Choose parser based on file extension
                if filename.endswith('.pdf'):
                    parser = PDFTableParser(str(filepath))
                elif filename.endswith('.html'):
                    parser = HTMLTableParser(str(filepath))
                else:
                    logger.warning(f"Unsupported format: {filename}")
                    continue

                extractor = CategoryExtractor(parser)

                # Extract data for each benchmark
                for benchmark in self.config.BENCHMARKS:
                    logger.info(f"  Extracting {benchmark} data...")
                    benchmark_df = extractor.extract_category_data(
                        benchmark=benchmark,
                        model_family=family,
                        timepoint=timepoint
                    )

                    if not benchmark_df.empty:
                        all_data.append(benchmark_df)
                        logger.info(f"  ✓ Extracted {len(benchmark_df)} categories")
                    else:
                        logger.warning(f"  ✗ No data found for {benchmark}")

            except Exception as e:
                logger.error(f"Failed to parse {filename}: {e}")
                failed_parses.append(f"{family} {timepoint}")

        if not all_data:
            raise Exception("No category-level data extracted from technical reports. Cannot proceed without real benchmark data.")

        # Combine all extracted data
        combined_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"\nExtraction complete: {len(combined_df)} total rows")

        if failed_parses:
            logger.warning(f"Some parses failed: {', '.join(failed_parses)}")
            logger.warning("Proceeding with available data - gate condition will validate if sufficient.")

        logger.info("")

        return combined_df


    def validate_data(self, df: pd.DataFrame) -> Dict:
        """Validate extracted data."""
        logger.info("=" * 60)
        logger.info("STAGE 3: VALIDATE DATA")
        logger.info("=" * 60)

        validator = DataAvailabilityValidator(df)
        results = validator.validate_all()

        logger.info("\nValidation Results:")
        logger.info(f"  Family Coverage: {results['family_count']} families "
                   f"({'PASS' if results['family_coverage_passed'] else 'FAIL'})")
        logger.info(f"  Timepoint Coverage: "
                   f"({'PASS' if results['timepoint_coverage_passed'] else 'FAIL'})")
        logger.info(f"  Category Granularity: "
                   f"({'PASS' if results['granularity_passed'] else 'FAIL'})")
        logger.info(f"  Data Completeness: {results['completeness']:.1f}% "
                   f"({'PASS' if results['completeness_passed'] else 'FAIL'})")
        logger.info(f"\n  OVERALL: {'✓ PASSED' if results['overall_passed'] else '✗ FAILED'}\n")

        return results

    def compute_metrics(self, df: pd.DataFrame) -> Dict:
        """Compute gate metrics."""
        logger.info("=" * 60)
        logger.info("STAGE 4: COMPUTE GATE METRICS")
        logger.info("=" * 60)

        analyzer = GateMetricsAnalyzer(df)
        metrics = analyzer.evaluate_gate_condition()

        logger.info(f"\n{metrics['gate_message']}\n")

        return metrics

    def generate_visualizations(self, df: pd.DataFrame, metrics: Dict) -> None:
        """Generate visualization figures."""
        logger.info("=" * 60)
        logger.info("STAGE 5: GENERATE VISUALIZATIONS")
        logger.info("=" * 60)

        metadata = self.collector.get_metadata() if self.collector else {}
        visualizer = ExperimentVisualizer(df, metrics)

        self.figures = visualizer.generate_all_figures(
            str(self.config.figures_dir),
            metadata=metadata
        )

        logger.info(f"Generated {len(self.figures)} figures:")
        for fig_path in self.figures:
            logger.info(f"  ✓ {fig_path}")
        logger.info("")

    def save_outputs(self, df: pd.DataFrame, metrics: Dict) -> None:
        """Save final outputs."""
        logger.info("=" * 60)
        logger.info("STAGE 6: SAVE OUTPUTS")
        logger.info("=" * 60)

        # Save extracted data
        data_path = self.config.extracted_dir / "h-e1_extracted_data.csv"
        df.to_csv(data_path, index=False)
        logger.info(f"✓ Saved extracted data: {data_path}")

        # Save validation results
        validation_path = self.config.extracted_dir / "h-e1_validation.json"

        # Convert numpy types to native Python types for JSON serialization
        def convert_to_json_serializable(obj):
            if isinstance(obj, dict):
                return {k: convert_to_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_json_serializable(item) for item in obj]
            elif hasattr(obj, 'item'):  # numpy types
                return obj.item()
            elif isinstance(obj, (bool, int, float, str)) or obj is None:
                return obj
            else:
                return str(obj)

        validation_data = {
            'gate_passed': bool(metrics['gate_passed']),
            'gate_message': str(metrics['gate_message']),
            'family_count': int(metrics['family_count']),
            'families_with_both_timepoints': metrics['families_with_both_timepoints'],
            'granularity': convert_to_json_serializable(metrics['granularity']),
            'completeness': float(metrics['completeness']),
            'validation_results': convert_to_json_serializable(self.validation_results),
            'timestamp': datetime.now().isoformat()
        }

        with open(validation_path, 'w') as f:
            json.dump(validation_data, f, indent=2)
        logger.info(f"✓ Saved validation results: {validation_path}")

        # Save metadata
        if self.collector:
            metadata_path = self.config.extracted_dir / "h-e1_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(self.collector.get_metadata(), f, indent=2)
            logger.info(f"✓ Saved metadata: {metadata_path}")

        logger.info("")

    def run(self) -> Dict[str, Any]:
        """
        Run the complete experiment pipeline.

        Returns:
            Results dictionary with gate decision
        """
        try:
            # Stage 0: Setup
            self.setup_environment()

            # Stage 1: Collect
            self.collect_reports()

            # Stage 2: Parse
            self.extracted_df = self.parse_and_extract()

            # Stage 3: Validate
            self.validation_results = self.validate_data(self.extracted_df)

            # Stage 4: Metrics
            self.metrics = self.compute_metrics(self.extracted_df)

            # Stage 5: Visualize
            self.generate_visualizations(self.extracted_df, self.metrics)

            # Stage 6: Save
            self.save_outputs(self.extracted_df, self.metrics)

            # Final summary
            logger.info("=" * 60)
            logger.info("EXPERIMENT COMPLETE")
            logger.info("=" * 60)
            logger.info(f"\nGate Result: {self.metrics['gate_message']}")
            logger.info(f"Figures generated: {len(self.figures)}")
            logger.info(f"Total data rows: {len(self.extracted_df)}")
            logger.info("")

            return {
                'success': True,
                'gate_passed': self.metrics['gate_passed'],
                'gate_message': self.metrics['gate_message'],
                'data_rows': len(self.extracted_df),
                'figures_generated': len(self.figures)
            }

        except Exception as e:
            logger.error(f"Experiment failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """Main entry point."""
    runner = H_E1_ExperimentRunner()
    results = runner.run()

    # Exit with appropriate code
    sys.exit(0 if results.get('success') else 1)


if __name__ == '__main__':
    main()
