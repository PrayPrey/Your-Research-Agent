from .waterbirds import WaterbirdsDataset, get_waterbirds_loader
from .celeba import CelebADataset, get_celeba_loader

__all__ = [
    "WaterbirdsDataset", "get_waterbirds_loader",
    "CelebADataset", "get_celeba_loader",
]
