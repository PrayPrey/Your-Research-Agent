"""H-M2 Main experiment runner."""
import os
import sys
import torch
import random
import numpy as np

# Local imports first
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from config import Config
from train_full import train_with_full_checkpoints
from probe_analysis import run_all_epochs
from evaluate import run_evaluation

# Add h-e1 code to path for data/model
sys.path.insert(0, os.path.join(script_dir, '..', '..', 'h-e1', 'code'))

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def main():
    cfg = Config()
    set_seed(cfg.seed)

    # Import h-e1 modules
    from data import get_dataloaders
    from model import build_resnet18

    print("=" * 60)
    print("H-M2: Spurious features are easier to learn than core features")
    print("=" * 60)

    # Check if training needed
    ckpt_paths = {}
    if os.path.exists(cfg.ckpt_dir):
        existing = [f for f in os.listdir(cfg.ckpt_dir) if f.endswith('.pt')]
        if len(existing) == cfg.n_epochs:
            print(f"Found {len(existing)} checkpoints, skipping training")
            for i in range(1, cfg.n_epochs + 1):
                ckpt_paths[i] = os.path.join(cfg.ckpt_dir, f"epoch_{i:03d}.pt")

    if not ckpt_paths:
        print(f"\n1. Training ResNet-18 for {cfg.n_epochs} epochs with full checkpointing...")
        loaders = get_dataloaders(cfg.data_root, cfg.batch_size, cfg.num_workers, cfg.img_size, cfg.norm_mean, cfg.norm_std)
        model = build_resnet18(cfg.num_classes, cfg.pretrained)
        ckpt_paths = train_with_full_checkpoints(model, loaders, cfg.n_epochs, cfg.lr, cfg.momentum, cfg.weight_decay, cfg.device, cfg.ckpt_dir)

    # Load data for probing
    from data import get_dataloaders
    loaders = get_dataloaders(cfg.data_root, cfg.batch_size, cfg.num_workers, cfg.img_size, cfg.norm_mean, cfg.norm_std)

    print(f"\n2. Running epoch-wise probe analysis...")
    results = run_all_epochs(ckpt_paths, loaders, cfg.device, cfg.cache_dir, cfg.probe_C, cfg.probe_max_iter)

    print(f"\n3. Evaluating mechanism...")
    metrics = run_evaluation(results, cfg.figures_dir, cfg.metrics_path, cfg.peak_window, cfg.auc_range)

    print("\n" + "=" * 60)
    print("RESULTS:")
    print(f"  Spurious peak epoch: {metrics['verification']['spurious_peak']}")
    print(f"  Core peak epoch:     {metrics['verification']['core_peak']}")
    print(f"  Peak difference:     {metrics['verification']['peak_diff']} epochs")
    print(f"  Wilcoxon p-value:    {metrics['wilcoxon_test']['p_value']:.2e}")
    print(f"  GATE PASSED:         {metrics['verification']['passed']}")
    print("=" * 60)

    return metrics

if __name__ == "__main__":
    main()
