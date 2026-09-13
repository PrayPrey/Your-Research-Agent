"""Training utilities for ERM and DRO endpoints"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def train_erm(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    device: str = "cuda",
    epochs: int = 5,
    lr: float = 0.001,
    weight_decay: float = 0.0001,
    save_path: str = None
) -> nn.Module:
    """
    Train ERM (Empirical Risk Minimization) model.

    Args:
        model: ResNet-50 model
        train_loader: Training data loader
        val_loader: Validation data loader
        device: Device for training
        epochs: Number of epochs
        lr: Learning rate
        weight_decay: Weight decay
        save_path: Path to save checkpoint

    Returns:
        Trained model
    """
    logger.info("Training ERM model...")
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for batch_idx, batch in enumerate(train_loader):
            images, labels, _ = batch
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()

            if batch_idx % 20 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs}, Batch {batch_idx}/{len(train_loader)}, "
                           f"Loss: {loss.item():.4f}")

        train_acc = 100. * train_correct / train_total
        logger.info(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss/len(train_loader):.4f}, "
                   f"Train Acc: {train_acc:.2f}%")

    # Save checkpoint
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            'state_dict': model.state_dict(),
            'epochs': epochs,
            'type': 'ERM'
        }, save_path)
        logger.info(f"Saved ERM checkpoint to {save_path}")

    return model


def train_dro(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    device: str = "cuda",
    epochs: int = 5,
    lr: float = 0.001,
    weight_decay: float = 0.0001,
    alpha: float = 0.01,
    save_path: str = None
) -> nn.Module:
    """
    Train Group-DRO (Distributionally Robust Optimization) model.

    Args:
        model: ResNet-50 model
        train_loader: Training data loader
        val_loader: Validation data loader
        device: Device for training
        epochs: Number of epochs
        lr: Learning rate
        weight_decay: Weight decay
        alpha: DRO step size for group weights
        save_path: Path to save checkpoint

    Returns:
        Trained model
    """
    logger.info("Training Group-DRO model...")
    model = model.to(device)
    criterion = nn.CrossEntropyLoss(reduction='none')
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)

    # Initialize group weights
    num_groups = 4
    group_weights = torch.ones(num_groups, device=device) / num_groups

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        group_losses = torch.zeros(num_groups, device=device)
        group_counts = torch.zeros(num_groups, device=device)

        for batch_idx, batch in enumerate(train_loader):
            images, labels, groups = batch
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            losses = criterion(outputs, labels)

            # Compute per-group losses
            for g in range(num_groups):
                mask = (groups == g)
                if mask.sum() > 0:
                    group_loss = losses[mask].mean()
                    group_losses[g] += group_loss.item() * mask.sum().item()
                    group_counts[g] += mask.sum().item()

            # Weighted loss
            batch_group_losses = torch.zeros(num_groups, device=device)
            for g in range(num_groups):
                mask = (groups == g)
                if mask.sum() > 0:
                    batch_group_losses[g] = losses[mask].mean()

            loss = (group_weights * batch_group_losses).sum()
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

            if batch_idx % 20 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs}, Batch {batch_idx}/{len(train_loader)}, "
                           f"Loss: {loss.item():.4f}")

        # Update group weights (increase weights for groups with higher loss)
        avg_group_losses = group_losses / (group_counts + 1e-8)
        group_weights = group_weights * torch.exp(alpha * avg_group_losses)
        group_weights = group_weights / group_weights.sum()

        logger.info(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss/len(train_loader):.4f}")
        logger.info(f"Group weights: {group_weights.cpu().numpy()}")

    # Save checkpoint
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            'state_dict': model.state_dict(),
            'epochs': epochs,
            'type': 'DRO',
            'group_weights': group_weights.cpu()
        }, save_path)
        logger.info(f"Saved DRO checkpoint to {save_path}")

    return model
