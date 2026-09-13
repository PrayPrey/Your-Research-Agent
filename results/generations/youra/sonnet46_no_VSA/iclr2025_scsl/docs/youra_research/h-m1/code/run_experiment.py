"""
H-M1 Experiment: Differential Confidence Trajectory Verification
Reuses H-E3 checkpoints. No new training.
"""

import os
import sys
import argparse
import torch

# Ensure we can import config from same dir
sys.path.insert(0, os.path.dirname(__file__))
import config

# Inject H-E3 code path
sys.path.insert(0, config.H_E3_CODE)

from compute_confidence import (
    extract_confidence_by_group,
    compute_trajectory,
    verify_mechanism_activated,
    save_results,
    load_checkpoint,
)
from visualize import save_all_figures


def main() -> None:
    config.ensure_dirs()

    from data import get_eval_loader
    loader = get_eval_loader(config.DATA_ROOT, split=0, batch_size=config.BATCH_SIZE)
    dataset = loader.dataset

    # H-M1 minority: G1 (landbird/water) + G2 (waterbird/land)
    # Do NOT use dataset.minority_mask — that is built from H-E3's MINORITY_GROUPS=(1,3)
    minority_mask = (dataset.group == 1) | (dataset.group == 2)
    assert minority_mask.sum() == 240, f"Expected 240 minority, got {minority_mask.sum()}"
    print(f"Dataset: {len(dataset)} samples, minority={minority_mask.sum().item()}")

    device = config.DEVICE
    print(f"Device: {device}")

    results_per_seed = {}
    for seed in config.SEEDS:
        print(f"\n--- Seed {seed} ---")
        torch.manual_seed(seed)
        traj = compute_trajectory(seed, loader, minority_mask, device)
        traj["tstar"] = config.TSTAR_PER_SEED[seed]
        traj["minority_mask"] = minority_mask  # store for viz (not serialized to JSON)
        results_per_seed[seed] = traj

        tstar = config.TSTAR_PER_SEED[seed]
        p_min = traj[tstar]["p_min"]
        p_maj = traj[tstar]["p_maj"]
        print(
            f"  t*={tstar}  p_min={p_min:.4f}  p_maj={p_maj:.4f}  gap={p_maj-p_min:.4f}"
        )

    mechanism_active, indicators = verify_mechanism_activated(results_per_seed)
    n_pass = sum(v["both_pass"] for v in indicators.values())

    print(f"\n=== GATE RESULT ===")
    print(f"Gate pass count: {n_pass}/5")
    print(f"Mechanism active: {mechanism_active}")
    for seed, ind in indicators.items():
        print(
            f"  Seed {seed}: boundary={ind['minority_boundary']}  saturated={ind['majority_saturated']}  gap={ind['gap']:.4f}  both_pass={ind['both_pass']}"
        )

    save_results(results_per_seed, mechanism_active, n_pass)
    save_all_figures(results_per_seed)

    print("\n=== H-M1 COMPLETE ===")
    print(f"Gate: {'PASS' if mechanism_active else 'FAIL'} ({n_pass}/5 seeds)")


def smoke_test(seed: int = 1, epoch: int = 1) -> None:
    """Single checkpoint pipeline check. Runs in <60s."""
    from data import get_eval_loader
    loader = get_eval_loader(config.DATA_ROOT, split=0, batch_size=256)
    dataset = loader.dataset
    minority_mask = (dataset.group == 1) | (dataset.group == 2)
    model = load_checkpoint(seed, epoch, config.DEVICE)
    p_per_sample, p_min, p_maj = extract_confidence_by_group(
        model, loader, minority_mask, config.DEVICE
    )
    assert p_per_sample.shape == (4795,), f"shape={p_per_sample.shape}"
    assert 0.0 < p_min < 1.0, f"p_min out of range: {p_min}"
    assert 0.0 < p_maj < 1.0, f"p_maj out of range: {p_maj}"
    print(f"SMOKE OK: p_min={p_min:.4f} p_maj={p_maj:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        smoke_test()
    else:
        main()
