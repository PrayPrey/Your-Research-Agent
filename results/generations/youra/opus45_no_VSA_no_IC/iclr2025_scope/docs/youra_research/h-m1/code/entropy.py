"""Attention entropy computation."""
import torch
from torch import Tensor


def _entropy_from_attn(attn: Tensor, attention_mask: Tensor) -> Tensor:
    """Per-layer masked Shannon entropy. attn: [B,H,L,L], mask: [B,L]."""
    if attn is None:
        return torch.tensor(0.0)
    mask_2d = attention_mask[:, None, None, :].float()
    masked = attn * mask_2d
    row_sum = masked.sum(dim=-1, keepdim=True)
    masked = torch.where(row_sum > 1e-9, masked / row_sum, torch.zeros_like(masked))
    log_masked = torch.where(masked > 1e-9, masked.log(), torch.zeros_like(masked))
    ent = -(masked * log_masked).sum(dim=-1)
    valid_query = attention_mask[:, None, :].float().expand_as(ent)
    total_valid = valid_query.sum().clamp_min(1)
    return (ent * valid_query).sum() / total_valid


def compute_attention_entropy(model, input_ids: Tensor, attention_mask: Tensor) -> float:
    """Mean Shannon entropy over all layers, masked and renormalized."""
    model.eval()
    with torch.no_grad():
        out = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_attentions=True,
        )
    if out.attentions is None or len(out.attentions) == 0:
        return 0.0
    entropies = []
    for layer_attn in out.attentions:
        if layer_attn is not None:
            ent = _entropy_from_attn(layer_attn, attention_mask)
            if not torch.isnan(ent):
                entropies.append(ent)
    if not entropies:
        return 0.0
    result = torch.stack(entropies).mean().item()
    return result if not (result != result) else 0.0
