"""End-to-end experiment runner for H-E1."""
import os
import sys
import json
import numpy as np

from config import Config
from data import download_waterbirds, get_dataloaders, is_minority, WaterbirdsDataset
from model import build_resnet18, OnsetDelayTracker
from train import set_seed, train_erm
from evaluate import run_evaluation


def main():
    cfg = Config()

    os.makedirs(cfg.output_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)

    set_seed(cfg.seed)

    print("Downloading Waterbirds dataset...")
    download_waterbirds(cfg.data_root, cfg.data_url)

    print("Creating dataloaders...")
    loaders = get_dataloaders(
        cfg.data_root, cfg.batch_size, cfg.num_workers,
        cfg.img_size, cfg.norm_mean, cfg.norm_std
    )

    train_dataset = WaterbirdsDataset(
        cfg.data_root, "train",
        transform=None
    )
    n_train = len(train_dataset)
    minority_mask = is_minority(train_dataset.y, train_dataset.place)

    print(f"Training samples: {n_train}")
    print(f"Minority samples: {minority_mask.sum()} ({100*minority_mask.mean():.1f}%)")

    print("Building model...")
    model = build_resnet18(cfg.num_classes, cfg.pretrained)

    tracker = OnsetDelayTracker(n_train, cfg.n_epochs, cfg.onset_threshold)

    print(f"Training for {cfg.n_epochs} epochs...")
    tracker = train_erm(
        model, loaders, tracker,
        cfg.n_epochs, cfg.lr, cfg.momentum, cfg.weight_decay, cfg.device
    )

    print("Running evaluation...")
    results = run_evaluation(tracker, minority_mask, cfg.figures_dir, cfg.t_early)

    gate_pass = bool(
        results["precision"] > 0.5 and
        results["recall"] > 0.3 and
        results["mann_whitney_pvalue"] < 0.05
    )
    results["gate_pass"] = gate_pass
    results["gate_type"] = "MUST_WORK"

    with open(cfg.metrics_path, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*50)
    print("RESULTS:")
    print(f"  Precision@T_early={cfg.t_early}: {results['precision']:.4f} (threshold: >0.5)")
    print(f"  Recall@T_early={cfg.t_early}: {results['recall']:.4f} (threshold: >0.3)")
    print(f"  Mann-Whitney p-value: {results['mann_whitney_pvalue']:.4e} (threshold: <0.05)")
    print(f"\n  GATE VERDICT: {'PASS' if gate_pass else 'FAIL'}")
    print("="*50)

    return 0 if gate_pass else 1


if __name__ == "__main__":
    sys.exit(main())
