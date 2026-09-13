"""
Evaluation metrics for H-E1
"""

import torch
import torch.nn as nn
import numpy as np
import csv


def compute_group_accuracies(model, data_loader, num_groups=4, device='cuda'):
    """
    Compute per-group accuracies.

    Args:
        model: PyTorch model
        data_loader: DataLoader
        num_groups: Number of groups
        device: 'cuda' or 'cpu'

    Returns:
        group_accs: List of group accuracies
        group_counts: List of group sample counts
    """
    model.eval()
    model = model.to(device)

    group_correct = torch.zeros(num_groups)
    group_total = torch.zeros(num_groups)

    with torch.no_grad():
        for images, labels, groups in data_loader:
            images = images.to(device)
            labels = labels.to(device)
            groups_cpu = groups  # Keep on CPU

            outputs = model(images)
            _, predicted = outputs.max(1)

            predicted_cpu = predicted.cpu()
            labels_cpu = labels.cpu()

            for g in range(num_groups):
                mask = (groups_cpu == g)
                if mask.sum() > 0:
                    group_correct[g] += predicted_cpu[mask].eq(labels_cpu[mask]).sum().item()
                    group_total[g] += mask.sum().item()

    # Compute accuracies
    group_accs = []
    for g in range(num_groups):
        if group_total[g] > 0:
            group_accs.append(100.0 * group_correct[g].item() / group_total[g].item())
        else:
            group_accs.append(0.0)

    return group_accs, group_total.tolist()


def compute_worst_group_accuracy(group_accs):
    """Compute worst-group accuracy"""
    return min(group_accs)


def evaluate_alignment(erm_alignment, dro_alignment):
    """
    Evaluate alignment difference between ERM and DRO.

    Returns:
        result: Dict with comparison metrics
    """
    return {
        'erm_alignment': erm_alignment,
        'dro_alignment': dro_alignment,
        'difference': erm_alignment - dro_alignment,
        'ratio': erm_alignment / (dro_alignment + 1e-10)
    }


def save_metrics(metrics, path):
    """Save metrics to CSV"""
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=metrics.keys())
        writer.writeheader()
        writer.writerow(metrics)
