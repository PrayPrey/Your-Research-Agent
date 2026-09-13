#!/usr/bin/env python3
"""
Main experiment runner for Dynamic Dataset Health Scores (DDHS) evaluation.
Compares DDHS against multiple baseline methods.
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ExperimentConfig, BaselineConfig
from data_generator import SyntheticDataGenerator, DatasetMetadata
from health_scores import DDHSCalculator
from baselines import (
    DownloadsOnlyBaseline, StaticWeightBaseline, DataShapleyBaseline,
    RecencyOnlyBaseline, DocumentationOnlyBaseline, get_all_baselines
)
from evaluation import (
    DeprecationPredictor, UserAlignmentEvaluator, EfficiencyEvaluator,
    ScalabilityBenchmark, compute_comprehensive_evaluation
)
from visualization import (
    setup_style, plot_deprecation_prediction_comparison,
    plot_user_alignment_comparison, plot_efficiency_comparison,
    plot_score_distribution, plot_score_vs_expert, plot_scalability,
    plot_deprecation_by_score_bin, plot_comprehensive_summary
)


def setup_logging(log_file: str) -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger('DDHS_Experiment')
    logger.setLevel(logging.INFO)

    # File handler
    fh = logging.FileHandler(log_file, mode='w')
    fh.setLevel(logging.INFO)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def run_experiment(config: ExperimentConfig, output_dir: str, logger: logging.Logger):
    """
    Run the full DDHS experiment.
    """
    logger.info("=" * 80)
    logger.info("Starting DDHS Experiment")
    logger.info("=" * 80)

    # Create output directories
    figures_dir = os.path.join(output_dir, 'figures')
    os.makedirs(figures_dir, exist_ok=True)

    # Set random seed
    np.random.seed(config.random_seed)

    # Generate synthetic repository data
    logger.info(f"\n1. Generating synthetic repository with {config.num_datasets} datasets...")
    generator = SyntheticDataGenerator(
        seed=config.random_seed,
        num_snapshots=config.num_historical_snapshots
    )
    datasets = generator.generate_repository(
        num_datasets=config.num_datasets,
        deprecation_rate=config.deprecation_rate
    )

    # Convert to DataFrame for analysis
    df = generator.to_dataframe(datasets)
    logger.info(f"   Generated {len(datasets)} datasets")
    logger.info(f"   Deprecated: {df['is_deprecated'].sum()} ({df['is_deprecated'].mean()*100:.1f}%)")
    logger.info(f"   Domains: {df['domain'].nunique()}")

    # Get ground truth
    expert_scores = [ds.quality_score_expert for ds in datasets]
    is_deprecated = [ds.is_deprecated for ds in datasets]

    # Initialize methods
    logger.info("\n2. Initializing methods...")

    methods = {
        'DDHS': DDHSCalculator(
            weights=config.get_weights(),
            usi_params={'alpha': config.usi_alpha, 'beta': config.usi_beta, 'gamma': config.usi_gamma},
            cri_params={'omega1': config.cri_omega1, 'omega2': config.cri_omega2, 'omega3': config.cri_omega3}
        ),
        **get_all_baselines()
    }

    logger.info(f"   Methods to evaluate: {list(methods.keys())}")

    # Run evaluation for all methods
    logger.info("\n3. Evaluating methods...")

    all_results = {}
    all_scores = {}

    for method_name, method in methods.items():
        logger.info(f"\n   Evaluating: {method_name}")

        start_time = time.time()
        scores, dimension_scores = method.evaluate_repository(datasets)
        elapsed_time = time.time() - start_time

        # Compute evaluation metrics
        eval_results = compute_comprehensive_evaluation(
            method_name=method_name,
            scores=scores,
            expert_scores=expert_scores,
            is_deprecated=is_deprecated,
            computation_time=elapsed_time,
            n_datasets=len(datasets)
        )

        all_results[method_name] = eval_results
        all_scores[method_name] = scores

        logger.info(f"      AUC-ROC: {eval_results['deprecation']['auc_roc']:.4f}")
        logger.info(f"      Kendall's tau: {eval_results['alignment']['kendall_tau']:.4f}")
        logger.info(f"      Time: {elapsed_time:.4f}s ({elapsed_time/len(datasets)*1000:.2f}ms/dataset)")

    # Run scalability benchmark
    logger.info("\n4. Running scalability benchmark...")

    scalability_sizes = [50, 100, 200, 500]
    scalability_results = []

    for method_name in ['DDHS', 'Downloads-Only', 'Static-Weighted']:
        logger.info(f"   Benchmarking: {method_name}")

        for size in scalability_sizes:
            test_datasets = generator.generate_repository(num_datasets=size)

            times = []
            for _ in range(3):
                method = DDHSCalculator() if method_name == 'DDHS' else get_all_baselines()[method_name]
                start = time.time()
                method.evaluate_repository(test_datasets)
                times.append(time.time() - start)

            scalability_results.append({
                'method': method_name,
                'n_datasets': size,
                'mean_time': np.mean(times),
                'std_time': np.std(times),
                'time_per_dataset': np.mean(times) / size
            })

    # Generate visualizations
    logger.info("\n5. Generating visualizations...")

    # Deprecation prediction comparison
    fig = plot_deprecation_prediction_comparison(
        all_results,
        save_path=os.path.join(figures_dir, 'deprecation_prediction_comparison.png')
    )
    plt.close(fig)

    # User alignment comparison
    fig = plot_user_alignment_comparison(
        all_results,
        save_path=os.path.join(figures_dir, 'user_alignment_comparison.png')
    )
    plt.close(fig)

    # Efficiency comparison
    fig = plot_efficiency_comparison(
        all_results,
        save_path=os.path.join(figures_dir, 'efficiency_comparison.png')
    )
    plt.close(fig)

    # Score distributions
    fig = plot_score_distribution(
        all_scores,
        save_path=os.path.join(figures_dir, 'score_distributions.png')
    )
    plt.close(fig)

    # Score vs expert
    fig = plot_score_vs_expert(
        all_scores,
        expert_scores,
        save_path=os.path.join(figures_dir, 'score_vs_expert.png')
    )
    plt.close(fig)

    # Scalability
    fig = plot_scalability(
        scalability_results,
        save_path=os.path.join(figures_dir, 'scalability.png')
    )
    plt.close(fig)

    # Deprecation by score bin (for DDHS)
    fig = plot_deprecation_by_score_bin(
        all_scores['DDHS'],
        is_deprecated,
        'DDHS',
        save_path=os.path.join(figures_dir, 'deprecation_by_score_bin.png')
    )
    plt.close(fig)

    # Comprehensive summary
    fig = plot_comprehensive_summary(
        all_results,
        save_path=os.path.join(figures_dir, 'comprehensive_summary.png')
    )
    plt.close(fig)

    # Save results to JSON
    logger.info("\n6. Saving results...")

    # Prepare results for JSON serialization
    json_results = {}
    for method, results in all_results.items():
        json_results[method] = {
            'deprecation': {k: float(v) if isinstance(v, (np.floating, float)) else v
                          for k, v in results['deprecation'].items()},
            'alignment': {k: float(v) if isinstance(v, (np.floating, float)) else v
                         for k, v in results['alignment'].items()},
            'efficiency': {k: float(v) if isinstance(v, (np.floating, float)) else v
                          for k, v in results['efficiency'].items()}
        }

    with open(os.path.join(output_dir, 'results.json'), 'w') as f:
        json.dump({
            'config': {
                'num_datasets': config.num_datasets,
                'deprecation_rate': config.deprecation_rate,
                'random_seed': config.random_seed,
                'weights': config.get_weights()
            },
            'results': json_results,
            'scalability': scalability_results
        }, f, indent=2)

    # Create summary tables
    logger.info("\n7. Creating summary tables...")

    # Deprecation prediction table
    deprecation_df = pd.DataFrame([
        {
            'Method': method,
            'AUC-ROC': results['deprecation']['auc_roc'],
            'Avg Precision': results['deprecation']['avg_precision'],
            'F1 (Optimal)': results['deprecation']['f1_at_optimal'],
            'Precision@10%': results['deprecation']['precision_at_10'],
            'Recall@10%': results['deprecation']['recall_at_10']
        }
        for method, results in all_results.items()
    ])
    deprecation_df = deprecation_df.sort_values('AUC-ROC', ascending=False)
    deprecation_df.to_csv(os.path.join(output_dir, 'deprecation_results.csv'), index=False)

    # Alignment table
    alignment_df = pd.DataFrame([
        {
            'Method': method,
            "Kendall's τ": results['alignment']['kendall_tau'],
            "Spearman's ρ": results['alignment']['spearman_rho'],
            "Pearson's r": results['alignment']['pearson_r'],
            'MAE': results['alignment']['mae'],
            'RMSE': results['alignment']['rmse']
        }
        for method, results in all_results.items()
    ])
    alignment_df = alignment_df.sort_values("Kendall's τ", ascending=False)
    alignment_df.to_csv(os.path.join(output_dir, 'alignment_results.csv'), index=False)

    # Efficiency table
    efficiency_df = pd.DataFrame([
        {
            'Method': method,
            'Total Time (s)': results['efficiency']['total_time'],
            'Time/Dataset (ms)': results['efficiency']['time_per_dataset'] * 1000,
            'Datasets': results['efficiency']['n_datasets']
        }
        for method, results in all_results.items()
    ])
    efficiency_df = efficiency_df.sort_values('Time/Dataset (ms)')
    efficiency_df.to_csv(os.path.join(output_dir, 'efficiency_results.csv'), index=False)

    # Scalability table
    scalability_df = pd.DataFrame(scalability_results)
    scalability_df.to_csv(os.path.join(output_dir, 'scalability_results.csv'), index=False)

    # Print final summary
    logger.info("\n" + "=" * 80)
    logger.info("EXPERIMENT COMPLETE")
    logger.info("=" * 80)

    logger.info("\nDeprecation Prediction Results:")
    logger.info(deprecation_df.to_string(index=False))

    logger.info("\nUser Alignment Results:")
    logger.info(alignment_df.to_string(index=False))

    logger.info("\nEfficiency Results:")
    logger.info(efficiency_df.to_string(index=False))

    logger.info(f"\nResults saved to: {output_dir}")
    logger.info(f"Figures saved to: {figures_dir}")

    return all_results, all_scores


def main():
    """Main entry point"""
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    global plt
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser(description='Run DDHS Experiment')
    parser.add_argument('--num-datasets', type=int, default=200,
                       help='Number of datasets to simulate')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed')
    parser.add_argument('--output-dir', type=str, default='outputs',
                       help='Output directory')
    args = parser.parse_args()

    # Setup configuration
    config = ExperimentConfig(
        num_datasets=args.num_datasets,
        random_seed=args.seed
    )

    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Setup logging
    log_file = os.path.join(output_dir, 'log.txt')
    logger = setup_logging(log_file)

    logger.info(f"Experiment started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Configuration: {config}")

    try:
        # Run experiment
        results, scores = run_experiment(config, output_dir, logger)

        logger.info(f"\nExperiment completed successfully at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        logger.error(f"Experiment failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
