"""End-to-end experiment runner for H-M1."""
import sys
import os

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

from config import Config
from train_checkpointed import train_with_checkpoints
from probe_train import run_probes_for_checkpoint
import evaluate as m1_evaluate

H_E1_CODE = os.path.join(CODE_DIR, "..", "..", "h-e1", "code")
sys.path.insert(0, H_E1_CODE)

import torch
from train import set_seed
from data import get_dataloaders
from model import build_resnet18


def main():
    cfg = Config()
    os.chdir(CODE_DIR)
    os.makedirs(cfg.ckpt_dir, exist_ok=True)
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

    print("Building model...")
    model = build_resnet18(num_classes=cfg.num_classes, pretrained=cfg.pretrained)

    print("Training with checkpoints...")
    ckpt_paths = train_with_checkpoints(
        model=model,
        loaders=loaders,
        n_epochs=cfg.n_epochs,
        checkpoint_epochs=list(cfg.checkpoint_epochs),
        lr=cfg.lr,
        momentum=cfg.momentum,
        weight_decay=cfg.weight_decay,
        device=device,
        ckpt_dir=cfg.ckpt_dir,
    )

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
