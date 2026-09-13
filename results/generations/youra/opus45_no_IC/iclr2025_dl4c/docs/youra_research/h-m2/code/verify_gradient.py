"""Gradient exclusion verification for FGO mechanism."""

import torch
import torch.nn as nn
from typing import Dict, Any


class GradientExclusionVerifier:
    """Verify that masked tokens receive zero gradient in FGO loss."""

    def __init__(self, model: nn.Module):
        self.model = model
        self._captured_grad = None
        self._hook_handle = None

    def verify(
        self,
        logprobs: torch.Tensor,
        old_logprobs: torch.Tensor,
        advantages: torch.Tensor,
        mask: torch.Tensor,
        clip_eps: float = 0.2
    ) -> Dict[str, Any]:
        """
        Verify gradient exclusion for masked positions.

        Args:
            logprobs: [B, seq_len] current log probs (requires_grad=True)
            old_logprobs: [B, seq_len] old log probs (detached)
            advantages: [B, seq_len] advantage estimates
            mask: [B, seq_len] FGO mask (1=executed, 0=masked)
            clip_eps: PPO clip epsilon

        Returns:
            Dict with gradient norms and verification status
        """
        # Compute FGO-masked PPO loss
        ratio = torch.exp(logprobs - old_logprobs)
        clipped = torch.clamp(ratio, 1 - clip_eps, 1 + clip_eps)
        per_token_loss = -torch.min(ratio * advantages, clipped * advantages)
        masked_loss = per_token_loss * mask
        loss = masked_loss.sum() / (mask.sum() + 1e-8)

        # Backward to compute gradients
        if logprobs.grad is not None:
            logprobs.grad.zero_()
        loss.backward(retain_graph=True)

        if logprobs.grad is None:
            return {
                "executed_grad_norm": 0.0,
                "non_executed_grad_norm": 0.0,
                "gradient_exclusion_verified": False,
                "error": "No gradient computed"
            }

        # Compute per-position gradient norms
        grad = logprobs.grad.detach()
        per_token_grad_norm = grad.abs()

        # Split by mask
        mask_bool = mask.bool()
        executed_norms = per_token_grad_norm[mask_bool]
        non_executed_norms = per_token_grad_norm[~mask_bool]

        exec_mean = executed_norms.mean().item() if executed_norms.numel() > 0 else 0.0
        non_exec_mean = non_executed_norms.mean().item() if non_executed_norms.numel() > 0 else 0.0

        # Verification: non-executed should be ~0, executed should be >0
        verified = (non_exec_mean < 1e-6) and (exec_mean > 1e-6 or mask.sum() == 0)

        return {
            "executed_grad_norm": float(exec_mean),
            "non_executed_grad_norm": float(non_exec_mean),
            "gradient_exclusion_verified": verified,
            "num_executed": int(mask.sum().item()),
            "num_masked": int((~mask_bool).sum().item()),
            "loss": float(loss.item())
        }


def verify_gradient_exclusion_simple(
    mask: torch.Tensor,
    per_token_loss: torch.Tensor
) -> Dict[str, float]:
    """
    Simple verification: check that masked positions have zero loss contribution.

    Args:
        mask: [B, seq_len] FGO mask
        per_token_loss: [B, seq_len] per-token loss values before masking

    Returns:
        Dict with verification metrics
    """
    mask_bool = mask.bool()
    masked_contribution = per_token_loss[~mask_bool].abs().sum().item()
    unmasked_contribution = per_token_loss[mask_bool].abs().sum().item()

    verified = masked_contribution < 1e-10

    return {
        "masked_loss_contribution": float(masked_contribution),
        "unmasked_loss_contribution": float(unmasked_contribution),
        "gradient_exclusion_verified": verified
    }
