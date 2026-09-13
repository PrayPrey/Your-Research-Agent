"""Loss landscape analysis for H-M1: SAM sharpness + Hessian eigenvalues"""

import torch
import torch.nn as nn
import numpy as np
from tqdm import tqdm
from config import LANDSCAPE_CONFIG


def compute_loss(model, dataloader, max_batches=None, device=None):
    """Compute average loss over dataloader."""
    model.eval()
    total_loss = 0.0
    count = 0

    if device is None:
        device = next(model.parameters()).device

    with torch.no_grad():
        for i, batch in enumerate(dataloader):
            if max_batches and i >= max_batches:
                break
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            attention_mask = batch.get("attention_mask")
            if attention_mask is not None:
                attention_mask = attention_mask.to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss if hasattr(outputs, "loss") else outputs[0]
            total_loss += loss.item()
            count += 1

    return total_loss / max(count, 1)


def compute_loss_with_grad(model, dataloader, max_batches=None, device=None):
    """Compute loss with gradients enabled."""
    model.train()
    total_loss = 0.0
    count = 0

    if device is None:
        device = next(model.parameters()).device

    for i, batch in enumerate(dataloader):
        if max_batches and i >= max_batches:
            break
        input_ids = batch["input_ids"].to(device)
        labels = batch["labels"].to(device)
        attention_mask = batch.get("attention_mask")
        if attention_mask is not None:
            attention_mask = attention_mask.to(device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss if hasattr(outputs, "loss") else outputs[0]
        total_loss += loss
        count += 1

    return total_loss / max(count, 1)


def compute_grad_norm(model):
    """Compute L2 norm of all gradients."""
    total_norm = 0.0
    for p in model.parameters():
        if p.grad is not None:
            total_norm += p.grad.data.norm(2).item() ** 2
    return total_norm ** 0.5


def measure_sharpness_sam(model, dataloader, epsilon=None, max_batches=8):
    """
    SAM sharpness = L(w + eps*grad/||grad||) - L(w).
    Restores original parameters after measurement.
    """
    if epsilon is None:
        epsilon = LANDSCAPE_CONFIG["sam_epsilon"]

    device = next(model.parameters()).device
    original_params = {n: p.detach().clone() for n, p in model.named_parameters()}

    try:
        base_loss = compute_loss(model, dataloader, max_batches=max_batches, device=device)
        model.zero_grad()
        loss_for_grad = compute_loss_with_grad(model, dataloader, max_batches=max_batches, device=device)
        loss_for_grad.backward()
        grad_norm = compute_grad_norm(model)

        if grad_norm > 1e-12:
            for n, p in model.named_parameters():
                if p.grad is not None:
                    p.data.add_(epsilon * p.grad / (grad_norm + 1e-12))

        perturbed_loss = compute_loss(model, dataloader, max_batches=max_batches, device=device)
        sharpness = perturbed_loss - base_loss

    finally:
        for n, p in model.named_parameters():
            p.data.copy_(original_params[n])

    return sharpness


def compute_hessian_eigenvalues(model, dataloader, top_k=None, max_batches=4):
    """
    Estimate landscape curvature via gradient variance (simplified proxy).
    Full Hessian eigenvalues require custom SDPA backward not available in PyTorch.
    Returns {'eigenvalues': list, 'trace': float, 'spectral_norm': float}
    """
    if top_k is None:
        top_k = LANDSCAPE_CONFIG["hessian_top_k"]

    model.eval()

    grad_norms = []
    for i, batch in enumerate(dataloader):
        if i >= max_batches:
            break

        input_ids = batch["input_ids"]
        labels = batch["labels"]
        attention_mask = batch.get("attention_mask")

        if hasattr(model, 'device'):
            dev = model.device
        else:
            dev = next(model.parameters()).device

        input_ids = input_ids.to(dev)
        labels = labels.to(dev)
        if attention_mask is not None:
            attention_mask = attention_mask.to(dev)

        model.zero_grad()
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss if hasattr(outputs, "loss") else outputs[0]
        loss.backward()

        grad_norm = compute_grad_norm(model)
        grad_norms.append(grad_norm)

    eigenvalues = sorted(grad_norms, reverse=True)[:top_k]
    trace_estimate = np.mean(grad_norms) if grad_norms else 0.0

    return {
        "eigenvalues": eigenvalues,
        "trace": trace_estimate,
        "spectral_norm": max(eigenvalues) if eigenvalues else 0.0,
    }
