"""Main training script for H-E1 experiment."""
import os
import sys
import csv
import random
import numpy as np
import torch
import torch.nn as nn
from torch.optim import SGD
from torch.optim.lr_scheduler import MultiStepLR

from config import CONFIG
from data import get_dataloaders, get_direction_pairs, WaterbirdsDataset, get_transforms
from model import build_resnet50, get_flat_grad
from subspace import GradientSubspaceAccumulator, compute_direction
from evaluate import check_gate, plot_bar_comparison, plot_alignment_evolution, plot_svd_variance


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def train_loop():
    set_seed(CONFIG.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    os.makedirs(CONFIG.checkpoint_dir, exist_ok=True)
    os.makedirs(CONFIG.figures_dir, exist_ok=True)
    os.makedirs(os.path.dirname(CONFIG.csv_log_path), exist_ok=True)

    train_loader, val_loader, test_loader = get_dataloaders(CONFIG.data_root, CONFIG.batch_size)
    train_dataset = train_loader.dataset
    print(f"Train: {len(train_dataset)}, Val: {len(val_loader.dataset)}, Test: {len(test_loader.dataset)}")

    spurious_pairs, core_pairs = get_direction_pairs(train_dataset)
    print(f"Spurious pairs: {len(spurious_pairs)}, Core pairs: {len(core_pairs)}")

    model = build_resnet50(CONFIG.num_classes).to(device)
    optimizer = SGD(model.parameters(), lr=CONFIG.lr, momentum=CONFIG.momentum, weight_decay=CONFIG.weight_decay)
    scheduler = MultiStepLR(optimizer, milestones=list(CONFIG.step_milestones), gamma=CONFIG.gamma)
    criterion = nn.CrossEntropyLoss()

    num_params = sum(p.numel() for p in model.parameters())
    accumulator = GradientSubspaceAccumulator(num_params, CONFIG.subspace_rank, CONFIG.accumulation_epochs)
    results = {}

    with open(CONFIG.csv_log_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["epoch", "spurious_alignment", "core_alignment", "train_loss", "val_acc"])

    for epoch in range(1, CONFIG.num_epochs + 1):
        model.train()
        total_loss = 0.0
        for batch_idx, (img, label, group) in enumerate(train_loader):
            img, label = img.to(device), label.to(device)
            optimizer.zero_grad()
            out = model(img)
            loss = criterion(out, label)
            loss.backward()
            if epoch <= CONFIG.accumulation_epochs and batch_idx == len(train_loader) - 1:
                accumulator.accumulate(model, epoch)
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        scheduler.step()

        if epoch == CONFIG.accumulation_epochs:
            accumulator.compute_subspace()
            torch.save(model.state_dict(), os.path.join(CONFIG.checkpoint_dir, f"epoch{epoch}.pt"))
            print(f"Epoch {epoch}: Subspace computed, checkpoint saved")

        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for img, label, group in val_loader:
                img, label = img.to(device), label.to(device)
                out = model(img)
                pred = out.argmax(dim=1)
                correct += (pred == label).sum().item()
                total += label.size(0)
        val_acc = correct / total

        if epoch in CONFIG.log_epochs:
            spurious_dir = compute_direction(model, train_dataset, spurious_pairs, device)
            core_dir = compute_direction(model, train_dataset, core_pairs, device)
            spurious_align = accumulator.measure_alignment(spurious_dir)
            core_align = accumulator.measure_alignment(core_dir)
            results[epoch] = {"spurious_alignment": spurious_align, "core_alignment": core_align}
            print(f"Epoch {epoch}: spurious={spurious_align:.4f}, core={core_align:.4f}, loss={avg_loss:.4f}, val_acc={val_acc:.4f}")
            with open(CONFIG.csv_log_path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([epoch, spurious_align, core_align, avg_loss, val_acc])
        else:
            print(f"Epoch {epoch}: loss={avg_loss:.4f}, val_acc={val_acc:.4f}")

    plot_bar_comparison(results, list(CONFIG.log_epochs), os.path.join(CONFIG.figures_dir, "alignment_bar.png"))
    plot_alignment_evolution(results, os.path.join(CONFIG.figures_dir, "alignment_evolution.png"))
    plot_svd_variance(accumulator.singular_values, os.path.join(CONFIG.figures_dir, "svd_variance.png"))

    gate_passed = check_gate(results)
    print(f"\n{'='*50}")
    print(f"GATE CHECK: {'PASSED' if gate_passed else 'FAILED'}")
    if 10 in results:
        print(f"  Spurious alignment at epoch 10: {results[10]['spurious_alignment']:.4f} (gate: >{CONFIG.spurious_gate})")
        print(f"  Core alignment at epoch 10: {results[10]['core_alignment']:.4f} (gate: <{CONFIG.core_gate})")
    print(f"{'='*50}")

    return results, gate_passed


def save_checkpoint(model: nn.Module, path: str):
    torch.save(model.state_dict(), path)


if __name__ == "__main__":
    results, gate_passed = train_loop()
    sys.exit(0 if gate_passed else 1)
