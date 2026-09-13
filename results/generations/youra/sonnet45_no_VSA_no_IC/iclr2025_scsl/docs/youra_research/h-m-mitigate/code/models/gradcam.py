"""GradCAM wrapper for spurious region localization."""

import torch
import torch.nn as nn
from pytorch_grad_cam import GradCAM as _GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget


class GradCAMWrapper:
    """Wrapper for GradCAM to compute spurious masks."""

    def __init__(self, model: nn.Module, target_layer: nn.Module, device: torch.device):
        """
        Args:
            model: CNN model (e.g., ResNet-50)
            target_layer: Layer to compute CAM from (e.g., model.layer4[-1])
            device: torch device
        """
        self.model = model
        self.device = device
        self.gradcam = _GradCAM(model=model, target_layers=[target_layer])

    def compute_cam(self, images: torch.Tensor, targets: list) -> torch.Tensor:
        """Compute GradCAM heatmaps.

        Args:
            images: Input images (B, 3, H, W) - MUST be on correct device
            targets: List of ClassifierOutputTarget (length B)

        Returns:
            CAM heatmaps (B, H', W') in [0, 1]
        """
        # Ensure model is in eval mode
        was_training = self.model.training
        self.model.eval()

        # Images already on device from caller
        cams = self.gradcam(input_tensor=images, targets=targets)

        # Restore training mode
        if was_training:
            self.model.train()

        return torch.from_numpy(cams).to(self.device)

    def compute_difference_map(
        self,
        majority_images: torch.Tensor,
        majority_labels: torch.Tensor,
        minority_images: torch.Tensor,
        minority_labels: torch.Tensor,
        percentile_threshold: int = 75,
    ) -> torch.Tensor:
        """Compute majority vs minority CAM difference map.

        Args:
            majority_images: Majority group images (N_maj, 3, H, W)
            majority_labels: Majority group labels (N_maj,)
            minority_images: Minority group images (N_min, 3, H, W)
            minority_labels: Minority group labels (N_min,)
            percentile_threshold: Threshold percentile for mask (default 75)

        Returns:
            Binary mask (H', W') where 1 = spurious region
        """
        # Subsample to max 16 samples per group (computational overhead)
        n_maj = min(16, len(majority_images))
        n_min = min(16, len(minority_images))

        maj_imgs = majority_images[:n_maj]
        maj_labels = majority_labels[:n_maj]
        min_imgs = minority_images[:n_min]
        min_labels = minority_labels[:n_min]

        # Compute CAMs for majority group
        maj_targets = [
            ClassifierOutputTarget(label.item()) for label in maj_labels
        ]
        maj_cams = self.compute_cam(maj_imgs, maj_targets)  # (N_maj, H', W')

        # Compute CAMs for minority group
        min_targets = [
            ClassifierOutputTarget(label.item()) for label in min_labels
        ]
        min_cams = self.compute_cam(min_imgs, min_targets)  # (N_min, H', W')

        # Average across samples
        maj_cam_mean = maj_cams.mean(dim=0)  # (H', W')
        min_cam_mean = min_cams.mean(dim=0)  # (H', W')

        # Absolute difference
        diff = torch.abs(maj_cam_mean - min_cam_mean)  # (H', W')

        # Threshold at percentile
        threshold = torch.quantile(diff.flatten(), percentile_threshold / 100.0)
        mask = (diff > threshold).float()

        return mask


def create_gradcam_for_resnet50(model: nn.Module, device: torch.device) -> GradCAMWrapper:
    """Create GradCAM wrapper for ResNet-50.

    Args:
        model: ResNet-50 model
        device: torch device

    Returns:
        GradCAMWrapper instance targeting layer4[-1]
    """
    target_layer = model.layer4[-1]
    return GradCAMWrapper(model, target_layer, device)


def create_gradcam_for_resnet18(model: nn.Module, device: torch.device) -> GradCAMWrapper:
    """Create GradCAM wrapper for ResNet-18 (MNIST).

    Args:
        model: ResNet-18 model
        device: torch device

    Returns:
        GradCAMWrapper instance targeting layer4[-1]
    """
    target_layer = model.layer4[-1]
    return GradCAMWrapper(model, target_layer, device)
