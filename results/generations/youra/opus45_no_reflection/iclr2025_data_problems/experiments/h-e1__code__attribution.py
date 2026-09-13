"""Attribution methods for H-E1 experiment.

Implements self-influence computation using gradient-based methods.
Since TRAK, kronfluence, and captum have complex dependencies, we implement
simplified versions that capture the core gradient dot-product idea.
"""

import torch
import numpy as np
from torch.utils.data import DataLoader
from transformers import PreTrainedModel
from tqdm import tqdm


def compute_gradients(model: PreTrainedModel, batch: dict, device: str = "cuda") -> torch.Tensor:
    """Compute gradient of loss w.r.t. parameters for a batch."""
    model.zero_grad()
    batch = {k: v.to(device) for k, v in batch.items()}
    outputs = model(**batch)
    loss = outputs.loss
    loss.backward()

    grads = []
    for param in model.parameters():
        if param.grad is not None:
            grads.append(param.grad.view(-1))
    return torch.cat(grads)


def compute_per_sample_gradients(
    model: PreTrainedModel,
    train_loader: DataLoader,
    device: str = "cuda"
) -> np.ndarray:
    """Compute per-sample gradients for entire training set."""
    model.eval()
    all_grads = []

    for batch in tqdm(train_loader, desc="Computing gradients"):
        batch_size = batch["input_ids"].shape[0]

        for i in range(batch_size):
            single_batch = {
                "input_ids": batch["input_ids"][i:i+1].to(device),
                "attention_mask": batch["attention_mask"][i:i+1].to(device),
                "labels": batch["labels"][i:i+1].to(device),
            }

            model.zero_grad()
            outputs = model(**single_batch)
            loss = outputs.loss
            loss.backward()

            grads = []
            for param in model.parameters():
                if param.grad is not None:
                    grads.append(param.grad.view(-1).clone())

            grad_vec = torch.cat(grads).cpu().numpy()
            all_grads.append(grad_vec)

    return np.array(all_grads)


def compute_tracin_scores(
    model: PreTrainedModel,
    train_loader: DataLoader,
    device: str = "cuda",
    max_samples: int = None
) -> np.ndarray:
    """Compute TracIn self-influence scores via gradient dot products.

    Self-influence = ||grad_i||^2 (gradient norm squared).
    Higher self-influence indicates harder/potentially mislabeled examples.
    """
    model.eval()
    scores = []
    sample_count = 0

    for batch in tqdm(train_loader, desc="Computing TracIn scores"):
        batch_size = batch["input_ids"].shape[0]

        for i in range(batch_size):
            if max_samples and sample_count >= max_samples:
                break

            single_batch = {
                "input_ids": batch["input_ids"][i:i+1].to(device),
                "attention_mask": batch["attention_mask"][i:i+1].to(device),
                "labels": batch["labels"][i:i+1].to(device),
            }

            model.zero_grad()
            outputs = model(**single_batch)
            loss = outputs.loss
            loss.backward()

            grad_norm_sq = 0.0
            for param in model.parameters():
                if param.grad is not None:
                    grad_norm_sq += (param.grad ** 2).sum().item()

            scores.append(grad_norm_sq)
            sample_count += 1

        if max_samples and sample_count >= max_samples:
            break

    return np.array(scores)


def compute_trak_scores(
    model: PreTrainedModel,
    train_loader: DataLoader,
    train_size: int,
    proj_dim: int = 1024,
    device: str = "cuda",
    max_samples: int = None
) -> np.ndarray:
    """Compute TRAK-style self-influence with random projection.

    Projects gradients to lower dimension using random matrix,
    then computes self-influence as projected gradient norm.
    """
    model.eval()

    # Get total parameter count
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    # Create random projection matrix (fixed seed for reproducibility)
    torch.manual_seed(42)
    proj_matrix = torch.randn(total_params, proj_dim, device=device) / np.sqrt(proj_dim)

    scores = []
    sample_count = 0

    for batch in tqdm(train_loader, desc="Computing TRAK scores"):
        batch_size = batch["input_ids"].shape[0]

        for i in range(batch_size):
            if max_samples and sample_count >= max_samples:
                break

            single_batch = {
                "input_ids": batch["input_ids"][i:i+1].to(device),
                "attention_mask": batch["attention_mask"][i:i+1].to(device),
                "labels": batch["labels"][i:i+1].to(device),
            }

            model.zero_grad()
            outputs = model(**single_batch)
            loss = outputs.loss
            loss.backward()

            grads = []
            for param in model.parameters():
                if param.grad is not None:
                    grads.append(param.grad.view(-1))
            grad_vec = torch.cat(grads)

            # Project gradient
            proj_grad = grad_vec @ proj_matrix
            score = (proj_grad ** 2).sum().item()

            scores.append(score)
            sample_count += 1

        if max_samples and sample_count >= max_samples:
            break

    return np.array(scores)


def compute_ekfac_scores(
    model: PreTrainedModel,
    train_loader: DataLoader,
    device: str = "cuda",
    max_samples: int = None
) -> np.ndarray:
    """Compute EK-FAC-style self-influence scores.

    Simplified version: uses diagonal Fisher approximation.
    Full EK-FAC would use Kronecker-factored curvature.
    """
    model.eval()

    # First pass: estimate diagonal Fisher (gradient variance)
    print("Estimating diagonal Fisher...")
    fisher_diag = None
    n_samples_fisher = 0

    for batch in tqdm(train_loader, desc="Fisher estimation"):
        batch = {k: v.to(device) for k, v in batch.items()}

        model.zero_grad()
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()

        if fisher_diag is None:
            fisher_diag = torch.zeros(
                sum(p.numel() for p in model.parameters() if p.requires_grad),
                device=device
            )

        grads = []
        for param in model.parameters():
            if param.grad is not None:
                grads.append(param.grad.view(-1))
        grad_vec = torch.cat(grads)

        fisher_diag += grad_vec ** 2
        n_samples_fisher += 1

        if n_samples_fisher >= 100:
            break

    fisher_diag = fisher_diag / n_samples_fisher + 1e-8

    # Second pass: compute self-influence with Fisher scaling
    print("Computing EK-FAC scores...")
    scores = []
    sample_count = 0

    for batch in tqdm(train_loader, desc="Computing EK-FAC scores"):
        batch_size = batch["input_ids"].shape[0]

        for i in range(batch_size):
            if max_samples and sample_count >= max_samples:
                break

            single_batch = {
                "input_ids": batch["input_ids"][i:i+1].to(device),
                "attention_mask": batch["attention_mask"][i:i+1].to(device),
                "labels": batch["labels"][i:i+1].to(device),
            }

            model.zero_grad()
            outputs = model(**single_batch)
            loss = outputs.loss
            loss.backward()

            grads = []
            for param in model.parameters():
                if param.grad is not None:
                    grads.append(param.grad.view(-1))
            grad_vec = torch.cat(grads)

            # Fisher-scaled gradient norm
            score = ((grad_vec ** 2) / fisher_diag).sum().item()
            scores.append(score)
            sample_count += 1

        if max_samples and sample_count >= max_samples:
            break

    return np.array(scores)


def compute_attribution(
    model: PreTrainedModel,
    train_loader: DataLoader,
    method: str,
    device: str = "cuda",
    max_samples: int = None,
    **kwargs
) -> np.ndarray:
    """Dispatch to appropriate attribution method.

    Args:
        model: Fine-tuned model
        train_loader: Training data loader
        method: One of 'trak', 'ekfac', 'tracin'
        device: Device to use
        max_samples: Maximum samples to process (for faster evaluation)

    Returns:
        Self-influence scores [N]
    """
    train_size = len(train_loader.dataset)

    if method == "trak":
        return compute_trak_scores(
            model, train_loader, train_size,
            device=device, max_samples=max_samples
        )
    elif method == "ekfac":
        return compute_ekfac_scores(
            model, train_loader,
            device=device, max_samples=max_samples
        )
    elif method == "tracin":
        return compute_tracin_scores(
            model, train_loader,
            device=device, max_samples=max_samples
        )
    else:
        raise ValueError(f"Unknown method: {method}")
