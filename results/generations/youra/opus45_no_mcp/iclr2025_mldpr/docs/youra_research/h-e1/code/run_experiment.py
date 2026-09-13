#!/usr/bin/env python3
import os
import json
import random
import numpy as np
import torch

from config import CONFIG
from data import (load_cifar10, load_cinic10, load_svhn,
                  sample_svhn_extra, make_loader)
from model import build_resnet18
from train import train_one_condition, set_seed
from evaluate import compute_generalization_gap
from stats import compare_gaps
from visualize import plot_gap_comparison, plot_accuracy_comparison, plot_training_curves


def main():
    set_seed(CONFIG['seed'])
    device = torch.device(CONFIG['device'] if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")

    os.makedirs(CONFIG['checkpoint_dir'], exist_ok=True)
    os.makedirs(CONFIG['figures_dir'], exist_ok=True)

    # Train both conditions
    print("\n=== Training CIFAR-10 condition ===")
    cifar_ckpt = train_one_condition('cifar10', CONFIG)
    print(f"CIFAR-10 checkpoint: {cifar_ckpt}")

    print("\n=== Training SVHN condition ===")
    svhn_ckpt = train_one_condition('svhn', CONFIG)
    print(f"SVHN checkpoint: {svhn_ckpt}")

    # Load models
    cifar_model = build_resnet18(CONFIG['num_classes']).to(device)
    cifar_model.load_state_dict(torch.load(cifar_ckpt, map_location=device))

    svhn_model = build_resnet18(CONFIG['num_classes']).to(device)
    svhn_model.load_state_dict(torch.load(svhn_ckpt, map_location=device))

    # Prepare evaluation loaders
    cifar_mean, cifar_std = CONFIG['cifar10_norm']
    svhn_mean, svhn_std = CONFIG['svhn_norm']

    _, cifar_test = load_cifar10(CONFIG['data_root'], cifar_mean, cifar_std)
    cinic_test = load_cinic10(CONFIG['data_root'], cifar_mean, cifar_std)

    _, svhn_test, svhn_extra = load_svhn(CONFIG['data_root'], svhn_mean, svhn_std)
    svhn_extra_sampled = sample_svhn_extra(svhn_extra, CONFIG['svhn_extra_sample_size'], CONFIG['seed'])

    cifar_test_loader = make_loader(cifar_test, CONFIG['batch_size'], shuffle=False)
    cinic_loader = make_loader(cinic_test, CONFIG['batch_size'], shuffle=False)
    svhn_test_loader = make_loader(svhn_test, CONFIG['batch_size'], shuffle=False)
    svhn_extra_loader = make_loader(svhn_extra_sampled, CONFIG['batch_size'], shuffle=False)

    # Compute generalization gaps
    print("\n=== Evaluating ===")
    cifar_results = compute_generalization_gap(cifar_model, cifar_test_loader, cinic_loader, device)
    svhn_results = compute_generalization_gap(svhn_model, svhn_test_loader, svhn_extra_loader, device)

    print(f"CIFAR-10: in_domain={cifar_results['in_domain_acc']:.2f}%, held_out={cifar_results['held_out_acc']:.2f}%, gap={cifar_results['gap']:.2f}%")
    print(f"SVHN: in_domain={svhn_results['in_domain_acc']:.2f}%, held_out={svhn_results['held_out_acc']:.2f}%, gap={svhn_results['gap']:.2f}%")

    # Statistical comparison
    stats = compare_gaps([cifar_results['gap']], [svhn_results['gap']])
    print(f"\nStatistics: Cohen's d={stats['d']}, t={stats['t']}, p={stats['p']}")

    # PoC check
    poc_pass = cifar_results['gap'] > svhn_results['gap']
    print(f"\nPoC Pass (gap_high > gap_low): {poc_pass}")

    # Load training histories for visualization
    history = {}
    for cond in ['cifar10', 'svhn']:
        hist_path = os.path.join(CONFIG['checkpoint_dir'], f"{cond}_history.json")
        if os.path.exists(hist_path):
            with open(hist_path, 'r') as f:
                history[cond] = json.load(f)

    # Generate figures
    plot_gap_comparison(cifar_results['gap'], svhn_results['gap'],
                        os.path.join(CONFIG['figures_dir'], 'gap_comparison.png'))
    plot_accuracy_comparison({'cifar10': cifar_results, 'svhn': svhn_results},
                             os.path.join(CONFIG['figures_dir'], 'accuracy_comparison.png'))
    if history:
        plot_training_curves(history, os.path.join(CONFIG['figures_dir'], 'training_curves.png'))

    # Save results
    results = {
        "cifar10": cifar_results,
        "svhn": svhn_results,
        "stats": stats,
        "poc_pass": poc_pass,
        "gate_metrics": {
            "cohens_d": stats['d'],
            "p_value": stats['p'],
            "direction_check": poc_pass,
        }
    }
    with open(CONFIG['results_path'], 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {CONFIG['results_path']}")

    # CSV output for pipeline
    csv_path = os.path.join('outputs', 'results.csv')
    os.makedirs('outputs', exist_ok=True)
    with open(csv_path, 'w') as f:
        f.write("condition,in_domain_acc,held_out_acc,gap\n")
        f.write(f"cifar10,{cifar_results['in_domain_acc']},{cifar_results['held_out_acc']},{cifar_results['gap']}\n")
        f.write(f"svhn,{svhn_results['in_domain_acc']},{svhn_results['held_out_acc']},{svhn_results['gap']}\n")
    print(f"CSV saved to {csv_path}")


if __name__ == '__main__':
    main()
