"""Entropy computation from token logits."""
import torch
import numpy as np


def compute_token_entropy(scores: tuple) -> float:
    """Compute mean Shannon entropy across generated tokens.

    Args:
        scores: tuple of [1, vocab_size] tensors from generate()

    Returns:
        Mean entropy across all tokens.
    """
    if not scores:
        return float('nan')

    entropies = []
    for score in scores:
        probs = torch.softmax(score[0].float(), dim=-1)  # ensure float32
        # Mask zero probs to avoid 0 * -inf = nan
        mask = probs > 0
        log_probs = torch.zeros_like(probs)
        log_probs[mask] = torch.log(probs[mask])
        h = -torch.sum(probs * log_probs).item()
        entropies.append(h)

    return np.mean(entropies) if entropies else float('nan')


def compute_sample_entropies(responses: list[dict]) -> list[float]:
    """Compute entropy for each response.

    Returns list of entropy values (nan for failed samples).
    """
    return [compute_token_entropy(r.get("scores", ())) for r in responses]
