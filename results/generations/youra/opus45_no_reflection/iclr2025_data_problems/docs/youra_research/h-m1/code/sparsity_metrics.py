"""Sparsity metrics for H-M1: upper triangle analysis."""
import torch
import numpy as np
from typing import Tuple


def upper_triangle_sparsity(attn_matrix: torch.Tensor, threshold: float = 1e-6) -> float:
    """
    Compute fraction of upper triangle entries below threshold.
    attn_matrix: [..., S, S] where last 2 dims are query x key.
    Returns scalar fraction.
    """
    S = attn_matrix.shape[-1]
    if S < 2:
        return 0.0

    mask = torch.triu(torch.ones(S, S, device=attn_matrix.device), diagonal=1).bool()
    upper_values = attn_matrix[..., mask]
    if upper_values.numel() == 0:
        return 0.0
    return (upper_values.abs() < threshold).float().mean().item()


def compute_attention_sparsity(attention_weights: list[tuple]) -> dict:
    """
    Compute overall and upper triangle sparsity across all samples/layers.
    attention_weights: list of per-sample tuples (12 x [1, H, S, S]).
    Returns {overall_sparsity, upper_sparsity, is_causal}.
    """
    upper_scores = []
    overall_scores = []

    for sample_attns in attention_weights:
        for layer_attn in sample_attns:  # [1, H, S, S]
            upper_scores.append(upper_triangle_sparsity(layer_attn))
            overall_scores.append((layer_attn.abs() < 1e-6).float().mean().item())

    upper_mean = np.mean(upper_scores)
    return {
        "overall_sparsity": float(np.mean(overall_scores)),
        "upper_sparsity": float(upper_mean),
        "is_causal": upper_mean > 0.99,
    }


def per_layer_sparsity(attention_weights: list[tuple], num_layers: int = 12) -> list[float]:
    """
    Compute per-layer upper triangle sparsity.
    Returns list of 12 floats (one per layer).
    """
    layer_scores = [[] for _ in range(num_layers)]

    for sample_attns in attention_weights:
        for layer_idx, layer_attn in enumerate(sample_attns):
            if layer_idx < num_layers:
                layer_scores[layer_idx].append(upper_triangle_sparsity(layer_attn))

    return [float(np.mean(scores)) if scores else 0.0 for scores in layer_scores]


def attention_entropy(attn_matrix: torch.Tensor) -> torch.Tensor:
    """
    Compute per-head attention entropy.
    attn_matrix: [B, H, S, S]
    Returns: [B, H] entropy values.
    """
    # Add small epsilon to avoid log(0)
    eps = 1e-10
    attn_probs = attn_matrix + eps
    # Entropy over key dimension
    entropy = -torch.sum(attn_probs * torch.log(attn_probs), dim=-1)  # [B, H, S]
    return entropy.mean(dim=-1)  # [B, H] average over query positions


def aggregate_across_samples(per_sample_metrics: list[dict]) -> dict:
    """
    Aggregate metrics across samples with mean/std.
    """
    if not per_sample_metrics:
        return {}

    keys = per_sample_metrics[0].keys()
    result = {}
    for k in keys:
        values = [m[k] for m in per_sample_metrics if isinstance(m[k], (int, float))]
        if values:
            result[f"{k}_mean"] = float(np.mean(values))
            result[f"{k}_std"] = float(np.std(values))
    return result
