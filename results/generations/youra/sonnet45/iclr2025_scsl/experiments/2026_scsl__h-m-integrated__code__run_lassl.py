"""Run LA-SSL training with learning-speed aware sampling."""

import sys
import os
from pathlib import Path
import torch
import numpy as np
from torch.utils.data import DataLoader

# Setup paths - add h-e1 first, then current directory
current_dir = Path(__file__).parent.absolute()
h_e1_path = (current_dir.parent.parent / 'h-e1' / 'code').absolute()

# Change to current directory for relative imports
os.chdir(current_dir)

# Add h-e1 to path FIRST
sys.path.insert(0, str(h_e1_path))

# Now import from h-e1
from models.simclr import SimCLR
from data.dataset import WaterbirdsDataset, get_ssl_transforms
from training.ssl_trainer import DualAugmentationDataset

# Add current directory for local imports
sys.path.insert(0, str(current_dir))

# Import local modules using direct file execution
import importlib.util

# Load LASSLTrainer
trainer_spec = importlib.util.spec_from_file_location(
    "training.lassl_trainer",
    current_dir / "training" / "lassl_trainer.py"
)
trainer_module = importlib.util.module_from_spec(trainer_spec)
trainer_spec.loader.exec_module(trainer_module)
LASSLTrainer = trainer_module.LASSLTrainer

# Load LASSLSampler
sampler_spec = importlib.util.spec_from_file_location(
    "models.lassl_sampler",
    current_dir / "models" / "lassl_sampler.py"
)
sampler_module = importlib.util.module_from_spec(sampler_spec)
sampler_spec.loader.exec_module(sampler_module)
LASSLSampler = sampler_module.LASSLSampler

# Load config
config_spec = importlib.util.spec_from_file_location(
    "config",
    current_dir / "config.py"
)
config_module = importlib.util.module_from_spec(config_spec)
config_spec.loader.exec_module(config_module)
LASSL_CONFIG = config_module.LASSL_CONFIG
DATA_CONFIG = config_module.DATA_CONFIG
ENVIRONMENT_CONFIG = config_module.ENVIRONMENT_CONFIG


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def main():
    """Train LA-SSL with learning-speed aware sampling."""
    print("=" * 60)
    print("LA-SSL Training (M-4)")
    print("=" * 60)

    # Set device
    device = ENVIRONMENT_CONFIG['device']
    print(f"Using device: {device}")

    # Create output directories
    checkpoint_dir = Path(ENVIRONMENT_CONFIG['checkpoint_dir']) / 'lassl'
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Train for each seed
    for seed_idx, seed in enumerate(LASSL_CONFIG['seeds']):
        print(f"\n[Seed {seed_idx + 1}/{len(LASSL_CONFIG['seeds'])}] Seed: {seed}")
        print("-" * 60)

        # Set seed
        set_seed(seed)

        # Load dataset
        print("Loading Waterbirds dataset...")
        root_dir = DATA_CONFIG['root_dir']
        ssl_transform = get_ssl_transforms()

        train_dataset = WaterbirdsDataset(
            root_dir=root_dir,
            split='train',
            transform=None  # DualAugmentationDataset will handle transforms
        )

        # Wrap with dual augmentation
        dual_dataset = DualAugmentationDataset(train_dataset, ssl_transform)

        print(f"Train samples: {len(train_dataset)}")

        # Initialize LA-SSL sampler
        print("Initializing LA-SSL sampler...")
        sampler = LASSLSampler(
            dataset_size=len(dual_dataset),
            alpha=LASSL_CONFIG['sampler_alpha'],
            window_size=LASSL_CONFIG['sampler_window']
        )

        # Create DataLoader with LA-SSL sampler
        train_loader = DataLoader(
            dual_dataset,
            batch_size=LASSL_CONFIG['batch_size'],
            sampler=sampler,
            num_workers=DATA_CONFIG['num_workers'],
            pin_memory=True
        )

        # Initialize model (same architecture as SimCLR)
        print("Initializing SimCLR model...")
        model = SimCLR(
            encoder_name=LASSL_CONFIG['encoder_name'],
            projection_dim=LASSL_CONFIG['projection_dim'],
            pretrained=LASSL_CONFIG['pretrained']
        )

        # Initialize LA-SSL trainer
        trainer = LASSLTrainer(
            model=model,
            train_loader=train_loader,
            sampler=sampler,
            device=device,
            checkpoint_dir=str(checkpoint_dir / f'seed_{seed}'),
            lr=LASSL_CONFIG['lr'],
            weight_decay=LASSL_CONFIG['weight_decay'],
            temperature=LASSL_CONFIG['temperature'],
            momentum=LASSL_CONFIG['momentum']
        )

        # Train
        print(f"Training for {LASSL_CONFIG['epochs']} epochs...")
        trainer.train(
            num_epochs=LASSL_CONFIG['epochs'],
            save_freq=LASSL_CONFIG['checkpoint_freq']
        )

        print(f"\n✓ Seed {seed} complete!")

    print("\n" + "=" * 60)
    print("LA-SSL Training Complete!")
    print(f"Checkpoints saved to: {checkpoint_dir}")
    print("=" * 60)


if __name__ == '__main__':
    main()
