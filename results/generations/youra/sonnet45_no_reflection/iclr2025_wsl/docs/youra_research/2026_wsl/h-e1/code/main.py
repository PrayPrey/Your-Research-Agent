"""Main experiment script for H-E1 Quotient Space Existence"""

import os
import torch
import numpy as np
import json
from src.config import (
    DATASET_CONFIG, PROPOSED_CONFIG, TRAINING_CONFIG,
    EVALUATION_CONFIG, VISUALIZATION_CONFIG
)
from src.data import create_dataloaders, create_frozen_k_loader
from src.models.proposed import SlotEquivariantEncoder
from src.train import Trainer
from src.evaluate import Evaluator
from src.visualize import (
    plot_gate_metrics, plot_training_curves,
    plot_quotient_space_tsne, plot_reconstruction_error_distribution
)


def set_seed(seed: int):
    """Set random seeds for reproducibility"""
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def setup_experiment():
    """Setup directories and environment"""
    os.makedirs('./checkpoints', exist_ok=True)
    os.makedirs('./figures', exist_ok=True)
    os.makedirs('./results', exist_ok=True)

    set_seed(TRAINING_CONFIG['seed'])

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    return device


def run_experiment(K: int, lambda_equiv: float, device: str):
    """Run single experiment with given hyperparameters"""
    print(f"\n{'='*60}")
    print(f"Running experiment: K={K}, λ_equiv={lambda_equiv}")
    print(f"{'='*60}\n")

    # Reduced weight dimension for faster proof-of-concept
    weight_dim = 1000

    # Create dataloaders
    print("Creating dataloaders...")
    train_loader, val_loader, test_loader = create_dataloaders(
        weight_dim=weight_dim,
        batch_size=TRAINING_CONFIG['batch_size'],
        seed=TRAINING_CONFIG['seed']
    )

    rnn_loader = create_frozen_k_loader(
        weight_dim=weight_dim,
        batch_size=TRAINING_CONFIG['batch_size'],
        seed=TRAINING_CONFIG['seed']
    )

    # Create model
    print("Creating model...")
    model = SlotEquivariantEncoder(
        weight_dim=weight_dim,
        K=K,
        hidden_dim=PROPOSED_CONFIG['hidden_dim'],
        num_arch_classes=PROPOSED_CONFIG['num_arch_classes'],
        arch_embed_dim=PROPOSED_CONFIG['arch_embed_dim']
    )

    # Train model
    print("Training model...")
    trainer = Trainer(model, train_loader, val_loader, TRAINING_CONFIG, device)

    # Reduced epochs for proof-of-concept
    num_epochs = 20
    history = trainer.train(num_epochs=num_epochs, lambda_equiv=lambda_equiv)

    # Load best checkpoint
    print("Loading best checkpoint...")
    trainer.load_checkpoint('./checkpoints/best_model.pt')

    # Evaluate
    print("Evaluating model...")
    evaluator = Evaluator(model, test_loader, device)
    metrics = evaluator.evaluate_all(rnn_loader)

    print(f"\nResults:")
    print(f"  Reconstruction Error: {metrics['reconstruction_error']:.2f}%")
    print(f"  Frozen-K Generalization: {metrics['frozen_k_generalization']:.2f}%")
    print(f"  Kernel Robustness: {metrics['kernel_robustness']:.2f}%")

    # Visualizations
    print("Generating visualizations...")

    # Gate metrics
    targets = {
        'reconstruction_error': EVALUATION_CONFIG['target_reconstruction_error'],
        'frozen_k_generalization': EVALUATION_CONFIG['target_frozen_k_gen'],
        'kernel_robustness': EVALUATION_CONFIG['target_kernel_robustness']
    }
    plot_gate_metrics(targets, metrics, './figures/gate_metrics.png')

    # Training curves
    plot_training_curves(history, './figures/training_curves.png')

    # Quotient space t-SNE
    print("Generating t-SNE visualization...")
    embeddings = []
    labels = []
    model.eval()
    with torch.no_grad():
        for batch in test_loader:
            weights = batch['weights'].to(device)
            arch_labels = batch['arch_label'].to(device)
            z = model(weights, arch_labels)
            embeddings.append(z.cpu().numpy())
            labels.append(arch_labels.cpu().numpy())

    embeddings = np.vstack(embeddings)
    labels = np.concatenate(labels)
    plot_quotient_space_tsne(embeddings, labels, './figures/quotient_space_tsne.png')

    # Reconstruction error distribution
    errors = []
    with torch.no_grad():
        for batch in test_loader:
            weights = batch['weights'].to(device)
            arch_labels = batch['arch_label'].to(device)
            z = model(weights, arch_labels)
            weights_recon = model.reconstruct_weights(z)

            batch_errors = torch.mean((weights - weights_recon) ** 2, dim=1)
            errors.extend(batch_errors.cpu().numpy())

    errors = np.array(errors) * 100
    plot_reconstruction_error_distribution(errors, './figures/error_distribution.png')

    return metrics, history


def main():
    """Main entry point"""
    print("H-E1 Quotient Space Existence - Experiment")
    print("=" * 60)

    device = setup_experiment()

    # Run main experiment with default hyperparameters
    K = PROPOSED_CONFIG['K']
    lambda_equiv = TRAINING_CONFIG['lambda_equiv']

    metrics, history = run_experiment(K, lambda_equiv, device)

    # Determine gate verdict
    targets = EVALUATION_CONFIG
    gate_passed = (
        metrics['reconstruction_error'] < targets['target_reconstruction_error'] and
        metrics['frozen_k_generalization'] < targets['target_frozen_k_gen'] and
        metrics['kernel_robustness'] >= targets['target_kernel_robustness']
    )

    print("\n" + "=" * 60)
    print("GATE VERDICT")
    print("=" * 60)
    print(f"Reconstruction Error: {metrics['reconstruction_error']:.2f}% "
          f"(target: <{targets['target_reconstruction_error']}%) "
          f"{'✓' if metrics['reconstruction_error'] < targets['target_reconstruction_error'] else '✗'}")
    print(f"Frozen-K Generalization: {metrics['frozen_k_generalization']:.2f}% "
          f"(target: <{targets['target_frozen_k_gen']}%) "
          f"{'✓' if metrics['frozen_k_generalization'] < targets['target_frozen_k_gen'] else '✗'}")
    print(f"Kernel Robustness: {metrics['kernel_robustness']:.2f}% "
          f"(target: ≥{targets['target_kernel_robustness']}%) "
          f"{'✓' if metrics['kernel_robustness'] >= targets['target_kernel_robustness'] else '✗'}")
    print(f"\nOverall: {'PASS' if gate_passed else 'FAIL'}")
    print("=" * 60)

    # Save results
    results = {
        'metrics': metrics,
        'gate_verdict': 'PASS' if gate_passed else 'FAIL',
        'hyperparameters': {
            'K': K,
            'lambda_equiv': lambda_equiv
        }
    }

    with open('./results/experiment_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\nEXPERIMENT COMPLETE")
    print(f"Results saved to ./results/experiment_results.json")
    print(f"Figures saved to ./figures/")


if __name__ == '__main__':
    main()
