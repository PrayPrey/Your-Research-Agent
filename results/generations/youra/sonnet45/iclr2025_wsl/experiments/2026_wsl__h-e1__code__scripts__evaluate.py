"""
Evaluation script for CAWE model.
Computes Spearman ρ with bootstrap CI and per-architecture metrics.
"""
import torch
import numpy as np
from scipy.stats import spearmanr
import json
import os
import sys
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cawe.models import CAWE
from cawe.data import create_dataloaders


def bootstrap_ci(predictions, targets, n_bootstrap=1000, confidence=0.95):
    """
    Compute bootstrap confidence interval for Spearman ρ.

    Args:
        predictions: Predicted values
        targets: Ground truth values
        n_bootstrap: Number of bootstrap resamples
        confidence: Confidence level (default 0.95)

    Returns:
        rho: Point estimate
        ci_lower: Lower bound of CI
        ci_upper: Upper bound of CI
    """
    rho, _ = spearmanr(predictions, targets)

    rhos = []
    n = len(predictions)
    for _ in range(n_bootstrap):
        indices = np.random.choice(n, size=n, replace=True)
        pred_sample = [predictions[i] for i in indices]
        target_sample = [targets[i] for i in indices]
        if len(set(pred_sample)) > 1 and len(set(target_sample)) > 1:
            rho_sample, _ = spearmanr(pred_sample, target_sample)
            rhos.append(rho_sample)

    alpha = 1 - confidence
    ci_lower = np.percentile(rhos, 100 * alpha / 2)
    ci_upper = np.percentile(rhos, 100 * (1 - alpha / 2))

    return rho, ci_lower, ci_upper


def evaluate_model(model, loader, device):
    """
    Evaluate model on dataset.

    Returns:
        predictions: List of predictions
        targets: List of ground truth values
        arch_families: List of architecture families
    """
    model.eval()
    predictions = []
    targets = []
    arch_families_list = []

    with torch.no_grad():
        for batch in loader:
            state_dicts, arch_families, gaps = batch

            for i in range(len(arch_families)):
                pred = model(state_dicts[i], arch_families[i])
                predictions.append(pred.item())
                targets.append(gaps[i].item())
                arch_families_list.append(arch_families[i])

    return predictions, targets, arch_families_list


def per_architecture_metrics(predictions, targets, arch_families):
    """
    Compute per-architecture Spearman ρ.

    Returns:
        metrics: Dictionary with rho for each architecture
    """
    metrics = {}
    for arch in set(arch_families):
        indices = [i for i, a in enumerate(arch_families) if a == arch]
        if len(indices) > 1:
            arch_preds = [predictions[i] for i in indices]
            arch_targets = [targets[i] for i in indices]
            if len(set(arch_preds)) > 1 and len(set(arch_targets)) > 1:
                rho, _ = spearmanr(arch_preds, arch_targets)
                metrics[arch] = rho
            else:
                metrics[arch] = 0.0
        else:
            metrics[arch] = 0.0

    return metrics


def main():
    parser = argparse.ArgumentParser(description='Evaluate CAWE model')
    parser.add_argument('--model-path', type=str, default='../outputs/best_model.pt', help='Path to trained model')
    parser.add_argument('--output-dir', type=str, default='../outputs', help='Output directory')
    parser.add_argument('--n-bootstrap', type=int, default=1000, help='Number of bootstrap resamples')
    args = parser.parse_args()

    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # Load data
    print("Loading REAL model zoo data...")
    _, _, test_loader = create_dataloaders(batch_size=16, test_samples=60)
    print(f"Test samples: {len(test_loader.dataset)}")

    # Load model
    print(f"\nLoading model from {args.model_path}...")
    model = CAWE(token_dim=128, nft_channels=64).to(device)
    checkpoint = torch.load(args.model_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    print("Model loaded successfully")

    # Evaluate
    print("\nEvaluating...")
    predictions, targets, arch_families = evaluate_model(model, test_loader, device)

    # Primary metric: Spearman ρ with bootstrap CI
    print("\nComputing bootstrap CI...")
    rho, ci_lower, ci_upper = bootstrap_ci(predictions, targets, n_bootstrap=args.n_bootstrap)

    print(f"\nPrimary Metric:")
    print(f"  Spearman ρ: {rho:.4f}")
    print(f"  95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")

    # Secondary metric: Per-architecture performance
    per_arch = per_architecture_metrics(predictions, targets, arch_families)
    print(f"\nPer-Architecture Metrics:")
    for arch, arch_rho in per_arch.items():
        print(f"  {arch}: ρ = {arch_rho:.4f}")

    # Save results
    results = {
        'overall': {
            'spearman_rho': float(rho),
            'ci_lower': float(ci_lower),
            'ci_upper': float(ci_upper),
            'n_samples': len(predictions)
        },
        'per_architecture': {arch: float(r) for arch, r in per_arch.items()},
        'gate_evaluation': {
            'primary_criterion': 'Spearman ρ > 0.7 (95% CI lower bound)',
            'primary_result': bool(ci_lower > 0.7),
            'secondary_criterion': 'All per-architecture ρ > 0.65',
            'secondary_result': bool(all(r > 0.65 for r in per_arch.values()))
        }
    }

    os.makedirs(args.output_dir, exist_ok=True)
    with open(os.path.join(args.output_dir, 'evaluation_results.json'), 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {os.path.join(args.output_dir, 'evaluation_results.json')}")


if __name__ == '__main__':
    main()
