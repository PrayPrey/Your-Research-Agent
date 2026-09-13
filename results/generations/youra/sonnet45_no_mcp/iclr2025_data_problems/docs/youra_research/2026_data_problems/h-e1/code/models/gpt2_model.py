"""
GPT-2 Style Transformer Model
Decoder-only architecture for language modeling with 1B and 7B scale configurations.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional


class GPT2Config:
    """Configuration for GPT-2 model."""

    def __init__(
        self,
        vocab_size: int = 50257,
        n_layer: int = 24,
        n_head: int = 16,
        n_embd: int = 1536,
        n_positions: int = 2048,
        dropout: float = 0.1
    ):
        self.vocab_size = vocab_size
        self.n_layer = n_layer
        self.n_head = n_head
        self.n_embd = n_embd
        self.n_positions = n_positions
        self.dropout = dropout


class MultiHeadAttention(nn.Module):
    """Multi-head self-attention mechanism."""

    def __init__(self, config: GPT2Config):
        super().__init__()
        self.n_head = config.n_head
        self.n_embd = config.n_embd
        self.head_dim = config.n_embd // config.n_head

        assert config.n_embd % config.n_head == 0

        # Query, Key, Value projections
        self.qkv = nn.Linear(config.n_embd, 3 * config.n_embd)
        self.out_proj = nn.Linear(config.n_embd, config.n_embd)

        self.dropout = nn.Dropout(config.dropout)

        # Causal mask
        self.register_buffer(
            "causal_mask",
            torch.tril(torch.ones(config.n_positions, config.n_positions))
                .view(1, 1, config.n_positions, config.n_positions)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, seq_len, n_embd)
        Returns:
            (batch, seq_len, n_embd)
        """
        B, T, C = x.size()

        # Calculate Q, K, V
        qkv = self.qkv(x)
        q, k, v = qkv.split(self.n_embd, dim=2)

        # Reshape to (B, n_head, T, head_dim)
        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)

        # Attention scores
        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)

        # Apply causal mask
        scores = scores.masked_fill(
            self.causal_mask[:, :, :T, :T] == 0,
            float('-inf')
        )

        attn = F.softmax(scores, dim=-1)
        attn = self.dropout(attn)

        # Weighted sum of values
        out = attn @ v  # (B, n_head, T, head_dim)
        out = out.transpose(1, 2).contiguous().view(B, T, C)

        return self.out_proj(out)


class FeedForward(nn.Module):
    """Position-wise feed-forward network."""

    def __init__(self, config: GPT2Config):
        super().__init__()
        self.fc1 = nn.Linear(config.n_embd, 4 * config.n_embd)
        self.fc2 = nn.Linear(4 * config.n_embd, config.n_embd)
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = F.gelu(x)
        x = self.fc2(x)
        x = self.dropout(x)
        return x


class TransformerBlock(nn.Module):
    """Single transformer decoder block."""

    def __init__(self, config: GPT2Config):
        super().__init__()
        self.ln1 = nn.LayerNorm(config.n_embd)
        self.attn = MultiHeadAttention(config)
        self.ln2 = nn.LayerNorm(config.n_embd)
        self.ffn = FeedForward(config)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Pre-norm architecture
        x = x + self.attn(self.ln1(x))
        x = x + self.ffn(self.ln2(x))
        return x


class GPT2Model(nn.Module):
    """GPT-2 style decoder-only transformer."""

    def __init__(self, config: GPT2Config):
        super().__init__()
        self.config = config

        # Token and position embeddings
        self.token_embedding = nn.Embedding(config.vocab_size, config.n_embd)
        self.position_embedding = nn.Embedding(config.n_positions, config.n_embd)
        self.dropout = nn.Dropout(config.dropout)

        # Transformer blocks
        self.blocks = nn.ModuleList([
            TransformerBlock(config) for _ in range(config.n_layer)
        ])

        # Final layer norm and output projection
        self.ln_f = nn.LayerNorm(config.n_embd)
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size, bias=False)

        # Weight tying
        self.token_embedding.weight = self.lm_head.weight

        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(
        self,
        input_ids: torch.Tensor,
        labels: Optional[torch.Tensor] = None
    ) -> tuple:
        """
        Args:
            input_ids: (batch, seq_len) token indices
            labels: (batch, seq_len) target tokens for loss computation

        Returns:
            If labels provided: (loss, logits)
            Otherwise: logits
        """
        B, T = input_ids.size()

        # Get embeddings
        token_emb = self.token_embedding(input_ids)  # (B, T, n_embd)
        pos_emb = self.position_embedding(torch.arange(T, device=input_ids.device))  # (T, n_embd)

        x = self.dropout(token_emb + pos_emb)

        # Forward through transformer blocks
        for block in self.blocks:
            x = block(x)

        x = self.ln_f(x)
        logits = self.lm_head(x)  # (B, T, vocab_size)

        loss = None
        if labels is not None:
            # Compute cross-entropy loss
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)),
                labels.view(-1),
                ignore_index=-100
            )

        return (loss, logits) if loss is not None else logits

    def get_num_params(self) -> int:
        """Return total number of parameters."""
        return sum(p.numel() for p in self.parameters())


def create_model(scale: str) -> GPT2Model:
    """
    Create GPT-2 model for specified scale.

    Args:
        scale: "1B" or "7B"

    Returns:
        GPT2Model instance
    """
    configs = {
        "1B": GPT2Config(
            vocab_size=50257,
            n_layer=24,
            n_head=16,
            n_embd=1536,
            n_positions=2048,
            dropout=0.1
        ),
        "7B": GPT2Config(
            vocab_size=50257,
            n_layer=32,
            n_head=32,
            n_embd=4096,
            n_positions=2048,
            dropout=0.1
        )
    }

    if scale not in configs:
        raise ValueError(f"Unknown scale: {scale}. Choose '1B' or '7B'")

    model = GPT2Model(configs[scale])
    print(f"Created {scale} model with {model.get_num_params():,} parameters")
    return model
