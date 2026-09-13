import os
import pandas as pd
import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


class WaterbirdsDataset(Dataset):
    SPLIT_MAP = {"train": 0, "val": 1, "test": 2}

    def __init__(self, root: str, split: str, transform=None):
        self.root = root
        self.split = split
        self.transform = transform

        metadata_path = os.path.join(root, "metadata.csv")
        self.metadata = pd.read_csv(metadata_path)

        split_id = self.SPLIT_MAP[split]
        self.metadata = self.metadata[self.metadata["split"] == split_id].reset_index(drop=True)

    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, idx: int) -> dict:
        row = self.metadata.iloc[idx]
        img_path = os.path.join(self.root, row["img_filename"])
        image = Image.open(img_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        core_label = int(row["y"])
        spurious_label = int(row["place"])
        group_id = 2 * spurious_label + core_label  # 0..3

        return {
            "image": image,
            "core_label": torch.tensor(core_label, dtype=torch.long),
            "spurious_label": torch.tensor(spurious_label, dtype=torch.long),
            "group_id": torch.tensor(group_id, dtype=torch.long),
        }


def get_waterbirds_loader(
    root: str,
    split: str,
    batch_size: int,
    num_workers: int,
    augment: bool = False,
) -> DataLoader:
    if augment:
        transform = transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])
    else:
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])

    dataset = WaterbirdsDataset(root=root, split=split, transform=transform)
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=(split == "train"),
        num_workers=num_workers,
        pin_memory=True,
    )
    return loader
