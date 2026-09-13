"""Dataset loaders for 6 fine-grained classification benchmarks."""
import os
from pathlib import Path
from typing import Optional, Tuple

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import datasets, transforms
from PIL import Image
import scipy.io


def get_transforms(train: bool) -> transforms.Compose:
    """Get transforms for training or evaluation."""
    normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
    if train:
        return transforms.Compose([
            transforms.RandomResizedCrop(224),
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


class CUBDataset(Dataset):
    """CUB-200-2011 dataset."""

    def __init__(self, root: str, train: bool = True, transform=None):
        self.root = Path(root) / "CUB_200_2011"
        self.transform = transform
        images_txt = self.root / "images.txt"
        train_test_split = self.root / "train_test_split.txt"
        labels_txt = self.root / "image_class_labels.txt"

        with open(images_txt) as f:
            id_to_path = {int(l.split()[0]): l.split()[1] for l in f}
        with open(train_test_split) as f:
            id_to_train = {int(l.split()[0]): int(l.split()[1]) for l in f}
        with open(labels_txt) as f:
            id_to_label = {int(l.split()[0]): int(l.split()[1]) - 1 for l in f}

        self.samples = []
        for img_id, path in id_to_path.items():
            is_train = id_to_train[img_id] == 1
            if is_train == train:
                self.samples.append((self.root / "images" / path, id_to_label[img_id]))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label


class StanfordDogsDataset(Dataset):
    """Stanford Dogs dataset."""

    def __init__(self, root: str, train: bool = True, transform=None):
        self.root = Path(root) / "stanford_dogs"
        self.transform = transform
        split = "train" if train else "test"
        mat_file = self.root / f"{split}_list.mat"
        mat = scipy.io.loadmat(str(mat_file))
        file_list = mat["file_list"]
        labels = mat["labels"].flatten() - 1

        self.samples = []
        for i, (f, l) in enumerate(zip(file_list, labels)):
            path = self.root / "Images" / f[0][0]
            self.samples.append((path, int(l)))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label


class StanfordCarsDataset(Dataset):
    """Stanford Cars dataset."""

    def __init__(self, root: str, train: bool = True, transform=None):
        self.root = Path(root) / "stanford_cars"
        self.transform = transform
        split = "cars_train" if train else "cars_test"
        mat_file = self.root / f"{split}_annos.mat" if train else self.root / "cars_test_annos_withlabels.mat"
        mat = scipy.io.loadmat(str(mat_file))
        annos = mat["annotations"][0]

        self.samples = []
        img_dir = self.root / split
        for anno in annos:
            fname = anno[5][0] if len(anno) > 5 else anno[4][0]
            label = int(anno[4][0][0] if len(anno) > 5 else anno[3][0][0]) - 1
            self.samples.append((img_dir / fname, label))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label


class NABirdsDataset(Dataset):
    """NABirds dataset for probe feature extraction."""

    def __init__(self, root: str, train: bool = True, transform=None):
        self.root = Path(root) / "nabirds"
        self.transform = transform
        images_txt = self.root / "images.txt"
        train_test_split = self.root / "train_test_split.txt"
        labels_txt = self.root / "image_class_labels.txt"

        if not images_txt.exists():
            raise FileNotFoundError(f"NABirds dataset not found at {self.root}")

        with open(images_txt) as f:
            id_to_path = {l.split()[0]: l.split()[1] for l in f}
        with open(train_test_split) as f:
            id_to_train = {l.split()[0]: int(l.split()[1]) for l in f}
        with open(labels_txt) as f:
            lines = [l.strip().split() for l in f]
            id_to_label = {l[0]: int(l[1]) for l in lines}

        label_set = sorted(set(id_to_label.values()))
        label_map = {old: new for new, old in enumerate(label_set)}

        self.samples = []
        for img_id, path in id_to_path.items():
            is_train = id_to_train.get(img_id, 0) == 1
            if is_train == train:
                self.samples.append((self.root / "images" / path, label_map[id_to_label[img_id]]))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label


DATASET_NUM_CLASSES = {
    "cub": 200,
    "dogs": 120,
    "flowers": 102,
    "cars": 196,
    "aircraft": 100,
    "nabirds": 555,
}


def build_dataset(name: str, root: str, train: bool) -> Dataset:
    """Build dataset by name."""
    transform = get_transforms(train)
    name = name.lower()

    if name == "cub":
        return CUBDataset(root, train, transform)
    elif name == "dogs":
        return StanfordDogsDataset(root, train, transform)
    elif name == "flowers":
        return datasets.Flowers102(root, split="train" if train else "test",
                                   transform=transform, download=True)
    elif name == "cars":
        return StanfordCarsDataset(root, train, transform)
    elif name == "aircraft":
        return datasets.FGVCAircraft(root, split="train" if train else "test",
                                     transform=transform, download=True)
    elif name == "nabirds":
        return NABirdsDataset(root, train, transform)
    else:
        raise ValueError(f"Unknown dataset: {name}")


def build_dataloader(name: str, root: str, train: bool, batch_size: int,
                     num_workers: int = 4) -> DataLoader:
    """Build DataLoader for dataset."""
    dataset = build_dataset(name, root, train)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=train,
        num_workers=num_workers,
        pin_memory=True,
        drop_last=train,
    )
