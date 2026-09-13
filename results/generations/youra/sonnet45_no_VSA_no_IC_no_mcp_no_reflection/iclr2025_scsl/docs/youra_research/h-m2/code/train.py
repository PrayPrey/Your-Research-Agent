"""
Training orchestration for h-m2: Multi-architecture ablation experiments.
"""

from dataclasses import dataclass
import torch
from typing import Literal
from model import create_model, AblationTrainer


@dataclass
class ArchitectureConfig:
    """Configuration for one architecture experiment."""
    arch_name: Literal['resnet50', 'vit_b16']
    lr: float
    weight_decay: float
    batch_size: int
    max_epochs: int = 30
    seed: int = 0


def run_architecture_experiment(
    config: ArchitectureConfig,
    train_loader,
    device: str = 'cuda'
) -> dict:
    """
    Run ablation training for one architecture on one seed.

    Args:
        config: Architecture-specific hyperparameters
        train_loader: DataLoader with (images, labels)
        device: 'cuda' or 'cpu'

    Returns:
        {
            'arch_name': str,
            'seed': int,
            'E_spurious': int | None,
            'E_core': int | None,
            'delta': float | None
        }
    """
    # Set seed
    torch.manual_seed(config.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(config.seed)

    print(f"\n=== Training {config.arch_name} (seed {config.seed}) ===")

    # Create spurious-only model
    print("\n--- Spurious-only variant ---")
    model_spurious = create_model(config.arch_name, num_classes=2)
    trainer_spurious = AblationTrainer(
        model_spurious, 'Waterbirds', config.lr, config.weight_decay, device
    )
    E_spurious = trainer_spurious.train_variant('spurious', train_loader, config.max_epochs)

    # Create core-only model
    print("\n--- Core-only variant ---")
    model_core = create_model(config.arch_name, num_classes=2)
    trainer_core = AblationTrainer(
        model_core, 'Waterbirds', config.lr, config.weight_decay, device
    )
    E_core = trainer_core.train_variant('core', train_loader, config.max_epochs)

    # Compute temporal gap
    delta = (E_core - E_spurious) if (E_spurious and E_core) else None

    result = {
        'arch_name': config.arch_name,
        'seed': config.seed,
        'E_spurious': E_spurious,
        'E_core': E_core,
        'delta': delta
    }

    print(f"\nResults: E_spurious={E_spurious}, E_core={E_core}, Δ={delta}")

    return result
