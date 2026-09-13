#!/usr/bin/env python3
"""H-D1 experiment orchestrator."""
import os
import sys
import json
import numpy as np

# Add code dir to path
sys.path.insert(0, os.path.dirname(__file__))

import config
from wb_loader import load_wb_results, extract_primary
from celeba_data import load_celeba_balanced, get_celeba_dataloader
from feature_extract import extract_and_save_celeba_features
from probe import run_celeba_probing
from analysis import run_all_analyses
from viz import generate_all_figures


def main():
    print("=" * 60)
    print("H-D1: Directional Paradigm × Dataset Interaction Analysis")
    print("=" * 60)

    # Step 1: Load WB results from H-E1
    print("\n[1] Loading Waterbirds results from H-E1...")
    wb_results = load_wb_results()
    erm_wb, moco_wb = extract_primary(wb_results)
    print(f"    ERM WB ratios:  mean={np.mean(erm_wb):.4f} ± {np.std(erm_wb):.4f}")
    print(f"    MoCo WB ratios: mean={np.mean(moco_wb):.4f} ± {np.std(moco_wb):.4f}")

    # Step 2: Load CelebA data
    print("\n[2] Loading CelebA dataset (group-balanced)...")
    dataset, task_labels, spurious_labels, train_idx, test_idx = load_celeba_balanced()
    all_idx = np.concatenate([train_idx, test_idx])
    print(f"    Total balanced samples: {len(all_idx)}")
    print(f"    Train: {len(train_idx)}, Test: {len(test_idx)}")
    for t in [0, 1]:
        for s in [0, 1]:
            mask = (task_labels[all_idx] == t) & (spurious_labels[all_idx] == s)
            print(f"    Group (Blond={t}, Male={s}): {mask.sum()} samples")

    # Step 3: Extract CelebA features (ERM + MoCo)
    # Features are extracted in all_idx order → local indices 0..N-1
    print("\n[3] Extracting CelebA features...")
    features_by_paradigm = {}
    for paradigm in config.PRIMARY_PARADIGMS:
        save_path = config.CELEBA_FEATURES_PATH[paradigm]
        dataloader = get_celeba_dataloader(dataset, all_idx)
        feats = extract_and_save_celeba_features(paradigm, dataloader, save_path)
        features_by_paradigm[paradigm] = feats
        print(f"    {paradigm}: features shape {feats.shape}")

    # Map absolute indices to local feature-array positions
    abs_to_local = {int(abs_i): local_i for local_i, abs_i in enumerate(all_idx)}
    local_train = np.array([abs_to_local[i] for i in train_idx])
    local_test  = np.array([abs_to_local[i] for i in test_idx])
    local_all   = np.arange(len(all_idx))

    # Local task/spurious labels in all_idx order
    task_local     = task_labels[all_idx]
    spurious_local = spurious_labels[all_idx]

    # Step 4: Run CelebA probing
    print("\n[4] Running CelebA linear probing (5 seeds × 2 paradigms)...")
    celeba_results = run_celeba_probing(
        features_by_paradigm, task_local, spurious_local, local_all,
        save_path=config.CELEBA_PROBE_RESULTS_PATH
    )
    for p, ratios in celeba_results.items():
        print(f"    {p}: mean={np.mean(ratios):.4f} ± {np.std(ratios):.4f}")

    # Step 5: Run all analyses
    print("\n[5] Running statistical analyses...")
    # Merge WB dino/barlowtwins into celeba_results for full interaction plot
    celeba_results_full = dict(celeba_results)
    # Only erm/moco for CelebA; dino/barlowtwins not extracted for CelebA
    results = run_all_analyses(wb_results, celeba_results_full)

    # Step 6: Generate figures
    print("\n[6] Generating figures...")
    # For interaction plot, create stub for dino/barlowtwins on CelebA
    celeba_for_viz = dict(celeba_results)
    generate_all_figures(wb_results, celeba_for_viz, results)

    # Step 7: Print verdict
    print("\n" + "=" * 60)
    print("GATE VERDICT:", results['gate_verdict'].upper())
    print("INTERPRETATION:", results['interpretation']['interpretation'])
    wb = results['wb_primary']
    ca = results['ca_primary']
    print(f"\nWaterbirds directional test (MoCo > ERM):")
    print(f"  t={wb['t']:.3f}, p={wb['p_directional']:.4f}, d={wb['cohen_d']:.3f}")
    print(f"  MoCo mean={wb['moco_mean']:.4f}, ERM mean={wb['erm_mean']:.4f}")
    print(f"  Direction: {wb['direction']}")
    print(f"\nCelebA null test (two-sided):")
    print(f"  t={ca['t']:.3f}, p={ca['p_two_sided']:.4f}, d={ca['cohen_d']:.3f}")
    print(f"  MoCo mean={ca['moco_mean']:.4f}, ERM mean={ca['erm_mean']:.4f}")
    print(f"\nGate conditions:")
    print(f"  WB p < 0.05: {wb['p_directional'] < 0.05} (p={wb['p_directional']:.4f})")
    print(f"  CelebA p > 0.10: {ca['p_two_sided'] > 0.10} (p={ca['p_two_sided']:.4f})")
    print(f"\nScientific finding:")
    print(f"  {results['interpretation']['scientific_finding'][:200]}...")
    print("=" * 60)
    print("EXPERIMENT COMPLETE")


if __name__ == '__main__':
    main()
