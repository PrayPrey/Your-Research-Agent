"""Common utilities for training and evaluation."""

import random

import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def create_resnet50(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """Create ResNet-50 with modified FC layer.

    Args:
        num_classes: Number of output classes
        pretrained: Use ImageNet pretrained weights

    Returns:
        ResNet-50 model
    """
    if pretrained:
        model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    else:
        model = models.resnet50(weights=None)

    # Replace FC layer
    model.fc = nn.Linear(model.fc.in_features, num_classes)

    return model


def create_resnet18(num_classes: int = 10, pretrained: bool = False) -> nn.Module:
    """Create ResNet-18 for MNIST+Color.

    Args:
        num_classes: Number of output classes (10 for MNIST)
        pretrained: Use ImageNet pretrained weights

    Returns:
        ResNet-18 model
    """
    if pretrained:
        model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    else:
        model = models.resnet18(weights=None)

    # Modify first conv layer for 28x28 input
    model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    model.maxpool = nn.Identity()

    # Replace FC layer
    model.fc = nn.Linear(model.fc.in_features, num_classes)

    return model


def get_train_transforms() -> transforms.Compose:
    """Training augmentation for Waterbirds (224x224)."""
    return transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
            ),
        ]
    )


def get_eval_transforms() -> transforms.Compose:
    """Evaluation preprocessing for Waterbirds (224x224)."""
    return transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
            ),
        ]
    )


def get_mnist_transforms() -> transforms.Compose:
    """MNIST+Color transforms (no normalization - already RGB)."""
    return transforms.Compose([transforms.ToTensor()])


class GroupTracker:
    """Track per-group metrics during training/validation."""

    def __init__(self, num_groups: int = 4):
        self.num_groups = num_groups
        self.reset()

    def reset(self):
        """Reset accumulators."""
        self.group_correct = [0] * self.num_groups
        self.group_total = [0] * self.num_groups
        self.total_correct = 0
        self.total_samples = 0

    def update(self, predictions: torch.Tensor, labels: torch.Tensor, group_ids: torch.Tensor):
        """Update metrics from batch.

        Args:
            predictions: Model predictions (B,)
            labels: Ground truth labels (B,)
            group_ids: Group IDs (B,) in range [0, num_groups-1]
        """
        correct = (predictions == labels).cpu().numpy()
        labels = labels.cpu().numpy()
        group_ids = group_ids.cpu().numpy()

        for g in range(self.num_groups):
            mask = group_ids == g
            self.group_correct[g] += correct[mask].sum()
            self.group_total[g] += mask.sum()

        self.total_correct += correct.sum()
        self.total_samples += len(labels)

    def compute_metrics(self) -> dict:
        """Compute worst-group accuracy (WGA) and average accuracy.

        Returns:
            {
                "wga": float,
                "avg_acc": float,
                "group_0_acc": float,
                "group_1_acc": float,
                "group_2_acc": float,
                "group_3_acc": float,
            }
        """
        group_accs = []
        for g in range(self.num_groups):
            if self.group_total[g] > 0:
                acc = self.group_correct[g] / self.group_total[g]
            else:
                acc = 0.0
            group_accs.append(acc)

        wga = min(group_accs) if group_accs else 0.0
        avg_acc = self.total_correct / self.total_samples if self.total_samples > 0 else 0.0

        metrics = {"wga": wga, "avg_acc": avg_acc}
        for g in range(self.num_groups):
            metrics[f"group_{g}_acc"] = group_accs[g]

        return metrics
