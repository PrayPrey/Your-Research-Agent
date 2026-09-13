"""Waterbirds dataset loading with group labels."""
import os
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import pandas as pd
from config import CONFIG


class WaterbirdsDataset(Dataset):
    def __init__(self, root: str, split: str, transform=None):
        self.root = root
        self.transform = transform
        metadata = pd.read_csv(os.path.join(root, "metadata.csv"))
        split_map = {"train": 0, "val": 1, "test": 2}
        self.data = metadata[metadata["split"] == split_map[split]].reset_index(drop=True)
        self.y = self.data["y"].values
        self.place = self.data["place"].values
        self.group = self.y * 2 + self.place

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        img_path = os.path.join(self.root, row["img_filename"])
        img = Image.open(img_path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, int(row["y"]), int(self.group[idx])


def get_transforms(train: bool):
    if train:
        return transforms.Compose([
            transforms.RandomResizedCrop(CONFIG.image_size),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(CONFIG.norm_mean, CONFIG.norm_std),
        ])
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(CONFIG.image_size),
        transforms.ToTensor(),
        transforms.Normalize(CONFIG.norm_mean, CONFIG.norm_std),
    ])


def get_dataloaders(root: str, batch_size: int):
    train_ds = WaterbirdsDataset(root, "train", get_transforms(True))
    val_ds = WaterbirdsDataset(root, "val", get_transforms(False))
    test_ds = WaterbirdsDataset(root, "test", get_transforms(False))
    g = torch.Generator().manual_seed(CONFIG.seed)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              num_workers=CONFIG.num_workers, generator=g, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False,
                            num_workers=CONFIG.num_workers, pin_memory=True)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False,
                             num_workers=CONFIG.num_workers, pin_memory=True)
    return train_loader, val_loader, test_loader


def get_direction_pairs(dataset):
    """Get index pairs for spurious/core direction computation.
    Spurious: same label, different background (place).
    Core: different label (hence different bird type).
    """
    n = len(dataset)
    y = dataset.y
    place = dataset.place
    spurious_pairs = []
    core_pairs = []
    for i in range(min(n, 1000)):
        for j in range(i + 1, min(n, 1000)):
            if y[i] == y[j] and place[i] != place[j]:
                spurious_pairs.append((i, j, y[i]))
            if y[i] != y[j]:
                core_pairs.append((i, j, y[i]))
    return spurious_pairs[:200], core_pairs[:200]
