"""
Model infrastructure for h-e1: ResNet baseline with gradient tracking.
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
    Trainer with gradient norm tracking and convergence detection.

    Convergence criterion: gradient norm < 10% of peak for 3 consecutive epochs.
    """

    def __init__(
        self,
        model: nn.Module,
        dataset_name: str,
        lr: float,
        weight_decay: float,
        device: str = 'cuda'
    ):
        self.model = model.to(device)
        self.dataset_name = dataset_name
        self.device = device

        self.optimizer = torch.optim.SGD(
            model.parameters(),
            lr=lr,
            momentum=0.9,
            weight_decay=weight_decay
        )
        self.criterion = nn.CrossEntropyLoss()

        # Gradient tracking
        self.grad_norms = []
        self.peak_grad_norm = 0.0
        self.convergence_window = []

    def compute_gradient_norm(self) -> float:
        """Compute L2 norm of all model gradients."""
        total_norm = 0.0
        for p in self.model.parameters():
            if p.grad is not None:
                total_norm += p.grad.data.norm(2).item() ** 2
        return total_norm ** 0.5

    def check_convergence(self, threshold: float = 0.1, window: int = 3) -> bool:
        """
        Check if gradient norm has converged.

        Returns True if grad_norm < threshold * peak_grad_norm
        for `window` consecutive epochs.
        """
        if len(self.grad_norms) < window:
            return False

        if self.peak_grad_norm == 0.0:
            return False

        recent_norms = self.grad_norms[-window:]
        threshold_value = threshold * self.peak_grad_norm

        return all(norm < threshold_value for norm in recent_norms)

    def train_epoch(self, dataloader, variant: Literal['spurious', 'core', 'baseline']):
        """
        Train one epoch with optional feature masking.

        variant:
            - 'spurious': Apply spurious mask to isolate spurious feature
            - 'core': Apply core mask to isolate core feature
            - 'baseline': No masking (standard ERM)
        """
        from data import apply_spurious_mask, apply_core_mask

        self.model.train()
        total_loss = 0.0

        for images, labels in dataloader:
            images = images.to(self.device)
            labels = labels.to(self.device)

            # Apply masking based on variant
            if variant == 'spurious':
                images = apply_spurious_mask(images, self.dataset_name)
            elif variant == 'core':
                images = apply_core_mask(images, self.dataset_name)
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
        Train with gradient tracking until convergence.

        Returns:
            Convergence epoch (1-indexed) or None if no convergence by max_epochs.
        """
        self.grad_norms = []
        self.peak_grad_norm = 0.0

        for epoch in range(1, max_epochs + 1):
            avg_loss = self.train_epoch(dataloader, variant)

            # Compute gradient norm after epoch
            # Need to do one backward pass to populate gradients
            # Use validation set for this (approximation)
            self.model.eval()
            with torch.no_grad():
                sample_images, sample_labels = next(iter(dataloader))
                sample_images = sample_images.to(self.device)
                sample_labels = sample_labels.to(self.device)

                if variant == 'spurious':
                    from data import apply_spurious_mask
                    sample_images = apply_spurious_mask(sample_images, self.dataset_name)
                elif variant == 'core':
                    from data import apply_core_mask
                    sample_images = apply_core_mask(sample_images, self.dataset_name)

            # Compute gradient on sample
            self.model.train()
            self.optimizer.zero_grad()
            outputs = self.model(sample_images)
            loss = self.criterion(outputs, sample_labels)
            loss.backward()

            grad_norm = self.compute_gradient_norm()
            self.grad_norms.append(grad_norm)

            # Update peak
            if grad_norm > self.peak_grad_norm:
                self.peak_grad_norm = grad_norm

            # Check convergence
            if self.check_convergence():
                return epoch

            if epoch % 10 == 0:
                print(f"  Epoch {epoch}/{max_epochs} | Loss: {avg_loss:.4f} | GradNorm: {grad_norm:.4f}")

        # No convergence
        return None
