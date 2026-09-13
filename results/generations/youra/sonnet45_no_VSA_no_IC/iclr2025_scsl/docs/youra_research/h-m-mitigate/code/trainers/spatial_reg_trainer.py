"""Spatial gradient regularization trainer for spurious mitigation."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

from utils.common import GroupTracker


class SpatialRegTrainer:
    """Trainer with spatial gradient regularization.

    Penalizes gradient divergence in GradCAM-identified spurious regions.
    """

    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        device: torch.device,
        config: dict,
        gradcam_wrapper=None,
    ):
        """
        Args:
            model: CNN model
            train_loader: Training DataLoader
            val_loader: Validation DataLoader
            device: torch device
            config: {lr, lambda_init, percentile_threshold, epochs, patience}
            gradcam_wrapper: GradCAMWrapper instance (optional, created if None)
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.config = config

        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.SGD(
            model.parameters(),
            lr=config["lr"],
            momentum=config.get("momentum", 0.9),
            weight_decay=config.get("weight_decay", 1e-4),
        )

        self.lambda_penalty = config["lambda_init"]
        self.percentile_threshold = config["percentile_threshold"]
        self.tracker = GroupTracker()

        # GradCAM for spurious mask computation
        if gradcam_wrapper is None:
            from models.gradcam import create_gradcam_for_resnet50

            self.gradcam = create_gradcam_for_resnet50(model, device)
        else:
            self.gradcam = gradcam_wrapper

        self.cached_mask = None
        self.best_wga = 0.0
        self.best_epoch = 0
        self.patience_counter = 0

    def compute_spurious_mask(
        self, imgs: torch.Tensor, labels: torch.Tensor, group_ids: torch.Tensor
    ) -> torch.Tensor:
        """Compute spurious mask from GradCAM difference.

        Args:
            imgs: Batch images (B, 3, H, W)
            labels: Batch labels (B,)
            group_ids: Batch group IDs (B,)

        Returns:
            mask: Binary mask (H', W') in [0, 1]
        """
        # Identify majority and minority samples
        # Majority: groups 0 and 2, Minority: groups 1 and 3
        majority_mask = (group_ids == 0) | (group_ids == 2)
        minority_mask = (group_ids == 1) | (group_ids == 3)

        # Handle edge case: no samples in either group
        if majority_mask.sum() == 0 or minority_mask.sum() == 0:
            # Return zero mask
            return torch.zeros(7, 7, device=self.device)

        # Extract samples (ensure on correct device)
        maj_imgs = imgs[majority_mask].to(self.device)
        maj_labels = labels[majority_mask].to(self.device)
        min_imgs = imgs[minority_mask].to(self.device)
        min_labels = labels[minority_mask].to(self.device)

        # Compute difference map
        mask = self.gradcam.compute_difference_map(
            maj_imgs,
            maj_labels,
            min_imgs,
            min_labels,
            percentile_threshold=self.percentile_threshold,
        )

        return mask

    def compute_regularization_loss(
        self, imgs: torch.Tensor, mask: torch.Tensor
    ) -> torch.Tensor:
        """Compute gradient variance penalty on masked regions.

        Args:
            imgs: Batch images (B, 3, H, W) - REQUIRES GRAD
            mask: Binary mask (H', W')

        Returns:
            Scalar regularization loss
        """
        # Enable gradients on input
        imgs.requires_grad_(True)

        # Forward pass
        outputs = self.model(imgs)

        # Compute gradients w.r.t. input
        grads = torch.autograd.grad(
            outputs.sum(), imgs, create_graph=True, retain_graph=True
        )[0]  # (B, 3, H, W)

        # Variance across channels
        var_spatial = grads.var(dim=1)  # (B, H, W)

        # Resize mask to match spatial dimensions
        mask_resized = F.interpolate(
            mask.unsqueeze(0).unsqueeze(0), size=var_spatial.shape[1:], mode="nearest"
        ).squeeze()  # (H, W)

        # Masked variance
        masked_var = var_spatial * mask_resized.unsqueeze(0)

        # Mean over batch and spatial dimensions
        return masked_var.mean()

    def train_epoch(self, epoch: int) -> dict:
        """Train for one epoch.

        Returns:
            {loss, wga, avg_acc}
        """
        self.model.train()
        self.tracker.reset()

        total_loss = 0.0
        total_ce_loss = 0.0
        total_reg_loss = 0.0
        n_batches = 0

        for batch_idx, (imgs, labels, metadata) in enumerate(self.train_loader):
            imgs, labels = imgs.to(self.device), labels.to(self.device)
            group_ids = metadata[:, 2].to(self.device)

            # Update cached mask every 10 batches (reduce GradCAM overhead)
            if batch_idx % 10 == 0:
                # GradCAM needs gradients, don't use no_grad()
                self.cached_mask = self.compute_spurious_mask(
                    imgs, labels, group_ids
                )

            # Classification loss
            outputs = self.model(imgs)
            loss_ce = self.criterion(outputs, labels)

            # Regularization loss
            loss_reg = self.compute_regularization_loss(imgs, self.cached_mask)

            # Total loss
            loss = loss_ce + self.lambda_penalty * loss_reg

            # Backprop
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            # Track metrics
            preds = outputs.argmax(dim=1)
            self.tracker.update(preds, labels, group_ids)

            total_loss += loss.item()
            total_ce_loss += loss_ce.item()
            total_reg_loss += loss_reg.item()
            n_batches += 1

        metrics = self.tracker.compute_metrics()
        metrics["loss"] = total_loss / n_batches
        metrics["ce_loss"] = total_ce_loss / n_batches
        metrics["reg_loss"] = total_reg_loss / n_batches
        metrics["lambda"] = self.lambda_penalty

        return metrics

    def validate(self) -> dict:
        """Validate and adaptively adjust lambda.

        Returns:
            {loss, wga, avg_acc}
        """
        self.model.eval()
        self.tracker.reset()

        total_loss = 0.0
        n_batches = 0

        with torch.no_grad():
            for imgs, labels, metadata in self.val_loader:
                imgs, labels = imgs.to(self.device), labels.to(self.device)
                group_ids = metadata[:, 2].to(self.device)

                outputs = self.model(imgs)
                loss = self.criterion(outputs, labels)

                preds = outputs.argmax(dim=1)
                self.tracker.update(preds, labels, group_ids)

                total_loss += loss.item()
                n_batches += 1

        metrics = self.tracker.compute_metrics()
        metrics["loss"] = total_loss / n_batches

        # Adaptive lambda scaling based on WGA gap
        majority_accs = [metrics["group_0_acc"], metrics["group_2_acc"]]
        minority_accs = [metrics["group_1_acc"], metrics["group_3_acc"]]
        wga_gap = sum(majority_accs) / 2 - sum(minority_accs) / 2

        # Exponential scaling: increase lambda if gap is large
        self.lambda_penalty *= torch.exp(torch.tensor(0.1 * wga_gap)).item()
        self.lambda_penalty = max(0.001, min(1.0, self.lambda_penalty))  # Clamp

        return metrics

    def fit(self) -> dict:
        """Train with early stopping.

        Returns:
            {best_wga, best_epoch}
        """
        epochs = self.config["epochs"]
        patience = self.config.get("patience", 10)

        for epoch in range(epochs):
            train_metrics = self.train_epoch(epoch)
            val_metrics = self.validate()

            print(
                f"Epoch {epoch+1}/{epochs}: "
                f"Train Loss={train_metrics['loss']:.4f}, "
                f"Val WGA={val_metrics['wga']:.4f}, "
                f"Lambda={self.lambda_penalty:.4f}"
            )

            # Early stopping on WGA
            if val_metrics["wga"] > self.best_wga:
                self.best_wga = val_metrics["wga"]
                self.best_epoch = epoch
                self.patience_counter = 0
            else:
                self.patience_counter += 1

            if self.patience_counter >= patience:
                print(f"Early stopping at epoch {epoch+1}")
                break

        return {"best_wga": self.best_wga, "best_epoch": self.best_epoch}
