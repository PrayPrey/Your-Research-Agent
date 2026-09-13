"""
Main script to run AMR experiments
"""
import os
import sys
import json
import random
import numpy as np
import torch
import torch.optim as optim
from tqdm import tqdm
import argparse
from collections import defaultdict
import copy

from config import Config
from data_loader import get_data_loaders
from models import get_model
from amr_trainer import AMRTrainer, BaselineTrainer, GroupDROTrainer, JTTTrainer
from evaluation import evaluate_model, evaluate_all_groups
from visualization import (
    plot_training_curves, plot_group_performance,
    plot_method_comparison, plot_robustness_tradeoff,
    save_results_table
)


def set_seed(seed):
    """Set random seed for reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def train_epoch(model, train_loader, trainer, optimizer, epoch, method_name):
    """Train for one epoch"""
    model.train()
    epoch_metrics = defaultdict(list)

    pbar = tqdm(train_loader, desc=f'{method_name} Epoch {epoch}')

    for batch_idx, (inputs, targets, groups) in enumerate(pbar):
        # Training step
        metrics = trainer.train_step(inputs, targets, groups, optimizer)

        # Track metrics
        for key, value in metrics.items():
            epoch_metrics[key].append(value)

        # Update progress bar
        pbar.set_postfix({'loss': f"{metrics['loss']:.4f}"})

    # Average metrics
    avg_metrics = {k: np.mean(v) for k, v in epoch_metrics.items()}
    return avg_metrics


def train_method(method_name, config, train_loader, val_loader, test_loader):
    """Train a single method"""
    print(f"\n{'='*60}")
    print(f"Training {method_name}")
    print(f"{'='*60}")

    # Initialize model
    model = get_model(config)

    # Initialize optimizer
    if config.model_arch.startswith('resnet'):
        optimizer = optim.Adam(
            model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay
        )
    else:
        optimizer = optim.SGD(
            model.parameters(),
            lr=config.learning_rate,
            momentum=config.momentum,
            weight_decay=config.weight_decay
        )

    # Learning rate scheduler
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=config.num_epochs
    )

    # Initialize trainer
    total_steps = len(train_loader) * config.num_epochs

    if method_name == 'AMR':
        trainer = AMRTrainer(model, config, total_steps)
    elif method_name == 'GroupDRO':
        trainer = GroupDROTrainer(model, config, n_groups=4)
    elif method_name == 'JTT':
        trainer = JTTTrainer(model, config)
    else:  # ERM
        trainer = BaselineTrainer(model, config)

    # Training history
    history = {
        'train_loss': [],
        'val_avg_acc': [],
        'val_worst_acc': [],
        'val_margin': []
    }

    best_worst_acc = 0.0
    best_model = None

    # Training loop
    for epoch in range(1, config.num_epochs + 1):
        # Train
        train_metrics = train_epoch(
            model, train_loader, trainer, optimizer, epoch, method_name
        )

        history['train_loss'].append(train_metrics['loss'])

        # Evaluate
        if epoch % config.eval_every == 0 or epoch == config.num_epochs:
            val_results = evaluate_model(model, val_loader, config.device, n_groups=4)

            history['val_avg_acc'].append(val_results['overall_accuracy'])
            history['val_worst_acc'].append(val_results['worst_group_accuracy'])
            history['val_margin'].append(val_results['avg_margin'])

            print(f"\nEpoch {epoch}:")
            print(f"  Train Loss: {train_metrics['loss']:.4f}")
            print(f"  Val Avg Acc: {val_results['overall_accuracy']:.4f}")
            print(f"  Val Worst Group Acc: {val_results['worst_group_accuracy']:.4f}")
            print(f"  Val Avg Margin: {val_results['avg_margin']:.4f}")

            # Save best model
            if val_results['worst_group_accuracy'] > best_worst_acc:
                best_worst_acc = val_results['worst_group_accuracy']
                best_model = copy.deepcopy(model.state_dict())

        # Step scheduler
        scheduler.step()

    # Load best model and evaluate on test set
    if best_model is not None:
        model.load_state_dict(best_model)

    test_results = evaluate_model(model, test_loader, config.device, n_groups=4)
    detailed_results = evaluate_all_groups(model, test_loader, config.device, n_groups=4)

    print(f"\n{method_name} Test Results:")
    print(f"  Test Avg Acc: {test_results['overall_accuracy']:.4f}")
    print(f"  Test Worst Group Acc: {test_results['worst_group_accuracy']:.4f}")

    # Combine results
    final_results = {**test_results, **detailed_results}

    return history, final_results, model


def run_experiments(config, log_file):
    """Run all experiments"""
    print(f"Device: {config.device}")
    print(f"Dataset: {config.dataset_name}")
    print(f"Model: {config.model_arch}")

    # Create save directory
    os.makedirs(config.save_dir, exist_ok=True)

    # Log configuration
    with open(log_file, 'w') as f:
        f.write("Experiment Configuration\n")
        f.write("=" * 60 + "\n")
        for key, value in vars(config).items():
            f.write(f"{key}: {value}\n")
        f.write("\n")

    # Load data
    print("\nLoading data...")
    train_loader, val_loader, test_loader = get_data_loaders(config)

    print(f"Train samples: {len(train_loader.dataset)}")
    print(f"Val samples: {len(val_loader.dataset)}")
    print(f"Test samples: {len(test_loader.dataset)}")

    # Run experiments for each method
    all_histories = {}
    all_results = {}

    for method in config.baselines:
        set_seed(config.seed)

        try:
            history, results, model = train_method(
                method, config, train_loader, val_loader, test_loader
            )

            all_histories[method] = history
            all_results[method] = results

            # Log results
            with open(log_file, 'a') as f:
                f.write(f"\n{method} Results\n")
                f.write("-" * 60 + "\n")
                f.write(f"Overall Accuracy: {results['overall_accuracy']:.4f}\n")
                f.write(f"Worst Group Accuracy: {results['worst_group_accuracy']:.4f}\n")
                for g in range(4):
                    key = f'group_{g}_accuracy'
                    if key in results:
                        f.write(f"Group {g} Accuracy: {results[key]:.4f}\n")
                f.write("\n")

        except Exception as e:
            print(f"Error training {method}: {e}")
            import traceback
            traceback.print_exc()

            with open(log_file, 'a') as f:
                f.write(f"\n{method} Failed\n")
                f.write(f"Error: {str(e)}\n\n")

    return all_histories, all_results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='colored_mnist',
                       choices=['colored_mnist', 'waterbirds'])
    parser.add_argument('--epochs', type=int, default=30)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    # Create config
    config = Config.get_config(
        dataset_name=args.dataset,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        seed=args.seed
    )

    # Set seed
    set_seed(config.seed)

    # Log file
    log_file = os.path.join(config.save_dir, 'log.txt')

    # Run experiments
    all_histories, all_results = run_experiments(config, log_file)

    # Save results
    print("\nSaving results...")

    # Save JSON results
    results_file = os.path.join(config.save_dir, 'results.json')
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    # Generate visualizations
    print("\nGenerating visualizations...")

    # Training curves
    plot_training_curves(
        all_histories,
        os.path.join(config.save_dir, 'training_curves.png')
    )

    # Group performance
    plot_group_performance(
        all_results,
        os.path.join(config.save_dir, 'group_performance.png')
    )

    # Method comparison
    plot_method_comparison(
        all_results,
        os.path.join(config.save_dir, 'method_comparison.png')
    )

    # Robustness tradeoff
    plot_robustness_tradeoff(
        all_results,
        os.path.join(config.save_dir, 'robustness_tradeoff.png')
    )

    # Results table
    results_df = save_results_table(
        all_results,
        os.path.join(config.save_dir, 'results_table.csv')
    )

    print("\n" + "=" * 60)
    print("Results Summary")
    print("=" * 60)
    print(results_df.to_string(index=False))

    print(f"\nAll results saved to {config.save_dir}")
    print("Experiment completed successfully!")


if __name__ == '__main__':
    main()
