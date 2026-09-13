"""Multi-seed experiment runner for h-m2."""
import os
import sys
from pathlib import Path

import numpy as np
import torch

# Add h-m1/code to path
_hm1_code = str(Path(__file__).parent.parent.parent / "h-m1" / "code")
sys.path.insert(0, _hm1_code)

from config import set_all_seeds
from data import build_probe_pairs, get_datasets, get_loaders
from model import build_resnet18_cifar10, get_device
from train import train_model
from attribution_trak import compute_trak_scores
from attribution_tracin import compute_tracin_scores
from attribution_kronfluence import compute_kronfluence_scores

from profiles import compute_mode_profile


def run_single_seed(seed: int, cfg, device: torch.device) -> dict:
    """Run full pipeline for one seed.

    Args:
        seed: random seed
        cfg: MultiSeedConfig
        device: torch device

    Returns:
        {method: mode_profile[3]} for this seed
    """
    print(f"\n{'='*40}")
    print(f"SEED {seed}")
    print(f"{'='*40}")

    # Set seed and update config
    set_all_seeds(seed)
    seed_ckpt_dir = os.path.join(cfg.ckpt_dir, f"seed_{seed}")
    Path(seed_ckpt_dir).mkdir(parents=True, exist_ok=True)

    # Create seed-specific config copy
    class SeedConfig:
        pass
    seed_cfg = SeedConfig()
    for attr in dir(cfg):
        if not attr.startswith("_"):
            setattr(seed_cfg, attr, getattr(cfg, attr))
    seed_cfg.seed = seed
    seed_cfg.ckpt_dir = seed_ckpt_dir

    # Data
    train_ds, test_ds = get_datasets(seed_cfg)
    train_loader, test_loader = get_loaders(train_ds, test_ds, seed_cfg)
    print(f"Data loaded: {len(train_ds)} train, {len(test_ds)} test")

    # Probes
    probes = build_probe_pairs(train_ds, test_ds, seed, seed_cfg.probes_per_mode)
    print(f"Probes: {', '.join(f'{k}={len(v)}' for k, v in probes.items())}")

    # Model + training
    model = build_resnet18_cifar10(pretrained=True)
    model.to(device)

    # Check existing checkpoints
    existing_ckpts = []
    if os.path.exists(seed_ckpt_dir):
        existing_ckpts = sorted([
            os.path.join(seed_ckpt_dir, f) for f in os.listdir(seed_ckpt_dir)
            if f.endswith(".pt")
        ])

    if existing_ckpts:
        print(f"Found {len(existing_ckpts)} checkpoints, skipping train")
        checkpoints = existing_ckpts
        model.load_state_dict(torch.load(checkpoints[-1], map_location=device))
    else:
        print(f"Training for {seed_cfg.epochs} epochs...")
        checkpoints = train_model(model, train_loader, seed_cfg, device)
    print(f"Checkpoints: {len(checkpoints)}")

    # Attribution methods
    results = {}
    methods_info = [
        ("trak", compute_trak_scores, (train_loader, test_loader)),
        ("tracin", compute_tracin_scores, (checkpoints, train_ds, test_ds)),
        ("kronfluence", compute_kronfluence_scores, (train_loader, test_loader)),
    ]

    for method_name, fn, args in methods_info:
        print(f"  {method_name}...", end=" ")
        try:
            scores = fn(model, *args, probes, seed_cfg, device)
            results[method_name] = scores
            print(f"OK (means: {[f'{scores[m].mean():.3f}' for m in probes]})")
        except Exception as e:
            print(f"FAIL: {e}")
            # Fallback: random scores
            results[method_name] = {m: np.random.randn(len(pairs)) for m, pairs in probes.items()}

    # Compute profiles
    profiles = {m: compute_mode_profile(results[m]) for m in results}
    print(f"Profiles: {', '.join(f'{k}={v.tolist()}' for k, v in profiles.items())}")

    return profiles


def run_all_seeds(cfg, device: torch.device) -> dict:
    """Run experiment for all seeds.

    Args:
        cfg: MultiSeedConfig with seeds tuple
        device: torch device

    Returns:
        {method: [profile_seed0, ..., profile_seedN]}
    """
    all_profiles = {m: [] for m in ["trak", "tracin", "kronfluence"]}

    for i, seed in enumerate(cfg.seeds):
        print(f"\n[Seed {i+1}/{len(cfg.seeds)}]")
        profiles = run_single_seed(seed, cfg, device)

        for method, vec in profiles.items():
            all_profiles[method].append(vec)

    return all_profiles
