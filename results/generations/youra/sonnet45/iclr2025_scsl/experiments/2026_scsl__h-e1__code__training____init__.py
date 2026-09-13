"""Training modules for SSL and linear probing."""

from .ssl_trainer import SSLTrainer, DualAugmentationDataset

__all__ = [
    'SSLTrainer',
    'DualAugmentationDataset',
]
