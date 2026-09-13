"""Sharpness measurement for H-M4: SAM sharpness (reused from H-M2)"""

import torch
from tqdm import tqdm
from config import SHARPNESS_CONFIG


def compute_loss(model, batch, device):
    """Compute loss for a single batch."""
    input_ids = batch["input_ids"].to(device)
    labels = batch["labels"].to(device)
    attention_mask = batch.get("attention_mask")
    if attention_mask is not None:
        attention_mask = attention_mask.to(device)

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
    return outputs.loss.item()


def compute_loss_with_grad(model, batch, device):
    """Compute loss with gradients."""
    input_ids = batch["input_ids"].to(device)
    labels = batch["labels"].to(device)
    attention_mask = batch.get("attention_mask")
    if attention_mask is not None:
        attention_mask = attention_mask.to(device)

    outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
    return outputs.loss


def compute_grad_norm(model):
    """Compute L2 norm of all gradients."""
    total_norm = 0.0
    for p in model.parameters():
        if p.grad is not None:
            total_norm += p.grad.data.norm(2).item() ** 2
    return total_norm ** 0.5


def measure_sharpness_single_batch(model, batch, epsilon, device):
    """SAM sharpness for a single batch."""
    original_params = {n: p.detach().clone() for n, p in model.named_parameters()}

    try:
        base_loss = compute_loss(model, batch, device)

        model.zero_grad()
        loss_for_grad = compute_loss_with_grad(model, batch, device)
        loss_for_grad.backward()

        grad_norm = compute_grad_norm(model)

        if grad_norm > 1e-12:
            for n, p in model.named_parameters():
                if p.grad is not None:
                    p.data.add_(epsilon * p.grad / (grad_norm + 1e-12))

        perturbed_loss = compute_loss(model, batch, device)
        sharpness = perturbed_loss - base_loss

    finally:
        for n, p in model.named_parameters():
            p.data.copy_(original_params[n])

    return sharpness


def measure_task_sharpness(model, dataloader, max_batches: int = 50, sam_epsilon: float = 0.05):
    """
    Compute SAM sharpness over max_batches.
    Returns {'mean_sharpness': float, 'per_batch': list[float]}
    """
    if max_batches is None:
        max_batches = SHARPNESS_CONFIG["max_batches"]
    if sam_epsilon is None:
        sam_epsilon = SHARPNESS_CONFIG["sam_epsilon"]

    device = next(model.parameters()).device
    model.eval()

    per_batch = []
    pbar = tqdm(dataloader, total=min(max_batches, len(dataloader)), desc="Measuring sharpness")

    for i, batch in enumerate(pbar):
        if i >= max_batches:
            break

        sharpness = measure_sharpness_single_batch(model, batch, sam_epsilon, device)
        per_batch.append(sharpness)
        pbar.set_postfix({"sharpness": f"{sharpness:.4f}"})

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    mean_sharpness = sum(per_batch) / len(per_batch) if per_batch else 0.0

    return {
        "mean_sharpness": mean_sharpness,
        "per_batch": per_batch,
    }
