"""Run evaluation on existing checkpoints."""
import sys
import os

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

from config import Config
from probe_train import run_probes_for_checkpoint
H_E1_CODE = os.path.join(CODE_DIR, "..", "..", "h-e1", "code")
sys.path.insert(0, H_E1_CODE)

import importlib.util
spec = importlib.util.spec_from_file_location("m1_evaluate", os.path.join(CODE_DIR, "evaluate.py"))
m1_evaluate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m1_evaluate)

import torch
from train import set_seed
from data import get_dataloaders


def main():
    cfg = Config()
    os.chdir(CODE_DIR)
    os.makedirs(cfg.output_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)

    set_seed(cfg.seed)
    device = cfg.device if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    print("Loading data...")
    loaders = get_dataloaders(
        root_dir=cfg.data_root,
        batch_size=cfg.batch_size,
        num_workers=cfg.num_workers,
        img_size=cfg.img_size,
        norm_mean=cfg.norm_mean,
        norm_std=cfg.norm_std,
    )

    ckpt_paths = {5: "./checkpoints/epoch_5.pt", 20: "./checkpoints/epoch_20.pt", 50: "./checkpoints/epoch_50.pt"}

    print("\nRunning linear probes on checkpoints...")
    results = {}
    for epoch, path in sorted(ckpt_paths.items()):
        print(f"\nEpoch {epoch} checkpoint: {path}")
        probe_results = run_probes_for_checkpoint(
            ckpt_path=path,
            loaders=loaders,
            feature_dim=cfg.feature_dim,
            probe_epochs=cfg.probe_epochs,
            lr=cfg.probe_lr,
            device=device,
        )
        results[f"epoch_{epoch}"] = probe_results
        print(f"  Spurious acc: {probe_results['spurious_acc']:.4f}")
        print(f"  Core acc: {probe_results['core_acc']:.4f}")

    print("\nRunning evaluation...")
    verification = m1_evaluate.run_evaluation(results, cfg.figures_dir, cfg.metrics_path)

    print("\n" + "="*50)
    print("MECHANISM VERIFICATION RESULTS")
    print("="*50)
    print(f"Bias exists (spurious_acc(5) > core_acc(5)): {verification['bias_exists']}")
    print(f"Core improves (core_acc(50) > core_acc(5)): {verification['core_improves']}")
    print("="*50)

    if verification['bias_exists']:
        print("\n✓ GATE PASSED: Simplicity bias mechanism confirmed")
    else:
        print("\n✗ GATE FAILED: Simplicity bias not observed")

    return verification


if __name__ == "__main__":
    main()
