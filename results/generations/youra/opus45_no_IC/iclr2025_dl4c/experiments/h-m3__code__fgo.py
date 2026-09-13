"""FGO (Fine-Grained Optimization) mask construction and masked PPO loss."""

import torch
from typing import Set, List, Optional


def create_fgo_mask(token_ids: torch.Tensor, token_to_line: List[int], executed_lines: Set[int]) -> torch.Tensor:
    """
    Create FGO mask: 1 for executed tokens, 0 for unexecuted.

    Args:
        token_ids: [seq_len] token indices
        token_to_line: List mapping token position to source line
        executed_lines: Set of executed line numbers

    Returns:
        mask: [seq_len] binary mask (float)
    """
    seq_len = token_ids.shape[-1] if token_ids.dim() > 0 else len(token_ids)
    mask = torch.zeros(seq_len, dtype=torch.float, device=token_ids.device)

    for i in range(min(seq_len, len(token_to_line))):
        if token_to_line[i] in executed_lines:
            mask[i] = 1.0

    return mask


def fgo_ppo_loss(
    logprobs: torch.Tensor,
    old_logprobs: torch.Tensor,
    advantages: torch.Tensor,
    mask: torch.Tensor,
    clip_eps: float = 0.2
) -> torch.Tensor:
    """
    FGO-masked PPO loss (only executed tokens contribute).

    Args:
        logprobs: [B, seq_len] current policy log probs
        old_logprobs: [B, seq_len] old policy log probs
        advantages: [B, seq_len] advantage estimates
        mask: [B, seq_len] FGO mask (1=executed, 0=unexecuted)
        clip_eps: PPO clipping epsilon

    Returns:
        scalar loss
    """
    ratio = torch.exp(logprobs - old_logprobs)
    clipped = torch.clamp(ratio, 1 - clip_eps, 1 + clip_eps)
    per_token_loss = -torch.min(ratio * advantages, clipped * advantages)
    masked_loss = per_token_loss * mask
    return masked_loss.sum() / (mask.sum() + 1e-8)


def standard_ppo_loss(
    logprobs: torch.Tensor,
    old_logprobs: torch.Tensor,
    advantages: torch.Tensor,
    clip_eps: float = 0.2
) -> torch.Tensor:
    """
    Standard PPO loss (all tokens contribute equally).

    Args:
        logprobs: [B, seq_len] current policy log probs
        old_logprobs: [B, seq_len] old policy log probs
        advantages: [B, seq_len] advantage estimates
        clip_eps: PPO clipping epsilon

    Returns:
        scalar loss
    """
    mask = torch.ones_like(logprobs)
    return fgo_ppo_loss(logprobs, old_logprobs, advantages, mask, clip_eps)


def verify_fgo_mechanism(mask: torch.Tensor, logprobs: torch.Tensor) -> None:
    """Verify FGO is actually masking tokens."""
    total = mask.numel()
    executed = mask.sum().item()
    masked_ratio = 1 - (executed / total)

    assert executed < total, "FGO mask should exclude some tokens"
    print(f"[FGO] Masking {int((total - executed))} of {total} tokens ({masked_ratio*100:.1f}% unexecuted)")
