"""Text embedding pipeline for H-M1 experiment."""
import torch
import torch.nn as nn
from transformers import PreTrainedModel, PreTrainedTokenizerBase


class Projector(nn.Module):
    """Project encoder hidden dim to embedding dim."""

    def __init__(self, in_dim: int, out_dim: int = 256):
        super().__init__()
        self.proj = nn.Linear(in_dim, out_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.proj(x)


def embed_text(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    texts: list[str],
    projector: Projector,
    max_length: int = 512,
) -> torch.Tensor:
    """Get projected embeddings for text sequences via mean pooling."""
    device = next(model.parameters()).device
    inputs = tokenizer(
        texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=max_length,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.encoder(**inputs)
        hidden = outputs.last_hidden_state
        mask = inputs["attention_mask"].unsqueeze(-1)
        pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
        projected = projector(pooled)

    return projected
