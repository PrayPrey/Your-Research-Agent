"""
Dynamic Benchmark Renewal Framework (DBRF) - Main Experiment Script

This script implements and evaluates the Dynamic Benchmark Renewal Framework
for combating benchmark overfitting through continuous dataset renewal.

The framework consists of three components:
1. Contamination Detection Module
2. Structured Dataset Evolution Protocol
3. Cross-Version Performance Anchoring
"""

import os
import sys
import json
import time
import logging
import numpy as np
import torch
import random
from pathlib import Path

# Set up logging
log_dir = Path(__file__).parent.parent / "results"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "log.txt"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Set seeds for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

from contamination_detection import ContaminationDetectionModule
from dataset_evolution import DatasetEvolutionProtocol
from performance_anchoring import CrossVersionAnchoring
from baselines import StaticBenchmarkBaseline, RandomRenewalBaseline, AdversarialBaseline
from evaluation import run_full_evaluation
from visualization import create_all_figures

def main():
    logger.info("=" * 70)
    logger.info("Dynamic Benchmark Renewal Framework (DBRF) Experiment")
    logger.info("=" * 70)

    # Device setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Using device: {device}")
    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")

    # Experiment configuration
    config = {
        'seed': SEED,
        'device': str(device),
        'n_renewal_cycles': 3,
        'n_models': 10,          # Number of benchmark models to simulate
        'n_generations': 20,     # Number of model generations
        'benchmark_size': 1000,  # Number of benchmark instances
        'anchor_fraction': 0.1,  # Fraction of instances held as anchor set
        'saturation_alpha': 0.05,
        'kl_epsilon': 0.1,       # KL divergence tolerance for distribution fidelity
        'domains': ['image_classification', 'nlp', 'tabular'],
        'output_dir': str(log_dir),
    }

    logger.info(f"Configuration: {json.dumps(config, indent=2)}")

    all_results = {}

    # Run experiments per domain
    for domain in config['domains']:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running experiments for domain: {domain}")
        logger.info(f"{'='*50}")

        domain_results = run_domain_experiment(domain, config, device)
        all_results[domain] = domain_results

        logger.info(f"Completed domain: {domain}")

    # Aggregate results across domains
    logger.info("\nAggregating results across domains...")
    aggregated = aggregate_results(all_results, config)

    # Save results
    results_path = log_dir / "results.json"

    def convert_to_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        return obj

    def make_serializable(d):
        if isinstance(d, dict):
            return {k: make_serializable(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [make_serializable(i) for i in d]
        else:
            return convert_to_serializable(d)

    aggregated_serial = make_serializable(aggregated)
    with open(results_path, 'w') as f:
        json.dump(aggregated_serial, f, indent=2)
    logger.info(f"Results saved to {results_path}")

    # Generate figures
    logger.info("\nGenerating visualization figures...")
    create_all_figures(aggregated, config, log_dir)

    # Print summary
    print_summary(aggregated)

    logger.info("\nExperiment completed successfully!")
    return aggregated


def run_domain_experiment(domain, config, device):
    """Run the full DBRF experiment for a given domain."""
    logger.info(f"\nInitializing {domain} experiment...")

    # Initialize framework components
    contamination_module = ContaminationDetectionModule(
        alpha=config['saturation_alpha'],
        device=device
    )

    evolution_protocol = DatasetEvolutionProtocol(
        domain=domain,
        kl_epsilon=config['kl_epsilon'],
        device=device
    )

    anchoring_mechanism = CrossVersionAnchoring(
        anchor_fraction=config['anchor_fraction']
    )

    # Initialize baselines
    static_baseline = StaticBenchmarkBaseline()
    random_baseline = RandomRenewalBaseline()
    adversarial_baseline = AdversarialBaseline()

    domain_results = {
        'domain': domain,
        'dbrf': {},
        'baselines': {},
        'detection_metrics': {},
        'distribution_metrics': {},
        'anchoring_metrics': {},
    }

    # === Phase 1: Simulate model performance trajectories ===
    logger.info(f"  Phase 1: Simulating benchmark performance trajectories...")

    # Create benchmark data
    benchmark_data = evolution_protocol.create_initial_benchmark(
        size=config['benchmark_size']
    )

    # Simulate model generation performance (with controlled overfitting)
    perf_trajectories = simulate_performance_trajectories(
        benchmark_data,
        n_models=config['n_models'],
        n_generations=config['n_generations'],
        device=device,
        domain=domain
    )

    domain_results['performance_trajectories'] = perf_trajectories

    # === Phase 2: Contamination Detection ===
    logger.info(f"  Phase 2: Running Contamination Detection Module...")

    detection_results = contamination_module.detect_saturation(
        perf_trajectories['benchmark_scores'],
        perf_trajectories['shadow_scores']
    )

    domain_results['detection_metrics'] = detection_results
    logger.info(f"    Saturation detected: {detection_results['saturation_detected']}")
    logger.info(f"    Detection precision: {detection_results['precision']:.3f}")
    logger.info(f"    Detection recall: {detection_results['recall']:.3f}")

    # === Phase 3: Dataset Evolution Protocol ===
    logger.info(f"  Phase 3: Running Dataset Evolution Protocol...")

    evolution_results = []
    current_benchmark = benchmark_data

    for cycle in range(config['n_renewal_cycles']):
        logger.info(f"    Renewal cycle {cycle+1}/{config['n_renewal_cycles']}...")

        new_benchmark, cycle_metrics = evolution_protocol.evolve_benchmark(
            current_benchmark,
            cycle=cycle
        )

        evolution_results.append({
            'cycle': cycle + 1,
            'kl_divergence': float(cycle_metrics['kl_divergence']),
            'difficulty_l1': float(cycle_metrics['difficulty_l1']),
            'overfitting_reduction': float(cycle_metrics['overfitting_reduction'])
        })

        logger.info(f"      KL divergence: {cycle_metrics['kl_divergence']:.4f}")
        logger.info(f"      Difficulty L1: {cycle_metrics['difficulty_l1']:.4f}")
        logger.info(f"      Overfitting reduction: {cycle_metrics['overfitting_reduction']:.3f}")

        current_benchmark = new_benchmark

    domain_results['evolution_results'] = evolution_results

    # === Phase 4: Cross-Version Performance Anchoring ===
    logger.info(f"  Phase 4: Running Cross-Version Performance Anchoring...")

    anchoring_results = anchoring_mechanism.calibrate_scores(
        benchmark_data,
        current_benchmark,
        n_reference_models=config['n_models']
    )

    domain_results['anchoring_metrics'] = {
        'calibration_error': float(anchoring_results['calibration_error']),
        'rank_correlation': float(anchoring_results['rank_correlation']),
        'anchor_coverage': float(anchoring_results['anchor_coverage'])
    }

    logger.info(f"    Calibration error: {anchoring_results['calibration_error']:.4f}")
    logger.info(f"    Rank correlation: {anchoring_results['rank_correlation']:.4f}")

    # === Phase 5: Baseline Comparisons ===
    logger.info(f"  Phase 5: Running baseline comparisons...")

    # Static baseline (no renewal)
    static_results = static_baseline.evaluate(
        benchmark_data, perf_trajectories, config['n_renewal_cycles']
    )

    # Random renewal baseline
    random_results = random_baseline.evaluate(
        benchmark_data, evolution_protocol, perf_trajectories, config['n_renewal_cycles']
    )

    # Adversarial baseline (no difficulty calibration)
    adversarial_results = adversarial_baseline.evaluate(
        benchmark_data, evolution_protocol, perf_trajectories, config['n_renewal_cycles']
    )

    domain_results['baselines'] = {
        'static': static_results,
        'random_renewal': random_results,
        'adversarial': adversarial_results
    }

    # === Phase 6: DBRF aggregate performance ===
    domain_results['dbrf'] = run_full_evaluation(
        benchmark_data, current_benchmark, perf_trajectories,
        evolution_results, anchoring_results, config
    )

    return domain_results


def simulate_performance_trajectories(benchmark_data, n_models, n_generations, device, domain):
    """
    Simulate model performance over time with controlled benchmark overfitting.
    Models start with genuine improvements then overfit to the benchmark.
    """
    logger.info(f"    Simulating {n_models} models over {n_generations} generations...")

    n_instances = len(benchmark_data['features'])
    n_features = benchmark_data['features'].shape[1]

    # Ground truth: shadow evaluation set (never seen by models)
    shadow_size = max(200, n_instances // 5)
    shadow_data = {
        'features': np.random.randn(shadow_size, n_features).astype(np.float32),
        'labels': np.random.randint(0, 2, shadow_size)
    }

    benchmark_scores = np.zeros((n_generations, n_models))
    shadow_scores = np.zeros((n_generations, n_models))
    saturation_labels = np.zeros(n_generations, dtype=bool)

    # Mark last 40% of generations as saturated (ground truth for evaluation)
    saturation_start = int(n_generations * 0.6)
    saturation_labels[saturation_start:] = True

    for gen in range(n_generations):
        for model_idx in range(n_models):
            # Genuine improvement component (logistic growth) - caps at ~0.80
            t = gen / n_generations
            genuine_perf = 0.35 / (1 + np.exp(-6 * (t - 0.4))) + 0.50 + \
                           0.01 * np.random.randn()
            genuine_perf = min(genuine_perf, 0.85)

            # Benchmark overfitting component (increases after saturation)
            # Adds an above-curve boost once saturation begins
            if gen >= saturation_start:
                progress = (gen - saturation_start) / max(1, n_generations - saturation_start)
                overfit_boost = 0.06 * progress + 0.01 * np.random.randn()
                overfit_boost = max(0.0, overfit_boost)
            else:
                overfit_boost = 0.0

            # Shadow set performance (only genuine improvement, no overfitting)
            # Shadow performance closely tracks genuine_perf
            shadow_perf = genuine_perf + 0.005 * np.random.randn()
            shadow_perf = max(0.5, min(shadow_perf, 0.95))

            benchmark_scores[gen, model_idx] = min(genuine_perf + overfit_boost, 0.99)
            shadow_scores[gen, model_idx] = shadow_perf

    return {
        'benchmark_scores': benchmark_scores,
        'shadow_scores': shadow_scores,
        'saturation_labels': saturation_labels,
        'n_generations': n_generations,
        'n_models': n_models,
        'shadow_data': shadow_data
    }


def aggregate_results(all_results, config):
    """Aggregate results across all domains."""
    aggregated = {
        'config': config,
        'domains': all_results,
        'summary': {}
    }

    # Compute summary statistics
    for metric_name, metric_key_path in [
        ('detection_precision', ['detection_metrics', 'precision']),
        ('detection_recall', ['detection_metrics', 'recall']),
        ('calibration_error', ['anchoring_metrics', 'calibration_error']),
        ('rank_correlation', ['anchoring_metrics', 'rank_correlation']),
    ]:
        values = []
        for domain_data in all_results.values():
            data = domain_data
            for key in metric_key_path:
                data = data[key]
            values.append(float(data))

        aggregated['summary'][metric_name] = {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'values_per_domain': {
                domain: float(vals)
                for domain, vals in zip(all_results.keys(), values)
            }
        }

    # Average overfitting reduction across cycles and domains
    all_reductions = []
    for domain_data in all_results.values():
        for cycle_data in domain_data['evolution_results']:
            all_reductions.append(cycle_data['overfitting_reduction'])

    aggregated['summary']['overfitting_reduction'] = {
        'mean': float(np.mean(all_reductions)),
        'std': float(np.std(all_reductions))
    }

    # Average KL divergence across cycles and domains
    all_kl = []
    for domain_data in all_results.values():
        for cycle_data in domain_data['evolution_results']:
            all_kl.append(cycle_data['kl_divergence'])

    aggregated['summary']['kl_divergence'] = {
        'mean': float(np.mean(all_kl)),
        'std': float(np.std(all_kl))
    }

    # Baseline comparisons
    for baseline_name in ['static', 'random_renewal', 'adversarial']:
        baseline_reductions = []
        for domain_data in all_results.values():
            if baseline_name in domain_data['baselines']:
                baseline_reductions.append(
                    domain_data['baselines'][baseline_name].get('overfitting_reduction', 0.0)
                )

        aggregated['summary'][f'{baseline_name}_overfitting_reduction'] = {
            'mean': float(np.mean(baseline_reductions)) if baseline_reductions else 0.0,
            'std': float(np.std(baseline_reductions)) if baseline_reductions else 0.0
        }

    return aggregated


def print_summary(aggregated):
    """Print a summary of the experiment results."""
    summary = aggregated['summary']

    logger.info("\n" + "=" * 70)
    logger.info("EXPERIMENT SUMMARY")
    logger.info("=" * 70)

    logger.info("\n--- Contamination Detection ---")
    logger.info(f"  Detection Precision: {summary['detection_precision']['mean']:.3f} ± {summary['detection_precision']['std']:.3f}")
    logger.info(f"  Detection Recall:    {summary['detection_recall']['mean']:.3f} ± {summary['detection_recall']['std']:.3f}")

    logger.info("\n--- Dataset Evolution ---")
    logger.info(f"  Mean KL Divergence:       {summary['kl_divergence']['mean']:.4f} ± {summary['kl_divergence']['std']:.4f}")
    logger.info(f"  DBRF Overfitting Reduction: {summary['overfitting_reduction']['mean']:.3f} ± {summary['overfitting_reduction']['std']:.3f}")
    logger.info(f"  Static Baseline Reduction:  {summary['static_overfitting_reduction']['mean']:.3f}")
    logger.info(f"  Random Renewal Reduction:   {summary['random_renewal_overfitting_reduction']['mean']:.3f}")
    logger.info(f"  Adversarial Reduction:      {summary['adversarial_overfitting_reduction']['mean']:.3f}")

    logger.info("\n--- Cross-Version Anchoring ---")
    logger.info(f"  Calibration Error:   {summary['calibration_error']['mean']:.4f} ± {summary['calibration_error']['std']:.4f}")
    logger.info(f"  Rank Correlation:    {summary['rank_correlation']['mean']:.4f} ± {summary['rank_correlation']['std']:.4f}")

    logger.info("\n" + "=" * 70)


if __name__ == '__main__':
    main()
