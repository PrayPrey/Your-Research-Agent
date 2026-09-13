"""Training loop with early stopping"""
from typing import Dict, Tuple
from pathlib import Path
import sys
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import Adam
from torch.optim.lr_scheduler import StepLR
import numpy as np
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent))
from config import ExperimentConfig
from data import get_dataloaders
from models import StandardCNN


def set_seed(seed: int):
    """Set random seeds for reproducibility"""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def train_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer: Adam,
    scheduler: StepLR,
    criterion: nn.Module,
    device: str,
    gradient_clip_norm: float
) -> Dict[str, float]:
    """Train for one epoch.

    Args:
        model: CNN model
        dataloader: Training DataLoader
        optimizer: Adam optimizer
        scheduler: StepLR scheduler
        criterion: NLLLoss criterion
        device: "cuda" or "cpu"
        gradient_clip_norm: Gradient clipping threshold

    Returns:
        {"loss": float, "accuracy": float}
    """
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for images, labels in dataloader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        logits = model(images)  # [B, 10]
        loss = criterion(logits, labels)

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), gradient_clip_norm)
        optimizer.step()

        total_loss += loss.item() * images.size(0)
        preds = logits.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total += images.size(0)

    scheduler.step()

    return {
        "loss": total_loss / total,
        "accuracy": correct / total
    }


def validate(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: str
) -> Dict[str, float]:
    """Validation pass (no augmentation).

    Args:
        model: CNN model
        dataloader: Validation DataLoader
        criterion: NLLLoss criterion
        device: "cuda" or "cpu"

    Returns:
        {"loss": float, "accuracy": float}
    """
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)

            logits = model(images)
            loss = criterion(logits, labels)

            total_loss += loss.item() * images.size(0)
            preds = logits.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += images.size(0)

    return {
        "loss": total_loss / total,
        "accuracy": correct / total
    }


def train_model(
    config: ExperimentConfig,
    flip_prob: float,
    seed: int
) -> Tuple[nn.Module, Dict]:
    """Full training pipeline with early stopping.

    Args:
        config: Experiment configuration
        flip_prob: Horizontal flip probability
        seed: Random seed

    Returns:
        (best_model, result_dict)
    """
    set_seed(seed)

    # Get device
    device = config.training.device if torch.cuda.is_available() else "cpu"

    # Get dataloaders
    train_loader, test_loader = get_dataloaders(config.data, flip_prob)

    # Initialize model
    model = StandardCNN(config.model).to(device)

    # Optimizer and scheduler
    optimizer = Adam(
        model.parameters(),
        lr=config.training.lr,
        weight_decay=config.training.weight_decay
    )

    scheduler = StepLR(
        optimizer,
        step_size=config.training.scheduler_step,
        gamma=config.training.scheduler_gamma
    )

    criterion = nn.NLLLoss()

    # Training loop with early stopping
    best_val_acc = 0.0
    best_epoch = 0
    patience_counter = 0
    checkpoint_path = config.checkpoint_dir / f"model_p{flip_prob}_seed{seed}.pt"

    for epoch in range(config.training.max_epochs):
        train_metrics = train_epoch(
            model, train_loader, optimizer, scheduler,
            criterion, device, config.training.gradient_clip_norm
        )

        val_metrics = validate(model, test_loader, criterion, device)

        if val_metrics["accuracy"] > best_val_acc:
            best_val_acc = val_metrics["accuracy"]
            best_epoch = epoch
            patience_counter = 0
            # Save checkpoint
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_acc": best_val_acc
            }, checkpoint_path)
        else:
            patience_counter += 1

        if patience_counter >= config.training.patience:
            break

    # Load best checkpoint
    checkpoint = torch.load(checkpoint_path)
    model.load_state_dict(checkpoint["model_state_dict"])

    # Final test evaluation
    final_test_metrics = validate(model, test_loader, criterion, device)

    result = {
        "flip_prob": flip_prob,
        "seed": seed,
        "best_epoch": best_epoch,
        "best_val_acc": best_val_acc,
        "final_test_acc": final_test_metrics["accuracy"]
    }

    return model, result
