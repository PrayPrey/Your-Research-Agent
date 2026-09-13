"""H-M4 Baselines: Token entropy and sequence NLL computation."""
import torch
import torch.nn.functional as F
import numpy as np


def compute_token_entropy(logits: torch.Tensor) -> float:
    """Compute mean per-token entropy. logits: [gen_len, vocab]."""
    if logits.numel() == 0:
        return 0.0
    probs = F.softmax(logits, dim=-1)
    log_probs = F.log_softmax(logits, dim=-1)
    token_entropy = -(probs * log_probs).sum(dim=-1)
    return token_entropy.mean().item()


def compute_sequence_nll(logits: torch.Tensor, token_ids: torch.Tensor) -> float:
    """Compute avg NLL. logits: [gen_len, vocab], token_ids: [gen_len]."""
    if logits.numel() == 0 or token_ids.numel() == 0:
        return 0.0
    log_probs = F.log_softmax(logits, dim=-1)
    token_lp = log_probs.gather(1, token_ids.unsqueeze(1)).squeeze(1)
    return (-token_lp.mean()).item()


def compute_all_baselines(gen_outputs: list) -> dict:
    """Aggregate baselines over all generations. Negated for confidence direction."""
    entropy_scores = []
    nll_scores = []

    for out in gen_outputs:
        entropy = compute_token_entropy(out["scores"])
        nll = compute_sequence_nll(out["scores"], out["generated_ids"])
        entropy_scores.append(-entropy)  # Negate: higher = more confident
        nll_scores.append(-nll)  # Negate: higher = more confident

    return {
        "entropy_scores": np.array(entropy_scores),
        "nll_scores": np.array(nll_scores)
    }
