"""Main experiment script for NeuroSAT heterogeneity validation."""
import argparse
import json
import torch
from pathlib import Path
from data import SATDataLoader
from models import NeuroSAT
from train import Trainer
from metrics import HeterogeneityAnalyzer
from visualization import generate_all_figures


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='NeuroSAT Basin Entry Heterogeneity Experiment')

    # Data
    parser.add_argument('--data_dir', type=str, required=True,
                        help='Path to G4SATBench dataset directory')
    parser.add_argument('--batch_size', type=int, default=32,
                        help='Batch size for training/evaluation')

    # Model
    parser.add_argument('--d_model', type=int, default=128,
                        help='Hidden dimension for embeddings')
    parser.add_argument('--num_rounds', type=int, default=32,
                        help='Number of message-passing rounds')

    # Training
    parser.add_argument('--epochs', type=int, default=100,
                        help='Maximum number of training epochs')
    parser.add_argument('--lr', type=float, default=1e-4,
                        help='Learning rate')
    parser.add_argument('--weight_decay', type=float, default=1e-8,
                        help='Weight decay for optimizer')
    parser.add_argument('--early_stopping_patience', type=int, default=20,
                        help='Patience for early stopping')

    # Evaluation
    parser.add_argument('--num_test_samples', type=int, default=200,
                        help='Number of test samples for heterogeneity analysis')

    # Output
    parser.add_argument('--output_dir', type=str, required=True,
                        help='Directory to save results and checkpoints')

    # Device
    parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu',
                        help='Device to use (cuda/cpu)')

    return parser.parse_args()


def setup_experiment(args):
    """Set up data loaders and model."""
    print("=" * 80)
    print("EXPERIMENT SETUP")
    print("=" * 80)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Data loaders
    print(f"\n[1/3] Loading data from {args.data_dir}...")
    data_loader = SATDataLoader(
        root=args.data_dir,
        batch_size=args.batch_size,
        num_workers=4
    )
    train_loader = data_loader.get_train_loader()
    val_loader = data_loader.get_val_loader()
    test_loader = data_loader.get_test_loader()
    print(f"  ✓ Train: {len(train_loader.dataset)} samples")
    print(f"  ✓ Val: {len(val_loader.dataset)} samples")
    print(f"  ✓ Test: {len(test_loader.dataset)} samples")

    # Model
    print(f"\n[2/3] Initializing NeuroSAT model...")
    model = NeuroSAT(hidden_size=args.d_model, num_rounds=args.num_rounds)
    print(f"  ✓ Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"  ✓ Hidden dimension: {args.d_model}")
    print(f"  ✓ Message-passing rounds: {args.num_rounds}")

    # Training config
    print(f"\n[3/3] Training configuration...")
    config = {
        'lr': args.lr,
        'weight_decay': args.weight_decay,
        'early_stopping_patience': args.early_stopping_patience
    }
    print(f"  ✓ Learning rate: {args.lr}")
    print(f"  ✓ Weight decay: {args.weight_decay}")
    print(f"  ✓ Early stopping patience: {args.early_stopping_patience}")
    print(f"  ✓ Device: {args.device}")

    return train_loader, val_loader, test_loader, model, config, output_dir


def train_model(model, train_loader, val_loader, config, device, output_dir, epochs):
    """Train the NeuroSAT model."""
    print("\n" + "=" * 80)
    print("TRAINING PHASE")
    print("=" * 80)

    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        config=config,
        device=device,
        output_dir=str(output_dir)
    )

    results = trainer.train(epochs=epochs)

    print(f"\n✅ Training completed")
    print(f"  ✓ Best validation loss: {results['best_val_loss']:.4f}")
    print(f"  ✓ Total epochs: {len(results['history'])}")

    return trainer, results


def evaluate_heterogeneity(model, test_loader, device, output_dir, num_samples):
    """Evaluate basin entry heterogeneity metrics."""
    print("\n" + "=" * 80)
    print("HETEROGENEITY EVALUATION")
    print("=" * 80)

    # Initialize analyzer
    analyzer = HeterogeneityAnalyzer()

    # Collect solutions
    print(f"\n[1/3] Collecting solutions from {num_samples} test samples...")
    assignments, ground_truths, clauses_list = analyzer.collect_solutions(
        model=model,
        dataloader=test_loader,
        device=device
    )
    print(f"  ✓ Collected {len(assignments)} assignments")

    # Compute metrics
    print(f"\n[2/3] Computing heterogeneity metrics...")
    metrics = analyzer.analyze_distribution(
        assignments=assignments,
        ground_truths=ground_truths,
        clauses_list=clauses_list
    )

    # Print metrics
    print(f"\n  Hamming Distance (d/n) Metrics:")
    print(f"    • Range: {metrics['d_n_range']:.4f} (target: > 0.20)")
    print(f"    • Mean: {metrics['d_n_mean']:.4f}")
    print(f"    • Std: {metrics['d_n_std']:.4f}")
    print(f"    • IQR: {metrics['d_n_iqr']:.4f}")
    print(f"    • Quartiles: Q1={metrics['d_n_quartiles']['Q1']:.4f}, "
          f"Q2={metrics['d_n_quartiles']['Q2']:.4f}, "
          f"Q3={metrics['d_n_quartiles']['Q3']:.4f}")

    print(f"\n  Violation Entropy (H) Metrics:")
    print(f"    • Range: {metrics['entropy_range']:.4f} (target: > 2.0)")
    print(f"    • Mean: {metrics['entropy_mean']:.4f}")
    print(f"    • Std: {metrics['entropy_std']:.4f}")
    print(f"    • Quartiles: Q1={metrics['entropy_quartiles']['Q1']:.4f}, "
          f"Q2={metrics['entropy_quartiles']['Q2']:.4f}, "
          f"Q3={metrics['entropy_quartiles']['Q3']:.4f}")

    # Gate check
    gate_pass = analyzer.check_gate_criteria(metrics)
    print(f"\n  Gate Criteria:")
    print(f"    • d/n range > 0.20: {'✓ PASS' if metrics['d_n_range'] > 0.20 else '✗ FAIL'}")
    print(f"    • Entropy range > 2.0: {'✓ PASS' if metrics['entropy_range'] > 2.0 else '✗ FAIL'}")
    print(f"    • Overall: {'✅ PASS' if gate_pass else '❌ FAIL'}")

    # Generate figures
    print(f"\n[3/3] Generating visualization figures...")
    figures_dir = output_dir / 'figures'
    generate_all_figures(metrics, str(figures_dir))

    return metrics


def save_results(metrics, training_results, output_dir):
    """Save experiment results to JSON."""
    print("\n" + "=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)

    results = {
        'heterogeneity_metrics': {
            'd_n_range': metrics['d_n_range'],
            'd_n_iqr': metrics['d_n_iqr'],
            'd_n_mean': metrics['d_n_mean'],
            'd_n_std': metrics['d_n_std'],
            'd_n_quartiles': metrics['d_n_quartiles'],
            'entropy_range': metrics['entropy_range'],
            'entropy_mean': metrics['entropy_mean'],
            'entropy_std': metrics['entropy_std'],
            'entropy_quartiles': metrics['entropy_quartiles'],
            'pass_criteria': metrics['pass_criteria']
        },
        'training_summary': {
            'best_val_loss': training_results['best_val_loss'],
            'total_epochs': len(training_results['history'])
        },
        'gate_result': 'PASS' if metrics['pass_criteria'] else 'FAIL'
    }

    # Save to JSON
    results_path = output_dir / 'results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Results saved to {results_path}")
    print(f"  ✓ Heterogeneity metrics: {len(results['heterogeneity_metrics'])} metrics")
    print(f"  ✓ Training summary: {results['training_summary']['total_epochs']} epochs")
    print(f"  ✓ Gate result: {results['gate_result']}")

    return results


def main():
    """Main experiment orchestration."""
    # Parse arguments
    args = parse_args()

    # Setup
    train_loader, val_loader, test_loader, model, config, output_dir = setup_experiment(args)

    # Train
    trainer, training_results = train_model(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        config=config,
        device=args.device,
        output_dir=output_dir,
        epochs=args.epochs
    )

    # Load best model
    print(f"\n[Loading best model checkpoint...]")
    trainer.load_checkpoint(output_dir / 'best_model.pt')

    # Evaluate heterogeneity
    metrics = evaluate_heterogeneity(
        model=trainer.model,
        test_loader=test_loader,
        device=args.device,
        output_dir=output_dir,
        num_samples=args.num_test_samples
    )

    # Save results
    results = save_results(metrics, training_results, output_dir)

    # Final summary
    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)
    print(f"\nGate Result: {results['gate_result']}")
    print(f"Output directory: {output_dir}")
    print("\nGenerated files:")
    print(f"  • results.json")
    print(f"  • training_log.csv")
    print(f"  • best_model.pt")
    print(f"  • figures/gate_comparison.png")
    print(f"  • figures/dn_distribution.png")
    print(f"  • figures/entropy_distribution.png")
    print(f"  • figures/dn_entropy_scatter.png")
    print(f"  • figures/quartile_boxplot.png")
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
