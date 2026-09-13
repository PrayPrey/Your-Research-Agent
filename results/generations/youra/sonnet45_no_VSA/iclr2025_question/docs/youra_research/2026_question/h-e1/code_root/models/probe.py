"""Uncertainty probe models and training."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
from torch.optim.lr_scheduler import LinearLR, CosineAnnealingLR, SequentialLR
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import roc_auc_score
from tqdm import tqdm
import numpy as np


class UncertaintyProbe(nn.Module):
    """2-layer MLP probe for binary correctness prediction."""

    def __init__(self, hidden_dim=4096, probe_dim=128, dropout=0.1):
        super().__init__()
        self.probe = nn.Sequential(
            nn.Linear(hidden_dim, probe_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(probe_dim, 1),
            nn.Sigmoid()
        )

    def forward(self, hidden_states):
        """Forward pass. x: [N, 4096] -> [N, 1]"""
        return self.probe(hidden_states)


class HiddenStateDataset(Dataset):
    """Dataset for probe training."""

    def __init__(self, hidden_states, labels):
        self.hidden_states = torch.tensor(hidden_states, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.float32).unsqueeze(1)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.hidden_states[idx], self.labels[idx]


class ProbeTrainer:
    """Probe trainer with early stopping."""

    def __init__(self, probe, config, device="cuda"):
        self.probe = probe.to(device)
        self.config = config
        self.device = device
        self.best_auroc = 0.0
        self.patience_counter = 0

    def train_epoch(self, train_loader):
        """Train one epoch."""
        self.probe.train()
        total_loss = 0.0
        all_preds = []
        all_labels = []

        for hidden_states, labels in train_loader:
            hidden_states = hidden_states.to(self.device)
            labels = labels.to(self.device)

            # Forward
            preds = self.probe(hidden_states)
            loss = F.binary_cross_entropy(preds, labels)

            # Backward
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()
            all_preds.extend(preds.detach().cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

        avg_loss = total_loss / len(train_loader)
        train_auroc = roc_auc_score(all_labels, all_preds)
        return avg_loss, train_auroc

    def validate(self, val_loader):
        """Validate probe."""
        self.probe.eval()
        total_loss = 0.0
        all_preds = []
        all_labels = []

        with torch.no_grad():
            for hidden_states, labels in val_loader:
                hidden_states = hidden_states.to(self.device)
                labels = labels.to(self.device)

                preds = self.probe(hidden_states)
                loss = F.binary_cross_entropy(preds, labels)

                total_loss += loss.item()
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())

        avg_loss = total_loss / len(val_loader)
        val_auroc = roc_auc_score(all_labels, all_preds)
        return avg_loss, val_auroc

    def train(self, train_hidden, train_labels, val_hidden, val_labels, layer_name):
        """Full training with early stopping."""
        # Create datasets
        train_dataset = HiddenStateDataset(train_hidden, train_labels)
        val_dataset = HiddenStateDataset(val_hidden, val_labels)

        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.BATCH_SIZE,
            shuffle=True
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.BATCH_SIZE,
            shuffle=False
        )

        # Optimizer and scheduler
        self.optimizer = AdamW(
            self.probe.parameters(),
            lr=self.config.LEARNING_RATE,
            weight_decay=self.config.WEIGHT_DECAY
        )

        warmup_scheduler = LinearLR(
            self.optimizer,
            start_factor=0.1,
            total_iters=self.config.WARMUP_STEPS
        )
        cosine_scheduler = CosineAnnealingLR(
            self.optimizer,
            T_max=self.config.EPOCHS * len(train_loader)
        )

        print(f"\nTraining probe for {layer_name}...")
        best_epoch = 0

        for epoch in range(self.config.EPOCHS):
            # Train
            train_loss, train_auroc = self.train_epoch(train_loader)

            # Validate
            val_loss, val_auroc = self.validate(val_loader)

            print(f"Epoch {epoch+1}/{self.config.EPOCHS} | "
                  f"Train Loss: {train_loss:.4f}, AUROC: {train_auroc:.4f} | "
                  f"Val Loss: {val_loss:.4f}, AUROC: {val_auroc:.4f}")

            # Early stopping check
            if val_auroc > self.best_auroc:
                self.best_auroc = val_auroc
                best_epoch = epoch
                self.patience_counter = 0
                # Save best model
                self.save_checkpoint(layer_name, epoch, val_auroc)
            else:
                self.patience_counter += 1
                if self.patience_counter >= self.config.EARLY_STOPPING_PATIENCE:
                    print(f"Early stopping at epoch {epoch+1}")
                    break

            # Step schedulers
            if epoch * len(train_loader) < self.config.WARMUP_STEPS:
                warmup_scheduler.step()
            else:
                cosine_scheduler.step()

        print(f"Best validation AUROC: {self.best_auroc:.4f} at epoch {best_epoch+1}")
        return {
            'best_auroc': self.best_auroc,
            'best_epoch': best_epoch
        }

    def save_checkpoint(self, layer_name, epoch, auroc):
        """Save checkpoint."""
        import os
        checkpoint_path = os.path.join(
            self.config.CHECKPOINT_DIR,
            f"probe_{layer_name}_best.pth"
        )
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.probe.state_dict(),
            'auroc': auroc,
            'layer': layer_name
        }, checkpoint_path)

    def load_checkpoint(self, layer_name):
        """Load checkpoint."""
        import os
        checkpoint_path = os.path.join(
            self.config.CHECKPOINT_DIR,
            f"probe_{layer_name}_best.pth"
        )
        checkpoint = torch.load(checkpoint_path)
        self.probe.load_state_dict(checkpoint['model_state_dict'])
        return checkpoint
