"""Dataset loading for H-E1 using WILDS library.

Waterbirds and CelebA via wilds, yielding (x, y, group_id) per batch.
group_id = y_label * 2 + confounder.

Waterbirds groups:
    0: landbird+land (majority)
    1: landbird+water (minority)
    2: waterbird+land (minority)
    3: waterbird+water (majority)
minority_group_ids = {1, 2}

CelebA groups (metadata_fields=['male','y',...]):
    0: non-blond+female
    1: non-blond+male
    2: blond+female
    3: blond+male (minority, ~1387)
minority_group_ids = {3}
"""

from __future__ import annotations
import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset, Subset
import torchvision.transforms as T
import wilds

from config import DatasetConfig


_IMAGENET_MEAN = [0.485, 0.456, 0.406]
_IMAGENET_STD  = [0.229, 0.224, 0.225]


def _get_transforms(train: bool):
    base = [T.Resize(256), T.CenterCrop(224), T.ToTensor(),
            T.Normalize(_IMAGENET_MEAN, _IMAGENET_STD)]
    if train:
        base.insert(2, T.RandomHorizontalFlip())
    return T.Compose(base)


class _GroupedSubset(Dataset):
    """Wraps a WILDS subset, returning (x, y, group_id) where group_id is computed
    from the dataset's metadata array."""

    def __init__(self, wilds_dataset, split_name: str, transform):
        self._d = wilds_dataset
        self._subset = wilds_dataset.get_subset(split_name, transform=transform)
        self._indices = self._subset.indices

        meta = wilds_dataset.metadata_array[self._indices]
        self._group_ids = self._compute_group_ids(meta, wilds_dataset)

    @staticmethod
    def _compute_group_ids(meta: torch.Tensor, d) -> torch.Tensor:
        # Both waterbirds and celebA follow y*2+confounder encoding.
        # For waterbirds: meta[:,0]=background, meta[:,1]=y
        # For celebA:     meta[:,0]=male,       meta[:,1]=y(blond)
        confounder = meta[:, 0].long()
        y_label    = meta[:, 1].long()
        return y_label * 2 + confounder

    def __len__(self):
        return len(self._subset)

    def __getitem__(self, idx):
        x, y, _ = self._subset[idx]
        group_id = self._group_ids[idx]
        return x, y, group_id


def _stratified_indices(group_ids: torch.Tensor, n: int, seed: int) -> np.ndarray:
    """Return n indices stratified by group to preserve minority representation."""
    rng = np.random.RandomState(seed)
    groups = group_ids.numpy()
    unique = np.unique(groups)
    selected = []
    for g in unique:
        idx = np.where(groups == g)[0]
        k = max(1, round(n * len(idx) / len(groups)))
        chosen = rng.choice(idx, size=min(k, len(idx)), replace=False)
        selected.append(chosen)
    result = np.concatenate(selected)
    # trim to exactly n
    rng.shuffle(result)
    return result[:n]


def get_loaders(cfg: DatasetConfig, wilds_root: str) -> tuple[DataLoader, DataLoader, DataLoader, DataLoader]:
    """Returns (train_loader, val_loader, test_loader, train_eval_loader).
    train_loader yields (x, y, group_id) with shuffle=True.
    val/test/train_eval loaders have shuffle=False.
    If cfg.max_train_samples > 0, train set is stratified-subsampled.
    """
    dataset_name = "waterbirds" if cfg.name == "waterbirds" else "celebA"
    d = wilds.get_dataset(dataset_name, root_dir=wilds_root, download=False)

    train_ds      = _GroupedSubset(d, "train", _get_transforms(train=True))
    val_ds        = _GroupedSubset(d, "val",   _get_transforms(train=False))
    test_ds       = _GroupedSubset(d, "test",  _get_transforms(train=False))
    train_eval_ds = _GroupedSubset(d, "train", _get_transforms(train=False))

    if cfg.max_train_samples > 0 and len(train_ds) > cfg.max_train_samples:
        idx = _stratified_indices(train_ds._group_ids, cfg.max_train_samples, cfg.seed)
        train_ds      = Subset(train_ds,      idx)
        train_eval_ds = Subset(train_eval_ds, idx)
        print(f"  Subsampled train to {len(train_ds)} samples (stratified by group)")

    train_loader      = DataLoader(train_ds,      batch_size=cfg.batch_size, shuffle=True,  num_workers=4, pin_memory=True)
    val_loader        = DataLoader(val_ds,        batch_size=cfg.batch_size, shuffle=False, num_workers=4, pin_memory=True)
    test_loader       = DataLoader(test_ds,       batch_size=cfg.batch_size, shuffle=False, num_workers=4, pin_memory=True)
    train_eval_loader = DataLoader(train_eval_ds, batch_size=cfg.batch_size, shuffle=False, num_workers=4, pin_memory=True)

    return train_loader, val_loader, test_loader, train_eval_loader
