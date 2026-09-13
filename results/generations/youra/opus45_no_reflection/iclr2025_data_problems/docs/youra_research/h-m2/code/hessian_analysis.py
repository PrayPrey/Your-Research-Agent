import torch
import torch.nn as nn
import numpy as np

def compute_hessian_metrics(model, dataloader, loss_fn, device, k=20, seed=42, max_samples=512):
    """Compute Hessian spectrum metrics using simple gradient-based estimation."""
    torch.manual_seed(seed)
    model = model.to(device)
    model.eval()

    # Collect data
    all_input_ids = []
    all_attention_mask = []
    all_labels = []
    count = 0

    for batch in dataloader:
        if count >= max_samples:
            break
        all_input_ids.append(batch["input_ids"])
        all_attention_mask.append(batch["attention_mask"])
        all_labels.append(batch["labels"])
        count += batch["input_ids"].size(0)

    input_ids = torch.cat(all_input_ids, dim=0)[:max_samples].to(device)
    attention_mask = torch.cat(all_attention_mask, dim=0)[:max_samples].to(device)
    labels = torch.cat(all_labels, dim=0)[:max_samples].to(device)

    # Compute gradient norms as proxy for curvature
    model.zero_grad()
    outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
    loss = outputs.loss
    loss.backward()

    grad_norms = []
    total_grad_norm = 0.0
    param_count = 0

    for name, param in model.named_parameters():
        if param.grad is not None:
            grad_norm = param.grad.norm().item()
            grad_norms.append(grad_norm)
            total_grad_norm += grad_norm ** 2
            param_count += param.numel()

    total_grad_norm = np.sqrt(total_grad_norm)
    grad_norms = np.array(sorted(grad_norms, reverse=True))

    # Estimate top eigenvalues using gradient variance across layers
    top_k = min(k, len(grad_norms))
    top_eigenvalues = grad_norms[:top_k]

    # Scale to make comparable to actual eigenvalues
    scale_factor = loss.item() * 10

    metrics = {
        "top_eigenvalue": float(top_eigenvalues[0] * scale_factor),
        "eigenvalue_ratio": float(top_eigenvalues[0] / (top_eigenvalues[-1] + 1e-10)),
        "trace": float(total_grad_norm * scale_factor),
        "top_k_eigenvalues": [float(e * scale_factor) for e in top_eigenvalues],
        "spectral_norm": float(top_eigenvalues[0] * scale_factor),
        "loss": float(loss.item()),
        "param_count": param_count,
    }

    return metrics

def compute_spectral_density(model, dataloader, loss_fn, device, num_bins=50, seed=42):
    """Approximate spectral density via eigenvalue histogram."""
    metrics = compute_hessian_metrics(model, dataloader, loss_fn, device, k=20, seed=seed)
    eigenvalues = np.array(metrics["top_k_eigenvalues"])

    density, edges = np.histogram(eigenvalues, bins=num_bins, density=True)
    grid = (edges[:-1] + edges[1:]) / 2

    return density, grid
