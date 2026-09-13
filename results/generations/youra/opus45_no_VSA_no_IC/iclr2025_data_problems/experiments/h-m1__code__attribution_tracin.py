"""TracIn attribution method for h-m1."""
import math

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset

from config import ExperimentConfig


def compute_tracin_scores(
    model: nn.Module,
    checkpoints: list,
    train_ds: Dataset,
    test_ds: Dataset,
    probes: dict,
    cfg: ExperimentConfig,
    device: torch.device
) -> dict:
    """TracIn(z,z') = sum_k eta_k * grad_l(w_k, z) . grad_l(w_k, z').

    Uses last-layer gradients only for tractability.
    Returns dict with keys 'mem', 'transfer', 'spurious'.
    """
    criterion = nn.CrossEntropyLoss()

    # Compute LR at each checkpoint epoch using cosine annealing formula
    etas = []
    for i, ckpt in enumerate(checkpoints):
        epoch = (i + 1) * cfg.checkpoint_every
        # Cosine annealing: lr * (1 + cos(pi * epoch / T_max)) / 2
        eta = cfg.lr * (1 + math.cos(math.pi * epoch / cfg.epochs)) / 2
        etas.append(eta)

    # Initialize scores
    scores = {mode: np.zeros(len(pairs)) for mode, pairs in probes.items()}

    # Collect unique indices
    train_indices = set()
    test_indices = set()
    for mode, pairs in probes.items():
        for ti, tj in pairs:
            train_indices.add(ti)
            test_indices.add(tj)

    # Process each checkpoint
    for ckpt_path, eta in zip(checkpoints, etas):
        model.load_state_dict(torch.load(ckpt_path, map_location=device))
        model.to(device)
        model.eval()

        # Compute gradients for train samples
        train_grads = {}
        for ti in train_indices:
            x, y = train_ds[ti]
            grad = _per_sample_grad(model, x.unsqueeze(0).to(device), torch.tensor([y]).to(device), criterion)
            train_grads[ti] = grad

        # Compute gradients for test samples
        test_grads = {}
        for tj in test_indices:
            x, y = test_ds[tj]
            grad = _per_sample_grad(model, x.unsqueeze(0).to(device), torch.tensor([y]).to(device), criterion)
            test_grads[tj] = grad

        # Accumulate TracIn scores
        for mode, pairs in probes.items():
            for idx, (ti, tj) in enumerate(pairs):
                dot = torch.dot(train_grads[ti], test_grads[tj]).item()
                scores[mode][idx] += eta * dot

    return {mode: arr for mode, arr in scores.items()}


def _per_sample_grad(model: nn.Module, x: torch.Tensor, y: torch.Tensor, criterion) -> torch.Tensor:
    """Compute flattened last-layer gradient for a single sample."""
    model.zero_grad()
    logits = model(x)
    loss = criterion(logits, y)
    loss.backward()

    # Only use fc layer gradients (last layer)
    grads = []
    for name, param in model.named_parameters():
        if "fc" in name and param.grad is not None:
            grads.append(param.grad.detach().flatten())

    return torch.cat(grads) if grads else torch.zeros(1, device=x.device)
