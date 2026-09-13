"""Main entry point for H-E1 reproducibility analysis experiment."""
import os
import sys
import json
import logging
import yaml
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_collection.collector import DataCollector
from feature_engineering.doc_scorer import DocumentationScorer
from feature_engineering.extractor import FeatureExtractor
from analysis.correlation import ReproducibilityAnalyzer
from analysis.gate_checker import GateChecker
from visualization.plotter import ResultsVisualizer


def setup_logging():
    """Configure logging for the experiment."""
    os.makedirs('logs', exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/experiment.log'),
            logging.StreamHandler()
        ]
    )


def load_config(config_path: str = 'config.yaml') -> dict:
    """Load configuration from YAML file.

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def save_results(results: dict, output_path: str = 'results.json'):
    """Save experiment results to JSON.

    Args:
        results: Results dictionary
        output_path: Path to save results
    """
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)


def main():
    """Main experiment pipeline."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 80)
    logger.info("H-E1: Structural Documentation Completeness Analysis")
    logger.info("=" * 80)

    # Load configuration
    config = load_config()
    logger.info(f"Loaded configuration: {config['experiment']['name']}")

    # Phase A: Data Collection
    logger.info("\n" + "=" * 80)
    logger.info("PHASE A: Data Collection")
    logger.info("=" * 80)

    collector = DataCollector(random_seed=config['analysis']['random_seed'])
    raw_data = collector.collect_dataset(
        target_n=config['data_collection']['target_n'],
        output_path='data/raw_pwc_data.csv'
    )

    # Phase B: Feature Engineering
    logger.info("\n" + "=" * 80)
    logger.info("PHASE B: Feature Engineering")
    logger.info("=" * 80)

    extractor = FeatureExtractor(scorer=DocumentationScorer())
    processed_data = extractor.process_dataset(
        raw_data_path='data/raw_pwc_data.csv',
        output_path='data/processed_data.csv'
    )

    # Phase C: Statistical Analysis
    logger.info("\n" + "=" * 80)
    logger.info("PHASE C: Statistical Analysis")
    logger.info("=" * 80)

    analyzer = ReproducibilityAnalyzer(
        random_seed=config['analysis']['random_seed']
    )

    # Compute Spearman correlation
    rho, p_value, ci = analyzer.compute_spearman_correlation(processed_data)

    # Fit logistic regression
    odds_results = analyzer.fit_logistic_regression(processed_data)

    # Gate check
    logger.info("\n" + "=" * 80)
    logger.info("Gate Check")
    logger.info("=" * 80)

    gate_checker = GateChecker()
    gate_status = gate_checker.check_gate(rho, p_value, odds_results)

    # Phase D: Visualization
    logger.info("\n" + "=" * 80)
    logger.info("PHASE D: Visualization")
    logger.info("=" * 80)

    visualizer = ResultsVisualizer(
        style=config['visualization']['style'],
        figure_dir=config['visualization'].get('figures_dir', 'figures/')
    )

    analysis_results = {
        'rho': rho,
        'p_value': p_value,
        'ci': ci,
        'odds_results': odds_results,
        'gate_status': gate_status
    }

    visualizer.generate_all_figures(processed_data, analysis_results)

    # Save final results
    logger.info("\n" + "=" * 80)
    logger.info("Saving Results")
    logger.info("=" * 80)

    # Convert all values to native Python types for JSON serialization
    def to_json_serializable(obj):
        """Convert numpy/pandas types to native Python types."""
        import numpy as np
        if isinstance(obj, (np.integer, np.int_, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float_, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, dict):
            return {k: to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [to_json_serializable(v) for v in obj]
        return obj

    final_results = {
        'experiment_id': config['experiment']['id'],
        'timestamp': datetime.now().isoformat(),
        'sample_size': int(len(processed_data)),
        'spearman_correlation': {
            'rho': float(rho),
            'p_value': float(p_value),
            'ci_lower': float(ci[0]),
            'ci_upper': float(ci[1])
        },
        'logistic_regression': {
            k: {
                'OR': float(v['OR']),
                'CI_lower': float(v['CI_lower']),
                'CI_upper': float(v['CI_upper']),
                'p': float(v['p'])
            }
            for k, v in odds_results.items()
        },
        'gate_check': to_json_serializable(gate_status),
        'data_quality': {
            'reproduction_rate': float(processed_data['reproduced_within_12m'].mean()),
            'doc_score_distribution': {
                int(k): int(v) for k, v in
                processed_data['doc_score'].value_counts().sort_index().to_dict().items()
            }
        }
    }

    save_results(final_results, 'results.json')
    logger.info(f"Results saved to results.json")

    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("EXPERIMENT SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Sample Size: {len(processed_data)}")
    logger.info(f"Spearman ρ: {rho:.3f} (95% CI: [{ci[0]:.3f}, {ci[1]:.3f}])")
    logger.info(f"P-value: {p_value:.4f}")
    logger.info(f"Gate Status: {gate_status['status']}")
    logger.info(f"Routing Decision: {gate_status['routing_decision']}")
    logger.info(f"Next Hypothesis: {gate_status['next_hypothesis']}")
    logger.info("=" * 80)

    return 0


if __name__ == '__main__':
    sys.exit(main())
