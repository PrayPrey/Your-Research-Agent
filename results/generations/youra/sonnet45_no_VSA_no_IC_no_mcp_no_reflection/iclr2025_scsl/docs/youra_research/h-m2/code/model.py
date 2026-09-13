"""
Model infrastructure for h-m2: Multi-architecture comparison (ResNet-50 vs ViT-B/16).
Reuses accuracy-based convergence from h-e1, extends to timm models.
"""

import torch
import torch.nn as nn
import timm
from typing import Literal


def create_model(arch_name: Literal['resnet50', 'vit_b16'], num_classes: int = 2) -> nn.Module:
    """
    Create architecture model from scratch (no pretraining).

    Args:
        arch_name: 'resnet50' or 'vit_b16'
        num_classes: Output classes (2 for binary)

    Returns:
        Model with binary classification head
    """
    if arch_name == 'resnet50':
        model = timm.create_model('resnet50', pretrained=False, num_classes=num_classes)
    elif arch_name == 'vit_b16':
        model = timm.create_model('vit_base_patch16_224', pretrained=False, num_classes=num_classes)
    else:
        raise ValueError(f"Unknown architecture: {arch_name}")

    return model


class AblationTrainer:
    """
    Trainer with accuracy-based convergence detection (reused from h-e1).

    Convergence criterion: first epoch reaching target_accuracy (default 90%).
    """

    def __init__(
        self,
        model: nn.Module,
        dataset_name: str,
        lr: float,
        weight_decay: float,
        device: str = 'cuda',
        target_accuracy: float = 0.70  # Lowered for CMNIST spurious correlation
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

        # Track history for debugging
        self.epoch_history = []

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

                # Apply masking for ablation
                # Spurious: keep color (channel info), blur digit shape
                # Core: remove color (gray), keep digit shape
                if variant == 'spurious':
                    images = TF.gaussian_blur(images, kernel_size=31)  # Stronger blur
                elif variant == 'core':
                    gray = TF.rgb_to_grayscale(images, num_output_channels=1)
                    images = gray.repeat(1, 3, 1, 1)  # Replicate to 3 channels

                outputs = self.model(images)
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        return correct / total if total > 0 else 0.0

    def train_epoch(self, dataloader, variant: Literal['spurious', 'core', 'baseline']):
        """Train one epoch with optional feature masking."""
        import torchvision.transforms.functional as TF

        self.model.train()
        total_loss = 0.0

        for images, labels in dataloader:
            images = images.to(self.device)
            labels = labels.to(self.device)

            # Apply masking
            if variant == 'spurious':
                images = TF.gaussian_blur(images, kernel_size=31)
            elif variant == 'core':
                gray = TF.rgb_to_grayscale(images, num_output_channels=1)
                images = gray.repeat(1, 3, 1, 1)

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
        train_loader,
        max_epochs: int
    ) -> int | None:
        """
        Train until target accuracy is reached.

        Returns:
            Convergence epoch (1-indexed), or None if not converged
        """
        for epoch in range(1, max_epochs + 1):
            # Train
            loss = self.train_epoch(train_loader, variant)

            # Check convergence
            acc = self.compute_accuracy(train_loader, variant)
            self.epoch_history.append({'epoch': epoch, 'loss': loss, 'acc': acc})
            print(f"Epoch {epoch:02d}: loss={loss:.4f}, acc={acc:.4f}")

            if acc >= self.target_accuracy:
                print(f"Converged at epoch {epoch} (accuracy={acc:.4f})")
                return epoch

        print(f"Did not converge within {max_epochs} epochs (final acc={acc:.4f})")
        return None
