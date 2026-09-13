"""Waterbirds dataset loading and preprocessing."""
import os
import subprocess
import tarfile
import pandas as pd
import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


def download_waterbirds(root_dir: str, url: str) -> None:
    """Download and extract Waterbirds dataset if not present."""
    os.makedirs(root_dir, exist_ok=True)
    tar_path = os.path.join(root_dir, "waterbird_complete95_forest2water2.tar.gz")
    extracted_dir = os.path.join(root_dir, "waterbird_complete95_forest2water2")

    if os.path.exists(extracted_dir):
        return

    if not os.path.exists(tar_path):
        subprocess.run(["wget", "-q", url, "-O", tar_path], check=True)

    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(root_dir)


class WaterbirdsDataset(Dataset):
    """Waterbirds dataset with group labels."""

    def __init__(self, root_dir: str, split: str, transform=None):
        self.root_dir = os.path.join(root_dir, "waterbird_complete95_forest2water2")
        self.split = split
        self.transform = transform

        metadata_path = os.path.join(self.root_dir, "metadata.csv")
        self.metadata = pd.read_csv(metadata_path)

        split_map = {"train": 0, "val": 1, "test": 2}
        self.metadata = self.metadata[self.metadata["split"] == split_map[split]].reset_index(drop=True)

        self.y = self.metadata["y"].values
        self.place = self.metadata["place"].values
        self.img_filenames = self.metadata["img_filename"].values

    def __len__(self) -> int:
        return len(self.metadata)

    def __getitem__(self, idx: int):
        img_path = os.path.join(self.root_dir, self.img_filenames[idx])
        img = Image.open(img_path).convert("RGB")

        if self.transform:
            img = self.transform(img)

        return img, self.y[idx], self.place[idx], idx


def get_dataloaders(root_dir: str, batch_size: int, num_workers: int,
                   img_size: int, norm_mean: tuple, norm_std: tuple) -> dict:
    """Create train/val/test dataloaders."""
    transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=norm_mean, std=norm_std),
    ])

    loaders = {}
    for split in ["train", "val", "test"]:
        dataset = WaterbirdsDataset(root_dir, split, transform)
        loaders[split] = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=(split == "train"),
            num_workers=num_workers,
            pin_memory=True,
        )
    return loaders


def is_minority(y: np.ndarray, place: np.ndarray) -> np.ndarray:
    """Return bool array where minority = (y != place)."""
    return y != place
