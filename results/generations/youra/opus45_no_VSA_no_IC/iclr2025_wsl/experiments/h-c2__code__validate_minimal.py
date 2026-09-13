#!/usr/bin/env python3
"""Minimal H-C2 validation: NFN vs Statistics crossing point."""
import json
import sys
import time
from pathlib import Path
import torch
import torch.nn as nn
import numpy as np
from sklearn.metrics import r2_score
from sklearn.linear_model import Ridge
import random

print("H-C2 Minimal Validation", flush=True)

sys.path.insert(0, str(Path(__file__).parent))
from nfn_model import NFNAccuracyPredictor, collate_weights
from statistics_model import extract_statistics

def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)

# Load small zoo
print("Loading zoo...", flush=True)
t0 = time.time()
items = torch.load("data/model_zoo/synthetic_zoo_6000.pt", map_location='cpu')[:2000]
print(f"Loaded {len(items)} in {time.time()-t0:.1f}s", flush=True)

# Split
rng = random.Random(42)
shuffled = list(items)
rng.shuffle(shuffled)
test_set = shuffled[:300]
train_pool = shuffled[300:]
print(f"Train pool: {len(train_pool)}, Test: {len(test_set)}", flush=True)

def train_nfn_fast(train_items, epochs=5, hidden=64):
    """Fast NFN training."""
    model = NFNAccuracyPredictor(hidden_dim=hidden, num_layers=2)
    opt = torch.optim.Adam(model.parameters(), lr=3e-3)
    loss_fn = nn.MSELoss()

    for _ in range(epochs):
        model.train()
        x, y = collate_weights(train_items)
        opt.zero_grad()
        loss = loss_fn(model(x), y)
        loss.backward()
        opt.step()
    return model

def eval_nfn(model, test_items):
    model.eval()
    with torch.no_grad():
        x, y = collate_weights(test_items)
        pred = model(x).numpy()
    return r2_score(y.numpy(), pred)

def train_eval_stats_sklearn(train_items, test_items):
    """Use sklearn Ridge for speed."""
    X_train = np.stack([extract_statistics(sd).numpy() for sd, _ in train_items])
    y_train = np.array([acc for _, acc in train_items])
    X_test = np.stack([extract_statistics(sd).numpy() for sd, _ in test_items])
    y_test = np.array([acc for _, acc in test_items])

    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    return r2_score(y_test, pred)

# Run at key N values
N_VALUES = [100, 500, 1000]
SEEDS = [0, 1]  # 2 seeds for speed

results = []
for n in N_VALUES:
    print(f"\n--- N={n} ---", flush=True)
    for seed in SEEDS:
        set_seed(seed)
        train_subset = random.sample(train_pool, min(n, len(train_pool)))

        # NFN
        nfn = train_nfn_fast(train_subset)
        nfn_r2 = eval_nfn(nfn, test_set)

        # Stats
        stats_r2 = train_eval_stats_sklearn(train_subset, test_set)

        print(f"  seed={seed}: NFN={nfn_r2:.4f}, Stats={stats_r2:.4f}", flush=True)
        results.append({"n": n, "seed": seed, "nfn_r2": nfn_r2, "stats_r2": stats_r2})

    nfn_mean = np.mean([r["nfn_r2"] for r in results if r["n"] == n])
    stats_mean = np.mean([r["stats_r2"] for r in results if r["n"] == n])
    print(f"  MEAN: NFN={nfn_mean:.4f}, Stats={stats_mean:.4f}, Delta={nfn_mean - stats_mean:+.4f}", flush=True)

# Analysis
print("\n" + "="*60, flush=True)
print("CROSSING POINT ANALYSIS", flush=True)
print("="*60, flush=True)

n_star = None
for n in N_VALUES:
    nfn_r2s = [r["nfn_r2"] for r in results if r["n"] == n]
    stats_r2s = [r["stats_r2"] for r in results if r["n"] == n]
    nfn_mean, stats_mean = np.mean(nfn_r2s), np.mean(stats_r2s)
    delta = abs(nfn_mean - stats_mean)

    crossing = delta < 0.03
    print(f"N={n}: NFN={nfn_mean:.4f}, Stats={stats_mean:.4f}, Delta={delta:.4f} {'** CROSSING **' if crossing else ''}", flush=True)
    if n_star is None and crossing:
        n_star = n

gate_pass = n_star is not None and n_star < 2500
print(f"\nN*: {n_star}", flush=True)
print(f"Gate: {'PASSED' if gate_pass else 'NOT_SATISFIED'}", flush=True)

output = {
    "hypothesis": "h-c2",
    "results": results,
    "n_star": n_star,
    "gate_result": "PASSED" if gate_pass else "NOT_SATISFIED",
}
Path("results").mkdir(exist_ok=True)
with open("results/results.json", "w") as f:
    json.dump(output, f, indent=2)
print("EXPERIMENT COMPLETE", flush=True)
