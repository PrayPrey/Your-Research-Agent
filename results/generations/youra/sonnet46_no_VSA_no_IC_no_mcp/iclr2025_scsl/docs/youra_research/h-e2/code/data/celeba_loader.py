"""
CelebA loader using WILDS-format CSV files at ~/.wilds/celebA_v1.0/.
Attributes use -1/1 encoding; we convert to 0/1.
Partition: 0=train, 1=val, 2=test.
"""
import os
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset, Subset
from torchvision import transforms
from PIL import Image

WILDS_CELEBA_ROOT = os.path.expanduser('~/.wilds/celebA_v1.0')


class CelebAWILDS(Dataset):
    """Reads CelebA from WILDS CSV layout."""

    def __init__(self, root, split, transform=None):
        assert split in ('train', 'val', 'test')
        self.root = root
        self.img_dir = os.path.join(root, 'img_align_celeba')
        self.transform = transform

        split_id = {'train': 0, 'val': 1, 'test': 2}[split]
        part_df = pd.read_csv(os.path.join(root, 'list_eval_partition.csv'))
        attr_df = pd.read_csv(os.path.join(root, 'list_attr_celeba.csv'))
        merged = part_df.merge(attr_df, on='image_id')
        subset = merged[merged['partition'] == split_id].reset_index(drop=True)

        self.filenames = subset['image_id'].tolist()
        attr_cols = [c for c in attr_df.columns if c != 'image_id']
        # Convert -1/1 to 0/1
        raw = subset[attr_cols].values  # (N, 40)
        self.attr = torch.from_numpy(((raw + 1) // 2).astype(np.int64))  # 0/1
        self.attr_names = attr_cols

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        path = os.path.join(self.img_dir, self.filenames[idx])
        img = Image.open(path).convert('RGB')
        if self.transform:
            img = self.transform(img)
        return img, self.attr[idx]


def get_celeba_loaders(root=None, batch_size=256, download=False):
    root = root or WILDS_CELEBA_ROOT
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    train_ds = CelebAWILDS(root, 'train', transform=transform)
    test_ds = CelebAWILDS(root, 'test', transform=transform)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=False,
                              num_workers=4, pin_memory=True)
    return train_loader, test_ds


def get_balanced_celeba_indices(dataset, blond_attr, male_attr, n_per_group, seed):
    attrs = dataset.attr.numpy()  # (N, 40)
    blond = attrs[:, blond_attr]
    male = attrs[:, male_attr]
    groups = {
        (1, 1): np.where((blond == 1) & (male == 1))[0],
        (1, 0): np.where((blond == 1) & (male == 0))[0],
        (0, 1): np.where((blond == 0) & (male == 1))[0],
        (0, 0): np.where((blond == 0) & (male == 0))[0],
    }
    n = min(n_per_group, min(len(g) for g in groups.values()))
    rng = np.random.default_rng(seed)
    idx = np.concatenate([rng.choice(g, n, replace=False) for g in groups.values()])
    assert len(idx) == n * 4, f"Balanced test size wrong: {len(idx)}"
    return idx


def get_balanced_test_loader(dataset, indices, batch_size):
    subset = Subset(dataset, indices.tolist())
    loader = DataLoader(subset, batch_size=batch_size, shuffle=False,
                        num_workers=4, pin_memory=True)
    task_labels = dataset.attr[indices, 9].long()
    spur_labels = dataset.attr[indices, 20].long()
    return loader, task_labels, spur_labels
