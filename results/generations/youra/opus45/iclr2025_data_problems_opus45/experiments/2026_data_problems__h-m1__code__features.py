"""
Feature extraction from H-E1 ResNet-18 for H-M1 convex experiment.
Extracts 512-dim penultimate features from CIFAR-10.
"""

import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from sklearn.preprocessing import StandardScaler
import torchvision
import torchvision.transforms as transforms
from torchvision.models import resnet18

from config import HM1Config


def build_resnet18_cifar(device: str = 'cuda') -> nn.Module:
    """
    Build ResNet-18 modified for CIFAR-10 (matches h-e1 architecture).
    - conv1: kernel=3, stride=1, padding=1 (no downsampling)
    - maxpool: removed (Identity)
    - fc: 512 -> 10 classes
    """
    model = resnet18(weights=None)
    model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    model.maxpool = nn.Identity()
    model.fc = nn.Linear(model.fc.in_features, 10)
    return model.to(device)


class FeatureExtractor:
    """Extract ResNet-18 penultimate layer features."""

    def __init__(self, cfg: HM1Config, device: str = 'cuda'):
        self.cfg = cfg
        self.device = device

    def load_resnet(self) -> nn.Module:
        """Load H-E1 ResNet-18 from checkpoint."""
        model = build_resnet18_cifar(self.device)
        checkpoint_path = os.path.abspath(self.cfg.he1_checkpoint)

        if os.path.exists(checkpoint_path):
            state_dict = torch.load(checkpoint_path, map_location=self.device)
            model.load_state_dict(state_dict)
            print(f"Loaded checkpoint from {checkpoint_path}")
        else:
            print(f"Warning: Checkpoint not found at {checkpoint_path}, using random init")

        model.eval()
        return model

    def extract(
        self,
        dataloader: DataLoader,
        model: nn.Module,
    ) -> tuple:
        """
        Remove FC layer, extract 512-dim penultimate features.
        Returns: (features: np.ndarray[N, 512], labels: np.ndarray[N])
        """
        feature_extractor = nn.Sequential(*list(model.children())[:-1])
        feature_extractor.eval()

        all_features = []
        all_labels = []

        with torch.no_grad():
            for images, labels in dataloader:
                images = images.to(self.device)
                feats = feature_extractor(images)
                feats = feats.squeeze(-1).squeeze(-1)  # [B, 512]
                all_features.append(feats.cpu().numpy())
                all_labels.append(labels.numpy())

        features = np.concatenate(all_features, axis=0)
        labels = np.concatenate(all_labels, axis=0)

        return features, labels

    def get_features(self) -> tuple:
        """
        Full pipeline: load data -> extract -> StandardScaler normalize.
        Returns: (X_train, y_train, X_test, y_test)
        Caches to cfg.results_dir/features_cache.npz
        """
        cache_path = os.path.join(self.cfg.results_dir, 'features_cache.npz')

        if os.path.exists(cache_path):
            print(f"Loading cached features from {cache_path}")
            data = np.load(cache_path)
            return data['X_train'], data['y_train'], data['X_test'], data['y_test']

        # Load CIFAR-10
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
        ])

        train_dataset = torchvision.datasets.CIFAR10(
            root=self.cfg.data_root, train=True, download=True, transform=transform
        )
        test_dataset = torchvision.datasets.CIFAR10(
            root=self.cfg.data_root, train=False, download=True, transform=transform
        )

        # Create subsets
        np.random.seed(self.cfg.subset_seed)
        train_indices = np.random.permutation(len(train_dataset))[:self.cfg.train_subset_size]
        test_indices = np.random.permutation(len(test_dataset))[:self.cfg.test_subset_size]

        train_subset = Subset(train_dataset, train_indices)
        test_subset = Subset(test_dataset, test_indices)

        train_loader = DataLoader(train_subset, batch_size=256, shuffle=False)
        test_loader = DataLoader(test_subset, batch_size=256, shuffle=False)

        # Load model and extract features
        model = self.load_resnet()
        print("Extracting training features...")
        X_train_raw, y_train = self.extract(train_loader, model)
        print("Extracting test features...")
        X_test_raw, y_test = self.extract(test_loader, model)

        # Normalize with StandardScaler
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train_raw)
        X_test = scaler.transform(X_test_raw)

        # Cache
        np.savez(
            cache_path,
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
        )
        print(f"Features cached to {cache_path}")

        return X_train, y_train, X_test, y_test
