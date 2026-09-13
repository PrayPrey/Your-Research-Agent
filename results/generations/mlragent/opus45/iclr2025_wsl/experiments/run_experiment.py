"""
Main experiment script for SymVAE: Symmetry-Aware Variational Autoencoders
for Neural Network Weight Generation.

This script runs all experiments including:
1. Creating a model zoo of trained networks
2. Training SymVAE and baseline models
3. Evaluating generation quality, symmetry invariance, and interpolation smoothness
4. Running ablation studies
5. Generating visualizations and saving results
"""

import os
import sys
import json
import argparse
import logging
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from tqdm import tqdm

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import SymVAE, VanillaVAE, HyperNetwork, TargetMLP
from data import ModelZoo, WeightDataset, collate_weights, SyntheticTaskDataset
from training import (
    train_vae_epoch, evaluate_vae,
    train_hypernetwork_epoch, evaluate_hypernetwork,
    evaluate_generation_quality, evaluate_symmetry_invariance,
    evaluate_interpolation_smoothness
)
from visualization import (
    plot_training_curves, plot_model_comparison,
    plot_latent_space_variance, plot_generation_quality,
    plot_interpolation_smoothness, plot_ablation_study,
    create_summary_table, plot_radar_chart
)


def setup_logging(log_file: str):
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def get_device():
    """Get the best available device."""
    if torch.cuda.is_available():
        # Try to find a free GPU
        for i in range(torch.cuda.device_count()):
            try:
                torch.cuda.set_device(i)
                torch.cuda.empty_cache()
                # Test if we can allocate memory
                test = torch.zeros(1, device=f'cuda:{i}')
                del test
                return torch.device(f'cuda:{i}')
            except:
                continue
    return torch.device('cpu')


def create_model_zoo(architecture: List[int], device: torch.device,
                     n_models: int, n_epochs: int, task_type: str,
                     logger) -> List[Dict]:
    """Create model zoo by training networks on diverse tasks."""
    logger.info(f"Creating model zoo with {n_models} models...")
    zoo = ModelZoo(architecture, device)
    models = zoo.create_zoo(n_models=n_models, n_epochs=n_epochs,
                            task_type=task_type, verbose=True)
    logger.info(f"Model zoo created with {len(models)} models")

    # Log statistics
    val_losses = [m['val_loss'] for m in models]
    logger.info(f"Model zoo validation losses: mean={np.mean(val_losses):.4f}, "
                f"std={np.std(val_losses):.4f}, min={np.min(val_losses):.4f}, "
                f"max={np.max(val_losses):.4f}")

    return models


def train_model(model: nn.Module, model_name: str, train_loader: DataLoader,
                val_loader: DataLoader, device: torch.device,
                n_epochs: int, lr: float, beta: float, logger) -> Dict:
    """Train a weight generation model."""
    logger.info(f"Training {model_name}...")
    model = model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=10
    )

    train_history = {'total_loss': [], 'recon_loss': [], 'kl_loss': []}
    val_history = {'total_loss': [], 'recon_loss': [], 'kl_loss': []}
    best_val_loss = float('inf')
    best_state = None

    is_vae = hasattr(model, 'encode')

    for epoch in tqdm(range(n_epochs), desc=f"Training {model_name}"):
        if is_vae:
            train_metrics = train_vae_epoch(model, train_loader, optimizer, device, beta)
            val_metrics = evaluate_vae(model, val_loader, device, beta)

            for k in train_history:
                if k in train_metrics:
                    train_history[k].append(train_metrics[k])
                if k in val_metrics:
                    val_history[k].append(val_metrics[k])

            val_loss = val_metrics['total_loss']
        else:
            train_metrics = train_hypernetwork_epoch(model, train_loader, optimizer, device)
            val_metrics = evaluate_hypernetwork(model, val_loader, device)

            train_history['total_loss'].append(train_metrics['loss'])
            val_history['total_loss'].append(val_metrics['loss'])
            val_loss = val_metrics['loss']

        scheduler.step(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

        if (epoch + 1) % 20 == 0:
            logger.info(f"{model_name} Epoch {epoch+1}: train_loss={train_metrics.get('total_loss', train_metrics.get('loss')):.4f}, "
                        f"val_loss={val_loss:.4f}")

    # Restore best model
    if best_state is not None:
        model.load_state_dict(best_state)
        model = model.to(device)

    logger.info(f"{model_name} training completed. Best val loss: {best_val_loss:.4f}")

    return {
        'train_history': train_history,
        'val_history': val_history,
        'best_val_loss': best_val_loss
    }


def run_experiments(args):
    """Run all experiments."""
    # Setup
    output_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(output_dir, 'log.txt')
    logger = setup_logging(log_file)

    logger.info("=" * 60)
    logger.info("SymVAE Experiment Started")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Device setup
    device = get_device()
    logger.info(f"Using device: {device}")

    # Architecture configuration
    architecture = [args.input_dim] + [args.hidden_dim] * args.n_hidden_layers + [args.output_dim]
    logger.info(f"Target network architecture: {architecture}")

    # Hyperparameters
    config = {
        'architecture': architecture,
        'n_models': args.n_models,
        'n_epochs_zoo': args.n_epochs_zoo,
        'n_epochs_gen': args.n_epochs_gen,
        'batch_size': args.batch_size,
        'lr': args.lr,
        'beta': args.beta,
        'latent_dim': args.latent_dim,
        'task_type': args.task_type,
        'seed': args.seed
    }
    logger.info(f"Configuration: {json.dumps(config, indent=2)}")

    # Set random seeds
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    # Create model zoo
    start_time = time.time()
    model_zoo = create_model_zoo(
        architecture, device,
        n_models=args.n_models,
        n_epochs=args.n_epochs_zoo,
        task_type=args.task_type,
        logger=logger
    )
    zoo_time = time.time() - start_time
    logger.info(f"Model zoo creation time: {zoo_time:.2f}s")

    # Split model zoo into train/val/test
    n_train = int(0.7 * len(model_zoo))
    n_val = int(0.15 * len(model_zoo))
    n_test = len(model_zoo) - n_train - n_val

    train_zoo = model_zoo[:n_train]
    val_zoo = model_zoo[n_train:n_train+n_val]
    test_zoo = model_zoo[n_train+n_val:]

    logger.info(f"Data split: train={len(train_zoo)}, val={len(val_zoo)}, test={len(test_zoo)}")

    # Create data loaders
    train_dataset = WeightDataset(train_zoo)
    val_dataset = WeightDataset(val_zoo)
    test_dataset = WeightDataset(test_zoo)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size,
                              shuffle=True, collate_fn=collate_weights)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size,
                            shuffle=False, collate_fn=collate_weights)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size,
                             shuffle=False, collate_fn=collate_weights)

    # Initialize models
    models = {}
    training_results = {}

    # 1. SymVAE (Full)
    symvae_full = SymVAE(
        architecture=architecture,
        latent_dim=args.latent_dim,
        task_latent_dim=args.latent_dim // 2,
        arch_latent_dim=args.latent_dim // 2,
        hidden_dim=args.hidden_dim_gen,
        use_canonicalization=True,
        use_hierarchical=True
    )
    models['SymVAE_Full'] = symvae_full

    # 2. SymVAE (No Canonicalization)
    symvae_no_canon = SymVAE(
        architecture=architecture,
        latent_dim=args.latent_dim,
        task_latent_dim=args.latent_dim // 2,
        arch_latent_dim=args.latent_dim // 2,
        hidden_dim=args.hidden_dim_gen,
        use_canonicalization=False,
        use_hierarchical=True
    )
    models['SymVAE_NoCanon'] = symvae_no_canon

    # 3. SymVAE (No Hierarchical)
    symvae_no_hier = SymVAE(
        architecture=architecture,
        latent_dim=args.latent_dim,
        hidden_dim=args.hidden_dim_gen,
        use_canonicalization=True,
        use_hierarchical=False
    )
    models['SymVAE_NoHier'] = symvae_no_hier

    # 4. Vanilla VAE (Baseline)
    vanilla_vae = VanillaVAE(
        architecture=architecture,
        latent_dim=args.latent_dim,
        hidden_dim=args.hidden_dim_gen
    )
    models['Vanilla_VAE'] = vanilla_vae

    # 5. HyperNetwork (Baseline)
    hypernetwork = HyperNetwork(
        architecture=architecture,
        hidden_dim=args.hidden_dim_gen
    )
    models['HyperNetwork'] = hypernetwork

    # Train all models
    for model_name, model in models.items():
        start_time = time.time()
        results = train_model(
            model, model_name,
            train_loader, val_loader, device,
            n_epochs=args.n_epochs_gen,
            lr=args.lr,
            beta=args.beta,
            logger=logger
        )
        training_results[model_name] = results
        training_results[model_name]['training_time'] = time.time() - start_time

    # Evaluate all models
    logger.info("\n" + "=" * 60)
    logger.info("Evaluating models...")
    logger.info("=" * 60)

    evaluation_results = {}
    test_data = [test_dataset[i] for i in range(len(test_dataset))]

    for model_name, model in models.items():
        logger.info(f"Evaluating {model_name}...")
        model.eval()

        eval_result = {}

        # Generation quality
        gen_quality = evaluate_generation_quality(
            model, test_data, architecture, device, n_samples=3
        )
        eval_result.update(gen_quality)
        logger.info(f"  Generation quality: {gen_quality}")

        # Symmetry invariance (only for VAE models)
        if hasattr(model, 'encode'):
            sym_inv = evaluate_symmetry_invariance(model, test_data, device)
            eval_result.update(sym_inv)
            logger.info(f"  Symmetry invariance: {sym_inv}")

            # Interpolation smoothness
            interp = evaluate_interpolation_smoothness(model, test_data, architecture, device)
            eval_result.update(interp)
            logger.info(f"  Interpolation smoothness: {interp}")

        evaluation_results[model_name] = eval_result

    # Generate visualizations
    logger.info("\n" + "=" * 60)
    logger.info("Generating visualizations...")
    logger.info("=" * 60)

    figures_dir = output_dir

    # Training curves for each model
    for model_name, results in training_results.items():
        plot_training_curves(
            results['train_history'],
            results['val_history'],
            model_name,
            os.path.join(figures_dir, f'{model_name}_training_curves.png')
        )
        logger.info(f"Saved training curves for {model_name}")

    # Model comparison
    comparison_metrics = ['test_loss', 'test_accuracy'] if args.task_type == 'classification' else ['test_loss']
    plot_model_comparison(
        evaluation_results,
        comparison_metrics,
        'Model Comparison: Generation Quality',
        os.path.join(figures_dir, 'model_comparison.png')
    )
    logger.info("Saved model comparison plot")

    # Generation quality
    plot_generation_quality(
        evaluation_results,
        os.path.join(figures_dir, 'generation_quality.png'),
        task_type=args.task_type
    )
    logger.info("Saved generation quality plot")

    # Latent variance (symmetry invariance)
    vae_variance_results = {k: v for k, v in evaluation_results.items()
                           if 'latent_variance_mean' in v}
    if vae_variance_results:
        plot_latent_space_variance(
            vae_variance_results,
            os.path.join(figures_dir, 'latent_variance.png')
        )
        logger.info("Saved latent variance plot")

    # Interpolation smoothness
    interp_results = {k: v for k, v in evaluation_results.items()
                      if 'interpolation_smoothness_mean' in v}
    if interp_results:
        plot_interpolation_smoothness(
            interp_results,
            os.path.join(figures_dir, 'interpolation_smoothness.png')
        )
        logger.info("Saved interpolation smoothness plot")

    # Ablation study
    ablation_results = {
        'Full SymVAE': evaluation_results.get('SymVAE_Full', {}),
        'No Canonicalization': evaluation_results.get('SymVAE_NoCanon', {}),
        'No Hierarchical': evaluation_results.get('SymVAE_NoHier', {}),
        'Vanilla VAE': evaluation_results.get('Vanilla_VAE', {})
    }
    ablation_metrics = ['test_loss']
    if 'latent_variance_mean' in evaluation_results.get('SymVAE_Full', {}):
        ablation_metrics.append('latent_variance_mean')
    if 'interpolation_smoothness_mean' in evaluation_results.get('SymVAE_Full', {}):
        ablation_metrics.append('interpolation_smoothness_mean')

    plot_ablation_study(
        ablation_results,
        ablation_metrics,
        os.path.join(figures_dir, 'ablation_study.png')
    )
    logger.info("Saved ablation study plot")

    # Radar chart
    all_metrics = ['test_loss']
    if args.task_type == 'classification':
        all_metrics.append('test_accuracy')
    if 'latent_variance_mean' in evaluation_results.get('SymVAE_Full', {}):
        all_metrics.append('latent_variance_mean')
    if 'interpolation_smoothness_mean' in evaluation_results.get('SymVAE_Full', {}):
        all_metrics.append('interpolation_smoothness_mean')

    # Filter models that have all metrics
    radar_results = {}
    for model_name, results in evaluation_results.items():
        if all(m in results for m in all_metrics if not m.endswith('_std')):
            radar_results[model_name] = results

    if len(radar_results) >= 2:
        plot_radar_chart(
            radar_results,
            all_metrics,
            os.path.join(figures_dir, 'radar_comparison.png')
        )
        logger.info("Saved radar comparison plot")

    # Save results to JSON
    results_to_save = {
        'config': config,
        'training_results': {
            k: {
                'best_val_loss': v['best_val_loss'],
                'training_time': v['training_time']
            }
            for k, v in training_results.items()
        },
        'evaluation_results': evaluation_results
    }

    with open(os.path.join(figures_dir, 'results.json'), 'w') as f:
        json.dump(results_to_save, f, indent=2)
    logger.info("Saved results to results.json")

    # Create summary table
    summary_df = create_summary_table(evaluation_results, all_metrics)
    summary_df.to_csv(os.path.join(figures_dir, 'summary_table.csv'), index=False)
    logger.info("Saved summary table to summary_table.csv")

    logger.info("\n" + "=" * 60)
    logger.info("Experiment completed successfully!")
    logger.info("=" * 60)

    return results_to_save


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SymVAE Experiments')

    # Architecture
    parser.add_argument('--input_dim', type=int, default=10,
                        help='Input dimension of target networks')
    parser.add_argument('--hidden_dim', type=int, default=32,
                        help='Hidden dimension of target networks')
    parser.add_argument('--n_hidden_layers', type=int, default=2,
                        help='Number of hidden layers in target networks')
    parser.add_argument('--output_dim', type=int, default=2,
                        help='Output dimension of target networks')

    # Model zoo
    parser.add_argument('--n_models', type=int, default=100,
                        help='Number of models in the zoo')
    parser.add_argument('--n_epochs_zoo', type=int, default=50,
                        help='Epochs for training each model in zoo')

    # Weight generation models
    parser.add_argument('--n_epochs_gen', type=int, default=100,
                        help='Epochs for training weight generation models')
    parser.add_argument('--batch_size', type=int, default=16,
                        help='Batch size')
    parser.add_argument('--lr', type=float, default=1e-3,
                        help='Learning rate')
    parser.add_argument('--beta', type=float, default=0.1,
                        help='KL divergence weight')
    parser.add_argument('--latent_dim', type=int, default=64,
                        help='Latent dimension')
    parser.add_argument('--hidden_dim_gen', type=int, default=128,
                        help='Hidden dimension for generation models')

    # Task
    parser.add_argument('--task_type', type=str, default='classification',
                        choices=['classification', 'regression'],
                        help='Task type')

    # Misc
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed')

    args = parser.parse_args()
    run_experiments(args)
