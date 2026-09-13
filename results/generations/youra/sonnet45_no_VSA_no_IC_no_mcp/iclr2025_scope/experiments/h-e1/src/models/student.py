import torch
import torch.nn as nn
from typing import List, Optional


class SimplifiedSSMLayer(nn.Module):
    """Simplified SSM layer (fallback implementation without mamba-ssm)."""

    def __init__(self, d_model: int, d_state: int = 16):
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state

        # Linear projections
        self.input_proj = nn.Linear(d_model, d_state)
        self.state_proj = nn.Linear(d_state, d_state)
        self.output_proj = nn.Linear(d_state, d_model)

        # Layer norm
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: [batch, seq_len, d_model]
        Returns:
            [batch, seq_len, d_model]
        """
        batch, seq_len, _ = x.shape

        # Residual connection
        residual = x

        # Simple recurrent state update
        state = torch.zeros(batch, self.d_state, device=x.device, dtype=x.dtype)
        outputs = []

        for t in range(seq_len):
            # Project input to state space
            x_t = self.input_proj(x[:, t, :])

            # Update state (simplified SSM dynamics)
            state = 0.9 * self.state_proj(state) + 0.1 * x_t

            # Project back to model space
            out_t = self.output_proj(state)
            outputs.append(out_t)

        output = torch.stack(outputs, dim=1)

        # Residual + norm
        return self.norm(output + residual)


class StudentModel(nn.Module):
    """Simplified SSM student model with hidden state extraction."""

    def __init__(
        self,
        d_model: int = 768,
        n_layer: int = 12,
        vocab_size: int = 50257,
        ssm_d_state: int = 16,
        ssm_d_conv: int = 4,
        ssm_expand: int = 2
    ):
        super().__init__()

        # Embedding
        self.embedding = nn.Embedding(vocab_size, d_model)

        # SSM layers
        self.layers = nn.ModuleList([
            SimplifiedSSMLayer(d_model, ssm_d_state)
            for _ in range(n_layer)
        ])

        # LM head
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)

        self.hidden_states = []

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None
    ) -> List[torch.Tensor]:
        """
        Args:
            input_ids: [batch, seq_len]

        Returns:
            List of 12 tensors [batch, seq_len, 768]
        """
        self.hidden_states = []

        x = self.embedding(input_ids)

        for layer in self.layers:
            x = layer(x)
            self.hidden_states.append(x)

        return self.hidden_states
