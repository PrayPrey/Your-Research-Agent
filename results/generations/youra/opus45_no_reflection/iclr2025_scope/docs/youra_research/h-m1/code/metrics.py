"""Entropy and sparsity metrics for H-M1."""
import torch
import numpy as np
from torch import Tensor
from typing import List

def compute_entropy(attention_weights: Tensor, clamp_min: float = 1e-10) -> Tensor:
    """Shannon entropy per query position. attn: [B,H,S,S] -> [B,H,S]"""
    p = attention_weights.clamp(min=clamp_min)
    H = -(p * p.log()).sum(dim=-1)
    return H

def compute_sparsity(attention_weights: Tensor, top_k: int = 32) -> Tensor:
    """Top-k mass fraction per query position. attn: [B,H,S,S] -> [B,H,S]"""
    k = min(top_k, attention_weights.size(-1))
    topk_vals, _ = attention_weights.topk(k=k, dim=-1)
    return topk_vals.sum(dim=-1)

def aggregate_stats(values: List[float]) -> dict:
    """Compute mean, std, 95% CI."""
    arr = np.array(values)
    n = len(arr)
    mean = float(arr.mean())
    std = float(arr.std())
    ci_margin = 1.96 * std / np.sqrt(n) if n > 1 else 0.0
    return {
        "mean": mean,
        "std": std,
        "ci95_lo": mean - ci_margin,
        "ci95_hi": mean + ci_margin,
        "n": n
    }

def entropy_change_pct(entropy_a: float, entropy_b: float) -> float:
    """Percentage change from a to b."""
    return (entropy_b - entropy_a) / entropy_a if entropy_a != 0 else 0.0

def find_inflection_point(lengths: List[int], entropies: List[float]) -> int:
    """Find inflection point via second derivative of entropy vs log(length)."""
    log_len = np.log(lengths)
    d1 = np.gradient(entropies, log_len)
    d2 = np.gradient(d1, log_len)
    return int(np.argmax(np.abs(d2)))
