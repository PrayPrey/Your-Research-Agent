import os
import random
import numpy as np
import torch
import torch.nn as nn
from torch.optim import SGD
from torch.optim.lr_scheduler import StepLR
import json

from config import Config
from data import get_dataloaders, download_waterbirds
from model import build_resnet50, AttributionTracker


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def train_one_epoch(model, loader, optimizer, criterion, device) -> float:
    model.train()
    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    for images, labels, _, _ in loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)
        total_correct += (outputs.argmax(dim=1) == labels).sum().item()
        total_samples += images.size(0)

    return total_loss / total_samples, total_correct / total_samples


def evaluate(model, loader, criterion, device) -> tuple:
    model.eval()
    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    with torch.no_grad():
        for images, labels, _, _ in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * images.size(0)
            total_correct += (outputs.argmax(dim=1) == labels).sum().item()
            total_samples += images.size(0)

    return total_loss / total_samples, total_correct / total_samples


def run_training(config: Config):
    set_seed(config.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    download_waterbirds(config.data_root)
    loaders = get_dataloaders(config.data_root, config.batch_size, config.attribution_subset_size)

    model = build_resnet50(num_classes=2).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = SGD(model.parameters(), lr=config.lr, momentum=config.momentum, weight_decay=config.weight_decay)
    scheduler = StepLR(optimizer, step_size=config.step_size, gamma=config.gamma)

    tracker = AttributionTracker(model, model.layer4[-1])

    os.makedirs(config.output_dir, exist_ok=True)

    tracker.log_epoch(0, loaders["attribution"], device)

    for epoch in range(1, config.epochs + 1):
        train_loss, train_acc = train_one_epoch(model, loaders["train"], optimizer, criterion, device)
        val_loss, val_acc = evaluate(model, loaders["val"], criterion, device)
        scheduler.step()

        print(f"Epoch {epoch}/{config.epochs} | "
              f"Train Loss: {train_loss:.4f}, Acc: {train_acc:.4f} | "
              f"Val Loss: {val_loss:.4f}, Acc: {val_acc:.4f}")

        tracker.log_epoch(epoch, loaders["attribution"], device)

    results = {
        "epoch_ratios": tracker.epoch_ratios,
        "config": {
            "seed": config.seed,
            "batch_size": config.batch_size,
            "lr": config.lr,
            "epochs": config.epochs
        }
    }

    with open(os.path.join(config.output_dir, "epoch_ratios.json"), "w") as f:
        json.dump(results, f, indent=2)

    return tracker


def main():
    config = Config()
    tracker = run_training(config)

    from evaluate import check_gate, save_metrics
    gate_result = check_gate(tracker.epoch_ratios)
    save_metrics(tracker.epoch_ratios, gate_result, config.output_dir)

    from visualize import plot_ratio_over_epochs, plot_gate_comparison
    plot_ratio_over_epochs(tracker.epoch_ratios, os.path.join(config.output_dir, "../figures/ratio_over_epochs.png"))
    plot_gate_comparison(gate_result, os.path.join(config.output_dir, "../figures/gate_comparison.png"))

    print("\n" + "="*50)
    print("EXPERIMENT RESULTS")
    print("="*50)
    print(f"Gate PASS: {gate_result['pass']}")
    print(f"Dominance Epoch: {gate_result['dominance_epoch']}")
    print(f"Ratio at Dominance: {gate_result['ratio_at_dominance']:.4f}")
    print("="*50)


if __name__ == "__main__":
    main()
