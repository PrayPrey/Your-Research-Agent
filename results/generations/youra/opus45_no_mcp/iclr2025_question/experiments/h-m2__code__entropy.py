"""Token entropy computation (from h-e1 spec)"""
import torch


def token_entropy(logits: torch.Tensor) -> float:
    """Compute Shannon entropy for single token logits."""
    probs = torch.softmax(logits, dim=-1)
    log_probs = torch.log(probs + 1e-10)
    entropy = -torch.sum(probs * log_probs).item()
    return entropy


def compute_token_entropy(scores: list) -> float:
    """Compute mean entropy across all generated tokens."""
    if not scores:
        return 0.0
    entropies = [token_entropy(s) for s in scores]
    return sum(entropies) / len(entropies)
