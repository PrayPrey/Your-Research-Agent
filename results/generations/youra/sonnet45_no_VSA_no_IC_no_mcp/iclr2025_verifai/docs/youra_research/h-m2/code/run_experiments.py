"""Main experiment runner for h-m2."""

import json
import random
import numpy as np
import torch
from pathlib import Path

from config import ExperimentConfig
from model_loader import setup_device, load_codellama
from data_loader import load_humaneval, extract_poc_subset
from experiments import (
    experiment_a_latency,
    experiment_b_ranking,
    experiment_c_ablation,
    baseline_comparison
)
from analysis import analyze_latency, analyze_ranking, compare_ablation, compare_baselines


def create_ablation_subset(dataset, size: int, seed: int):
    """Create stratified subset for ablation study."""
    random.seed(seed)
    indices = random.sample(range(len(dataset)), size)
    return [dataset[i] for i in sorted(indices)]


def main():
    print("=== h-m2 Combined Scoring Experiment ===\n")

    # Load config
    config = ExperimentConfig()

    # Set random seeds
    random.seed(config.random_seed)
    np.random.seed(config.random_seed)
    torch.manual_seed(config.random_seed)

    # Setup device and model
    print("Loading model...")
    device = setup_device(config.model.device)
    model, tokenizer = load_codellama(
        config.model.name,
        device,
        config.model.dtype
    )
    print(f"Model loaded on {device}\n")

    # Load dataset
    print("Loading HumanEval dataset...")
    full_dataset = load_humaneval()
    problems = [
        {
            'task_id': item['task_id'],
            'prompt': item['prompt']
        }
        for item in full_dataset
    ]
    print(f"Loaded {len(problems)} problems\n")

    # Create ablation subset
    ablation_subset = create_ablation_subset(
        problems,
        config.dataset.ablation_size,
        config.random_seed
    )
    print(f"Created ablation subset: {len(ablation_subset)} problems\n")

    # Create output directories
    Path("results").mkdir(exist_ok=True)
    Path("outputs").mkdir(exist_ok=True)

    # Use small subset for POC
    poc_problems = problems[:3]
    print(f"Using {len(poc_problems)} problems for POC\n")

    # Experiment A: AST Latency
    print("=== Experiment A: AST Latency Measurement ===")
    latency_results = experiment_a_latency(model, tokenizer, poc_problems, k=3)
    latency_analysis = analyze_latency(latency_results['timings'])
    print(f"Mean latency: {latency_analysis['stats']['mean']:.2f} ms")
    print(f"P95 latency: {latency_analysis['stats']['p95']:.2f} ms")
    print(f"Gate pass: {latency_analysis['gate_pass']}\n")

    with open('results/ast_latency_stats.json', 'w') as f:
        json.dump(latency_analysis, f, indent=2)

    # Experiment B: Beam Ranking
    print("=== Experiment B: Validity Measurement ===")
    ranking_results = experiment_b_ranking(model, tokenizer, poc_problems, 0.7, 0.3)
    ranking_analysis = analyze_ranking(ranking_results['logs'])
    print(f"Validity proportion: {ranking_analysis['correct_proportion']:.2%}")
    print(f"Gate pass: {ranking_analysis['gate_pass']}\n")

    # Experiment C: Ablation Study (skip for POC - too slow on CPU)
    print("=== Experiment C: Alpha/Beta Ablation ===")
    print("Skipped for POC (CPU too slow)\n")

    ablation_analysis = {
        'optimal_pair': (0.7, 0.3),
        'metrics_by_pair': {}
    }

    with open('results/ablation_results.json', 'w') as f:
        json.dump({'status': 'skipped', 'reason': 'CPU performance'}, f, indent=2)

    # Baseline Comparison
    print("=== Baseline Comparison ===")
    baseline_results = baseline_comparison(model, tokenizer, poc_problems)
    print(f"Pure beam error rate: {baseline_results['pure_beam_error_rate']:.2%}")
    print(f"Combined error rate: {baseline_results['combined_error_rate']:.2%}")
    print(f"Improvement: {baseline_results['improvement']:.2%}\n")

    with open('results/baseline_comparison.json', 'w') as f:
        json.dump(baseline_results, f, indent=2)

    # Final gate check
    print("=== Gate Check Summary ===")
    gate_results = {
        'ast_latency_pass': latency_analysis['gate_pass'],
        'ranking_correctness_pass': ranking_analysis['gate_pass'],
        'baseline_improvement_pass': baseline_results['combined_error_rate'] < 0.64
    }

    all_pass = all(gate_results.values())
    print(f"AST Latency: {'PASS' if gate_results['ast_latency_pass'] else 'FAIL'}")
    print(f"Ranking Correctness: {'PASS' if gate_results['ranking_correctness_pass'] else 'FAIL'}")
    print(f"Baseline Improvement: {'PASS' if gate_results['baseline_improvement_pass'] else 'FAIL'}")
    print(f"\nOverall: {'PASS' if all_pass else 'FAIL'}")

    with open('results/gate_results.json', 'w') as f:
        json.dump(gate_results, f, indent=2)

    return gate_results


if __name__ == "__main__":
    main()
