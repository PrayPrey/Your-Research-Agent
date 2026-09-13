"""
Training orchestration for h-e1: Multi-seed experiment runner.
"""

from dataclasses import dataclass
import torch
from data import DatasetConfig, get_dataloader
from model_v2 import get_baseline_model, AblationTrainer  # v2: accuracy-based convergence


@dataclass
class TrainConfig:
    dataset: str
    lr: float
    max_epochs: int
    weight_decay: float
    batch_size: int
    seed: int


# Dataset-specific hyperparameters from PRD
# Note: max_epochs reduced to 20 for PoC validation (faster iteration)
DATASET_CONFIGS = {
    'CMNIST': {
        'lr': 0.001,
        'batch_size': 128,
        'max_epochs': 20,  # Reduced for PoC
        'weight_decay': 1e-4
    },
    'Waterbirds': {
        'lr': 0.001,
        'batch_size': 64,
        'max_epochs': 100,
        'weight_decay': 1e-4
    },
    'CelebA': {
        'lr': 0.0001,
        'batch_size': 64,
        'max_epochs': 80,
        'weight_decay': 1e-4
    },
    'NICO++': {
        'lr': 0.001,
        'batch_size': 64,
        'max_epochs': 100,
        'weight_decay': 1e-4
    }
}


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def run_single_experiment(config: TrainConfig) -> dict:
    """
    Run ablation training for one seed on one dataset.

    Returns:
        {
            'dataset': str,
            'seed': int,
            'E_spurious': int | None,
            'E_core': int | None,
            'E_baseline': int | None,
            'delta': float | None  # E_core - E_spurious if both converged
        }
    """
    set_seed(config.seed)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    print(f"\n{'='*60}")
    print(f"Running {config.dataset} | Seed {config.seed}")
    print(f"{'='*60}")

    # Load data
    dataset_config = DatasetConfig(
        name=config.dataset,
        batch_size=config.batch_size
    )
    train_loader = get_dataloader(dataset_config, split='train')

    results = {
        'dataset': config.dataset,
        'seed': config.seed,
        'E_spurious': None,
        'E_core': None,
        'E_baseline': None,
        'delta': None
    }

    # Train spurious-only variant
    print("\n[Spurious-only variant]")
    model_spurious = get_baseline_model(config.dataset, pretrained=False)  # No pretraining for PoC
    trainer_spurious = AblationTrainer(
        model_spurious,
        config.dataset,
        config.lr,
        config.weight_decay,
        device
    )
    E_spurious = trainer_spurious.train_variant('spurious', train_loader, config.max_epochs)
    results['E_spurious'] = E_spurious
    print(f"  Converged at epoch: {E_spurious if E_spurious else 'NO CONVERGENCE'}")

    # Train core-only variant
    print("\n[Core-only variant]")
    model_core = get_baseline_model(config.dataset, pretrained=False)  # No pretraining for PoC
    trainer_core = AblationTrainer(
        model_core,
        config.dataset,
        config.lr,
        config.weight_decay,
        device
    )
    E_core = trainer_core.train_variant('core', train_loader, config.max_epochs)
    results['E_core'] = E_core
    print(f"  Converged at epoch: {E_core if E_core else 'NO CONVERGENCE'}")

    # Train baseline variant
    print("\n[Baseline variant]")
    model_baseline = get_baseline_model(config.dataset, pretrained=False)  # No pretraining for PoC
    trainer_baseline = AblationTrainer(
        model_baseline,
        config.dataset,
        config.lr,
        config.weight_decay,
        device
    )
    E_baseline = trainer_baseline.train_variant('baseline', train_loader, config.max_epochs)
    results['E_baseline'] = E_baseline
    print(f"  Converged at epoch: {E_baseline if E_baseline else 'NO CONVERGENCE'}")

    # Compute temporal gap
    if E_spurious is not None and E_core is not None:
        results['delta'] = E_core - E_spurious
        print(f"\n  Temporal gap (Δ = E_core - E_spurious): {results['delta']:.1f} epochs")
    else:
        print(f"\n  Temporal gap: Cannot compute (missing convergence)")

    return results


def run_all_seeds(dataset: str, num_seeds: int = 10) -> list[dict]:
    """
    Run ablation experiments for all seeds on one dataset.

    Returns list of results dicts (one per seed).
    """
    if dataset not in DATASET_CONFIGS:
        raise ValueError(f"Unknown dataset: {dataset}")

    base_config = DATASET_CONFIGS[dataset]
    all_results = []

    for seed in range(num_seeds):
        config = TrainConfig(
            dataset=dataset,
            lr=base_config['lr'],
            max_epochs=base_config['max_epochs'],
            weight_decay=base_config['weight_decay'],
            batch_size=base_config['batch_size'],
            seed=seed
        )

        try:
            result = run_single_experiment(config)
            all_results.append(result)
        except Exception as e:
            print(f"\n[ERROR] Seed {seed} failed: {e}")
            # Record failed run
            all_results.append({
                'dataset': dataset,
                'seed': seed,
                'E_spurious': None,
                'E_core': None,
                'E_baseline': None,
                'delta': None
            })

    return all_results


if __name__ == '__main__':
    # Quick test on CMNIST with 1 seed
    print("Testing data loading and training pipeline...")
    results = run_all_seeds('CMNIST', num_seeds=1)
    print("\n" + "="*60)
    print("Test complete. Results:")
    print(results)
