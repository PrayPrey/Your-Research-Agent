"""Load H-E1 results or run training fallback for missing cells."""
import os
import sys
import json
import copy
import numpy as np
from typing import Optional

import config as cfg


def load_h_e1_results(path: str) -> Optional[dict]:
    """
    Load H-E1 results.json and convert to {encoder: {zoo: {size: {mean_r2, ci_lo, ci_hi, seed_r2s}}}}.
    H-E1 key format: {zoo}_{encoder}_{tier}_{size} → {r2, ci_low, ci_high}
    Returns None if file missing. Returns partial dict with whatever is present.
    """
    if not os.path.exists(path):
        return None

    with open(path) as f:
        raw = json.load(f)

    results = {}
    tier = "medium"
    zoos = ["cifar10"]
    encoders = ["flat_mlp", "flat_mlp_perm_aug", "gnn_nfn"]
    sizes = [100, 250, 500, 1000, "full"]

    for enc in encoders:
        for zoo in zoos:
            for size in sizes:
                # H-E1 key: {zoo}_{encoder}_{tier}_{size}
                enc_key = enc.replace("_perm_aug", "_perm_aug")  # keep as-is
                k = f"{zoo}_{enc}_{tier}_{size}"
                if k not in raw:
                    continue
                cell = raw[k]
                mean_r2 = cell.get("r2", cell.get("mean_r2", None))
                ci_lo = cell.get("ci_low", cell.get("ci_lo", mean_r2))
                ci_hi = cell.get("ci_high", cell.get("ci_hi", mean_r2))
                if mean_r2 is None:
                    continue
                results.setdefault(enc, {}).setdefault(zoo, {})[str(size)] = {
                    "mean_r2": float(mean_r2),
                    "ci_lo": float(ci_lo),
                    "ci_hi": float(ci_hi),
                    "seed_r2s": [float(mean_r2)],  # H-E1 stored aggregated, not per-seed
                }

    return results if results else None


def check_and_merge(h_e1_results, required_encoders, required_zoos, required_sizes):
    """Return (partial_results, missing_cells) where missing_cells=(enc,zoo,size) tuples."""
    partial = h_e1_results or {}
    missing = []
    for enc in required_encoders:
        for zoo in required_zoos:
            for n in required_sizes:
                if enc in partial and zoo in partial[enc] and str(n) in partial[enc][zoo]:
                    continue
                missing.append((enc, zoo, n))
    return partial, missing


def _setup_h_e1_imports():
    """Insert H-E1 and H-M1 code paths into sys.path."""
    for p in [cfg.H_E1_CODE_DIR, cfg.H_M1_CODE_DIR, cfg.MZDATASET_CODE_PATH]:
        if p not in sys.path:
            sys.path.insert(0, p)


def _monkey_patch_h_e1_config():
    """Override H-E1 config ZOO_PATHS and MZDATASET_CODE_PATH to local values."""
    _setup_h_e1_imports()
    import config as h_e1_cfg
    h_e1_cfg.ZOO_PATHS = cfg.ZOO_PATHS
    h_e1_cfg.MZDATASET_CODE_PATH = cfg.MZDATASET_CODE_PATH


def run_training_cell(enc_name, zoo_name, n_train, seed, device):
    """Train one (encoder, zoo, n_train, seed) cell. Returns R² on fixed test set."""
    _monkey_patch_h_e1_config()

    from data import load_zoo, subsample, FlatCollator
    from train import train_one, get_predictions
    from encoders import build_encoder
    import torch
    from torch.utils.data import DataLoader
    from sklearn.metrics import r2_score

    # Try GNNCollator
    try:
        from data import GNNCollator
        gnn_collator = GNNCollator()
    except ImportError:
        gnn_collator = None

    train_ds, val_ds, test_ds = load_zoo(zoo_name)
    sub_train = subsample(train_ds, n_train, seed)

    n_int = len(sub_train) if n_train == "full" else n_train
    batch_size = cfg.BATCH_SIZE_SMALL if n_int <= cfg.SMALL_SIZE_THRESHOLD else cfg.BATCH_SIZE

    flat_encoders = {"flat_mlp", "flat_mlp_perm_aug"}
    if enc_name in flat_encoders:
        collator = FlatCollator()
    else:
        collator = gnn_collator

    train_loader = DataLoader(sub_train, batch_size=batch_size, shuffle=True,
                              collate_fn=collator, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=64, shuffle=False,
                            collate_fn=collator, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=64, shuffle=False,
                             collate_fn=collator, num_workers=0)

    # Get input_dim from first batch
    first_batch = next(iter(train_loader))
    if enc_name in flat_encoders:
        input_dim = first_batch[0].shape[1]
    else:
        input_dim = 0  # not used for GNN

    encoder = build_encoder(enc_name, input_dim=input_dim,
                            target_params=cfg.PRIMARY_BUDGET,
                            zoo_arch=cfg.ZOO_ARCH,
                            sample_wsfeat=first_batch[0] if enc_name not in flat_encoders else None)

    torch.manual_seed(seed)
    train_one(encoder, train_loader, val_loader, enc_name,
              epochs=cfg.EPOCHS, lr=cfg.LR, weight_decay=cfg.WEIGHT_DECAY,
              seed=seed, device=device)

    preds, targets = get_predictions(encoder, test_loader, enc_name, device)
    return float(r2_score(targets, preds))


def bootstrap_ci(seed_r2s, n_boot=1000, ci=0.95):
    """Percentile bootstrap CI. Returns (mean, lo, hi)."""
    if len(seed_r2s) < 2:
        m = seed_r2s[0] if seed_r2s else 0.0
        return m, m, m
    arr = np.array(seed_r2s)
    mean = float(np.mean(arr))
    boot = [np.mean(np.random.choice(arr, len(arr), replace=True)) for _ in range(n_boot)]
    alpha = (1 - ci) / 2
    lo = float(np.percentile(boot, alpha * 100))
    hi = float(np.percentile(boot, (1 - alpha) * 100))
    return mean, lo, hi


_SKIP_FULL_TRAINING = True  # ponytail: skip "full" training for PoC; gnn_nfn/full takes >10min on 42K models


def run_training_fallback(missing_cells, device, existing_results=None):
    """Train all missing (enc, zoo, size) cells, 5 seeds each. Returns merged results dict."""
    results = copy.deepcopy(existing_results) if existing_results else {}

    for (enc, zoo, n) in missing_cells:
        if _SKIP_FULL_TRAINING and n == "full":
            print(f"  Skipping {enc}/{zoo}/full (PoC mode — 42K models × 100 epochs too slow; 4-point curve sufficient)")
            continue
        print(f"  Training: {enc} / {zoo} / {n} ...")
        seed_r2s = []
        for seed in cfg.SEEDS:
            try:
                r2 = run_training_cell(enc, zoo, n, seed, device)
                print(f"    seed={seed}: R²={r2:.4f}")
                seed_r2s.append(r2)
            except Exception as e:
                print(f"    seed={seed}: ERROR {e}")
                seed_r2s.append(float('nan'))

        # Filter NaN
        valid = [r for r in seed_r2s if not np.isnan(r)]
        if not valid:
            print(f"    WARNING: all seeds failed for {enc}/{zoo}/{n}")
            continue
        mean_r2, ci_lo, ci_hi = bootstrap_ci(valid)
        results.setdefault(enc, {}).setdefault(zoo, {})[str(n)] = {
            "mean_r2": mean_r2,
            "ci_lo": ci_lo,
            "ci_hi": ci_hi,
            "seed_r2s": valid,
        }
        print(f"    → mean_r2={mean_r2:.4f}, CI=[{ci_lo:.4f}, {ci_hi:.4f}]")

    return results


def get_results(device="cuda"):
    """Primary entry point. Load H-E1 results, train missing cells, return merged dict."""
    h_e1_results = load_h_e1_results(cfg.H_E1_RESULTS_JSON)
    if h_e1_results:
        print(f"✓ Loaded H-E1 results from {cfg.H_E1_RESULTS_JSON}")
    else:
        print(f"⚠ H-E1 results not found at {cfg.H_E1_RESULTS_JSON}")

    partial, missing = check_and_merge(
        h_e1_results,
        cfg.ENCODER_NAMES,
        cfg.ZOO_NAMES,
        cfg.TRAINING_SIZES,
    )

    if missing:
        print(f"  Missing {len(missing)} cells — running training fallback...")
        results = run_training_fallback(missing, device, existing_results=partial)
    else:
        print("  All cells present — skipping training.")
        results = partial

    return results
