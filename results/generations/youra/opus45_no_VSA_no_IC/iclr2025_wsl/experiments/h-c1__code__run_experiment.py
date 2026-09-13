"""H-C1: 3-way convergence experiment at N=5000 (Statistics vs MLP vs NFN)."""
import json
import time
import random
from pathlib import Path
import numpy as np
import torch

import config
from data import download_model_zoo, load_checkpoints, split_test_set
from nfn_model import NFNAccuracyPredictor, collate_weights
from mlp_model import MLPBaseline, collate_flat, infer_input_dim
from stats_model import train_stats_model, evaluate_stats_model
from train_common import train_model, evaluate_model, set_seed
from stats import summarize_gate
from evaluate import plot_r2_comparison, plot_pairwise_heatmap


def run_single(
    seed: int,
    train_pool: list,
    test_items: list,
    cfg: config.Config = config.CONFIG,
) -> dict:
    """Run single seed: train all 3 methods on N=5000, evaluate on test."""
    set_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    idx = random.Random(seed).sample(range(len(train_pool)), config.N_GATE)
    subset = [train_pool[i] for i in idx]

    stats_model = train_stats_model(subset)
    r2_stats = evaluate_stats_model(stats_model, test_items)["r2"]

    input_dim = infer_input_dim(subset[0][0])
    mlp = MLPBaseline(input_dim=input_dim, hidden_dim=cfg.mlp.hidden_dim)
    train_model(mlp, subset, collate_flat, cfg, device)
    r2_mlp = evaluate_model(mlp, test_items, collate_flat, device)["r2"]

    nfn = NFNAccuracyPredictor(hidden_dim=cfg.nfn.hidden_dim, num_layers=cfg.nfn.num_layers)
    train_model(nfn, subset, collate_weights, cfg, device)
    r2_nfn = evaluate_model(nfn, test_items, collate_weights, device)["r2"]

    return {
        "seed": seed,
        "n": config.N_GATE,
        "r2_stats": r2_stats,
        "r2_mlp": r2_mlp,
        "r2_nfn": r2_nfn,
    }


def run_sweep(train_pool: list, test_items: list, seeds: list = None) -> list:
    """Run all seeds at N=5000."""
    if seeds is None:
        seeds = config.CONFIG.train.seeds

    results = []
    for seed in seeds:
        t0 = time.time()
        r = run_single(seed, train_pool, test_items)
        r["elapsed_sec"] = time.time() - t0
        results.append(r)
        print(f"seed={seed} r2_stats={r['r2_stats']:.4f} r2_mlp={r['r2_mlp']:.4f} r2_nfn={r['r2_nfn']:.4f} ({r['elapsed_sec']:.0f}s)")

    return results


def main(seeds: list = None):
    """Main experiment: 3-way convergence at N=5000."""
    cfg = config.CONFIG

    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)

    zoo_path = download_model_zoo(cfg.data.zoo_dir)
    items = load_checkpoints(zoo_path)
    train_pool, test_items = split_test_set(items, cfg.data.n_test, cfg.data.split_seed)

    assert len(train_pool) >= config.N_GATE, f"Need {config.N_GATE} train samples, got {len(train_pool)}"

    print(f"\n=== H-C1: 3-Way Convergence at N={config.N_GATE} ===")
    print(f"Train pool: {len(train_pool)}, Test: {len(test_items)}")
    print(f"Gate threshold: |ΔR²| ≤ {config.R2_PAIR_DELTA_MAX}\n")

    results = run_sweep(train_pool, test_items, seeds)
    gate = summarize_gate(results)

    plot_r2_comparison(results, f"{cfg.figures_dir}/r2_comparison_N5000.png")
    plot_pairwise_heatmap(gate["pairwise_deltas"], f"{cfg.figures_dir}/pairwise_heatmap.png")

    output = {"results": results, "gate": gate}
    with open(f"{cfg.results_dir}/metrics.json", "w") as f:
        json.dump(output, f, indent=2, default=lambda x: x.tolist() if hasattr(x, 'tolist') else x)

    print(f"\n=== GATE RESULT ===")
    print(f"Means: stats={gate['means']['stats']:.4f}, mlp={gate['means']['mlp']:.4f}, nfn={gate['means']['nfn']:.4f}")
    print(f"Max pairwise delta: {gate['max_delta']:.4f} (threshold: {config.R2_PAIR_DELTA_MAX})")
    print(f"Sanity pass (all R² > {config.R2_SANITY_MIN}): {gate['sanity_pass']}")
    print(f"GATE PASS: {gate['gate_pass']}")

    return gate


if __name__ == "__main__":
    main()
