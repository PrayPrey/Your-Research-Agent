"""Main orchestration script for H-E1 Cross-Benchmark Rank Correlation Analysis."""

import sys
import os
from typing import Dict, Any

from config import get_default_config
from data_loader import TrustLLMLoader, MultiTrustLoader, FinTrustLoader, DataPreprocessor
from correlation_analyzer import CorrelationAnalyzer
from visualizer import CorrelationVisualizer
from validator import ResultValidator


def main():
    """Main execution pipeline for H-E1."""
    print("=" * 70)
    print("H-E1: Cross-Benchmark Ranking Disagreement Analysis")
    print("=" * 70)
    print()

    # Load configuration
    config = get_default_config()
    print(f"[Config] Hypothesis: {config.hypothesis_id}")
    print(f"[Config] Significance level: {config.statistics.significance_level}")
    print(f"[Config] Target range: [{config.statistics.target_rho_min}, {config.statistics.target_rho_max}]")
    print()

    # 1. Data Acquisition
    print("[Stage 1/5] Data Acquisition")
    print("-" * 70)

    trustllm_loader = TrustLLMLoader(url=config.data_sources.trustllm_url)
    trustllm_data = trustllm_loader.fetch_leaderboard()

    multitrust_loader = MultiTrustLoader(repo_path=config.data_sources.multitrust_repo)
    multitrust_data = multitrust_loader.load_evaluation_results()

    fintrust_loader = FinTrustLoader(source=config.data_sources.fintrust_source)
    fintrust_data = fintrust_loader.fetch_leaderboard()

    print()

    # 2. Preprocessing
    print("[Stage 2/5] Preprocessing")
    print("-" * 70)

    preprocessor = DataPreprocessor(min_overlap=config.preprocessing.min_model_overlap)

    try:
        filtered_data = preprocessor.filter_common_models(
            trustllm_data, multitrust_data, fintrust_data
        )
    except ValueError as e:
        print(f"\n[ERROR] {e}")
        print("[VERDICT] Gate FAILED: Insufficient model overlap")
        sys.exit(1)

    # Extract rankings
    rankings = {
        'TrustLLM': preprocessor.extract_rankings(filtered_data[0], config.preprocessing.score_column),
        'MultiTrust': preprocessor.extract_rankings(filtered_data[1], config.preprocessing.score_column),
        'FinTrust': preprocessor.extract_rankings(filtered_data[2], config.preprocessing.score_column)
    }

    model_overlap = len(rankings['TrustLLM'])
    print()

    # 3. Statistical Analysis
    print("[Stage 3/5] Statistical Analysis")
    print("-" * 70)

    analyzer = CorrelationAnalyzer(significance_level=config.statistics.significance_level)
    corr_matrix, pvalue_matrix = analyzer.compute_pairwise_correlations(rankings)

    gate_status = analyzer.check_gate_success(
        corr_matrix,
        pvalue_matrix,
        target_rho_min=config.statistics.target_rho_min,
        target_rho_max=config.statistics.target_rho_max
    )

    falsification = analyzer.check_falsification(
        corr_matrix,
        pvalue_matrix,
        scalar_threshold=config.statistics.scalar_threshold,
        random_threshold=config.statistics.random_threshold
    )

    print()

    # 4. Visualization
    print("[Stage 4/5] Visualization")
    print("-" * 70)

    viz_output_dir = os.path.join(config.hypothesis_folder, config.visualization.output_dir)
    visualizer = CorrelationVisualizer(output_dir=viz_output_dir)

    # Heatmap
    visualizer.plot_correlation_heatmap(
        corr_matrix,
        pvalue_matrix,
        dpi=config.visualization.dpi,
        figsize=config.visualization.heatmap_figsize
    )

    # Scatter plots for each pair
    benchmark_names = list(rankings.keys())
    for i, b1 in enumerate(benchmark_names):
        for j, b2 in enumerate(benchmark_names):
            if i < j:
                rho = corr_matrix.loc[b1, b2]
                pval = pvalue_matrix.loc[b1, b2]
                visualizer.plot_scatter_pair(
                    rankings[b1],
                    rankings[b2],
                    (b1, b2),
                    rho,
                    pval,
                    dpi=config.visualization.dpi,
                    figsize=config.visualization.scatter_figsize
                )

    # Gate metrics
    actual_correlations = {}
    for i, b1 in enumerate(benchmark_names):
        for j, b2 in enumerate(benchmark_names):
            if i < j:
                pair_name = f"{b1}-{b2}"
                actual_correlations[pair_name] = corr_matrix.loc[b1, b2]

    visualizer.plot_gate_metrics(
        target_range=(config.statistics.target_rho_min, config.statistics.target_rho_max),
        actual_correlations=actual_correlations,
        dpi=config.visualization.dpi,
        figsize=config.visualization.bar_figsize
    )

    print()

    # 5. Validation & Export
    print("[Stage 5/5] Validation & Export")
    print("-" * 70)

    validator = ResultValidator(hypothesis_folder=config.hypothesis_folder)

    # Prepare correlations dict for export
    correlations_dict = {}
    for pair_info in gate_status['all_pairs']:
        pair = pair_info['pair']
        correlations_dict[pair] = {
            'rho': pair_info['rho'],
            'pvalue': pair_info['pvalue'],
            'in_range': pair_info['in_range'],
            'significant': pair_info['significant']
        }

    validator.save_metrics_summary(
        correlations=correlations_dict,
        gate_status=gate_status,
        falsification=falsification,
        model_overlap=model_overlap
    )

    results = {
        'model_overlap': model_overlap,
        'gate_status': gate_status,
        'falsification': falsification
    }

    validator.generate_validation_report(results)

    # Final verdict
    print("\n" + "=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)
    print(f"Gate (MUST_WORK): {'PASSED ✓' if gate_status['passed'] else 'FAILED ✗'}")
    print(f"Falsification: {'YES ✗' if falsification['falsified'] else 'NO ✓'}")

    if gate_status['passed'] and not falsification['falsified']:
        print("\n[SUCCESS] Hypothesis h-e1 validated!")
        return 0
    else:
        print("\n[FAILURE] Hypothesis h-e1 not validated")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
