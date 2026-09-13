"""
Waterbirds Dataset Implementation
Loads Waterbirds dataset with group labels for spurious correlation analysis
"""

import os
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import pandas as pd


class WaterbirdsDataset(Dataset):
    """
    Waterbirds dataset with group labels.

    Groups:
        0: landbirds on land (majority, easy)
        1: landbirds on water (minority, hard)
        2: waterbirds on land (minority, hard)
        3: waterbirds on water (majority, easy)
    """

    def __init__(self, root_dir, split='train', transform=None):
        """
        Args:
            root_dir: Path to waterbird_complete95_forest2water2/
            split: 'train', 'val', or 'test'
            transform: torchvision transforms
        """
        self.root_dir = root_dir
        self.split = split
        self.transform = transform

        # Load metadata
        metadata_path = os.path.join(root_dir, 'metadata.csv')
        self.metadata = pd.read_csv(metadata_path)

        # Filter by split
        self.metadata = self.metadata[self.metadata['split'] == {'train': 0, 'val': 1, 'test': 2}[split]]

    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, idx):
        row = self.metadata.iloc[idx]

        # Load image
        img_path = os.path.join(self.root_dir, row['img_filename'])
        image = Image.open(img_path).convert('RGB')

        if self.transform:
            image = self.transform(image)

        # Labels
        label = int(row['y'])  # 0: landbird, 1: waterbird
        group = int(row['y']) * 2 + int(row['place'])  # Group encoding

        return image, label, group


def get_transforms(split='train'):
    """Get data transforms for given split"""
    if split == 'train':
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
    else:
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])


def get_dataloaders(data_dir, batch_size=128, num_workers=4):
    """
    Create train/val/test dataloaders.

    Returns:
        dict with keys 'train', 'val', 'test'
    """
    loaders = {}

    for split in ['train', 'val', 'test']:
        dataset = WaterbirdsDataset(
            root_dir=data_dir,
            split=split,
            transform=get_transforms(split)
        )

        loaders[split] = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=(split == 'train'),
            num_workers=num_workers,
            pin_memory=True
        )

    return loaders


def get_minority_loader(data_dir, batch_size=32, num_workers=4):
    """
    Create dataloader for minority groups only (groups 1 and 2).
    Used for minority gradient computation.

    Returns:
        DataLoader with minority samples
    """
    # Load full training set
    dataset = WaterbirdsDataset(
        root_dir=data_dir,
        split='train',
        transform=get_transforms('train')
    )

    # Filter minority groups (1, 2)
    minority_indices = []
    for idx in range(len(dataset)):
        _, _, group = dataset[idx]
        if group in [1, 2]:
            minority_indices.append(idx)

    # Create subset
    minority_dataset = torch.utils.data.Subset(dataset, minority_indices)

    return DataLoader(
        minority_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
