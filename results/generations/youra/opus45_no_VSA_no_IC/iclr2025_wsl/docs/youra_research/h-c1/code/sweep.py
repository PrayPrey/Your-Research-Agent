"""Sweep over N values and seeds for NFN vs MLP comparison."""
import time
import random
from typing import List, Dict

import config
from nfn_model import NFNAccuracyPredictor, collate_weights
from mlp_model import MLPBaseline, collate_flat, infer_input_dim
from train_common import train_model, evaluate_model, set_seed


def run_single(
    n: int, seed: int,
    train_pool: list, test_items: list,
    cfg: config.Config = config.CONFIG
) -> Dict:
    """Train NFN+MLP on same N-sample subset, eval both on test set."""
    set_seed(seed)

    # Sample N items from train pool
    rng = random.Random(seed)
    indices = rng.sample(range(len(train_pool)), n)
    subset = [train_pool[i] for i in indices]

    # Infer input dim for MLP
    input_dim = infer_input_dim(subset[0][0])

    device = "cuda" if __import__('torch').cuda.is_available() else "cpu"

    # Train NFN
    nfn = NFNAccuracyPredictor(
        hidden_dim=cfg.nfn.hidden_dim,
        num_layers=cfg.nfn.num_layers
    )
    set_seed(seed)  # Reset for reproducibility
    train_model(nfn, subset, collate_weights, cfg, device)
    r2_nfn = evaluate_model(nfn, test_items, collate_weights, device)["r2"]

    # Train MLP
    mlp = MLPBaseline(input_dim=input_dim, hidden_dim=cfg.mlp.hidden_dim)
    set_seed(seed)
    train_model(mlp, subset, collate_flat, cfg, device)
    r2_mlp = evaluate_model(mlp, test_items, collate_flat, device)["r2"]

    return {"n": n, "seed": seed, "r2_nfn": r2_nfn, "r2_mlp": r2_mlp}


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
            print(f"N={n} seed={seed} r2_nfn={r['r2_nfn']:.4f} r2_mlp={r['r2_mlp']:.4f} ({r['elapsed_sec']:.1f}s)")

    return results
