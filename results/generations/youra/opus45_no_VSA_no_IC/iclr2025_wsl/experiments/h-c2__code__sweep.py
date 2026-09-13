"""Sweep over N values and seeds for NFN vs Statistics comparison (H-C2)."""
import time
import random
from typing import List, Dict

import torch
import config
from nfn_model import NFNAccuracyPredictor, collate_weights
from statistics_model import (
    ScaledStatisticsPredictor,
    collate_statistics,
    infer_stats_dim,
)
from train_common import train_model, evaluate_model, set_seed


def run_single(
    n: int, seed: int,
    train_pool: list, test_items: list,
    cfg: config.Config = config.CONFIG
) -> Dict:
    """Train NFN + Statistics on same N-sample subset, eval both on test set."""
    set_seed(seed)

    rng = random.Random(seed)
    indices = rng.sample(range(len(train_pool)), n)
    subset = [train_pool[i] for i in indices]

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Train NFN
    nfn = NFNAccuracyPredictor(
        hidden_dim=cfg.nfn.hidden_dim,
        num_layers=cfg.nfn.num_layers
    )
    set_seed(seed)
    train_model(nfn, subset, collate_weights, cfg, device)
    r2_nfn = evaluate_model(nfn, test_items, collate_weights, device)["r2"]

    # Train Statistics baseline
    stats_dim = infer_stats_dim(subset[0][0])
    stats = ScaledStatisticsPredictor(in_dim=stats_dim)

    X_train, y_train = collate_statistics(subset)
    stats.fit_scaler(X_train)

    set_seed(seed)
    train_model(stats, subset, collate_statistics, cfg, device)
    r2_stats = evaluate_model(stats, test_items, collate_statistics, device)["r2"]

    return {"n": n, "seed": seed, "r2_nfn": r2_nfn, "r2_stats": r2_stats}


def run_sweep(
    train_pool: list, test_items: list,
    n_values: list = None,
    seeds: list = None,
) -> List[Dict]:
    """Run N x seed grid of experiments."""
    if n_values is None:
        n_values = config.N_VALUES
    if seeds is None:
        seeds = config.CONFIG.train.seeds

    results = []
    for n in n_values:
        for seed in seeds:
            t0 = time.time()
            r = run_single(n, seed, train_pool, test_items)
            r["elapsed_sec"] = time.time() - t0
            results.append(r)
            print(f"N={n} seed={seed} r2_nfn={r['r2_nfn']:.4f} r2_stats={r['r2_stats']:.4f} ({r['elapsed_sec']:.1f}s)")

    return results
