import os
import pandas as pd
from PIL import Image
import torch
from torch import Tensor
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import sys
sys.path.insert(0, os.path.dirname(__file__))
import config


class WaterbirdsDataset(Dataset):
    def __init__(self, root: str, split: int, transform=None):
        # split: 0=train, 1=val, 2=test
        self.root = root
        self.transform = transform
        meta = pd.read_csv(os.path.join(os.path.dirname(root), "metadata.csv"))
        meta = meta[meta["split"] == split].reset_index(drop=True)
        self.img_paths = [os.path.join(root, p) for p in meta["img_filename"].tolist()]
        self.y = torch.tensor(meta["y"].values, dtype=torch.long)
        # group: 0=landbird/land, 1=landbird/water, 2=waterbird/land, 3=waterbird/water
        # place=0→land, place=1→water; group = y*2 + place
        self.group = torch.tensor((meta["y"].values * 2 + meta["place"].values), dtype=torch.long)
        self.minority_mask = torch.tensor(
            [(g.item() in config.MINORITY_GROUPS) for g in self.group], dtype=torch.bool
        )

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, idx: int):
        img = Image.open(self.img_paths[idx]).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, self.y[idx], self.group[idx]


def _train_transform():
    return transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(config.IMAGENET_MEAN, config.IMAGENET_STD),
    ])


def _eval_transform():
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(config.IMAGENET_MEAN, config.IMAGENET_STD),
    ])


def get_train_loader(root: str, batch_size: int) -> DataLoader:
    ds = WaterbirdsDataset(root, split=0, transform=_train_transform())
    return DataLoader(ds, batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True)


def get_eval_loader(root: str, split: int, batch_size: int) -> DataLoader:
    ds = WaterbirdsDataset(root, split=split, transform=_eval_transform())
    return DataLoader(ds, batch_size=batch_size, shuffle=False, num_workers=4, pin_memory=True)
