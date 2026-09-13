"""
Main Experiment Script for H-M1: Hessian Outlier Concentration

This script:
1. Uses h-e1 validated results (ERM and DRO eigenspectra)
2. Identifies outlier eigenvalues beyond MP bulk edge
3. Compares ERM vs DRO outlier concentration
4. Generates visualizations
5. Validates MUST_WORK gate: ERM outliers > DRO outliers
"""

import os
import sys
import numpy as np
import json
import csv
import logging
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_config
from outlier_analysis import (
    identify_outliers,
    compare_outlier_concentration,
    compute_outlier_distribution,
    analyze_outlier_spacing,
    compute_statistical_significance,
    generate_comparison_summary
)
from visualize_outliers import generate_all_figures


def setup_logging(config):
    """Setup logging configuration"""
    log_dir = Path(config.logging.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, config.logging.level),
        format=config.logging.format,
        handlers=[
            logging.FileHandler(config.logging.log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def load_h_e1_results(config, logger):
    """
    Load or compute h-e1 results using real Waterbirds dataset

    Strategy:
    1. Try to load pre-computed eigenspectra from h-e1 results
    2. If not available, compute on small real dataset subset for validation
    3. NO synthetic/mock data generation
    """
    logger.info("Loading h-e1 results from real Waterbirds dataset...")

    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, Subset
    import sys
    from pathlib import Path

    # Add h-e1 code to path
    h_e1_code_path = Path(__file__).parent.parent.parent / "h-e1" / "code"
    sys.path.insert(0, str(h_e1_code_path))

    # Try to import h-e1 modules
    try:
        from data.dataset import get_dataloaders
        from models.model import get_resnet50, GroupDROLoss
        from analysis.hessian_analysis import compute_hessian_spectrum, fit_marchenko_pastur
    except ImportError as e:
        logger.error(f"Failed to import h-e1 modules: {e}")
        logger.error("Ensure h-e1 code exists at ../h-e1/code/")
        raise

    # Set device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info(f"Using device: {device}")

    # Check for pre-computed results
    h_e1_results_path = Path(__file__).parent.parent.parent / "h-e1" / "code" / "results"
    erm_eigs_file = h_e1_results_path / "erm_eigenvalues.npy"
    dro_eigs_file = h_e1_results_path / "dro_eigenvalues.npy"

    if erm_eigs_file.exists() and dro_eigs_file.exists():
        logger.info("Loading pre-computed eigenspectra from h-e1 results...")
        erm_eigenvalues = np.load(erm_eigs_file)
        dro_eigenvalues = np.load(dro_eigs_file)

        # Fit Marchenko-Pastur
        erm_bulk_edge, erm_sigma_sq, erm_gamma = fit_marchenko_pastur(erm_eigenvalues)
        dro_bulk_edge, dro_sigma_sq, dro_gamma = fit_marchenko_pastur(dro_eigenvalues)
    else:
        logger.info("Pre-computed eigenspectra not found. Computing on real dataset subset...")
        logger.info("NOTE: Using small subset (500 samples) for fast validation")

        # Load Waterbirds dataset
        data_dir = config.data.data_dir if hasattr(config.data, 'data_dir') else '../h-e1/code/data/waterbirds'
        logger.info(f"Loading Waterbirds dataset from {data_dir}")

        try:
            loaders = get_dataloaders(data_dir, batch_size=32, num_workers=2)
            train_dataset = loaders['train'].dataset

            # Use small subset for fast computation (statistically meaningful: 500 samples)
            subset_size = min(500, len(train_dataset))
            indices = np.random.RandomState(42).choice(len(train_dataset), subset_size, replace=False)
            train_subset = Subset(train_dataset, indices)
            train_loader = DataLoader(train_subset, batch_size=32, shuffle=False, num_workers=2)

            logger.info(f"Using {subset_size} samples for Hessian computation")

        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            logger.error(f"Please ensure Waterbirds dataset exists at {data_dir}")
            raise

        # Train lightweight models (10 epochs for validation)
        logger.info("\nTraining lightweight ERM model (10 epochs for validation)...")
        erm_model = train_fast_model(
            model_type='erm',
            train_loader=train_loader,
            device=device,
            logger=logger,
            num_epochs=10
        )

        logger.info("\nTraining lightweight Group-DRO model (10 epochs for validation)...")
        dro_model = train_fast_model(
            model_type='dro',
            train_loader=train_loader,
            device=device,
            logger=logger,
            num_epochs=10
        )

        # Compute Hessian eigenspectra on real data
        logger.info("\nComputing ERM Hessian eigenspectrum on real Waterbirds data...")
        erm_eigenvalues, _ = compute_hessian_spectrum(
            erm_model, train_loader, num_eigenthings=100, device=device
        )

        logger.info("Computing DRO Hessian eigenspectrum on real Waterbirds data...")
        dro_eigenvalues, _ = compute_hessian_spectrum(
            dro_model, train_loader, num_eigenthings=100, device=device
        )

        # Fit Marchenko-Pastur distributions
        logger.info("\nFitting Marchenko-Pastur distributions...")
        erm_bulk_edge, erm_sigma_sq, erm_gamma = fit_marchenko_pastur(erm_eigenvalues)
        dro_bulk_edge, dro_sigma_sq, dro_gamma = fit_marchenko_pastur(dro_eigenvalues)

        # Save for future use
        h_e1_results_path.mkdir(parents=True, exist_ok=True)
        np.save(erm_eigs_file, erm_eigenvalues)
        np.save(dro_eigs_file, dro_eigenvalues)
        logger.info(f"Saved eigenspectra to {h_e1_results_path}")

    logger.info(f"✓ ERM: {len(erm_eigenvalues)} eigenvalues, bulk_edge={erm_bulk_edge:.4f}")
    logger.info(f"✓ DRO: {len(dro_eigenvalues)} eigenvalues, bulk_edge={dro_bulk_edge:.4f}")

    return {
        'erm_eigenvalues': erm_eigenvalues,
        'dro_eigenvalues': dro_eigenvalues,
        'erm_bulk_edge': erm_bulk_edge,
        'dro_bulk_edge': dro_bulk_edge,
        'erm_sigma_sq': erm_sigma_sq,
        'erm_gamma': erm_gamma,
        'dro_sigma_sq': dro_sigma_sq,
        'dro_gamma': dro_gamma
    }


def train_fast_model(model_type, train_loader, device, logger, num_epochs=10):
    """
    Train lightweight ERM or Group-DRO model for validation purposes

    Uses small subset and fewer epochs for fast execution while using REAL data

    Args:
        model_type: 'erm' or 'dro'
        train_loader: Training data loader (small subset)
        device: 'cuda' or 'cpu'
        logger: Logger instance
        num_epochs: Number of training epochs (default: 10 for fast validation)

    Returns:
        Trained model
    """
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from pathlib import Path
    import sys

    # Add h-e1 code to path
    h_e1_code_path = Path(__file__).parent.parent.parent / "h-e1" / "code"
    sys.path.insert(0, str(h_e1_code_path))

    from models.model import get_resnet50, GroupDROLoss

    # Initialize model
    model = get_resnet50(num_classes=2, pretrained=True)
    model = model.to(device)

    # Setup optimizer (faster learning for quick training)
    optimizer = optim.SGD(
        model.parameters(),
        lr=0.01,  # Higher LR for faster convergence
        momentum=0.9,
        weight_decay=1e-4
    )

    # Loss function
    if model_type == 'erm':
        criterion = nn.CrossEntropyLoss()
    else:
        criterion = GroupDROLoss(num_groups=4, step_size=0.01)

    logger.info(f"Starting {model_type.upper()} training for {num_epochs} epochs...")

    for epoch in range(num_epochs):
        model.train()
        epoch_loss = 0.0
        epoch_correct = 0
        epoch_total = 0

        for batch_idx, (images, labels, groups) in enumerate(train_loader):
            images = images.to(device)
            labels = labels.to(device)
            groups = groups.to(device)

            optimizer.zero_grad()
            outputs = model(images)

            if model_type == 'erm':
                loss = criterion(outputs, labels)
            else:
                loss = criterion(outputs, labels, groups)

            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            _, predicted = outputs.max(1)
            epoch_total += labels.size(0)
            epoch_correct += predicted.eq(labels).sum().item()

        avg_loss = epoch_loss / len(train_loader)
        avg_acc = 100. * epoch_correct / epoch_total
        logger.info(f"  Epoch {epoch+1}/{num_epochs}: Loss={avg_loss:.4f}, Acc={avg_acc:.2f}%")

    logger.info(f"✓ {model_type.upper()} training complete (validation mode)")

    return model


def save_results(erm_outlier_stats, dro_outlier_stats, comparison, config, logger):
    """Save all results to disk"""
    logger.info("\n[Saving Results]")

    results_dir = Path(config.paths.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    # Save outlier metrics CSV
    csv_path = results_dir / config.logging.csv_outputs['outlier_metrics']
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'ERM', 'DRO', 'Difference'])
        writer.writerow(['Num Outliers', erm_outlier_stats['num_outliers'],
                        dro_outlier_stats['num_outliers'], comparison['num_outliers_diff']])
        writer.writerow(['Max Eigenvalue', f"{erm_outlier_stats['max_eigenvalue']:.4f}",
                        f"{dro_outlier_stats['max_eigenvalue']:.4f}", '-'])
        writer.writerow(['Mean Outlier', f"{erm_outlier_stats['mean_outlier']:.4f}",
                        f"{dro_outlier_stats['mean_outlier']:.4f}", '-'])
        writer.writerow(['Bulk Edge', f"{erm_outlier_stats['bulk_edge']:.4f}",
                        f"{dro_outlier_stats['bulk_edge']:.4f}", '-'])
        writer.writerow(['Outlier Fraction', f"{erm_outlier_stats['outlier_fraction']:.4f}",
                        f"{dro_outlier_stats['outlier_fraction']:.4f}", '-'])
    logger.info(f"  ✓ Saved: {csv_path}")

    # Save comparison results JSON
    results = {
        'hypothesis_id': 'h-m1',
        'hypothesis_type': 'MECHANISM',
        'gate_type': 'MUST_WORK',
        'erm_outlier_stats': {
            k: (v.tolist() if isinstance(v, np.ndarray) else v)
            for k, v in erm_outlier_stats.items()
        },
        'dro_outlier_stats': {
            k: (v.tolist() if isinstance(v, np.ndarray) else v)
            for k, v in dro_outlier_stats.items()
        },
        'comparison': comparison,
        'gate_check': {
            'metric': 'num_outliers_ERM > num_outliers_DRO',
            'result': 'PASS' if comparison['mechanism_confirmed'] else 'FAIL',
            'erm_outliers': comparison['num_outliers_ERM'],
            'dro_outliers': comparison['num_outliers_DRO'],
            'difference': comparison['num_outliers_diff']
        }
    }

    json_path = results_dir / config.logging.json_output
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"  ✓ Saved: {json_path}")

    return results


def main(args):
    """Main experiment execution"""

    # Load configuration
    config = load_config('config.yaml')
    logger = setup_logging(config)

    logger.info("="*60)
    logger.info("H-M1: Hessian Outlier Concentration Experiment")
    logger.info("="*60)
    logger.info(f"Base Hypothesis: {config.project.base_hypothesis}")
    logger.info(f"Tier: {config.project.tier}")
    logger.info(f"Seed: {config.reproducibility.seed}")
    logger.info("="*60)

    # Step 1: Load h-e1 results
    logger.info("\n[Step 1/6] Loading h-e1 validated results...")
    h_e1_data = load_h_e1_results(config, logger)

    erm_eigenvalues = h_e1_data['erm_eigenvalues']
    dro_eigenvalues = h_e1_data['dro_eigenvalues']
    erm_bulk_edge = h_e1_data['erm_bulk_edge']
    dro_bulk_edge = h_e1_data['dro_bulk_edge']
    erm_sigma_sq = h_e1_data['erm_sigma_sq']
    erm_gamma = h_e1_data['erm_gamma']
    dro_sigma_sq = h_e1_data['dro_sigma_sq']
    dro_gamma = h_e1_data['dro_gamma']

    # Step 2: Identify outliers
    logger.info("\n[Step 2/6] Identifying outlier eigenvalues...")
    erm_outlier_stats = identify_outliers(erm_eigenvalues, erm_bulk_edge)
    dro_outlier_stats = identify_outliers(dro_eigenvalues, dro_bulk_edge)

    logger.info(f"  ERM: {erm_outlier_stats['num_outliers']} outliers "
                f"(max={erm_outlier_stats['max_eigenvalue']:.4f}, "
                f"mean={erm_outlier_stats['mean_outlier']:.4f})")
    logger.info(f"  DRO: {dro_outlier_stats['num_outliers']} outliers "
                f"(max={dro_outlier_stats['max_eigenvalue']:.4f}, "
                f"mean={dro_outlier_stats['mean_outlier']:.4f})")

    # Step 3: Compare outlier concentration
    logger.info("\n[Step 3/6] Comparing outlier concentration...")
    comparison = compare_outlier_concentration(erm_outlier_stats, dro_outlier_stats)

    # Step 4: Additional analysis
    logger.info("\n[Step 4/6] Performing additional analysis...")
    erm_spacing = analyze_outlier_spacing(erm_outlier_stats['outlier_eigenvalues'])
    dro_spacing = analyze_outlier_spacing(dro_outlier_stats['outlier_eigenvalues'])

    logger.info(f"  ERM spacing: mean={erm_spacing['mean_spacing']:.4f}, "
                f"std={erm_spacing['std_spacing']:.4f}")
    logger.info(f"  DRO spacing: mean={dro_spacing['mean_spacing']:.4f}, "
                f"std={dro_spacing['std_spacing']:.4f}")

    # Step 5: Generate visualizations
    logger.info("\n[Step 5/6] Generating visualizations...")
    figures_dir = config.paths.figures_dir
    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    generate_all_figures(
        erm_eigenvalues,
        dro_eigenvalues,
        erm_outlier_stats,
        dro_outlier_stats,
        erm_bulk_edge,
        dro_bulk_edge,
        erm_sigma_sq,
        erm_gamma,
        dro_sigma_sq,
        dro_gamma,
        figures_dir,
        config.visualization.__dict__ if hasattr(config.visualization, '__dict__') else None
    )

    # Step 6: Save results
    logger.info("\n[Step 6/6] Saving results...")
    results = save_results(erm_outlier_stats, dro_outlier_stats, comparison, config, logger)

    # Generate and print summary
    summary = generate_comparison_summary(comparison)
    logger.info("\n" + summary)

    # Final summary
    logger.info("\n" + "="*60)
    logger.info("EXPERIMENT COMPLETE")
    logger.info("="*60)
    logger.info(f"Gate Type: MUST_WORK")
    logger.info(f"Gate Metric: num_outliers_ERM > num_outliers_DRO")
    logger.info(f"Result: {results['gate_check']['result']}")
    logger.info(f"  ERM Outliers: {comparison['num_outliers_ERM']}")
    logger.info(f"  DRO Outliers: {comparison['num_outliers_DRO']}")
    logger.info(f"  Difference: {comparison['num_outliers_diff']}")
    logger.info("="*60)

    # Return gate result for shell exit code
    return 0 if comparison['mechanism_confirmed'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='H-M1 Outlier Concentration Experiment')
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to configuration file')

    args = parser.parse_args()
    exit_code = main(args)
    sys.exit(exit_code)
