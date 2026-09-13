"""Main training script for h-c1 gradient-aware experiment."""

import torch
import torch.nn as nn
import torch.optim as optim
import yaml
import numpy as np
from pathlib import Path
import sys

# Add code directory to path
sys.path.append(str(Path(__file__).parent))

from data.waterbirds_loader import get_waterbirds_loader
from models.resnet import get_resnet50
from optimizers.gradient_aware import GradientAwareOptimizer
from training.trainer import Trainer
from training.evaluator import evaluate_model
from utils.rho_loader import load_rho_j_from_h_m1, map_rho_j_to_resnet50_params


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.backends.cudnn.deterministic = True


def train_erm(config: dict, seed: int) -> dict:
    """Train ERM baseline."""
    print(f"\n=== ERM Training (seed={seed}) ===")
    set_seed(seed)

    # Data
    train_loader = get_waterbirds_loader(
        config['data']['data_root'], 'train',
        config['data']['batch_size'], config['data']['num_workers']
    )
    val_loader = get_waterbirds_loader(
        config['data']['data_root'], 'val',
        config['data']['batch_size'], config['data']['num_workers']
    )
    test_loader = get_waterbirds_loader(
        config['data']['data_root'], 'test',
        config['data']['batch_size'], config['data']['num_workers']
    )

    # Model
    model = get_resnet50(
        num_classes=config['model']['num_classes'],
        pretrained=config['model']['pretrained']
    )

    # Optimizer
    optimizer = optim.SGD(
        model.parameters(),
        lr=config['optimizer']['lr'],
        momentum=config['optimizer']['momentum'],
        weight_decay=config['optimizer']['weight_decay']
    )

    # Train
    device = config['reproducibility']['device']
    checkpoint_dir = Path(config['output']['checkpoint_folder']) / f'erm_seed{seed}'

    trainer = Trainer(model, optimizer, train_loader, val_loader, device, checkpoint_dir)
    history = trainer.run(config['training']['epochs'])

    # Test evaluation
    model.load_state_dict(torch.load(checkpoint_dir / 'best_model.pt'))
    test_metrics = evaluate_model(model, test_loader, device)

    print(f"ERM Test WG-Acc: {test_metrics['worst_group_acc']:.2f}%")

    return {
        'history': history,
        'test_metrics': test_metrics
    }


def train_gradient_aware(config: dict, seed: int) -> dict:
    """Train Gradient-Aware method."""
    print(f"\n=== Gradient-Aware Training (seed={seed}) ===")
    set_seed(seed)

    # Data
    train_loader = get_waterbirds_loader(
        config['data']['data_root'], 'train',
        config['data']['batch_size'], config['data']['num_workers']
    )
    val_loader = get_waterbirds_loader(
        config['data']['data_root'], 'val',
        config['data']['batch_size'], config['data']['num_workers']
    )
    test_loader = get_waterbirds_loader(
        config['data']['data_root'], 'test',
        config['data']['batch_size'], config['data']['num_workers']
    )

    # Model
    model = get_resnet50(
        num_classes=config['model']['num_classes'],
        pretrained=config['model']['pretrained']
    )

    # Load ρ_j
    rho_j_dict = load_rho_j_from_h_m1(config)
    param_rho = map_rho_j_to_resnet50_params(rho_j_dict, model)

    # Gradient-aware optimizer
    optimizer = GradientAwareOptimizer(
        model.named_parameters(),
        optim.SGD,
        param_rho,
        base_lr=config['optimizer']['lr'],
        lr_floor=config['training']['lr_floor'],
        momentum=config['optimizer']['momentum'],
        weight_decay=config['optimizer']['weight_decay']
    )

    # Train
    device = config['reproducibility']['device']
    checkpoint_dir = Path(config['output']['checkpoint_folder']) / f'ga_seed{seed}'

    trainer = Trainer(model, optimizer, train_loader, val_loader, device, checkpoint_dir)
    history = trainer.run(config['training']['epochs'])

    # Test evaluation
    model.load_state_dict(torch.load(checkpoint_dir / 'best_model.pt'))
    test_metrics = evaluate_model(model, test_loader, device)

    print(f"GA Test WG-Acc: {test_metrics['worst_group_acc']:.2f}%")

    return {
        'history': history,
        'test_metrics': test_metrics,
        'rho_j_dict': rho_j_dict
    }


def main():
    """Run h-c1 experiment."""
    # Load config
    config_path = Path(__file__).parent.parent / 'config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    print(f"Config loaded from {config_path}")

    # Run experiments across seeds
    seeds = config['reproducibility']['seeds']
    erm_results = []
    ga_results = []

    for seed in seeds:
        erm_res = train_erm(config, seed)
        erm_results.append(erm_res['test_metrics']['worst_group_acc'])

        ga_res = train_gradient_aware(config, seed)
        ga_results.append(ga_res['test_metrics']['worst_group_acc'])

    # Statistical test
    from scipy.stats import ttest_rel

    erm_arr = np.array(erm_results)
    ga_arr = np.array(ga_results)

    print(f"\n=== Results Summary ===")
    print(f"ERM WG-Acc: {erm_arr.mean():.2f} ± {erm_arr.std():.2f}%")
    print(f"GA WG-Acc: {ga_arr.mean():.2f} ± {ga_arr.std():.2f}%")

    # Paired t-test
    t_stat, p_value = ttest_rel(ga_arr, erm_arr)
    print(f"Paired t-test: t={t_stat:.3f}, p={p_value:.4f}")

    # Save results
    results_dir = Path(config['output']['output_folder']) / 'results'
    results_dir.mkdir(exist_ok=True, parents=True)

    np.save(results_dir / 'erm_wg_acc.npy', erm_arr)
    np.save(results_dir / 'ga_wg_acc.npy', ga_arr)

    print(f"Results saved to {results_dir}")


if __name__ == '__main__':
    main()
