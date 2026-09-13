"""Run standard SimCLR training for M1 baseline."""

import sys
from pathlib import Path
import torch
import numpy as np
from torch.utils.data import DataLoader

# Add h-e1 to path
h_e1_path = Path(__file__).parent.parent.parent / 'h-e1' / 'code'
sys.path.insert(0, str(h_e1_path))

from models.simclr import SimCLR
from data.dataset import WaterbirdsDataset, get_ssl_transforms
from training.ssl_trainer import SSLTrainer, DualAugmentationDataset
from config import SIMCLR_CONFIG, DATA_CONFIG, ENVIRONMENT_CONFIG


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def main():
    """Train standard SimCLR for M1 baseline."""
    print("=" * 60)
    print("SimCLR Baseline Training (M-3)")
    print("=" * 60)

    # Set device
    device = ENVIRONMENT_CONFIG['device']
    print(f"Using device: {device}")

    # Create output directories
    checkpoint_dir = Path(ENVIRONMENT_CONFIG['checkpoint_dir']) / 'simclr'
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Train for each seed
    for seed_idx, seed in enumerate(SIMCLR_CONFIG['seeds']):
        print(f"\n[Seed {seed_idx + 1}/{len(SIMCLR_CONFIG['seeds'])}] Seed: {seed}")
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

        # Create DataLoader
        train_loader = DataLoader(
            dual_dataset,
            batch_size=SIMCLR_CONFIG['batch_size'],
            shuffle=True,
            num_workers=DATA_CONFIG['num_workers'],
            pin_memory=True
        )

        print(f"Train samples: {len(train_dataset)}")

        # Initialize model
        print("Initializing SimCLR model...")
        model = SimCLR(
            encoder_name=SIMCLR_CONFIG['encoder_name'],
            projection_dim=SIMCLR_CONFIG['projection_dim'],
            pretrained=SIMCLR_CONFIG['pretrained']
        )

        # Initialize trainer
        trainer = SSLTrainer(
            model=model,
            train_loader=train_loader,
            device=device,
            checkpoint_dir=str(checkpoint_dir / f'seed_{seed}'),
            lr=SIMCLR_CONFIG['lr'],
            weight_decay=SIMCLR_CONFIG['weight_decay'],
            temperature=SIMCLR_CONFIG['temperature'],
            momentum=SIMCLR_CONFIG['momentum']
        )

        # Train
        print(f"Training for {SIMCLR_CONFIG['epochs']} epochs...")
        trainer.train(
            num_epochs=SIMCLR_CONFIG['epochs'],
            save_freq=SIMCLR_CONFIG['checkpoint_freq']
        )

        print(f"\n✓ Seed {seed} complete!")

    print("\n" + "=" * 60)
    print("SimCLR Baseline Training Complete!")
    print(f"Checkpoints saved to: {checkpoint_dir}")
    print("=" * 60)


if __name__ == '__main__':
    main()
