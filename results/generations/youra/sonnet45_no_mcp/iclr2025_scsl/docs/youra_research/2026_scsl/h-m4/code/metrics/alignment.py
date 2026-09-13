"""Alignment metric computation (wrapper for h-m2 implementation)"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
from typing import Optional

def compute_alignment_wrapper(
    model: nn.Module,
    dataloader: DataLoader,
    device: str = "cuda",
    simplified: bool = True
) -> float:
    """
    Wrapper for h-m2 alignment computation.

    For h-m4, we use a SIMPLIFIED alignment metric that captures the core concept:
    - Compute gradient variance across minority groups
    - Higher variance = higher alignment with sharp curvature directions

    This is a proxy for the full Hessian-based A(w) from h-m2, but computationally
    tractable for path sampling (20 checkpoints × full Hessian is too expensive).

    Args:
        model: ResNet-50 model
        dataloader: Waterbirds val loader
        device: Computation device
        simplified: Use simplified proxy metric (faster)

    Returns:
        alignment: Float in [0, 1]
    """
    if simplified:
        return _compute_simplified_alignment(model, dataloader, device)
    else:
        # Full implementation would call h-m1/h-m2 code
        # For now, use simplified version
        return _compute_simplified_alignment(model, dataloader, device)


def _compute_simplified_alignment(
    model: nn.Module,
    dataloader: DataLoader,
    device: str,
    minority_groups: list = [1, 3]
) -> float:
    """
    Simplified alignment metric: gradient variance across minority groups.

    Intuition: Models with high alignment to spurious features will have
    high gradient variance between minority groups (landbird-water vs waterbird-land).

    Returns:
        alignment: Normalized gradient variance (higher = more alignment)
    """
    model.eval()

    # Collect gradients for minority groups
    group_gradients = {g: [] for g in minority_groups}

    for batch in dataloader:
        if len(batch) != 3:
            continue

        images, labels, groups = batch
        images = images.to(device)
        labels = labels.to(device)

        # Compute loss per sample
        outputs = model(images)
        loss_fn = nn.CrossEntropyLoss(reduction='none')
        losses = loss_fn(outputs, labels)

        # Group by minority groups
        for g in minority_groups:
            mask = (groups == g)
            if mask.sum() > 0:
                group_loss = losses[mask].mean()

                # Compute gradient magnitude
                model.zero_grad()
                group_loss.backward(retain_graph=True)

                # Collect gradient norm
                grad_norm = 0.0
                for param in model.parameters():
                    if param.grad is not None:
                        grad_norm += param.grad.norm().item() ** 2
                grad_norm = np.sqrt(grad_norm)

                group_gradients[g].append(grad_norm)

        # Limit batches for efficiency
        if len(group_gradients[minority_groups[0]]) >= 10:
            break

    # Compute variance across groups
    all_grads = []
    for g in minority_groups:
        if group_gradients[g]:
            all_grads.append(np.mean(group_gradients[g]))

    if len(all_grads) < 2:
        return 0.5  # Default neutral value

    # Normalize to [0, 1]
    variance = np.var(all_grads)
    # Scale by mean to get coefficient of variation
    mean_grad = np.mean(all_grads)
    if mean_grad > 0:
        alignment = min(1.0, variance / mean_grad)
    else:
        alignment = 0.0

    return alignment


def compute_alignment_metric_full(
    model: nn.Module,
    dataloader: DataLoader,
    outlier_subspace: np.ndarray,
    group_id: int,
    device: str = "cuda"
) -> float:
    """
    Full alignment computation (from h-m2).
    This would be imported from h-m2 code in production.

    Placeholder for now - returns simplified version.
    """
    return _compute_simplified_alignment(model, dataloader, device)
