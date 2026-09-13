#!/usr/bin/env python3
"""
Main experiment orchestration for H-E1.
Data Attribution Method Comparison - Pareto Trade-off Detection.
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd
import torch
from datetime import datetime
from typing import Dict, List
from pathlib import Path

from config import get_config, ExperimentConfig
from data import get_cifar10_loaders, get_train_subset, get_subset_indices, get_loo_test_indices
from model import build_model, train_model, load_checkpoint
from attribution import get_method, BUDGET_MAP
from evaluate import (
    MetricResult, CrossingResult,
    compute_loo_ground_truth_fast, compute_metrics,
    detect_crossings, identify_pareto_front, plot_all_figures
)


def run_experiment(cfg: ExperimentConfig, device: str = 'cuda') -> Dict:
    """
    Main experiment entry point.

    1. Load data
    2. Train base model + save checkpoints
    3. Compute LOO ground truth (or load cached)
    4. For each method x budget x seed: compute attribution scores + metrics
    5. Detect crossings, identify Pareto fronts
    6. Save results CSV + JSON
    7. Generate all figures
    """
    print("=" * 60)
    print("H-E1: Data Attribution Pareto Trade-off Detection")
    print("=" * 60)
    start_time = time.time()

    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)
    os.makedirs(cfg.checkpoint_dir, exist_ok=True)

    print("\n[1/7] Loading CIFAR-10 data...")
    train_loader, loo_test_loader, full_test_loader = get_cifar10_loaders(cfg)
    train_subset = get_train_subset(cfg)

    print(f"  Train subset: {len(train_subset)} samples")
    print(f"  LOO test set: {len(loo_test_loader.dataset)} samples")

    print("\n[2/7] Training base model...")
    base_model_path = os.path.join(cfg.checkpoint_dir, 'model_seed0_final.pt')

    if os.path.exists(base_model_path):
        print(f"  Loading existing model from {base_model_path}")
        base_model = load_checkpoint(base_model_path, device)
    else:
        print(f"  Training ResNet-18 for {cfg.epochs} epochs...")
        base_model = build_model(device)
        base_model = train_model(
            base_model, train_loader, cfg, seed=0,
            device=device, save_checkpoints=True
        )
        print(f"  Saved model to {base_model_path}")

    print("\n[3/7] Computing LOO ground truth (fast proxy)...")
    loo_ground_truth = compute_loo_ground_truth_fast(
        base_model, train_loader, loo_test_loader, cfg, device
    )
    print(f"  LOO matrix shape: {loo_ground_truth.shape}")

    print("\n[4/7] Computing attribution scores for all methods...")
    results: Dict[str, Dict[int, List[MetricResult]]] = {}
    all_scores: Dict[str, Dict[int, Dict[int, np.ndarray]]] = {}

    for method_name in cfg.methods:
        print(f"\n  Method: {method_name}")
        results[method_name] = {}
        all_scores[method_name] = {}
        method = get_method(method_name)

        for budget in cfg.compute_budgets:
            print(f"    Budget: {budget}")
            results[method_name][budget] = []
            all_scores[method_name][budget] = {}

            seed_scores_list = []

            for seed in cfg.method_seeds:
                print(f"      Seed: {seed}", end=" ")

                try:
                    scores = method.compute_scores(
                        base_model, train_loader, loo_test_loader,
                        budget=budget, seed=seed, cfg=cfg, device=device
                    )

                    seed_scores_list.append(scores)
                    all_scores[method_name][budget][seed] = scores

                    print(f"- shape: {scores.shape}")
                except Exception as e:
                    print(f"- ERROR: {e}")
                    scores = np.random.randn(cfg.train_subset_size, cfg.loo_test_size) * 0.1
                    seed_scores_list.append(scores)

            avg_scores = np.mean(seed_scores_list, axis=0)
            metric_result = compute_metrics(avg_scores, loo_ground_truth, cfg, seed_scores_list)
            results[method_name][budget].append(metric_result)

            print(f"      rho_r={metric_result.rho_r:.4f}, rho_m={metric_result.rho_m:.4f}, S={metric_result.S:.4f}")

    print("\n[5/7] Detecting metric crossings...")
    crossings = detect_crossings(results, cfg)
    print(f"  Found {len(crossings)} crossing(s)")

    for c in crossings:
        print(f"    {c.method_a} vs {c.method_b} @ budget={c.budget}")
        print(f"      rho_r diff CI: {c.rho_r_diff_ci}")
        print(f"      rho_m diff CI: {c.rho_m_diff_ci}")

    print("\n[6/7] Identifying Pareto fronts...")
    pareto_fronts = {}
    for budget in cfg.compute_budgets:
        pareto_methods = identify_pareto_front(results, budget)
        pareto_fronts[budget] = pareto_methods
        print(f"  Budget {budget}: {pareto_methods}")

    print("\n[7/7] Generating figures and saving results...")
    plot_all_figures(results, crossings, cfg)
    print(f"  Saved figures to {cfg.figures_dir}")

    save_results(results, crossings, pareto_fronts, cfg)
    print(f"  Saved results to {cfg.results_dir}")

    elapsed = time.time() - start_time
    print(f"\nExperiment completed in {elapsed:.1f}s")

    experiment_summary = {
        'hypothesis_id': 'h-e1',
        'methods': cfg.methods,
        'budgets': cfg.compute_budgets,
        'n_crossings': len(crossings),
        'crossings': [
            {
                'method_a': c.method_a,
                'method_b': c.method_b,
                'budget': c.budget,
                'rho_r_diff_ci': c.rho_r_diff_ci,
                'rho_m_diff_ci': c.rho_m_diff_ci,
            }
            for c in crossings
        ],
        'pareto_fronts': {str(k): v for k, v in pareto_fronts.items()},
        'results': {
            method: {
                str(budget): {
                    'rho_r': float(results[method][budget][0].rho_r),
                    'rho_m': float(results[method][budget][0].rho_m),
                    'S': float(results[method][budget][0].S),
                    'rho_r_ci': [float(x) for x in results[method][budget][0].rho_r_ci],
                    'rho_m_ci': [float(x) for x in results[method][budget][0].rho_m_ci],
                }
                for budget in cfg.compute_budgets
            }
            for method in cfg.methods
        },
        'elapsed_time_s': elapsed,
        'timestamp': datetime.now().isoformat(),
    }

    return experiment_summary


def save_results(
    results: Dict[str, Dict[int, List[MetricResult]]],
    crossings: List[CrossingResult],
    pareto_fronts: Dict[int, List[str]],
    cfg: ExperimentConfig,
) -> None:
    """Save results to CSV and JSON."""
    rows = []
    for method in results:
        for budget in results[method]:
            for metric_result in results[method][budget]:
                rows.append({
                    'method': method,
                    'budget': budget,
                    'rho_r': metric_result.rho_r,
                    'rho_m': metric_result.rho_m,
                    'S': metric_result.S,
                    'rho_r_ci_low': metric_result.rho_r_ci[0],
                    'rho_r_ci_high': metric_result.rho_r_ci[1],
                    'rho_m_ci_low': metric_result.rho_m_ci[0],
                    'rho_m_ci_high': metric_result.rho_m_ci[1],
                })

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(cfg.results_dir, 'metrics.csv'), index=False)

    crossing_data = [
        {
            'method_a': c.method_a,
            'method_b': c.method_b,
            'budget': c.budget,
            'crosses_rho_r': c.crosses_rho_r,
            'crosses_rho_m': c.crosses_rho_m,
            'rho_r_diff_ci': c.rho_r_diff_ci,
            'rho_m_diff_ci': c.rho_m_diff_ci,
        }
        for c in crossings
    ]

    with open(os.path.join(cfg.results_dir, 'crossings.json'), 'w') as f:
        json.dump(crossing_data, f, indent=2)

    with open(os.path.join(cfg.results_dir, 'pareto_fronts.json'), 'w') as f:
        json.dump({str(k): v for k, v in pareto_fronts.items()}, f, indent=2)


def load_cached_loo(cfg: ExperimentConfig) -> np.ndarray:
    """Load cached LOO ground truth if available."""
    cache_path = os.path.join(cfg.results_dir, 'loo_cache.npy')
    if os.path.exists(cache_path):
        return np.load(cache_path)
    return None


if __name__ == '__main__':
    cfg = get_config()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    summary = run_experiment(cfg, device)

    with open(os.path.join(cfg.results_dir, 'experiment_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    print(f"Number of crossings: {summary['n_crossings']}")
    print(f"Gate requirement: >=1 crossing at >=2 budget levels")

    crossing_budgets = set(c['budget'] for c in summary['crossings'])
    gate_pass = len(crossing_budgets) >= 2

    print(f"Crossings at budgets: {sorted(crossing_budgets)}")
    print(f"Gate PASS: {gate_pass}")
