"""
train.py - set_seed(), train_epoch(), collect_gradnorms()
"""

import os
import random
import csv

import numpy as np
import torch
import torch.nn as nn
from torch import Tensor
from torch.utils.data import DataLoader
from torch.optim import Optimizer

from src.model import GradientNormAnalyzer


def set_seed(seed: int = 1) -> None:
    """Fix torch, numpy, random seeds + cudnn deterministic."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def train_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: Optimizer,
    device: torch.device,
) -> dict:
    """
    Standard ERM training epoch: forward -> CE loss -> backward -> step.

    Returns: {'loss': float, 'acc': float}
    """
    model.train()
    criterion = nn.CrossEntropyLoss()

    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    for images, y, place in loader:
        images = images.to(device, non_blocking=True)
        y = y.to(device, non_blocking=True)

        optimizer.zero_grad()
        logits = model(images)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()

        batch_size = images.size(0)
        total_loss += loss.item() * batch_size
        preds = logits.argmax(dim=1)
        total_correct += (preds == y).sum().item()
        total_samples += batch_size

    avg_loss = total_loss / total_samples
    avg_acc = total_correct / total_samples
    return {'loss': avg_loss, 'acc': avg_acc}


def collect_gradnorms(
    model: nn.Module,
    analyzer: GradientNormAnalyzer,
    loader: DataLoader,
    device: torch.device,
    epoch: int,
    output_dir: str,
) -> dict:
    """
    Eval-mode pass over full training set to collect per-sample gradient norms.

    Saves gradnorm_epoch_{epoch}.npz to output_dir.
    Returns dict with arrays: g_raw, g_tilde, h_norm, sample_indices, group_labels, class_labels.
    All shape (N,).
    """
    model.eval()

    all_g_raw = []
    all_g_tilde = []
    all_h_norm = []
    all_idx = []
    all_group = []
    all_class = []

    sample_offset = 0

    with torch.no_grad():
        for images, y, place in loader:
            batch_size = images.size(0)
            images_dev = images.to(device, non_blocking=True)
            y_dev = y.to(device, non_blocking=True)

            g_raw_b, g_tilde_b, h_norm_b = analyzer.compute_batch_norms(images_dev, y_dev)
            analyzer.clear()

            group_b = y * 2 + place  # (B,) in {0,1,2,3} — CPU
            idx_b = torch.arange(sample_offset, sample_offset + batch_size, dtype=torch.long)
            sample_offset += batch_size

            all_g_raw.append(g_raw_b)
            all_g_tilde.append(g_tilde_b)
            all_h_norm.append(h_norm_b)
            all_idx.append(idx_b)
            all_group.append(group_b)
            all_class.append(y)

    arrays = {
        'g_raw':          torch.cat(all_g_raw).numpy().astype(np.float32),
        'g_tilde':        torch.cat(all_g_tilde).numpy().astype(np.float32),
        'h_norm':         torch.cat(all_h_norm).numpy().astype(np.float32),
        'sample_indices': torch.cat(all_idx).numpy().astype(np.int64),
        'group_labels':   torch.cat(all_group).numpy().astype(np.int64),
        'class_labels':   torch.cat(all_class).numpy().astype(np.int64),
    }

    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, f'gradnorm_epoch_{epoch}.npz')
    np.savez(save_path, **arrays)

    model.train()
    return arrays


def init_train_log(output_dir: str) -> str:
    """Create train_log.csv with header. Returns path."""
    os.makedirs(output_dir, exist_ok=True)
    log_path = os.path.join(output_dir, 'train_log.csv')
    with open(log_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['epoch', 'loss', 'acc', 'ratio', 'auc', 'balance_deviation'])
    return log_path


def append_train_log(
    log_path: str,
    epoch: int,
    loss: float,
    acc: float,
    ratio: float = float('nan'),
    auc: float = float('nan'),
    balance_deviation: float = float('nan'),
) -> None:
    """Append one row to train_log.csv."""
    with open(log_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([epoch, f'{loss:.6f}', f'{acc:.6f}',
                         f'{ratio:.6f}', f'{auc:.6f}', f'{balance_deviation:.6f}'])
