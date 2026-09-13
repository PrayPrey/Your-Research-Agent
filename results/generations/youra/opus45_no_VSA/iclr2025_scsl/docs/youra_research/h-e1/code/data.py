import os
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader, Subset
from torchvision import transforms
from PIL import Image

from config import CONFIG


class WaterbirdDataset(Dataset):
    def __init__(self, root: str, split: str = "train"):
        self.root = root
        metadata_path = os.path.join(root, "metadata.csv")
        self.metadata = pd.read_csv(metadata_path)

        split_map = {"train": 0, "val": 1, "test": 2}
        self.metadata = self.metadata[self.metadata["split"] == split_map[split]].reset_index(drop=True)

        self.metadata["group"] = 2 * self.metadata["y"] + self.metadata["place"]

        if split == "train":
            self.transform = transforms.Compose([
                transforms.RandomResizedCrop(CONFIG.img_size),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize(CONFIG.imagenet_mean, CONFIG.imagenet_std),
            ])
        else:
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(CONFIG.img_size),
                transforms.ToTensor(),
                transforms.Normalize(CONFIG.imagenet_mean, CONFIG.imagenet_std),
            ])

    def __len__(self) -> int:
        return len(self.metadata)

    def __getitem__(self, idx: int) -> tuple:
        row = self.metadata.iloc[idx]
        img_path = os.path.join(self.root, row["img_filename"])
        img = Image.open(img_path).convert("RGB")
        img = self.transform(img)
        label = int(row["y"])
        group = int(row["group"])
        return img, label, group


def get_group_loader(dataset: WaterbirdDataset, group_id: int, batch_size: int = 32) -> DataLoader:
    indices = [i for i, row in dataset.metadata.iterrows() if row["group"] == group_id]
    subset = Subset(dataset, indices)
    return DataLoader(subset, batch_size=batch_size, shuffle=False, num_workers=0)
