import os
import torch
from torch.utils.data import Dataset, DataLoader, Subset
from torchvision import transforms
from PIL import Image
import numpy as np
from config import IMAGENET_MEAN, IMAGENET_STD

class WaterbirdsDataset(Dataset):
    def __init__(self, root: str, split: str = "train", transform=None):
        self.root = root
        self.split = split
        self.transform = transform
        metadata_path = os.path.join(root, "metadata.csv")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"metadata.csv not found at {root}. Run download_waterbirds.py first.")
        import pandas as pd
        df = pd.read_csv(metadata_path)
        split_map = {"train": 0, "val": 1, "test": 2}
        df = df[df["split"] == split_map[split]]
        self.filenames = df["img_filename"].values
        self.labels = df["y"].values
        self.groups = df["place"].values * 2 + df["y"].values

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        img_path = os.path.join(self.root, self.filenames[idx])
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, self.labels[idx], self.groups[idx]

def get_transforms(split: str, image_size: int = 224):
    if split == "train":
        return transforms.Compose([
            transforms.RandomResizedCrop(image_size),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ])
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])

def load_waterbirds(root: str, split: str, image_size: int = 224) -> Dataset:
    transform = get_transforms(split, image_size)
    return WaterbirdsDataset(root, split, transform)

def get_dataloader(dataset: Dataset, batch_size: int, shuffle: bool, num_workers: int = 4) -> DataLoader:
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers, pin_memory=True, drop_last=False)

def get_group_subset(dataset: Dataset, groups: tuple) -> Subset:
    indices = [i for i, (_, _, g) in enumerate(dataset) if g in groups]
    return Subset(dataset, indices)

def get_group_indices(dataset: Dataset):
    all_groups = torch.tensor([dataset[i][2] for i in range(len(dataset))])
    return all_groups
