import os
import json
import random
import numpy as np
import torch
import torch.nn as nn
from torch.optim import SGD
from torch.optim.lr_scheduler import MultiStepLR

from config import Config
from data import get_dataloaders, download_waterbirds
from model import build_resnet50, GradientNormTracker


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def train_one_epoch(
    model: nn.Module,
    tracker: GradientNormTracker,
    loader,
    optimizer,
    criterion,
    device
) -> tuple:
    model.train()
    total_loss = 0.0
    total_spurious_norm = 0.0
    total_minority_norm = 0.0
    num_batches = 0

    for batch in loader:
        images, labels, spurious_aligned = batch
        images = images.to(device)
        labels = labels.to(device)
        spurious_aligned = spurious_aligned.to(device)

        optimizer.zero_grad()
        logits = model(images)
        loss = criterion(logits, labels)
        loss.backward()

        spurious_norm, minority_norm = tracker.compute_gradient_norms_by_group(spurious_aligned)

        optimizer.step()

        total_loss += loss.item()
        total_spurious_norm += spurious_norm
        total_minority_norm += minority_norm
        num_batches += 1

    return (
        total_loss / num_batches,
        total_spurious_norm / num_batches,
        total_minority_norm / num_batches
    )


def run_training(config: Config, seed: int) -> list:
    set_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    download_waterbirds(config.data_root)
    loaders = get_dataloaders(config.data_root, config.batch_size)

    model = build_resnet50(config.num_classes).to(device)
    tracker = GradientNormTracker(model, model.layer4[-1])

    optimizer = SGD(
        model.parameters(),
        lr=config.lr,
        momentum=config.momentum,
        weight_decay=config.weight_decay
    )
    scheduler = MultiStepLR(optimizer, milestones=list(config.step_sizes), gamma=config.gamma)
    criterion = nn.CrossEntropyLoss()

    records = []
    for epoch in range(1, config.epochs + 1):
        loss, spurious_norm, minority_norm = train_one_epoch(
            model, tracker, loaders["train"], optimizer, criterion, device
        )
        ratio = spurious_norm / minority_norm if minority_norm > 0 else float("inf")

        records.append({
            "epoch": epoch,
            "loss": loss,
            "spurious_norm": spurious_norm,
            "minority_norm": minority_norm,
            "ratio": ratio
        })

        print(f"[Seed {seed}] Epoch {epoch}/{config.epochs} - Loss: {loss:.4f}, "
              f"Spurious: {spurious_norm:.6f}, Minority: {minority_norm:.6f}, Ratio: {ratio:.4f}")

        scheduler.step()

    tracker.remove_hooks()
    return records


def main():
    config = Config()
    os.makedirs(config.output_dir, exist_ok=True)

    all_records = {}
    for seed in config.seeds:
        print(f"\n{'='*60}")
        print(f"Starting training with seed {seed}")
        print(f"{'='*60}")
        records = run_training(config, seed)
        all_records[seed] = records

    output_path = os.path.join(config.output_dir, "gradient_norm_records.json")
    with open(output_path, "w") as f:
        json.dump(all_records, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
