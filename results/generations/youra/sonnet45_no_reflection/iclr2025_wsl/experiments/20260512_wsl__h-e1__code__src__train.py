"""Training pipeline"""

import torch
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader
from typing import Dict, List
from .loss import combined_loss, reconstruction_loss


class Trainer:
    """Training orchestrator"""

    def __init__(
        self,
        model: torch.nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        config: dict,
        device: str = 'cuda'
    ):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.config = config
        self.device = device

        self.optimizer = setup_optimizer(
            model,
            lr=config['learning_rate'],
            weight_decay=config['weight_decay']
        )

        self.scheduler = setup_scheduler(
            self.optimizer,
            T_max=config['T_max']
        )

        self.best_val_loss = float('inf')
        self.patience_counter = 0

    def train_epoch(self, epoch: int, lambda_equiv: float) -> Dict[str, float]:
        """Train one epoch"""
        self.model.train()
        total_loss = 0.0
        total_recon = 0.0
        total_equiv = 0.0
        num_batches = 0

        for batch in self.train_loader:
            weights = batch['weights'].to(self.device)
            arch_labels = batch['arch_label'].to(self.device)

            self.optimizer.zero_grad()

            loss, recon_loss, equiv_loss = combined_loss(
                self.model,
                weights,
                arch_labels,
                lambda_equiv
            )

            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()
            total_recon += recon_loss.item()
            total_equiv += equiv_loss.item()
            num_batches += 1

        return {
            'loss': total_loss / num_batches,
            'recon_loss': total_recon / num_batches,
            'equiv_loss': total_equiv / num_batches
        }

    def validate(self) -> Dict[str, float]:
        """Validate on val set"""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0

        with torch.no_grad():
            for batch in self.val_loader:
                weights = batch['weights'].to(self.device)
                arch_labels = batch['arch_label'].to(self.device)

                z = self.model(weights, arch_labels)
                weights_recon = self.model.reconstruct_weights(z)

                loss = reconstruction_loss(weights, weights_recon)
                total_loss += loss.item()
                num_batches += 1

        return {'val_loss': total_loss / num_batches}

    def train(self, num_epochs: int, lambda_equiv: float = 0.5) -> Dict[str, List[float]]:
        """Full training loop"""
        history = {
            'train_loss': [],
            'recon_loss': [],
            'equiv_loss': [],
            'val_loss': []
        }

        for epoch in range(num_epochs):
            train_metrics = self.train_epoch(epoch, lambda_equiv)
            val_metrics = self.validate()

            history['train_loss'].append(train_metrics['loss'])
            history['recon_loss'].append(train_metrics['recon_loss'])
            history['equiv_loss'].append(train_metrics['equiv_loss'])
            history['val_loss'].append(val_metrics['val_loss'])

            # Early stopping
            if val_metrics['val_loss'] < self.best_val_loss - self.config['min_delta']:
                self.best_val_loss = val_metrics['val_loss']
                self.patience_counter = 0
                self.save_checkpoint(self.config['checkpoint_dir'] + '/best_model.pt', val_metrics)
            else:
                self.patience_counter += 1

            if self.patience_counter >= self.config['patience']:
                print(f"Early stopping at epoch {epoch}")
                break

            self.scheduler.step()

            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{num_epochs} - "
                      f"Loss: {train_metrics['loss']:.4f}, "
                      f"Val: {val_metrics['val_loss']:.4f}")

        return history

    def save_checkpoint(self, path: str, metrics: dict):
        """Save model checkpoint"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'metrics': metrics
        }, path)

    def load_checkpoint(self, path: str):
        """Load model checkpoint"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])


def setup_optimizer(
    model: torch.nn.Module,
    lr: float = 1e-3,
    weight_decay: float = 1e-4
) -> optim.Optimizer:
    """Create Adam optimizer"""
    return optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)


def setup_scheduler(
    optimizer: optim.Optimizer,
    T_max: int = 100
) -> CosineAnnealingLR:
    """Create cosine annealing scheduler"""
    return CosineAnnealingLR(optimizer, T_max=T_max)
