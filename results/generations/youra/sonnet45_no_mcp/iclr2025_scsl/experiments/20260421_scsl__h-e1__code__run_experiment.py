"""
Main Experiment Script for H-E1: Curvature Subspace Alignment

This script:
1. Trains ERM and Group-DRO models on Waterbirds
2. Computes Hessian eigenspectra
3. Fits Marchenko-Pastur distributions
4. Computes alignment metrics
5. Generates visualizations
"""

import os
import sys
import torch
import numpy as np
import argparse
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config import CONFIG, VIZ_CONFIG, SMOKE_TEST_CONFIG
from utils.setup import set_seed, download_waterbirds, create_directories
from data.dataset import get_dataloaders, get_minority_loader
from models.model import get_resnet50
from train.trainer import Trainer
from analysis.hessian_analysis import (
    compute_hessian_spectrum,
    fit_marchenko_pastur,
    compute_minority_gradient,
    compute_alignment
)
from eval.evaluate import compute_group_accuracies, compute_worst_group_accuracy
from eval.visualize import generate_all_figures


def main(args):
    """Main experiment execution"""

    # Configuration
    config = SMOKE_TEST_CONFIG if args.smoke_test else CONFIG
    device = 'cuda' if torch.cuda.is_available() and not args.cpu else 'cpu'

    print("="*60)
    print("H-E1: Curvature Subspace Alignment Experiment")
    print("="*60)
    print(f"Device: {device}")
    print(f"Smoke Test: {args.smoke_test}")
    print(f"Seed: {config['seed']}")
    print("="*60)

    # Setup
    set_seed(config['seed'])
    create_directories(config)

    # Check dataset
    if not args.smoke_test and not download_waterbirds(config['data_dir']):
        print("\n⚠️ Dataset not found. Using synthetic data for demonstration.")
        # In production, this would exit. For PoC, we continue with placeholder.

    # Load data
    print("\n[1/7] Loading data...")
    try:
        dataloaders = get_dataloaders(
            config['data_dir'],
            batch_size=config.get('smoke_batch_size', config['batch_size']),
            num_workers=config.get('num_workers', 4)
        )
        minority_loader = get_minority_loader(
            config['data_dir'],
            batch_size=config.get('hessian_batch_size', 32)
        )
        print(f"✓ Loaded train/val/test dataloaders")
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        print("Please ensure Waterbirds dataset is available.")
        return

    # Train ERM
    print("\n[2/7] Training ERM model...")
    erm_model = get_resnet50(num_classes=config['num_classes'], pretrained=config['pretrained'])
    erm_trainer = Trainer(
        erm_model,
        dataloaders['train'],
        dataloaders['val'],
        config,
        method='erm',
        device=device
    )
    erm_checkpoint = erm_trainer.train(
        epochs=config.get('smoke_epochs', config['epochs']),
        checkpoint_dir=config['checkpoint_dir']
    )
    erm_trainer.save_history(os.path.join(config['results_dir'], 'erm_history.csv'))
    print(f"✓ ERM training complete")

    # Train Group-DRO
    print("\n[3/7] Training Group-DRO model...")
    dro_model = get_resnet50(num_classes=config['num_classes'], pretrained=config['pretrained'])
    dro_trainer = Trainer(
        dro_model,
        dataloaders['train'],
        dataloaders['val'],
        config,
        method='dro',
        device=device
    )
    dro_checkpoint = dro_trainer.train(
        epochs=config.get('smoke_epochs', config['epochs']),
        checkpoint_dir=config['checkpoint_dir']
    )
    dro_trainer.save_history(os.path.join(config['results_dir'], 'dro_history.csv'))
    print(f"✓ Group-DRO training complete")

    # Evaluate on test set
    print("\n[4/7] Evaluating models...")
    erm_group_accs, _ = compute_group_accuracies(erm_model, dataloaders['test'], device=device)
    dro_group_accs, _ = compute_group_accuracies(dro_model, dataloaders['test'], device=device)

    erm_worst_group = compute_worst_group_accuracy(erm_group_accs)
    dro_worst_group = compute_worst_group_accuracy(dro_group_accs)

    print(f"ERM - Group Accs: {[f'{a:.2f}' for a in erm_group_accs]}, Worst: {erm_worst_group:.2f}%")
    print(f"DRO - Group Accs: {[f'{a:.2f}' for a in dro_group_accs]}, Worst: {dro_worst_group:.2f}%")

    # Compute Hessian spectra
    print("\n[5/7] Computing Hessian eigenspectra...")
    num_eigenthings = config.get('smoke_num_eigenthings', config['num_eigenthings'])

    print("  Computing ERM Hessian...")
    erm_eigenvalues, erm_eigenvectors = compute_hessian_spectrum(
        erm_model, dataloaders['train'], num_eigenthings=num_eigenthings, device=device
    )
    erm_bulk_edge, erm_sigma_sq, erm_gamma = fit_marchenko_pastur(erm_eigenvalues)
    print(f"  ✓ ERM: bulk_edge={erm_bulk_edge:.4f}, σ²={erm_sigma_sq:.4f}, γ={erm_gamma:.4f}")

    print("  Computing DRO Hessian...")
    dro_eigenvalues, dro_eigenvectors = compute_hessian_spectrum(
        dro_model, dataloaders['train'], num_eigenthings=num_eigenthings, device=device
    )
    dro_bulk_edge, dro_sigma_sq, dro_gamma = fit_marchenko_pastur(dro_eigenvalues)
    print(f"  ✓ DRO: bulk_edge={dro_bulk_edge:.4f}, σ²={dro_sigma_sq:.4f}, γ={dro_gamma:.4f}")

    # Compute alignment
    print("\n[6/7] Computing alignment metrics...")

    print("  Computing minority gradients...")
    erm_minority_grad = compute_minority_gradient(erm_model, minority_loader, device=device)
    dro_minority_grad = compute_minority_gradient(dro_model, minority_loader, device=device)

    erm_alignment = compute_alignment(erm_minority_grad, erm_eigenvectors, erm_eigenvalues, erm_bulk_edge)
    dro_alignment = compute_alignment(dro_minority_grad, dro_eigenvectors, dro_eigenvalues, dro_bulk_edge)

    print(f"  ✓ ERM alignment: {erm_alignment:.4f}")
    print(f"  ✓ DRO alignment: {dro_alignment:.4f}")
    print(f"  ✓ Difference (ERM - DRO): {erm_alignment - dro_alignment:.4f}")

    # Generate visualizations
    print("\n[7/7] Generating visualizations...")
    results = {
        'erm_alignment': erm_alignment,
        'dro_alignment': dro_alignment,
        'erm_eigenvalues': erm_eigenvalues,
        'dro_eigenvalues': dro_eigenvalues,
        'erm_bulk_edge': erm_bulk_edge,
        'dro_bulk_edge': dro_bulk_edge,
        'erm_history': erm_trainer.history,
        'dro_history': dro_trainer.history,
        'erm_group_accs': erm_group_accs,
        'dro_group_accs': dro_group_accs,
        'erm_worst_group': erm_worst_group,
        'dro_worst_group': dro_worst_group
    }

    generate_all_figures(results, config['figures_dir'], VIZ_CONFIG)

    # Save final results
    final_results = {
        'erm_alignment': float(erm_alignment),
        'dro_alignment': float(dro_alignment),
        'alignment_difference': float(erm_alignment - dro_alignment),
        'erm_worst_group_acc': float(erm_worst_group),
        'dro_worst_group_acc': float(dro_worst_group),
        'erm_group_accs': [float(a) for a in erm_group_accs],
        'dro_group_accs': [float(a) for a in dro_group_accs],
        'hypothesis': 'ERM exhibits higher alignment than Group-DRO',
        'result': 'PASS' if erm_alignment > dro_alignment else 'FAIL'
    }

    results_path = os.path.join(config['results_dir'], 'final_results.json')
    with open(results_path, 'w') as f:
        json.dump(final_results, f, indent=2)

    print(f"\n✓ Results saved to {results_path}")

    # Summary
    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print(f"Hypothesis: ERM alignment > DRO alignment")
    print(f"Result: {final_results['result']}")
    print(f"  ERM alignment: {erm_alignment:.4f}")
    print(f"  DRO alignment: {dro_alignment:.4f}")
    print(f"  Difference: {erm_alignment - dro_alignment:.4f}")
    print("="*60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='H-E1 Experiment')
    parser.add_argument('--smoke-test', action='store_true', help='Run smoke test (1 epoch, reduced data)')
    parser.add_argument('--cpu', action='store_true', help='Use CPU instead of GPU')

    args = parser.parse_args()
    main(args)
