import os
import numpy as np
import torch
from torch.utils.data import DataLoader, Subset
from torchvision import transforms
from wilds import get_dataset
from config import CELEBA_MIN_GROUP_SIZE, BATCH_SIZE


_IMAGENET_MEAN = [0.485, 0.456, 0.406]
_IMAGENET_STD  = [0.229, 0.224, 0.225]

CELEBA_TRANSFORM = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(_IMAGENET_MEAN, _IMAGENET_STD),
])

_WILDS_ROOT = os.path.expanduser('~/.wilds')


def load_celeba_balanced(min_per_group=CELEBA_MIN_GROUP_SIZE):
    """
    Load all CelebA splits, pool them, and create group-balanced train/test split.
    task_labels = Blond_Hair (y_array), spurious_labels = Male (metadata[:,0]).

    Returns:
        dataset: WILDS CelebA train subset (for Subset indexing)
        task_labels: np.ndarray shape (N_all,)
        spurious_labels: np.ndarray shape (N_all,)
        train_idx: np.ndarray of indices into the full dataset (202599)
        test_idx: np.ndarray of indices into the full dataset (202599)
    """
    ds = get_dataset('celebA', root_dir=_WILDS_ROOT, download=False)

    # Use all data for maximum balanced group size
    all_y = ds.y_array.numpy()                   # Blond_Hair
    all_meta = ds.metadata_array.numpy()          # [:,0]=male, [:,1]=y, [:,2]=domain
    spurious = all_meta[:, 0]                     # Male

    task_labels = all_y
    spurious_labels = spurious

    # Build 4 groups
    groups = {}
    for t in [0, 1]:
        for s in [0, 1]:
            mask = (task_labels == t) & (spurious_labels == s)
            groups[(t, s)] = np.where(mask)[0]

    min_size = min(len(v) for v in groups.values())
    per_group = min(min_per_group, min_size)
    print(f"[celeba] min group size: {min_size}, per_group: {per_group}")

    rng = np.random.default_rng(42)
    selected = []
    for key, idx in sorted(groups.items()):
        chosen = rng.choice(idx, size=per_group, replace=False)
        selected.append(chosen)
    selected_idx = np.concatenate(selected)
    rng.shuffle(selected_idx)

    n = len(selected_idx)
    split = int(0.8 * n)
    train_idx = selected_idx[:split]
    test_idx  = selected_idx[split:]

    # Use train split dataset for Subset (transform applied)
    # We'll create a combined dataset from all splits using train as base
    # Actually WILDS get_subset applies transform; we use train subset and re-index
    # Simplest: use full dataset with custom Subset
    full_dataset = ds.get_subset('train', transform=CELEBA_TRANSFORM)
    # But indices span full 202599 — we need a wrapper that indexes the raw dataset
    # Use a simple wrapper instead
    return ds, task_labels, spurious_labels, train_idx, test_idx


class CelebAIndexed(torch.utils.data.Dataset):
    """Wraps WILDS CelebA to index by absolute dataset indices with transform."""
    def __init__(self, wilds_dataset, indices, transform=None):
        self.ds = wilds_dataset
        self.indices = indices
        self.transform = transform or CELEBA_TRANSFORM

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, i):
        abs_idx = int(self.indices[i])
        x, y, meta = self.ds[abs_idx]
        # x is PIL image from WILDS
        if self.transform:
            x = self.transform(x)
        return x, y


def get_celeba_dataloader(wilds_dataset, indices, batch_size=BATCH_SIZE):
    dataset = CelebAIndexed(wilds_dataset, indices)
    return DataLoader(dataset, batch_size=batch_size, shuffle=False,
                      num_workers=4, pin_memory=True)
