"""Empirical Risk Minimization (ERM) baseline trainer."""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from utils.common import GroupTracker


class ERMTrainer:
    """Standard ERM trainer (no group balancing or regularization)."""

    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        device: torch.device,
        config: dict,
    ):
        """
        Args:
            model: CNN model
            train_loader: Training DataLoader
            val_loader: Validation DataLoader
            device: torch device
            config: {lr, epochs, patience}
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

        self.tracker = GroupTracker()
        self.best_wga = 0.0
        self.best_epoch = 0
        self.patience_counter = 0

    def train_epoch(self, epoch: int) -> dict:
        """Train for one epoch.

        Returns:
            {loss, wga, avg_acc}
        """
        self.model.train()
        self.tracker.reset()

        total_loss = 0.0
        n_batches = 0

        for imgs, labels, metadata in self.train_loader:
            imgs, labels = imgs.to(self.device), labels.to(self.device)
            group_ids = metadata[:, 2].to(self.device)

            # Forward
            outputs = self.model(imgs)
            loss = self.criterion(outputs, labels)

            # Backprop
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            # Track metrics
            preds = outputs.argmax(dim=1)
            self.tracker.update(preds, labels, group_ids)

            total_loss += loss.item()
            n_batches += 1

        metrics = self.tracker.compute_metrics()
        metrics["loss"] = total_loss / n_batches

        return metrics

    def validate(self) -> dict:
        """Validate.

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
                f"Val WGA={val_metrics['wga']:.4f}"
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
