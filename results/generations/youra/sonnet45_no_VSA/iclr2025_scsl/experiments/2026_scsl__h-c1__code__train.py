"""Training loop module."""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, List, Tuple
from tqdm import tqdm


def train_one_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    optimizer: optim.Optimizer,
    criterion: nn.Module,
    device: torch.device
) -> float:
    """Train model for one epoch.

    Args:
        model: StandardCNN model
        train_loader: Training DataLoader
        optimizer: Adam optimizer
        criterion: CrossEntropyLoss
        device: cuda or cpu

    Returns:
        Average training loss for epoch
    """
    model.train()
    running_loss = 0.0

    for data, target in tqdm(train_loader, desc="Training", leave=False):
        data, target = data.to(device), target.to(device)

        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * data.size(0)

    avg_loss = running_loss / len(train_loader.dataset)
    return avg_loss


def validate(
    model: nn.Module,
    val_loader: DataLoader,
    criterion: nn.Module,
    device: torch.device
) -> Tuple[float, float]:
    """Validate model on test/validation set.

    Args:
        model: StandardCNN model
        val_loader: Validation DataLoader
        criterion: CrossEntropyLoss
        device: cuda or cpu

    Returns:
        (average_loss, accuracy) where accuracy in [0, 1]
    """
    model.eval()
    running_loss = 0.0
    correct = 0

    with torch.no_grad():
        for data, target in val_loader:
            data, target = data.to(device), target.to(device)

            output = model(data)
            loss = criterion(output, target)

            running_loss += loss.item() * data.size(0)
            pred = output.argmax(dim=1)
            correct += (pred == target).sum().item()

    avg_loss = running_loss / len(val_loader.dataset)
    accuracy = correct / len(val_loader.dataset)

    return avg_loss, accuracy


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    device: torch.device,
    max_epochs: int = 30,
    lr: float = 0.001,
    patience: int = 5
) -> Dict[str, List[float]]:
    """Full training loop with early stopping.

    Args:
        model: StandardCNN model
        train_loader: Training DataLoader
        test_loader: Test DataLoader (for validation)
        device: cuda or cpu
        max_epochs: Maximum training epochs
        lr: Learning rate for Adam
        patience: Early stopping patience (epochs without improvement)

    Returns:
        Training history dict with keys: ['train_loss', 'val_loss', 'val_acc']
    """
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    history = {
        'train_loss': [],
        'val_loss': [],
        'val_acc': []
    }

    best_val_acc = 0.0
    epochs_no_improve = 0

    for epoch in range(max_epochs):
        # Train
        train_loss = train_one_epoch(model, train_loader, optimizer, criterion, device)

        # Validate
        val_loss, val_acc = validate(model, test_loader, criterion, device)

        # Record history
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)

        # Print progress
        print(f"Epoch {epoch+1}/{max_epochs} - "
              f"Train Loss: {train_loss:.4f}, "
              f"Val Loss: {val_loss:.4f}, "
              f"Val Acc: {val_acc:.4f}")

        # Early stopping check
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"Early stopping triggered at epoch {epoch+1}")
                break

    return history
