"""Training pipeline for NeuroSAT."""
import torch
import torch.nn as nn
from torch.optim import Adam, Optimizer
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from typing import Dict
import csv
from pathlib import Path


def unsupervised_loss(p_sat: torch.Tensor, is_sat: torch.Tensor) -> torch.Tensor:
    """
    NeuroSAT unsupervised loss.
    Args:
        p_sat: [B] probabilities
        is_sat: [B] labels
    Returns:
        loss: scalar
    """
    is_sat = is_sat.float()
    loss = -is_sat * torch.log(p_sat + 1e-8) - (1 - is_sat) * torch.log(1 - p_sat + 1e-8)
    return loss.mean()


def train_epoch(model: nn.Module, dataloader: DataLoader, optimizer: Optimizer, device: str) -> float:
    """Train one epoch. Returns: avg_loss"""
    model.train()
    total_loss = 0.0
    num_batches = 0

    for batch in dataloader:
        batch = batch.to(device)

        optimizer.zero_grad()

        # Forward pass
        l_emb, c_emb = model(batch)

        # Predict satisfiability
        p_sat = model.predict_sat(l_emb, batch.literal_batch)

        # Compute loss
        loss = unsupervised_loss(p_sat, batch.is_sat.squeeze())

        # Backward pass
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        num_batches += 1

    return total_loss / num_batches if num_batches > 0 else 0.0


def validate_epoch(model: nn.Module, dataloader: DataLoader, device: str) -> float:
    """Validate one epoch. Returns: avg_loss"""
    model.eval()
    total_loss = 0.0
    num_batches = 0

    with torch.no_grad():
        for batch in dataloader:
            batch = batch.to(device)

            # Forward pass
            l_emb, c_emb = model(batch)

            # Predict satisfiability
            p_sat = model.predict_sat(l_emb, batch.literal_batch)

            # Compute loss
            loss = unsupervised_loss(p_sat, batch.is_sat.squeeze())

            total_loss += loss.item()
            num_batches += 1

    return total_loss / num_batches if num_batches > 0 else 0.0


class Trainer:
    """Training orchestrator."""

    def __init__(self, model: nn.Module, train_loader: DataLoader, val_loader: DataLoader,
                 config: Dict, device: str, output_dir: str):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.config = config
        self.device = device
        self.output_dir = Path(output_dir)

        # Optimizer
        self.optimizer = Adam(
            model.parameters(),
            lr=config.get('lr', 1e-4),
            weight_decay=config.get('weight_decay', 1e-8)
        )

        # LR Scheduler
        self.scheduler = ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.5,
            patience=10
        )

        # Tracking
        self.best_val_loss = float('inf')
        self.patience_counter = 0
        self.history = []

    def train(self, epochs: int) -> Dict:
        """Train for epochs with early stopping."""
        patience = self.config.get('early_stopping_patience', 20)

        # CSV logging
        log_file = self.output_dir / 'training_log.csv'
        with open(log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['epoch', 'train_loss', 'val_loss', 'lr'])

        print(f"Starting training for {epochs} epochs...")

        for epoch in range(epochs):
            # Train
            train_loss = train_epoch(self.model, self.train_loader, self.optimizer, self.device)

            # Validate
            val_loss = validate_epoch(self.model, self.val_loader, self.device)

            # Update scheduler
            self.scheduler.step(val_loss)

            # Log
            current_lr = self.optimizer.param_groups[0]['lr']
            self.history.append({
                'epoch': epoch,
                'train_loss': train_loss,
                'val_loss': val_loss,
                'lr': current_lr
            })

            # Write to CSV
            with open(log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([epoch, train_loss, val_loss, current_lr])

            # Print progress
            if epoch % 10 == 0:
                print(f"Epoch {epoch}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}, lr={current_lr:.2e}")

            # Early stopping
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.patience_counter = 0
                self.save_checkpoint(self.output_dir / 'best_model.pt')
            else:
                self.patience_counter += 1
                if self.patience_counter >= patience:
                    print(f"Early stopping at epoch {epoch}")
                    break

        return {'history': self.history, 'best_val_loss': self.best_val_loss}

    def save_checkpoint(self, path: Path):
        """Save model checkpoint."""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'best_val_loss': self.best_val_loss,
        }, path)

    def load_checkpoint(self, path: Path):
        """Load model checkpoint."""
        checkpoint = torch.load(path)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.best_val_loss = checkpoint['best_val_loss']
