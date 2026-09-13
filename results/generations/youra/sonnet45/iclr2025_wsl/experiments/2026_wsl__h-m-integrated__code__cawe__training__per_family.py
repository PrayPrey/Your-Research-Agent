"""Per-Family Ablation Training Module for h-m-integrated.

Trains separate CAWE models on single-architecture subsets (CNN-only, Transformer-only, MLP-only)
to validate that the compositional mechanism preserves architecture-specific signals.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from typing import Dict, Tuple, List
from scipy.stats import spearmanr
import numpy as np


class PerFamilyTrainer:
    """Trainer for per-family ablation experiments."""

    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        test_loader: DataLoader,
        lr: float = 1e-4,
        weight_decay: float = 1e-2,
        epochs: int = 100,
        patience: int = 10,
        device: str = 'cuda'
    ):
        """Initialize trainer.

        Args:
            model: CAWE model
            train_loader: Training dataloader
            val_loader: Validation dataloader
            test_loader: Test dataloader
            lr: Learning rate
            weight_decay: Weight decay
            epochs: Max training epochs
            patience: Early stopping patience
            device: Device to use
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.test_loader = test_loader
        self.epochs = epochs
        self.patience = patience
        self.device = device

        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=lr,
            weight_decay=weight_decay
        )
        self.criterion = nn.MSELoss()

    def train_single_family(self, family: str) -> Dict[str, float]:
        """Train on single architecture family.

        Args:
            family: Architecture family ('cnn', 'transformer', 'mlp')

        Returns:
            Dict with metrics: {'spearman_rho': float, 'best_loss': float}
        """
        # Filter datasets by architecture family
        train_loader = self._filter_by_family(self.train_loader, family)
        val_loader = self._filter_by_family(self.val_loader, family)
        test_loader = self._filter_by_family(self.test_loader, family)

        print(f"\n=== Training on {family.upper()} family ===")
        print(f"Train samples: {len(train_loader.dataset)}")
        print(f"Val samples: {len(val_loader.dataset)}")
        print(f"Test samples: {len(test_loader.dataset)}")

        best_val_loss = float('inf')
        patience_counter = 0

        for epoch in range(self.epochs):
            # Training
            train_loss = self._train_epoch(train_loader, family)
            val_loss = self._validate_epoch(val_loader, family)

            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{self.epochs}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}")

            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
            else:
                patience_counter += 1

            if patience_counter >= self.patience:
                print(f"Early stopping at epoch {epoch+1}")
                break

        # Evaluate on test set
        spearman_rho = self._evaluate_spearman(test_loader, family)
        print(f"Test Spearman ρ: {spearman_rho:.4f}")

        return {
            'spearman_rho': spearman_rho,
            'best_loss': best_val_loss,
            'final_epoch': epoch + 1
        }

    def _filter_by_family(self, loader: DataLoader, family: str) -> DataLoader:
        """Filter dataloader by architecture family."""
        dataset = loader.dataset
        indices = [i for i, (_, arch, _) in enumerate(dataset) if arch == family]
        filtered_dataset = Subset(dataset, indices)
        return DataLoader(
            filtered_dataset,
            batch_size=loader.batch_size,
            shuffle=True if 'train' in str(loader) else False,
            num_workers=0
        )

    def _train_epoch(self, loader: DataLoader, family: str) -> float:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0

        for batch in loader:
            weights, arch_family, targets = batch
            weights = {k: v.to(self.device) for k, v in weights.items()}
            targets = targets.to(self.device)

            self.optimizer.zero_grad()
            outputs = self.model(weights, family)
            loss = self.criterion(outputs, targets)
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()

        return total_loss / len(loader)

    def _validate_epoch(self, loader: DataLoader, family: str) -> float:
        """Validate for one epoch."""
        self.model.eval()
        total_loss = 0

        with torch.no_grad():
            for batch in loader:
                weights, arch_family, targets = batch
                weights = {k: v.to(self.device) for k, v in weights.items()}
                targets = targets.to(self.device)

                outputs = self.model(weights, family)
                loss = self.criterion(outputs, targets)

                total_loss += loss.item()

        return total_loss / len(loader)

    def _evaluate_spearman(self, loader: DataLoader, family: str) -> float:
        """Evaluate Spearman correlation on test set."""
        self.model.eval()
        predictions = []
        targets_list = []

        with torch.no_grad():
            for batch in loader:
                weights, arch_family, targets = batch
                weights = {k: v.to(self.device) for k, v in weights.items()}

                outputs = self.model(weights, family)
                predictions.extend(outputs.cpu().numpy())
                targets_list.extend(targets.numpy())

        # Compute Spearman correlation
        rho, _ = spearmanr(predictions, targets_list)
        return float(rho)
