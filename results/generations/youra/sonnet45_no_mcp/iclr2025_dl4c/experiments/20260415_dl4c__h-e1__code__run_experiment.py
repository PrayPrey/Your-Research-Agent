#!/usr/bin/env python3
"""
Main experiment script for h-e1: Execution Trace Feature Extraction
EXISTENCE Hypothesis: Prove that standardized execution trace features can be extracted
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import pandas as pd
import numpy as np

from src.config import get_default_config
from src.data.benchmark_loader import create_loader
from src.data.published_results import PublishedResultsCollector
from src.features.extractor import ExecutionTraceExtractor
from src.execution.executor import extract_runtime_and_errors_from_benchmark
from src.validation.validator import FeatureValidator
from src.visualization.plots import VisualizationGenerator


def setup_logging(config):
    """Setup logging configuration."""
    log_path = Path(config.output_directory) / "experiment.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def main():
    """Main experiment execution."""
    print("=" * 80)
    print("H-E1: EXECUTION TRACE FEATURE EXTRACTION")
    print("=" * 80)
    print()

    # Load configuration
    config = get_default_config()
    logger = setup_logging(config)

    logger.info("Starting h-e1 experiment: Execution trace feature extraction")
    logger.info(f"Random seed: {config.random_seed}")

    # Set random seed
    np.random.seed(config.random_seed)

    # Create output directories
    Path(config.output_directory).mkdir(parents=True, exist_ok=True)
    Path(config.visualization.figures_directory).mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # STEP 1: Load Benchmark Datasets
    # =========================================================================
    print("\n[STEP 1] Loading Benchmark Datasets")
    print("-" * 80)

    benchmarks = {}
    for benchmark_config in config.published_results.benchmarks:
        try:
            logger.info(f"Loading {benchmark_config.name}...")
            loader = create_loader(benchmark_config.name, cache_dir=f"data/{benchmark_config.name}")
            dataset = loader.load_dataset()

            if dataset is not None:
                benchmarks[benchmark_config.name] = {
                    'loader': loader,
                    'dataset': dataset,
                    'problem_count': loader.get_problem_count()
                }
                print(f"✓ {benchmark_config.name}: {loader.get_problem_count()} problems loaded")
            else:
                print(f"⚠ {benchmark_config.name}: Dataset not available (will use published results)")

        except Exception as e:
            logger.warning(f"Could not load {benchmark_config.name}: {e}")
            print(f"⚠ {benchmark_config.name}: Using published results only")

    # =========================================================================
    # STEP 2: Load Published Results from Literature
    # =========================================================================
    print("\n[STEP 2] Loading Published Results from Literature")
    print("-" * 80)

    collector = PublishedResultsCollector(config.published_results.results_directory)

    # Load published results from research papers
    humaneval_path, mbpp_path = collector.load_published_results_from_literature()
    print(f"✓ Loaded published results from peer-reviewed papers:")
    print(f"  - HumanEval: {humaneval_path}")
    print(f"  - MBPP: {mbpp_path}")

    # Validate results
    validation = collector.validate_results()
    for benchmark, val_result in validation.items():
        status = "✓" if val_result['valid'] else "⚠"
        print(f"{status} {benchmark}: {val_result['model_count']} models (from literature)")

    # =========================================================================
    # STEP 3: Extract Features
    # =========================================================================
    print("\n[STEP 3] Extracting Execution Trace Features")
    print("-" * 80)

    all_features = []

    for benchmark_name in ['HumanEval', 'MBPP']:
        logger.info(f"Processing {benchmark_name}...")
        extractor = ExecutionTraceExtractor(benchmark_name)

        # Get benchmark dataset for runtime/error extraction
        benchmark_data = benchmarks.get(benchmark_name)

        # Get models for this benchmark
        models = collector.list_available_models(benchmark_name)
        print(f"\n{benchmark_name}: Processing {len(models)} models")

        for model in models:
            # Get published pass@k scores from literature
            passk_scores = collector.get_passk_scores(model, benchmark_name)

            # Extract REAL runtime and error data from benchmark execution
            if benchmark_data and benchmark_data['dataset'] is not None:
                logger.info(f"Extracting runtime/error data for {model} on {benchmark_name}...")
                passing_solutions, failed_solutions = extract_runtime_and_errors_from_benchmark(
                    benchmark_data['loader'],
                    model,
                    sample_size=50  # Sample 50 problems for efficiency
                )
            else:
                # If dataset unavailable, use empty data (features will be marked incomplete)
                logger.warning(f"Dataset not available for {benchmark_name}, runtime/error data unavailable")
                passing_solutions = []
                failed_solutions = []

            # Construct evaluation results from REAL data
            # pass@k from published literature + runtime/errors from actual execution
            pass_at_1 = passk_scores.get('pass@1')
            if pass_at_1 is not None:
                n_samples = 100
                n_correct = int((pass_at_1 / 100.0) * n_samples)
            else:
                n_samples = 0
                n_correct = 0

            evaluation_results = {
                'outputs': [{'n_samples': n_samples, 'n_correct': n_correct}],
                'passing': passing_solutions,
                'failed': failed_solutions
            }

            features = extractor.extract_all_features(model, evaluation_results)

            # Use published pass@k scores from literature (these are ground truth)
            if passk_scores.get('pass@1') is not None:
                features['pass@1'] = passk_scores['pass@1']
            if passk_scores.get('pass@10') is not None:
                features['pass@10'] = passk_scores['pass@10']
            if passk_scores.get('pass@100') is not None:
                features['pass@100'] = passk_scores['pass@100']

            all_features.append(features)
            runtime_status = f"{len(passing_solutions)} samples" if passing_solutions else "N/A"
            print(f"  ✓ {model}: pass@1={features.get('pass@1', 'N/A')}, runtime_data={runtime_status}")

    # Create feature DataFrame
    feature_df = pd.DataFrame(all_features)

    # Save to CSV
    output_csv = Path(config.output_directory) / "features.csv"
    feature_df.to_csv(output_csv, index=False)
    print(f"\n✓ Features saved to: {output_csv}")

    # =========================================================================
    # STEP 4: Validate Completeness
    # =========================================================================
    print("\n[STEP 4] Validating Feature Completeness")
    print("-" * 80)

    validator = FeatureValidator(feature_df, threshold=config.validation.completeness_threshold)

    # Calculate completeness
    completeness_rate = validator.calculate_completeness()
    print(f"\nFeature Completeness: {completeness_rate:.1f}%")

    # Check gate condition
    gate_passed = validator.validate_gate_condition()
    gate_status = "PASS ✓" if gate_passed else "FAIL ✗"
    print(f"Gate Condition (≥95%): {gate_status}")

    # Generate validation report
    report = validator.generate_report()
    report_path = Path(config.validation.validation_report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"✓ Validation report saved to: {report_path}")

    # =========================================================================
    # STEP 5: Generate Visualizations
    # =========================================================================
    print("\n[STEP 5] Generating Visualizations")
    print("-" * 80)

    viz = VisualizationGenerator(feature_df, config.visualization.figures_directory)
    figures = viz.generate_all_figures(completeness_rate, config.validation.completeness_threshold)

    print(f"\n✓ Generated {len(figures)} figures:")
    for fig_path in figures:
        print(f"  - {fig_path}")

    # =========================================================================
    # STEP 6: Save Experiment Results
    # =========================================================================
    print("\n[STEP 6] Saving Experiment Results")
    print("-" * 80)

    experiment_results = {
        'hypothesis_id': 'h-e1',
        'experiment_type': 'EXISTENCE',
        'completed_at': datetime.now().isoformat(),
        'gate_type': 'MUST_WORK',
        'gate_result': 'PASS' if gate_passed else 'FAIL',
        'metrics': {
            'feature_completeness': completeness_rate,
            'completeness_threshold': config.validation.completeness_threshold,
            'total_model_benchmark_pairs': len(feature_df),
            'complete_pairs': report['complete_pairs'],
            'benchmarks_processed': ['HumanEval', 'MBPP'],
            'models_evaluated': len(feature_df['model'].unique())
        },
        'figures_generated': figures,
        'validation_report': str(report_path)
    }

    results_path = Path(config.output_directory) / "experiment_results.json"
    with open(results_path, 'w') as f:
        json.dump(experiment_results, f, indent=2)

    print(f"✓ Experiment results saved to: {results_path}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)
    print(f"\nHypothesis: h-e1 (EXISTENCE)")
    print(f"Gate Type: MUST_WORK")
    print(f"Gate Result: {experiment_results['gate_result']}")
    print(f"\nMetrics:")
    print(f"  - Feature Completeness: {completeness_rate:.1f}%")
    print(f"  - Threshold: {config.validation.completeness_threshold}%")
    print(f"  - Model-Benchmark Pairs: {len(feature_df)}")
    print(f"  - Complete Pairs: {report['complete_pairs']}")
    print(f"\nOutputs:")
    print(f"  - Features: {output_csv}")
    print(f"  - Results: {results_path}")
    print(f"  - Report: {report_path}")
    print(f"  - Figures: {len(figures)} files in {config.visualization.figures_directory}/")
    print("\n" + "=" * 80)

    return 0 if gate_passed else 1


if __name__ == "__main__":
    sys.exit(main())
