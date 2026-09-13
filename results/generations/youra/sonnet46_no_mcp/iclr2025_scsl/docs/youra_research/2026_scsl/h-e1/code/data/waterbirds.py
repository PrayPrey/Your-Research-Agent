import os
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


class WaterbirdsDataset(Dataset):
    SPLIT_MAP = {"train": 0, "val": 1, "test": 2}

    def __init__(self, root: str, split: str, transform=None):
        self.root = root
        self.transform = transform
        split_id = self.SPLIT_MAP[split]
        meta_path = os.path.join(root, "metadata.csv")
        df = pd.read_csv(meta_path)
        self.df = df[df["split"] == split_id].reset_index(drop=True)

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> dict:
        row = self.df.iloc[idx]
        img_path = os.path.join(self.root, row["img_filename"])
        image = Image.open(img_path).convert("RGB")
        if self.transform is not None:
            image = self.transform(image)
        return {
            "image": image,
            "core_label": int(row["y"]),
            "spurious_label": int(row["place"]),
        }


def get_waterbirds_loader(
    root: str,
    split: str,
    batch_size: int,
    num_workers: int,
    augment: bool = False,
) -> DataLoader:
    if augment:
        tf = transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])
    else:
        tf = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])
    dataset = WaterbirdsDataset(root=root, split=split, transform=tf)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=(split == "train"),
        num_workers=num_workers,
        pin_memory=True,
    )
