#!/usr/bin/env python3
"""Quick H-C2 experiment with reduced zoo size for faster validation."""
import json
import sys
import time
from pathlib import Path
import torch
import torch.nn as nn
import numpy as np
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler

print("Starting quick H-C2 experiment...", flush=True)

# Use subset of zoo
N_VALUES = [100, 500, 1000, 2500]  # key checkpoints
SEEDS = [0, 1, 2]  # 3 seeds
SUBSET_SIZE = 3500  # need 500 test + enough train for N=2500

# Import local modules
sys.path.insert(0, str(Path(__file__).parent))
from data import ResNet20
from nfn_model import NFNAccuracyPredictor, extract_weight_tensors, collate_weights
from statistics_model import StatisticsPredictor, extract_statistics

def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    import random
    random.seed(seed)

def load_zoo_subset(path, n=SUBSET_SIZE):
    """Load only first n models."""
    print(f"Loading {n} models from zoo...", flush=True)
    t0 = time.time()
    items = torch.load(path, map_location='cpu')[:n]
    print(f"Loaded {len(items)} in {time.time()-t0:.1f}s", flush=True)
    return items

def train_model(model, train_data, collate_fn, epochs=15, lr=1e-3, bs=64):
    """Simple training loop."""
    device = 'cpu'
    model = model.to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    loss_fn = nn.MSELoss()

    for _ in range(epochs):
        indices = torch.randperm(len(train_data)).tolist()
        for start in range(0, len(indices), bs):
            batch = [train_data[i] for i in indices[start:start+bs]]
            x, y = collate_fn(batch)
            if isinstance(x, list):
                x = [t.to(device) for t in x]
            else:
                x = x.to(device)
            y = y.to(device)

            opt.zero_grad()
            pred = model(x)
            loss = loss_fn(pred, y)
            loss.backward()
            opt.step()
    return model

def evaluate(model, test_data, collate_fn):
    """Evaluate and return R²."""
    device = 'cpu'
    model = model.to(device).eval()
    preds, trues = [], []

    with torch.no_grad():
        for start in range(0, len(test_data), 32):
            batch = test_data[start:start+32]
            x, y = collate_fn(batch)
            if isinstance(x, list):
                x = [t.to(device) for t in x]
            else:
                x = x.to(device)
            pred = model(x)
            preds.extend(pred.cpu().numpy())
            trues.extend(y.numpy())

    return r2_score(trues, preds)

def collate_statistics(items):
    """Collate for statistics model."""
    feats = torch.stack([extract_statistics(sd) for sd, _ in items])
    accs = torch.tensor([acc for _, acc in items], dtype=torch.float32)
    return feats, accs

def main():
    t_start = time.time()

    # Load subset
    zoo_path = "data/model_zoo/synthetic_zoo_6000.pt"
    items = load_zoo_subset(zoo_path, SUBSET_SIZE)

    # Split: test=200, train pool=rest
    import random
    rng = random.Random(42)
    shuffled = list(items)
    rng.shuffle(shuffled)
    test_set = shuffled[:200]
    train_pool = shuffled[200:]
    print(f"Train pool: {len(train_pool)}, Test: {len(test_set)}", flush=True)

    results = []

    for n in N_VALUES:
        print(f"\n=== N={n} ===", flush=True)
        nfn_r2s, stats_r2s = [], []

        for seed in SEEDS:
            set_seed(seed)
            rng = random.Random(seed)
            train_subset = rng.sample(train_pool, min(n, len(train_pool)))

            # NFN
            nfn = NFNAccuracyPredictor(hidden_dim=64)  # smaller for speed
            train_model(nfn, train_subset, collate_weights, epochs=10)
            nfn_r2 = evaluate(nfn, test_set, collate_weights)
            nfn_r2s.append(nfn_r2)

            # Statistics
            X_train, y_train = collate_statistics(train_subset)
            scaler = StandardScaler().fit(X_train.numpy())
            X_train_s = torch.tensor(scaler.transform(X_train.numpy()), dtype=torch.float32)

            stats_model = StatisticsPredictor(in_dim=X_train_s.shape[1])
            train_data_stats = list(zip(X_train_s, y_train))
            collate_stats = lambda b: (torch.stack([x for x,_ in b]), torch.stack([y for _,y in b]))
            train_model(stats_model, train_data_stats, collate_stats, epochs=30)

            X_test, y_test = collate_statistics(test_set)
            X_test_s = torch.tensor(scaler.transform(X_test.numpy()), dtype=torch.float32)

            stats_model.eval()
            with torch.no_grad():
                pred = stats_model(X_test_s).numpy()
            stats_r2 = r2_score(y_test.numpy(), pred)
            stats_r2s.append(stats_r2)

            print(f"  seed={seed}: NFN R²={nfn_r2:.4f}, Stats R²={stats_r2:.4f}", flush=True)
            results.append({"n": n, "seed": seed, "nfn_r2": nfn_r2, "stats_r2": stats_r2})

        nfn_mean = np.mean(nfn_r2s)
        stats_mean = np.mean(stats_r2s)
        delta = abs(nfn_mean - stats_mean)
        print(f"  Mean: NFN={nfn_mean:.4f}, Stats={stats_mean:.4f}, Delta={delta:.4f}", flush=True)

    # Find crossing point
    print("\n" + "="*60, flush=True)
    print("H-C2 CROSSING POINT ANALYSIS", flush=True)
    print("="*60, flush=True)

    n_star = None
    for n in N_VALUES:
        nfn_r2s = [r["nfn_r2"] for r in results if r["n"] == n]
        stats_r2s = [r["stats_r2"] for r in results if r["n"] == n]
        nfn_mean = np.mean(nfn_r2s)
        stats_mean = np.mean(stats_r2s)
        delta = abs(nfn_mean - stats_mean)

        # Check CI overlap
        nfn_sem = np.std(nfn_r2s, ddof=1) / np.sqrt(len(nfn_r2s))
        stats_sem = np.std(stats_r2s, ddof=1) / np.sqrt(len(stats_r2s))
        nfn_lo, nfn_hi = nfn_mean - 1.96*nfn_sem, nfn_mean + 1.96*nfn_sem
        stats_lo, stats_hi = stats_mean - 1.96*stats_sem, stats_mean + 1.96*stats_sem
        ci_overlap = nfn_lo <= stats_hi and stats_lo <= nfn_hi

        status = "CROSSING" if (delta < 0.03 and ci_overlap) else ""
        print(f"N={n:4d}: NFN={nfn_mean:.4f}±{nfn_sem:.4f}, Stats={stats_mean:.4f}±{stats_sem:.4f}, Delta={delta:.4f} {status}", flush=True)

        if n_star is None and delta < 0.03 and ci_overlap:
            n_star = n

    gate_pass = n_star is not None and n_star < 2500

    print(f"\nCrossing point N*: {n_star}", flush=True)
    print(f"Gate SHOULD_WORK: {'PASSED' if gate_pass else 'NOT_SATISFIED'}", flush=True)
    print(f"Total time: {time.time()-t_start:.1f}s", flush=True)

    # Save results
    output = {
        "results": results,
        "n_star": n_star,
        "gate_result": "PASSED" if gate_pass else "NOT_SATISFIED",
        "elapsed_sec": time.time() - t_start,
    }
    Path("results").mkdir(exist_ok=True)
    with open("results/quick_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\nEXPERIMENT COMPLETE", flush=True)
    return output

if __name__ == "__main__":
    main()
