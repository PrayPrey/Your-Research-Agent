"""Unified training loop for ERM and Gradient-Aware methods."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from pathlib import Path
from typing import Dict, List
import sys
sys.path.append(str(Path(__file__).parent))
from evaluator import evaluate_model


class Trainer:
    """Unified training loop supporting ERM and Gradient-Aware."""

    def __init__(
        self,
        model: nn.Module,
        optimizer,
        train_loader: DataLoader,
        val_loader: DataLoader,
        device: str = 'cuda',
        checkpoint_dir: str = './checkpoints'
    ):
        """Initialize trainer."""
        self.model = model.to(device)
        self.optimizer = optimizer
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True, parents=True)

    def train_epoch(self) -> float:
        """
        Train one epoch.

        Returns:
            average loss
        """
        self.model.train()
        total_loss = 0
        n_batches = 0

        for x, y, _ in self.train_loader:
            x, y = x.to(self.device), y.to(self.device)

            self.optimizer.zero_grad()
            logits = self.model(x)
            loss = F.cross_entropy(logits, y)
            loss.backward()

            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)

            self.optimizer.step()

            total_loss += loss.item()
            n_batches += 1

        return total_loss / max(n_batches, 1)

    def validate(self) -> Dict[str, float]:
        """
        Validate on val set.

        Returns:
            {avg_acc, worst_group_acc, per_group_acc}
        """
        return evaluate_model(self.model, self.val_loader, self.device)

    def run(self, epochs: int) -> Dict[str, List[float]]:
        """
        Run training for N epochs.

        Returns:
            {train_loss: [...], val_wg_acc: [...]}
        """
        history = {'train_loss': [], 'val_wg_acc': []}
        best_wg_acc = 0.0

        for epoch in range(epochs):
            loss = self.train_epoch()
            metrics = self.validate()

            history['train_loss'].append(loss)
            history['val_wg_acc'].append(metrics['worst_group_acc'])

            # Checkpoint best model
            if metrics['worst_group_acc'] > best_wg_acc:
                best_wg_acc = metrics['worst_group_acc']
                torch.save(
                    self.model.state_dict(),
                    self.checkpoint_dir / 'best_model.pt'
                )

            if (epoch + 1) % 5 == 0:
                print(f"Epoch {epoch+1}/{epochs}: "
                      f"Loss={loss:.4f}, "
                      f"WG-Acc={metrics['worst_group_acc']:.2f}%")

        return history
