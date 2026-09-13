#!/usr/bin/env python3
"""
H-M2 Experiment: Deep Network Metric Decoupling
Tests R^2 drop from convex (H-M1) to non-convex (ResNet-18).
MUST_WORK gate: R^2_deep < 0.80

Full pipeline:
1. Load config, model, data, LOO cache
2. Compute deep attribution scores (4 methods x 5 budgets x 3 seeds)
3. Build metrics DataFrame
4. R^2 regression analysis
5. Partial correlation analysis
6. Load H-M1 baseline
7. Evaluate gate conditions
8. Save results
9. Generate figures
10. Print gate summary
"""

import os
import sys
import torch
import argparse
from datetime import datetime

# Add local directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config, HM2Config
from deep_analysis import (
    load_deep_model,
    load_loo_cache,
    get_he1_loaders,
    compute_deep_attribution_scores,
    build_deep_metrics_df,
)
from comparison import (
    compute_r2_deep,
    compute_partial_corr_deep,
    compute_r2_by_method,
    compute_r2_by_budget,
    load_hm1_baseline,
    evaluate_gate,
    save_results,
)
from visualize import generate_all_figures


def main():
    """Run full H-M2 experiment pipeline."""
    parser = argparse.ArgumentParser(description='H-M2 Deep Network Metric Decoupling Experiment')
    parser.add_argument('--device', type=str, default='cuda', help='Device (cuda/cpu)')
    args = parser.parse_args()

    print("=" * 60)
    print("H-M2: Deep Network Metric Decoupling Experiment")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Step 1: Configuration
    print("[1/10] Loading configuration...")
    cfg = get_config()

    # Set device
    device = args.device
    if device == 'cuda' and not torch.cuda.is_available():
        device = 'cpu'
        print("CUDA not available, using CPU")
    print(f"Using device: {device}")
    print()

    # Step 2: Load model
    print("[2/10] Loading deep model (ResNet-18)...")
    model = load_deep_model(cfg, device)
    print()

    # Step 3: Load LOO cache
    print("[3/10] Loading LOO ground truth cache...")
    loo_exact = load_loo_cache(cfg)
    print()

    # Step 4: Load data loaders
    print("[4/10] Loading data loaders...")
    train_loader, test_loader = get_he1_loaders(cfg)
    print()

    # Step 5: Compute attribution scores
    print("[5/10] Computing attribution scores...")
    print(f"  Methods: {cfg.methods}")
    print(f"  Budgets: {cfg.compute_budgets}")
    print(f"  Seeds: {cfg.seeds}")
    method_scores = compute_deep_attribution_scores(
        cfg, model, train_loader, test_loader, device
    )
    print()

    # Step 6: Build metrics DataFrame
    print("[6/10] Building metrics DataFrame...")
    metrics_df = build_deep_metrics_df(method_scores, loo_exact)
    print()

    # Step 7: R^2 and partial correlation analysis
    print("[7/10] Computing R^2 regression analysis...")
    r2_deep = compute_r2_deep(metrics_df)
    partial_corr_deep = compute_partial_corr_deep(metrics_df, cfg)
    r2_by_method = compute_r2_by_method(metrics_df)
    r2_by_budget = compute_r2_by_budget(metrics_df, cfg)
    print()

    # Step 8: Load H-M1 baseline
    print("[8/10] Loading H-M1 convex baseline...")
    hm1_baseline = load_hm1_baseline(cfg)
    print(f"  Convex R^2 (rho_r): {hm1_baseline['r2_rho_r']:.4f}")
    print(f"  Convex R^2 (rho_m): {hm1_baseline['r2_rho_m']:.4f}")
    print()

    # Step 9: Evaluate gate
    print("[9/10] Evaluating MUST_WORK gate...")
    gate_results = evaluate_gate(r2_deep, partial_corr_deep, hm1_baseline, cfg)
    print()

    # Step 10: Save results
    print("[10/10] Saving results...")
    save_results(
        metrics_df=metrics_df,
        r2_results=r2_deep,
        partial_corr_deep=partial_corr_deep,
        hm1_baseline=hm1_baseline,
        gate_results=gate_results,
        r2_by_method=r2_by_method,
        cfg=cfg,
    )
    print()

    # Generate figures
    print("Generating figures...")
    generate_all_figures(
        metrics_df=metrics_df,
        r2_deep=r2_deep,
        partial_corr_deep=partial_corr_deep,
        hm1_baseline=hm1_baseline,
        gate_results=gate_results,
        r2_by_method=r2_by_method,
        r2_deep_by_budget=r2_by_budget,
        cfg=cfg,
    )
    print()

    # Final summary
    print("=" * 60)
    print("H-M2 EXPERIMENT COMPLETE")
    print("=" * 60)
    print()
    print("=== GATE RESULT ===")
    print(f"MUST_WORK Gate: {'PASS' if gate_results['gate_pass'] else 'FAIL'}")
    print()
    print(f"SC-2 (R^2 < {cfg.r2_threshold}): {'PASS' if gate_results['sc2_pass'] else 'FAIL'}")
    print(f"  R^2(rho_r) = {r2_deep['r2_rho_r']:.4f}")
    print(f"  R^2(rho_m) = {r2_deep['r2_rho_m']:.4f}")
    print()
    print(f"SC-3 (corr < {cfg.partial_corr_threshold}): {'PASS' if gate_results['sc3_pass'] else 'FAIL'}")
    print(f"  min_corr = {gate_results['min_partial_corr']:.4f}")
    print()
    print(f"SC-4 (delta_R^2 > {cfg.delta_r2_threshold}): {'PASS' if gate_results['sc4_pass'] else 'FAIL'}")
    print(f"  delta_R^2 = {gate_results['delta_r2']:.4f}")
    print()
    print("Key Findings:")
    print(f"  - Deep R^2 avg: {r2_deep['r2_avg']:.4f}")
    print(f"  - Convex R^2 avg: {hm1_baseline['r2_avg']:.4f}")
    print(f"  - Demonstrates {'structural metric decoupling' if gate_results['gate_pass'] else 'metrics still coupled'}")
    print()
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    return gate_results


if __name__ == '__main__':
    main()
