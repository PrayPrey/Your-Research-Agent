import os
import numpy as np
import pandas as pd
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


class WaterbirdsDataset(Dataset):
    def __init__(self, root_dir: str, split: str, transform=None):
        self.root_dir = root_dir
        self.split = split
        self.transform = transform

        metadata_path = os.path.join(root_dir, "metadata.csv")
        self.metadata = pd.read_csv(metadata_path)

        split_map = {"train": 0, "val": 1, "test": 2}
        split_idx = split_map[split]
        self.metadata = self.metadata[self.metadata["split"] == split_idx].reset_index(drop=True)

        self.img_dir = root_dir

    def __len__(self) -> int:
        return len(self.metadata)

    def __getitem__(self, idx: int) -> tuple:
        row = self.metadata.iloc[idx]
        img_path = os.path.join(self.img_dir, row["img_filename"])
        image = Image.open(img_path).convert("RGB")

        label = int(row["y"])
        place = int(row["place"])
        spurious_aligned = int(label == place)

        if self.transform:
            image = self.transform(image)

        return image, label, spurious_aligned


def get_dataloaders(root_dir: str, batch_size: int) -> dict:
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    return {
        "train": DataLoader(
            WaterbirdsDataset(root_dir, "train", train_transform),
            batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True
        )
    }


def download_waterbirds(root_dir: str) -> None:
    os.makedirs(root_dir, exist_ok=True)
    import subprocess
    url = "https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz"
    tar_path = os.path.join(os.path.dirname(root_dir), "waterbirds.tar.gz")

    if not os.path.exists(os.path.join(root_dir, "metadata.csv")):
        print(f"Downloading Waterbirds to {tar_path}...")
        subprocess.run(["wget", "-q", url, "-O", tar_path], check=True)
        subprocess.run(["tar", "-xzf", tar_path, "-C", os.path.dirname(root_dir)], check=True)
        extracted_dir = os.path.join(os.path.dirname(root_dir), "waterbird_complete95_forest2water2")
        if os.path.exists(extracted_dir) and extracted_dir != root_dir:
            subprocess.run(["mv", extracted_dir, root_dir], check=True)
        os.remove(tar_path)
        print("Waterbirds downloaded and extracted.")
