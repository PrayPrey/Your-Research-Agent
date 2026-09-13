"""
Simple transformer model for multi-stage training experiments.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional, Tuple


class SimpleTransformer(nn.Module):
    """Simple transformer model for language modeling."""

    def __init__(self, vocab_size: int, hidden_size: int, num_layers: int,
                 num_heads: int, max_seq_length: int, dropout: float = 0.1):
        super().__init__()

        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.max_seq_length = max_seq_length

        # Embeddings
        self.token_embedding = nn.Embedding(vocab_size, hidden_size)
        self.position_embedding = nn.Embedding(max_seq_length, hidden_size)

        # Transformer layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_size,
            nhead=num_heads,
            dim_feedforward=hidden_size * 4,
            dropout=dropout,
            activation="gelu",
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)

        # Output head
        self.output_projection = nn.Linear(hidden_size, vocab_size)

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize model weights."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
                if module.bias is not None:
                    torch.nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, input_ids: torch.Tensor,
                attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass.

        Args:
            input_ids: (batch_size, seq_length)
            attention_mask: (batch_size, seq_length)

        Returns:
            logits: (batch_size, seq_length, vocab_size)
        """
        batch_size, seq_length = input_ids.shape

        # Create position ids
        position_ids = torch.arange(seq_length, dtype=torch.long, device=input_ids.device)
        position_ids = position_ids.unsqueeze(0).expand(batch_size, -1)

        # Embeddings
        token_embeds = self.token_embedding(input_ids)
        position_embeds = self.position_embedding(position_ids)
        hidden_states = token_embeds + position_embeds

        # Create attention mask
        if attention_mask is None:
            attention_mask = (input_ids != 0).float()

        # Transformer expects mask where 0 is attend, -inf is ignore
        # PyTorch transformer uses additive mask
        mask = (1.0 - attention_mask) * -10000.0

        # Apply transformer
        hidden_states = self.transformer(hidden_states, src_key_padding_mask=mask)

        # Project to vocabulary
        logits = self.output_projection(hidden_states)

        return logits

    def compute_loss(self, input_ids: torch.Tensor, labels: torch.Tensor,
                    attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Compute cross-entropy loss."""
        logits = self.forward(input_ids, attention_mask)

        # Flatten for loss computation
        loss = F.cross_entropy(
            logits.view(-1, self.vocab_size),
            labels.view(-1),
            ignore_index=-100
        )

        return loss

    def compute_preference_loss(self, chosen_ids: torch.Tensor,
                               rejected_ids: torch.Tensor) -> torch.Tensor:
        """
        Compute preference learning loss (DPO-style).

        Args:
            chosen_ids: (batch_size, seq_length)
            rejected_ids: (batch_size, seq_length)

        Returns:
            loss: scalar
        """
        # Get log probabilities for chosen and rejected
        chosen_logits = self.forward(chosen_ids)
        rejected_logits = self.forward(rejected_ids)

        # Compute log probs (simplified - just use mean logit)
        chosen_logprobs = F.log_softmax(chosen_logits, dim=-1)
        rejected_logprobs = F.log_softmax(rejected_logits, dim=-1)

        # Take mean over sequence
        chosen_score = chosen_logprobs.mean()
        rejected_score = rejected_logprobs.mean()

        # DPO-style loss: maximize difference
        loss = -F.logsigmoid(chosen_score - rejected_score)

        return loss

    def get_flat_params(self) -> torch.Tensor:
        """Get flattened parameters."""
        return torch.cat([p.flatten() for p in self.parameters()])

    def set_flat_params(self, flat_params: torch.Tensor):
        """Set parameters from flattened tensor."""
        offset = 0
        for p in self.parameters():
            numel = p.numel()
            p.data = flat_params[offset:offset + numel].view_as(p)
            offset += numel

    def get_embedding_params(self) -> torch.Tensor:
        """Get embedding layer parameters."""
        return torch.cat([
            self.token_embedding.weight.flatten(),
            self.position_embedding.weight.flatten()
        ])


def create_model(config: dict) -> SimpleTransformer:
    """Create a model from configuration."""
    return SimpleTransformer(
        vocab_size=config["vocab_size"],
        hidden_size=config["hidden_size"],
        num_layers=config["num_layers"],
        num_heads=config["num_heads"],
        max_seq_length=config["max_seq_length"],
        dropout=config["dropout"]
    )
