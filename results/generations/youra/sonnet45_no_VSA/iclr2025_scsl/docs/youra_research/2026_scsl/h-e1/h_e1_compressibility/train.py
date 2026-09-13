"""Training script for h-e1 compressibility experiment."""

import argparse
import csv
from pathlib import Path
from typing import Dict, Tuple
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from data import get_dataloaders
from model import get_model
from optimizers import get_optimizer, SAM, METHOD_CONFIGS
from utils import set_seed, save_checkpoint, setup_logging


TRAINING_CONFIG = {
    "epochs": 20,
    "validate_every": 1,
    "checkpoint_every": 2,
    "early_stopping": False,
    "loss_function": "cross_entropy",
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "gradient_clip_enabled": False,
    "mixed_precision": False
}


def train_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: str,
    method: str,
    swa_model = None,
    epoch: int = 0
) -> Dict[str, float]:
    """Train one epoch."""
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for images, labels, _ in dataloader:
        images, labels = images.to(device), labels.to(device)

        if method == "SAM":
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.first_step(zero_grad=True)

            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.second_step(zero_grad=True)
        else:
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

        total_loss += loss.item()
        if method != "SAM":
            preds = outputs.argmax(dim=1)
        else:
            with torch.no_grad():
                preds = model(images).argmax(dim=1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

    if method == "SWA" and swa_model is not None and epoch >= METHOD_CONFIGS["SWA"]["swa_start_epoch"]:
        swa_model.update_parameters(model)

    return {
        "train_loss": total_loss / len(dataloader),
        "train_acc": correct / total
    }


def evaluate(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: str
) -> Dict[str, float]:
    """Evaluate model."""
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels, _ in dataloader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item()
            preds = outputs.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    return {
        "loss": total_loss / len(dataloader),
        "accuracy": correct / total
    }


def compute_worst_group_accuracy(
    model: nn.Module,
    dataloader: DataLoader,
    device: str
) -> Tuple[float, Dict[Tuple[int, int], float]]:
    """Compute worst-group and per-group accuracy."""
    model.eval()
    per_group = {(c, col): {"correct": 0, "total": 0} for c in range(10) for col in range(2)}

    with torch.no_grad():
        for images, labels, colors in dataloader:
            images = images.to(device)
            outputs = model(images)
            preds = outputs.argmax(dim=1).cpu()

            for pred, label, color in zip(preds, labels, colors):
                group = (label.item(), color.item())
                per_group[group]["total"] += 1
                if pred == label:
                    per_group[group]["correct"] += 1

    per_group_acc = {
        g: counts["correct"] / counts["total"]
        for g, counts in per_group.items()
        if counts["total"] > 0
    }

    worst_group_acc = min(per_group_acc.values()) if per_group_acc else 0.0
    return worst_group_acc, per_group_acc


def main(
    method: str,
    seed: int,
    epochs: int = 20,
    batch_size: int = 256,
    lr: float = 0.01,
    checkpoint_dir: str = "results/checkpoints",
    log_dir: str = "results/logs",
    device: str = "cuda"
):
    """Training CLI entry point."""
    set_seed(seed)
    logger = setup_logging(log_dir, method, seed)

    logger.info(f"Starting training: method={method}, seed={seed}, device={device}")

    dataloaders = get_dataloaders(batch_size=batch_size)
    model = get_model(method=method).to(device)
    optimizer = get_optimizer(model, method, lr=lr)
    criterion = nn.CrossEntropyLoss()

    swa_model = None
    if method == "SWA":
        swa_model = torch.optim.swa_utils.AveragedModel(model)

    Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    log_file = Path(log_dir) / f"{method}_seed{seed}_training_log.csv"
    with open(log_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "method", "seed", "epoch", "train_loss", "train_acc",
            "val_loss", "val_acc", "test_acc", "worst_group_acc"
        ])
        writer.writeheader()

        for epoch in range(1, epochs + 1):
            train_metrics = train_epoch(
                model, dataloaders["train"], optimizer, criterion,
                device, method, swa_model, epoch
            )

            val_metrics = evaluate(model, dataloaders["val"], criterion, device)
            test_metrics = evaluate(model, dataloaders["test"], criterion, device)
            worst_group_acc, _ = compute_worst_group_accuracy(model, dataloaders["test"], device)

            logger.info(
                f"Epoch {epoch}/{epochs} - "
                f"Train Loss: {train_metrics['train_loss']:.4f}, "
                f"Train Acc: {train_metrics['train_acc']:.4f}, "
                f"Val Acc: {val_metrics['accuracy']:.4f}, "
                f"Test Acc: {test_metrics['accuracy']:.4f}, "
                f"Worst-Group Acc: {worst_group_acc:.4f}"
            )

            writer.writerow({
                "method": method,
                "seed": seed,
                "epoch": epoch,
                "train_loss": train_metrics["train_loss"],
                "train_acc": train_metrics["train_acc"],
                "val_loss": val_metrics["loss"],
                "val_acc": val_metrics["accuracy"],
                "test_acc": test_metrics["accuracy"],
                "worst_group_acc": worst_group_acc
            })

            if epoch % TRAINING_CONFIG["checkpoint_every"] == 0:
                checkpoint_path = Path(checkpoint_dir) / f"{method}_seed{seed}_epoch{epoch}.pt"
                save_checkpoint(
                    model, optimizer, epoch,
                    {
                        "train_loss": train_metrics["train_loss"],
                        "train_acc": train_metrics["train_acc"],
                        "test_acc": test_metrics["accuracy"],
                        "worst_group_acc": worst_group_acc
                    },
                    str(checkpoint_path), seed, method
                )

    final_checkpoint = Path(checkpoint_dir) / f"{method}_seed{seed}_epoch{epochs}.pt"
    if not final_checkpoint.exists():
        save_checkpoint(
            model, optimizer, epochs,
            {
                "train_loss": train_metrics["train_loss"],
                "train_acc": train_metrics["train_acc"],
                "test_acc": test_metrics["accuracy"],
                "worst_group_acc": worst_group_acc
            },
            str(final_checkpoint), seed, method
        )

    logger.info("Training complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", type=str, required=True,
                        choices=["ERM", "SAM", "SWA", "Dropout", "SpectralNorm"])
    parser.add_argument("--seed", type=int, required=True,
                        choices=[42, 43, 44, 45, 46])
    parser.add_argument("--checkpoint-dir", type=str, default="results/checkpoints/")
    parser.add_argument("--log-dir", type=str, default="results/logs/")
    parser.add_argument("--device", type=str, default="cuda",
                        choices=["cuda", "cpu"])

    args = parser.parse_args()

    main(
        method=args.method,
        seed=args.seed,
        checkpoint_dir=args.checkpoint_dir,
        log_dir=args.log_dir,
        device=args.device
    )
