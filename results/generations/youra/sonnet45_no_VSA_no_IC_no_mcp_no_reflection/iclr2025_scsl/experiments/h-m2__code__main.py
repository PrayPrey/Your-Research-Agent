"""
Main entry point for h-m2 PoC validation: Architecture comparison.
"""

import os
import json
import torch
from data import get_cmnist_dataloader
from train import run_architecture_experiment, ArchitectureConfig
from config import (
    RESNET_CONFIG, VIT_CONFIG, EXPERIMENT_CONFIG, REPRODUCIBILITY_CONFIG, OUTPUT_CONFIG
)


def run_poc():
    """
    Run PoC: 1 architecture (ResNet-50), 1 seed, verify Δ > 0.
    """
    # Set reproducibility
    if REPRODUCIBILITY_CONFIG['torch_deterministic']:
        torch.use_deterministic_algorithms(True, warn_only=True)
    if REPRODUCIBILITY_CONFIG['cudnn_deterministic']:
        torch.backends.cudnn.deterministic = True
    if not REPRODUCIBILITY_CONFIG['cudnn_benchmark']:
        torch.backends.cudnn.benchmark = False

    device = EXPERIMENT_CONFIG['device']
    print(f"Device: {device}")

    # Load CMNIST (fallback: Waterbirds download failed)
    print("Loading CMNIST dataset...")
    train_loader = get_cmnist_dataloader(
        batch_size=RESNET_CONFIG['batch_size'],
        split='train',
        num_workers=4,
        subset_fraction=0.1  # Use 10% for faster PoC
    )
    print(f"Train set: {len(train_loader.dataset)} samples")

    # Create output dirs
    os.makedirs(OUTPUT_CONFIG['results_dir'], exist_ok=True)
    os.makedirs(OUTPUT_CONFIG['figures_dir'], exist_ok=True)

    # Run ResNet-50 PoC
    config_resnet = ArchitectureConfig(
        arch_name='resnet50',
        lr=RESNET_CONFIG['lr'],
        weight_decay=RESNET_CONFIG['weight_decay'],
        batch_size=RESNET_CONFIG['batch_size'],
        max_epochs=EXPERIMENT_CONFIG['epochs'],
        seed=EXPERIMENT_CONFIG['seed_start']
    )

    result_resnet = run_architecture_experiment(config_resnet, train_loader, device)

    # PoC success check
    if result_resnet['delta'] is not None and result_resnet['delta'] > 0:
        print("\n✓ PoC PASS: ResNet-50 Δ > 0")
        poc_status = 'PASS'
    else:
        print("\n✗ PoC FAIL: ResNet-50 Δ ≤ 0 or convergence failed")
        poc_status = 'FAIL'

    # Save PoC results
    poc_results = {
        'poc_status': poc_status,
        'resnet50': result_resnet
    }

    with open(os.path.join(OUTPUT_CONFIG['results_dir'], 'poc_results.json'), 'w') as f:
        json.dump(poc_results, f, indent=2)

    print(f"\nPoC results saved to {OUTPUT_CONFIG['results_dir']}/poc_results.json")
    return poc_results


def run_full_experiment():
    """
    Run full experiment: ResNet-50 vs ViT-B/16, 1 seed each (PoC mode).
    """
    # Set reproducibility
    if REPRODUCIBILITY_CONFIG['torch_deterministic']:
        torch.use_deterministic_algorithms(True, warn_only=True)
    if REPRODUCIBILITY_CONFIG['cudnn_deterministic']:
        torch.backends.cudnn.deterministic = True
    if not REPRODUCIBILITY_CONFIG['cudnn_benchmark']:
        torch.backends.cudnn.benchmark = False

    device = EXPERIMENT_CONFIG['device']
    print(f"Device: {device}")

    # Create output dirs
    os.makedirs(OUTPUT_CONFIG['results_dir'], exist_ok=True)
    os.makedirs(OUTPUT_CONFIG['figures_dir'], exist_ok=True)

    # Run ResNet-50
    print("\n" + "="*60)
    print("RESNET-50 EXPERIMENT")
    print("="*60)
    train_loader_resnet = get_cmnist_dataloader(
        batch_size=RESNET_CONFIG['batch_size'],
        split='train',
        num_workers=4,
        subset_fraction=0.1
    )
    config_resnet = ArchitectureConfig(
        arch_name='resnet50',
        lr=RESNET_CONFIG['lr'],
        weight_decay=RESNET_CONFIG['weight_decay'],
        batch_size=RESNET_CONFIG['batch_size'],
        max_epochs=EXPERIMENT_CONFIG['epochs'],
        seed=EXPERIMENT_CONFIG['seed_start']
    )
    result_resnet = run_architecture_experiment(config_resnet, train_loader_resnet, device)

    # Run ViT-B/16
    print("\n" + "="*60)
    print("VIT-B/16 EXPERIMENT")
    print("="*60)
    train_loader_vit = get_cmnist_dataloader(
        batch_size=VIT_CONFIG['batch_size'],
        split='train',
        num_workers=4,
        subset_fraction=0.1
    )
    config_vit = ArchitectureConfig(
        arch_name='vit_b16',
        lr=VIT_CONFIG['lr'],
        weight_decay=VIT_CONFIG['weight_decay'],
        batch_size=VIT_CONFIG['batch_size'],
        max_epochs=EXPERIMENT_CONFIG['epochs'],
        seed=EXPERIMENT_CONFIG['seed_start']
    )
    result_vit = run_architecture_experiment(config_vit, train_loader_vit, device)

    # Compute comparison
    delta_resnet = result_resnet['delta']
    delta_vit = result_vit['delta']

    if delta_resnet is not None and delta_vit is not None:
        diff = delta_resnet - delta_vit
        print(f"\n=== COMPARISON ===")
        print(f"Δ_ResNet = {delta_resnet:.2f} epochs")
        print(f"Δ_ViT    = {delta_vit:.2f} epochs")
        print(f"Δ_ResNet - Δ_ViT = {diff:.2f} epochs")

        if diff >= 2:
            print("✓ Gate threshold met (Δ_diff ≥ 2 epochs)")
            gate_status = 'PASS'
        else:
            print("✗ Gate threshold NOT met (Δ_diff < 2 epochs)")
            gate_status = 'FAIL'
    else:
        print("\n✗ Convergence failed for at least one architecture")
        gate_status = 'FAIL'

    # Save full results
    full_results = {
        'gate_status': gate_status,
        'resnet50': result_resnet,
        'vit_b16': result_vit,
        'comparison': {
            'delta_resnet': delta_resnet,
            'delta_vit': delta_vit,
            'diff': diff if delta_resnet and delta_vit else None
        }
    }

    with open(os.path.join(OUTPUT_CONFIG['results_dir'], 'full_results.json'), 'w') as f:
        json.dump(full_results, f, indent=2)

    print(f"\nFull results saved to {OUTPUT_CONFIG['results_dir']}/full_results.json")
    return full_results


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'full':
        run_full_experiment()
    else:
        run_poc()
