"""
E1-5: Pipeline Integration - main.py Orchestration
Implements main pipeline execution logic.
"""

import sys
import json
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import ValidationConfig, PlotConfig
from data.collector import PapersWithCodeCollector
from validation.validator import BenchmarkValidator
from analysis.statistics import StatisticalAnalyzer
from reporting.generator import ReportGenerator


def run_validation_pipeline(config: ValidationConfig) -> dict:
    """
    Execute full validation pipeline.

    Orchestration flow:
    1. Initialize all modules
    2. Collect data (DataCollector)
    3. Filter (BenchmarkValidator)
    4. Validate gate (BenchmarkValidator)
    5. Statistical analysis (StatisticalAnalyzer)
    6. Generate figures (ReportGenerator)
    7. Generate report (ReportGenerator)

    Args:
        config: Validation configuration

    Returns:
        Results dict with all metrics
    """
    print("=" * 60)
    print("Phase 4: H-E1 Benchmark Data Validation")
    print("=" * 60)

    # 1. Initialize modules
    print("\n📦 Initializing modules...")
    collector = PapersWithCodeCollector(
        base_url=config.API_BASE_URL,
        rate_limit=config.RATE_LIMIT,
        max_retries=config.MAX_RETRIES
    )

    validator = BenchmarkValidator(
        min_count=config.MIN_BENCHMARKS,
        min_results=config.MIN_RESULTS_PER_BENCHMARK
    )

    analyzer = StatisticalAnalyzer(
        effect_size=config.EFFECT_SIZE,
        alpha=config.ALPHA,
        power=config.POWER
    )

    reporter = ReportGenerator(
        output_dir=config.FIGURES_DIR,
        dpi=PlotConfig.DPI
    )

    # 2. Collect data
    print("\n📥 Collecting data from Papers with Code API...")
    raw_df = collector.fetch_benchmarks(
        task=config.TASK_FILTER,
        start_year=config.START_YEAR,
        end_year=config.END_YEAR
    )

    if raw_df.empty:
        print("❌ ERROR: No data collected from API")
        return {
            'error': 'API collection failed',
            'gate_result': 'FAIL',
            'gate_type': 'MUST_WORK'
        }

    # Save raw data
    collector.save_raw_json(raw_df, config.RAW_DATA_DIR)

    # 3. Filter benchmarks
    print("\n🔍 Filtering benchmarks by inclusion criteria...")
    filtered_df = validator.filter_by_criteria(raw_df)

    # Save processed data
    Path(config.PROCESSED_DATA_DIR).mkdir(parents=True, exist_ok=True)
    csv_path = Path(config.PROCESSED_DATA_DIR) / "benchmarks_filtered.csv"
    filtered_df.to_csv(csv_path, index=False)
    print(f"💾 Processed data saved: {csv_path}")

    # 4. Validate hypothesis
    print("\n✅ Validating hypothesis against gate...")
    validation_result = validator.validate_hypothesis(filtered_df)

    # 5. Statistical analysis
    power_result = analyzer.check_power_sufficiency(validation_result['total_benchmarks'])
    domain_result = analyzer.analyze_domain_coverage(filtered_df)
    depth_result = analyzer.analyze_reproduction_depth(filtered_df)

    # 6. Generate figures
    print("\n📊 Generating visualizations...")
    figure_paths = {}

    figure_paths['gate_metric'] = reporter.generate_gate_metric_chart(
        threshold=validation_result['threshold'],
        actual=validation_result['total_benchmarks'],
        passes=validation_result['passes']
    )

    figure_paths['reproduction'] = reporter.generate_reproduction_histogram(filtered_df)
    figure_paths['domain'] = reporter.generate_domain_pie_chart(domain_result['distribution'])
    figure_paths['timeline'] = reporter.generate_timeline_chart(filtered_df)
    figure_paths['power'] = reporter.generate_power_chart(
        required_n=power_result['required_n'],
        actual_n=power_result['actual_n']
    )

    # 7. Generate validation report
    print("\n📝 Generating validation report...")
    report_content = reporter.generate_validation_report(
        validation_result=validation_result,
        power_result=power_result,
        domain_result=domain_result,
        depth_result=depth_result,
        figure_paths=figure_paths
    )

    # Compile final results
    results = {
        'gate_result': validation_result['status'],
        'gate_type': 'MUST_WORK',
        'validation': validation_result,
        'power_analysis': power_result,
        'domain_coverage': domain_result,
        'reproduction_depth': depth_result,
        'figures': figure_paths,
        'report': report_content
    }

    return results


def save_results(results: dict, output_path: str) -> None:
    """
    Save validation results to files.

    Args:
        results: Results dict
        output_path: Base output file path
    """
    # Save markdown report
    report_path = Path(output_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w') as f:
        f.write(results['report'])

    print(f"✅ Validation report saved: {report_path}")

    # Save JSON results (for experiment_results.json)
    json_path = report_path.parent / "experiment_results.json"
    json_results = {
        'gate_result': results['gate_result'],
        'gate_type': results['gate_type'],
        'primary_metrics': {
            'benchmark_count': results['validation']['total_benchmarks'],
            'threshold': results['validation']['threshold'],
            'passes': results['validation']['passes']
        },
        'secondary_metrics': {
            'power_analysis': results['power_analysis'],
            'domain_coverage': results['domain_coverage'],
            'reproduction_depth': results['reproduction_depth']
        },
        'figures': results['figures']
    }

    with open(json_path, 'w') as f:
        json.dump(json_results, f, indent=2)

    print(f"✅ Experiment results saved: {json_path}")


def main():
    """Main entry point."""
    # Load configuration
    config = ValidationConfig()

    # Run pipeline
    results = run_validation_pipeline(config)

    # Check for errors
    if 'error' in results:
        print(f"\n❌ Pipeline failed: {results['error']}")
        sys.exit(1)

    # Save outputs
    save_results(results, config.OUTPUT_FILE)

    # Final summary
    print("\n" + "=" * 60)
    print("Pipeline Execution Summary")
    print("=" * 60)
    print(f"Gate Result: {results['gate_result']}")
    print(f"Benchmark Count: {results['validation']['total_benchmarks']}")
    print(f"Threshold: {results['validation']['threshold']}")
    print(f"Power Sufficient: {results['power_analysis']['power_sufficient']}")
    print(f"Domains Covered: {results['domain_coverage']['domain_count']}")
    print("=" * 60)

    if results['gate_result'] == 'PASS':
        print("✅ Hypothesis VALIDATED - Proceed to Phase 5")
    else:
        print("❌ Hypothesis FAILED - Study infeasible")


if __name__ == "__main__":
    main()
