"""
dataset.py - WaterbirdsDataset and get_dataloaders()

Waterbirds benchmark dataset (Sagawa et al. 2019 GroupDRO pattern).
metadata.csv columns: img_id, img_filename, y, split, place, place_filename
split: 0=train, 1=val, 2=test
group_id = y * 2 + place  (G0=landbird/land, G1=landbird/water, G2=waterbird/land, G3=waterbird/water)
"""

import os
import pandas as pd
from PIL import Image

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

SPLIT_MAP = {'train': 0, 'val': 1, 'test': 2}


def get_transform(split: str) -> transforms.Compose:
    """
    train_shuffle uses RandomResizedCrop + RandomHorizontalFlip.
    train_ordered / val / test use Resize + CenterCrop (deterministic).
    """
    normalize = transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    if split == 'train_shuffle':
        return transforms.Compose([
            transforms.Resize(256),
            transforms.RandomCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            normalize,
        ])
    else:
        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            normalize,
        ])


class WaterbirdsDataset(Dataset):
    """
    Waterbirds dataset with group labels for post-hoc evaluation.

    Returns: (image_tensor, y_class, place_label)
      - y_class  : int in {0, 1}  (landbird=0, waterbird=1)
      - place    : int in {0, 1}  (land=0, water=1)
      - group_id = y * 2 + place  (computed outside, for reference)
    """

    def __init__(self, root: str, split: str = 'train', transform=None):
        self.root = root
        self.transform = transform

        metadata = pd.read_csv(os.path.join(root, 'metadata.csv'))
        split_id = SPLIT_MAP[split]
        self.data = metadata[metadata['split'] == split_id].reset_index(drop=True)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int):
        row = self.data.iloc[idx]
        img_path = os.path.join(self.root, row['img_filename'])
        img = Image.open(img_path).convert('RGB')
        if self.transform is not None:
            img = self.transform(img)
        return img, int(row['y']), int(row['place'])


def get_dataloaders(
    root: str,
    batch_size: int = 128,
    num_workers: int = 4,
) -> dict:
    """
    Returns DataLoaders dict with keys:
      'train_shuffle' : shuffled training set (for ERM training)
      'train_ordered' : unshuffled training set (for gradient norm collection)
      'val'           : validation set
    """
    train_shuffle_ds = WaterbirdsDataset(root, split='train',
                                         transform=get_transform('train_shuffle'))
    train_ordered_ds = WaterbirdsDataset(root, split='train',
                                         transform=get_transform('train_ordered'))
    val_ds = WaterbirdsDataset(root, split='val',
                               transform=get_transform('val'))

    loaders = {
        'train_shuffle': DataLoader(
            train_shuffle_ds,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=True,
            drop_last=False,
        ),
        'train_ordered': DataLoader(
            train_ordered_ds,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True,
            drop_last=False,
        ),
        'val': DataLoader(
            val_ds,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True,
            drop_last=False,
        ),
    }
    return loaders
