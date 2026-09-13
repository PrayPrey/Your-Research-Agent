"""Dataset classes for Waterbirds and CelebA with group labels."""
import os
import numpy as np
import pandas as pd
from PIL import Image
import torch
from torch import Tensor
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from typing import Tuple


def get_transforms(augment: bool, dataset_name: str) -> transforms.Compose:
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
    if augment:
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


class GroupDataset(Dataset):
    def __init__(self, data_dir: str, split: str, transform=None):
        self.data_dir = data_dir
        self.split = split
        self.transform = transform
        self.x_array = []   # image paths
        self.y_array = []   # class labels
        self.g_array = []   # group labels

    def __len__(self) -> int:
        return len(self.y_array)

    def __getitem__(self, idx: int) -> Tuple[Tensor, int, int]:
        img_path = self.x_array[idx]
        img = Image.open(img_path).convert('RGB')
        if self.transform:
            img = self.transform(img)
        y = int(self.y_array[idx])
        g = int(self.g_array[idx])
        return img, y, g


class WaterBirdsDataset(GroupDataset):
    SPLIT_MAP = {'train': 0, 'val': 1, 'test': 2}

    def __init__(self, data_dir: str, split: str, augment: bool = False):
        augment_flag = augment and split == 'train'
        transform = get_transforms(augment_flag, 'waterbirds')
        super().__init__(data_dir, split, transform)

        metadata_path = os.path.join(data_dir, 'metadata.csv')
        df = pd.read_csv(metadata_path)
        split_id = self.SPLIT_MAP[split]
        df = df[df['split'] == split_id].reset_index(drop=True)

        # group_idx: 0=landbird-land, 1=landbird-water, 2=waterbird-land, 3=waterbird-water
        # computed as 2*y + place (y=bird type, place=background type)
        has_group_idx = 'group_idx' in df.columns
        for _, row in df.iterrows():
            img_filename = str(row['img_filename'])
            img_path = os.path.join(data_dir, img_filename)
            self.x_array.append(img_path)
            self.y_array.append(int(row['y']))
            if has_group_idx:
                self.g_array.append(int(row['group_idx']))
            else:
                # group = 2*y + place (GroupDRO convention)
                self.g_array.append(int(row['y']) * 2 + int(row['place']))

        self.y_array = np.array(self.y_array)
        self.g_array = np.array(self.g_array)


class CelebADataset(GroupDataset):
    SPLIT_MAP = {'train': 0, 'val': 1, 'test': 2}

    def __init__(self, data_dir: str, split: str, augment: bool = False):
        augment_flag = augment and split == 'train'
        transform = get_transforms(augment_flag, 'celeba')
        super().__init__(data_dir, split, transform)

        metadata_path = os.path.join(data_dir, 'metadata.csv')
        df = pd.read_csv(metadata_path)
        split_id = self.SPLIT_MAP[split]
        df = df[df['split'] == split_id].reset_index(drop=True)

        img_dir = os.path.join(data_dir, 'img_align_celeba')
        for _, row in df.iterrows():
            img_path = os.path.join(img_dir, row['image_id'])
            self.x_array.append(img_path)
            self.y_array.append(int(row['y']))
            self.g_array.append(int(row['group_idx']))

        self.y_array = np.array(self.y_array)
        self.g_array = np.array(self.g_array)


def get_dataloader(dataset: GroupDataset, batch_size: int,
                   shuffle: bool = False, num_workers: int = 4) -> DataLoader:
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle,
                      num_workers=num_workers, pin_memory=True)
