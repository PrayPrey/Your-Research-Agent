"""Orchestrator for H-M3: PermAug partial equivariance benefit experiment."""
import os
import sys
import json
import argparse
import numpy as np

# Make local modules importable
_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _CODE_DIR)

import config
from results_loader import load_baselines, save_results
from perm_train import train_all_sizes
from analysis import bootstrap_ci, compute_gap_analysis, check_ordering_gate
from visualize import plot_gate_metrics, plot_ordering_curve, plot_gap_fraction, plot_training_curves


def main(device: str = "cuda") -> dict:
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

    # 1. Load baselines (flat_mlp, gnn_nfn) from H-M2
    print("\n[H-M3] Step 1: Loading baselines from H-M2...")
    baselines = load_baselines(config.H_M2_RESULTS_JSON)
    print(f"  Loaded encoders: {list(baselines.keys())}")

    # 2. Train PermAug at all training sizes
    print("\n[H-M3] Step 2: Training Flat-MLP + PermAug...")
    perm_aug_raw = train_all_sizes(config.TRAINING_SIZES, zoo_name="cifar10", device=device)

    # 3. Compute bootstrap CI for perm_aug results
    print("\n[H-M3] Step 3: Computing bootstrap CI for PermAug...")
    np.random.seed(config.SEED)
    perm_aug_r2s = {"cifar10": {}}
    train_curves = {}

    for sz_str, cell in perm_aug_raw.items():
        r2 = cell["r2"]
        mean, ci_lo, ci_hi = bootstrap_ci([r2], n_boot=config.N_BOOT)
        perm_aug_r2s["cifar10"][sz_str] = {
            "mean_r2": mean,
            "ci_lo": ci_lo,
            "ci_hi": ci_hi,
            "seed_r2s": [r2],
        }
        train_curves[f"perm_aug_N={sz_str}"] = cell["train_losses"]

    # 4. Merge all results
    all_results = {
        "flat_mlp": baselines["flat_mlp"],
        "flat_mlp_perm_aug": perm_aug_r2s,
        "gnn_nfn": baselines["gnn_nfn"],
    }

    # 5. Gap analysis and gate check
    print("\n[H-M3] Step 4: Gap analysis and gate check...")
    gap_analysis = compute_gap_analysis(all_results, zoo="cifar10")
    gate_passed, gate_details = check_ordering_gate(all_results, zoo="cifar10",
                                                     gate_sizes=[100, 250])

    # 6. Assemble full results and save
    result_str = "GATE PASSED" if gate_passed else "GATE FAILED"
    all_results["gap_analysis"] = gap_analysis
    all_results["gate"] = {
        "satisfied": gate_passed,
        "result_str": result_str,
        "details": gate_details,
    }

    results_path = os.path.join(config.RESULTS_DIR, "results.json")
    save_results(all_results, results_path)

    # 7. Generate 4 figures
    print("\n[H-M3] Step 5: Generating figures...")
    plot_gate_metrics(all_results, os.path.join(config.FIGURES_DIR, "gate_metrics.png"))
    plot_ordering_curve(all_results, os.path.join(config.FIGURES_DIR, "ordering_plot.png"))
    plot_gap_fraction(gap_analysis, os.path.join(config.FIGURES_DIR, "gap_fraction.png"))
    plot_training_curves(train_curves, os.path.join(config.FIGURES_DIR, "training_curves.png"))

    # 8. Print summary table
    print("\n" + "=" * 75)
    print(f"H-M3 RESULTS SUMMARY — {result_str}")
    print("=" * 75)
    print(f"{'Encoder':<25} {'N':>6} {'R²':>8} {'CI_lo':>8} {'CI_hi':>8}")
    print("-" * 75)
    for enc in ["flat_mlp", "flat_mlp_perm_aug", "gnn_nfn"]:
        zoo_data = all_results[enc].get("cifar10", {})
        for sz in config.TRAINING_SIZES:
            sz_str = str(sz)
            if sz_str in zoo_data:
                d = zoo_data[sz_str]
                print(f"{enc:<25} {sz:>6} {d['mean_r2']:>8.4f} {d['ci_lo']:>8.4f} {d['ci_hi']:>8.4f}")

    print("\nGap Analysis:")
    for sz_str, g in gap_analysis.items():
        print(f"  N={sz_str}: gap_total={g['gap_total']:.4f} "
              f"gap_perm={g['gap_perm_aug']:.4f} "
              f"fraction={g['perm_aug_fraction']:.3f}")

    print(f"\nGate: {result_str}")
    for sz_str, d in gate_details.items():
        print(f"  N={sz_str}: passed={d['passed']}, "
              f"cond1={d.get('cond1_flat_below_perm')}, cond2={d.get('cond2_perm_below_gnn')}")

    print("=" * 75)
    return all_results


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--device", default="cuda")
    args = p.parse_args()
    main(args.device)
