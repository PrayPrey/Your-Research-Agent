"""
Training loop with GradCAM temporal ratio tracking for h-e3.
"""

import sys
sys.path.insert(0, '../../h-e1/code/')  # Import h-e1 infrastructure

from dataclasses import dataclass
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from data import get_dataloader, DatasetConfig
from model import get_baseline_model
from gradcam_tracker import GradCAMTemporalTracker


@dataclass
class TrainConfig:
    dataset: str
    lr: float
    max_epochs: int
    batch_size: int
    seed: int
    tracking_interval: int  # Compute R_temporal every N epochs


def run_experiment(config: TrainConfig) -> dict:
    """
    Train ResNet baseline with GradCAM tracking.

    Returns:
        {
            'R_temporal_history': dict[int, float],
            'worst_group_acc': float,
            'delta': float  # R_temporal(5) - R_temporal(50)
        }
    """
    # Set seed
    torch.manual_seed(config.seed)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Setup data
    dataset_config = DatasetConfig(name=config.dataset, batch_size=config.batch_size)
    train_loader = get_dataloader(dataset_config, split='train')
    val_loader = get_dataloader(dataset_config, split='val')

    # Setup model
    model = get_baseline_model(config.dataset, pretrained=True)
    model.to(device)

    # Optimizer
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=config.lr,
        momentum=0.9,
        weight_decay=1e-4
    )

    # Learning rate scheduler
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)

    criterion = nn.CrossEntropyLoss()

    # GradCAM tracker (target layer4)
    target_layer = model.layer4[-1]  # ResNet final conv block
    tracker = GradCAMTemporalTracker(model, target_layer, device)

    print(f"Starting training: {config.dataset}, {config.max_epochs} epochs")

    # Training loop
    for epoch in range(1, config.max_epochs + 1):
        avg_loss = train_epoch(model, train_loader, optimizer, criterion, device)

        # Track R_temporal every N epochs
        if epoch % config.tracking_interval == 0:
            R = tracker.compute_epoch_ratio(val_loader, config.dataset, max_batches=100)
            tracker.record_epoch(epoch, R)
            print(f"Epoch {epoch}/{config.max_epochs} | Loss: {avg_loss:.4f} | R_temporal: {R:.4f}")
        else:
            print(f"Epoch {epoch}/{config.max_epochs} | Loss: {avg_loss:.4f}")

        scheduler.step()

    # Compute delta
    R_history = tracker.get_history()
    delta = None
    if 5 in R_history and 50 in R_history:
        delta = R_history[5] - R_history[50]

    # Evaluate worst-group accuracy
    worst_group_acc = evaluate_worst_group(model, val_loader, device)

    return {
        'R_temporal_history': R_history,
        'worst_group_acc': worst_group_acc,
        'delta': delta,
        'model': model,
        'tracker': tracker
    }


def train_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: str
) -> float:
    """Standard training epoch. Returns: avg_loss"""
    model.train()
    total_loss = 0.0

    for batch in dataloader:
        # Unpack batch (handle WILDS format)
        if len(batch) == 3:
            images, labels, metadata = batch
        else:
            images, labels = batch

        images = images.to(device)
        labels = labels.to(device).long()

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    return total_loss / len(dataloader)


def evaluate_worst_group(model: nn.Module, dataloader: DataLoader, device: str) -> float:
    """Compute worst-group accuracy for sanity check."""
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for batch in dataloader:
            # Unpack batch
            if len(batch) == 3:
                images, labels, metadata = batch
            else:
                images, labels = batch

            images = images.to(device)
            labels = labels.to(device).long()

            outputs = model(images)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    return correct / total if total > 0 else 0.0
