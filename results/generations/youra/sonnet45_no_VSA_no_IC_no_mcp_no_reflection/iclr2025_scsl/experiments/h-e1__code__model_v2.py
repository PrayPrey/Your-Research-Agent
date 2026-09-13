"""
Model infrastructure v2: Accuracy-based convergence for PoC validation.

Simpler convergence criterion: first epoch reaching 90% train accuracy.
"""

import torch
import torch.nn as nn
from torchvision import models
from typing import Literal


def get_baseline_model(dataset_name: str, pretrained: bool = True) -> nn.Module:
    """
    Load ResNet baseline model with ImageNet initialization.

    ResNet-18 for CMNIST, ResNet-50 for Waterbirds/CelebA/NICO++.
    Final FC layer replaced with binary classification head.
    """
    if dataset_name == 'CMNIST':
        model = models.resnet18(weights='IMAGENET1K_V1' if pretrained else None)
        in_features = model.fc.in_features
    else:
        model = models.resnet50(weights='IMAGENET1K_V1' if pretrained else None)
        in_features = model.fc.in_features

    # Replace final FC with binary classifier
    model.fc = nn.Linear(in_features, 2)

    return model


class AblationTrainer:
    """
    Trainer with accuracy-based convergence detection.

    Convergence criterion: first epoch reaching target_accuracy (default 90%).
    """

    def __init__(
        self,
        model: nn.Module,
        dataset_name: str,
        lr: float,
        weight_decay: float,
        device: str = 'cuda',
        target_accuracy: float = 0.90
    ):
        self.model = model.to(device)
        self.dataset_name = dataset_name
        self.device = device
        self.target_accuracy = target_accuracy

        self.optimizer = torch.optim.SGD(
            model.parameters(),
            lr=lr,
            momentum=0.9,
            weight_decay=weight_decay
        )
        self.criterion = nn.CrossEntropyLoss()

    def compute_accuracy(self, dataloader, variant: Literal['spurious', 'core', 'baseline']) -> float:
        """Compute classification accuracy on dataloader with variant-specific masking."""
        import torchvision.transforms.functional as TF

        self.model.eval()
        correct = 0
        total = 0

        with torch.no_grad():
            for images, labels in dataloader:
                images = images.to(self.device)
                labels = labels.to(self.device)

                # Apply same masking as training
                if variant == 'spurious':
                    images = TF.gaussian_blur(images, kernel_size=15)
                elif variant == 'core':
                    images = TF.rgb_to_grayscale(images, num_output_channels=3)

                outputs = self.model(images)
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        return correct / total if total > 0 else 0.0

    def train_epoch(self, dataloader, variant: Literal['spurious', 'core', 'baseline']):
        """
        Train one epoch with optional feature masking.

        variant:
            - 'spurious': Apply spurious mask to isolate spurious feature
            - 'core': Apply core mask to isolate core feature
            - 'baseline': No masking (standard ERM)
        """
        import torchvision.transforms.functional as TF

        self.model.train()
        total_loss = 0.0

        for images, labels in dataloader:
            images = images.to(self.device)
            labels = labels.to(self.device)

            # Apply masking based on variant
            if variant == 'spurious':
                # Spurious-only (CMNIST: blur to destroy shape, keep color)
                images = TF.gaussian_blur(images, kernel_size=15)
            elif variant == 'core':
                # Core-only (CMNIST: grayscale to destroy color, keep shape)
                images = TF.rgb_to_grayscale(images, num_output_channels=3)
            # else: baseline, no masking

            self.optimizer.zero_grad()
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()

        return total_loss / len(dataloader)

    def train_variant(
        self,
        variant: Literal['spurious', 'core', 'baseline'],
        dataloader,
        max_epochs: int
    ) -> int | None:
        """
        Train until target accuracy reached.

        Returns:
            Convergence epoch (1-indexed) or None if target not reached by max_epochs.
        """
        for epoch in range(1, max_epochs + 1):
            avg_loss = self.train_epoch(dataloader, variant)

            # Compute accuracy (pass variant for consistent masking)
            accuracy = self.compute_accuracy(dataloader, variant)

            if epoch % 5 == 0:
                print(f"  Epoch {epoch}/{max_epochs} | Loss: {avg_loss:.4f} | Acc: {accuracy:.2%}")

            # Check convergence
            if accuracy >= self.target_accuracy:
                print(f"  → Converged at epoch {epoch} (accuracy {accuracy:.2%})")
                return epoch

        # No convergence
        print(f"  → NO CONVERGENCE (final accuracy {accuracy:.2%})")
        return None
