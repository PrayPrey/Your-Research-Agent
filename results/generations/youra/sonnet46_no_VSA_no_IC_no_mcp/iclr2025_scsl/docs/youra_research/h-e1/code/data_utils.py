import numpy as np
import torch
from torch.utils.data import DataLoader, Subset
import torchvision.transforms as T
import wilds

from config import (
    DATA_ROOT, DATASET_NAME, DATASET_DOWNLOAD,
    BATCH_SIZE, RESIZE, CROP, IMG_MEAN, IMG_STD,
)


def _get_transform():
    return T.Compose([
        T.Resize(RESIZE),
        T.CenterCrop(CROP),
        T.ToTensor(),
        T.Normalize(mean=IMG_MEAN, std=IMG_STD),
    ])


def get_waterbirds_subsets(transform=None):
    """Returns (train_data, val_data, test_data) WILDS subsets."""
    if transform is None:
        transform = _get_transform()
    dataset = wilds.get_dataset(DATASET_NAME, download=DATASET_DOWNLOAD, root_dir=DATA_ROOT)
    train_data = dataset.get_subset('train', transform=transform)
    val_data = dataset.get_subset('val', transform=transform)
    test_data = dataset.get_subset('test', transform=transform)
    return train_data, val_data, test_data


def get_balanced_probe_indices(metadata_array, seed):
    """
    Returns indices for group-balanced sample from val split.
    4 groups = {bird_label} x {background_label}.
    """
    rng = np.random.default_rng(seed)
    # metadata_array[:, 0] = background (spurious label)
    # metadata_array[:, 1] = bird species (task label) — actually y holds task label
    # In WILDS Waterbirds: metadata col 0 = background, col 1 = split
    # y itself is the bird label. We build groups from y and metadata[:,0].
    # This function receives the full metadata_array from the val subset.
    if isinstance(metadata_array, torch.Tensor):
        meta_np = metadata_array.numpy()
    else:
        meta_np = np.array(metadata_array)
    spur_lbls = meta_np[:, 0].astype(int)   # background: 0=land, 1=water
    task_lbls = meta_np[:, 1].astype(int)   # bird: 0=landbird, 1=waterbird
    group_ids = 2 * task_lbls + spur_lbls   # 0..3
    groups = [np.where(group_ids == g)[0] for g in range(4)]
    min_count = min(len(g) for g in groups)
    assert min_count > 0, "Empty group in val split"
    chosen = [rng.choice(g, size=min_count, replace=False) for g in groups]
    return np.concatenate(chosen)


def get_probe_train_loader(val_data, seed, batch_size=BATCH_SIZE):
    """Group-balanced sample from val split; equal samples per group."""
    metadata_array = val_data.metadata_array
    indices = get_balanced_probe_indices(metadata_array, seed)
    subset = Subset(val_data, indices)
    return DataLoader(subset, batch_size=batch_size, shuffle=False, num_workers=4, pin_memory=True)


def get_test_loader(test_data, batch_size=BATCH_SIZE):
    """Full test split loader, no subsampling."""
    return DataLoader(test_data, batch_size=batch_size, shuffle=False, num_workers=4, pin_memory=True)


def get_full_val_loader(val_data, batch_size=BATCH_SIZE):
    """Full val split loader (for feature caching before group-balanced selection)."""
    return DataLoader(val_data, batch_size=batch_size, shuffle=False, num_workers=4, pin_memory=True)
