"""
H-E1 Experiment: Canonical Channel Permutation Invariance & Orbit-PE Computability
Entry point: python run_experiment.py

MUST_WORK gate:
  - mean |Δacc| < 0.001 for CNN Zoo
  - mean |Δacc| < 0.001 for Transformer Zoo
  - orbit-PE success rate == 1.0
"""
import json
import os
import sys
import time
from typing import Dict, List

import torch

# Ensure code dir is on path
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

from config import load_config
from data_loader import CNNZooLoader, TransformerZooLoader
from evaluate import run_cnn_evaluation, run_transformer_evaluation
from orbit_pe import compute_orbit_pe, compute_orbit_pe_success_rate
from visualize import (
    plot_gate_metrics_comparison,
    plot_delta_acc_distribution,
    plot_orbit_pe_success_table,
    plot_per_seed_stability,
)


# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
RESEARCH_DIR = os.path.dirname(CODE_DIR)  # h-e1/
DATA_CACHE = os.path.join(
    os.path.dirname(RESEARCH_DIR), ".data_cache", "datasets"
)
CNN_ZOO_DIR = os.path.join(DATA_CACHE, "cnn_zoo", "cifar10_cnn_sample_ep21-25")
MNIST_DIR = os.path.join(DATA_CACHE, "transformer_zoo", "mnist")
FIGURES_DIR = os.path.join(RESEARCH_DIR, "figures")
RESULTS_PATH = os.path.join(RESEARCH_DIR, "experiment_results.json")
RESULTS_CSV = os.path.join(CODE_DIR, "outputs", "results.csv")


def compute_summary_metrics(results: List[Dict]) -> Dict:
    """Aggregate mean/std/max per architecture family."""
    if not results:
        return {"mean": 0.0, "std": 0.0, "max": 0.0, "count": 0}
    deltas = [r["delta_acc"] for r in results]
    import numpy as np
    return {
        "mean": float(np.mean(deltas)),
        "std": float(np.std(deltas)),
        "max": float(np.max(deltas)),
        "count": len(deltas),
    }


def evaluate_gate(metrics: Dict) -> bool:
    """Returns True iff PASS: mean_delta_cnn < 0.001 AND mean_delta_transformer < 0.001
    AND orbit_pe_success_rate == 1.0."""
    cnn_ok = metrics.get("mean_delta_acc_cnn", 1.0) < 0.001
    tf_ok = metrics.get("mean_delta_acc_transformer", 1.0) < 0.001
    orbit_ok = metrics.get("orbit_pe_success_rate", 0.0) >= 1.0
    return cnn_ok and tf_ok and orbit_ok


def save_results(metrics: Dict, gate_pass: bool, path: str) -> None:
    """Save results.json with all metrics."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    output = {**metrics, "gate_pass": gate_pass}
    with open(path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"✓ Results saved: {path}")


def save_results_csv(cnn_results: List[Dict], tf_results: List[Dict], path: str) -> None:
    """Save per-sample results to CSV."""
    import csv
    os.makedirs(os.path.dirname(path), exist_ok=True)
    all_results = [{"arch": "cnn", **r} for r in cnn_results] + \
                  [{"arch": "transformer", **r} for r in tf_results]
    if all_results:
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)
    print(f"✓ CSV saved: {path}")


def main():
    print("=" * 70)
    print("H-E1 EXPERIMENT: Canonical Channel Permutation Invariance")
    print("=" * 70)
    start_time = time.time()

    # Select GPU
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
        print(f"Device: {device} ({torch.cuda.get_device_name(0)})")
    else:
        device = torch.device("cpu")
        print(f"Device: CPU")

    cfg = load_config(os.path.join(CODE_DIR, "config.yaml"))
    perm_seeds = list(range(cfg.n_permutations))

    os.makedirs(FIGURES_DIR, exist_ok=True)

    # ─── Step 1: Load CNN Zoo Checkpoints ──────────────────────────────────
    print("\n[1/5] Loading CNN Zoo checkpoints...")
    cnn_loader = CNNZooLoader(CNN_ZOO_DIR, n_checkpoints=cfg.n_cnn_checkpoints, seed=cfg.sample_seed)
    cnn_checkpoints = cnn_loader.load_checkpoints()
    print(f"  Loaded {len(cnn_checkpoints)} CNN checkpoints")

    # ─── Step 2: Load Transformer Zoo Checkpoints ──────────────────────────
    print("\n[2/5] Loading Transformer Zoo checkpoints...")
    tf_loader = TransformerZooLoader(
        mnist_dir=MNIST_DIR,
        n_mnist=cfg.n_transformer_checkpoints,
        seed=cfg.sample_seed,
    )
    tf_checkpoints = tf_loader.load_checkpoints()
    print(f"  Loaded {len(tf_checkpoints)} Transformer checkpoints")

    # ─── Step 3: Run CNN Evaluation ─────────────────────────────────────────
    print(f"\n[3/5] Running CNN permutation evaluation ({len(cnn_checkpoints)} × {len(perm_seeds)} = {len(cnn_checkpoints)*len(perm_seeds)} runs)...")
    cnn_results = run_cnn_evaluation(cnn_checkpoints, perm_seeds, device)

    # ─── Step 4: Run Transformer Evaluation ─────────────────────────────────
    print(f"\n[4/5] Running Transformer permutation evaluation ({len(tf_checkpoints)} × {len(perm_seeds)} = {len(tf_checkpoints)*len(perm_seeds)} runs)...")
    tf_results = run_transformer_evaluation(tf_checkpoints, perm_seeds, device)

    # ─── Step 5: Orbit-PE Computability Check ───────────────────────────────
    print("\n[5/5] Running Orbit-PE computability check...")

    # Use representative state_dicts from each zoo
    orbit_success_flags = {}

    if cnn_checkpoints:
        cnn_sd = cnn_checkpoints[0]["state_dict"]
        cnn_type_map = {}
        for k, v in cnn_sd.items():
            if k.endswith(".weight"):
                if v.dim() == 4:
                    cnn_type_map[k] = "Conv2d"
                elif v.dim() == 2:
                    cnn_type_map[k] = "Linear"
        _, cnn_flags = compute_orbit_pe(cnn_sd, cnn_type_map)
        orbit_success_flags.update(cnn_flags)

    if tf_checkpoints:
        tf_sd = tf_checkpoints[0]["state_dict"]
        tf_type_map = {}
        for k, v in tf_sd.items():
            if k.endswith(".weight"):
                if v.dim() == 4:
                    tf_type_map[k] = "Conv2d"
                elif v.dim() == 2:
                    if any(x in k.lower() for x in ["queri", "keys", "values", "proj", "attention"]):
                        tf_type_map[k] = "MultiheadAttention"
                    else:
                        tf_type_map[k] = "Linear"
        n_heads = tf_checkpoints[0].get("arch_config", {}).get("n_heads", 2)
        _, tf_flags = compute_orbit_pe(tf_sd, tf_type_map, n_heads=n_heads)
        orbit_success_flags.update(tf_flags)

    orbit_success_rate = compute_orbit_pe_success_rate(orbit_success_flags)
    print(f"  Orbit-PE success rate: {orbit_success_rate:.4f}")

    # ─── Compute Summary Metrics ────────────────────────────────────────────
    cnn_metrics = compute_summary_metrics(cnn_results)
    tf_metrics = compute_summary_metrics(tf_results)
    cnn_deltas = [r["delta_acc"] for r in cnn_results]
    tf_deltas = [r["delta_acc"] for r in tf_results]

    metrics = {
        "mean_delta_acc_cnn": cnn_metrics["mean"],
        "std_delta_acc_cnn": cnn_metrics["std"],
        "max_delta_acc_cnn": cnn_metrics["max"],
        "n_cnn_evaluations": cnn_metrics["count"],
        "mean_delta_acc_transformer": tf_metrics["mean"],
        "std_delta_acc_transformer": tf_metrics["std"],
        "max_delta_acc_transformer": tf_metrics["max"],
        "n_transformer_evaluations": tf_metrics["count"],
        "orbit_pe_success_rate": orbit_success_rate,
        "threshold": cfg.delta_acc_threshold,
        "elapsed_seconds": time.time() - start_time,
    }

    gate_pass = evaluate_gate(metrics)

    # ─── Generate Figures ───────────────────────────────────────────────────
    print("\nGenerating figures...")
    plot_gate_metrics_comparison(
        cnn_metrics["mean"], tf_metrics["mean"], cfg.delta_acc_threshold,
        os.path.join(FIGURES_DIR, "gate_metrics_comparison.png")
    )
    plot_delta_acc_distribution(
        cnn_deltas, tf_deltas,
        os.path.join(FIGURES_DIR, "delta_acc_distribution.png")
    )
    plot_orbit_pe_success_table(
        orbit_success_flags,
        os.path.join(FIGURES_DIR, "orbit_pe_success_table.png")
    )
    plot_per_seed_stability(
        cnn_results, tf_results,
        os.path.join(FIGURES_DIR, "per_seed_stability.png")
    )

    # ─── Save Results ───────────────────────────────────────────────────────
    save_results(metrics, gate_pass, RESULTS_PATH)
    save_results_csv(cnn_results, tf_results, RESULTS_CSV)

    # ─── Print Gate Verdict ─────────────────────────────────────────────────
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("EXPERIMENT RESULTS")
    print("=" * 70)
    print(f"CNN Zoo:         mean |Δacc| = {cnn_metrics['mean']:.6f} (threshold: {cfg.delta_acc_threshold})")
    print(f"Transformer Zoo: mean |Δacc| = {tf_metrics['mean']:.6f} (threshold: {cfg.delta_acc_threshold})")
    print(f"Orbit-PE:        success rate = {orbit_success_rate:.4f}")
    print(f"Elapsed:         {elapsed:.1f}s")
    print()
    if gate_pass:
        print("GATE VERDICT: ✓ PASS")
        print("  H-E1 MUST_WORK gate SATISFIED:")
        print("  - Permutation is a valid symmetry (|Δacc| < 0.1%)")
        print("  - Orbit-PE is computable for all layer types")
    else:
        print("GATE VERDICT: ✗ FAIL")
        failed = []
        if cnn_metrics["mean"] >= 0.001:
            failed.append(f"CNN mean |Δacc| = {cnn_metrics['mean']:.6f} >= 0.001")
        if tf_metrics["mean"] >= 0.001:
            failed.append(f"Transformer mean |Δacc| = {tf_metrics['mean']:.6f} >= 0.001")
        if orbit_success_rate < 1.0:
            failed.append(f"Orbit-PE success rate = {orbit_success_rate:.4f} < 1.0")
        for f in failed:
            print(f"  FAILED: {f}")
    print("=" * 70)
    print("EXPERIMENT COMPLETE")

    return gate_pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
