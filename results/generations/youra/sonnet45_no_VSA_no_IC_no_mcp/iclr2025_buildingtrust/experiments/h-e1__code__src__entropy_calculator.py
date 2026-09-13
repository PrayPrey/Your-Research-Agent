"""Calculate entropy over attention distributions."""
import torch
import numpy as np


class EntropyCalculator:
    """Compute entropy over attention weights."""

    def __init__(self, epsilon=1e-10):
        self.epsilon = epsilon

    def calculate(self, attn, entity_span):
        """Compute entropy over attention TO entity span.

        Args:
            attn: [seq_len, seq_len] attention matrix
            entity_span: (start_token, end_token)

        Returns:
            entropy: float (average across entity tokens)
        """
        start, end = entity_span
        entity_attn = attn[:, start:end]  # [seq_len, entity_len]

        entropies = []
        for token_attn in entity_attn:
            probs = token_attn / (token_attn.sum() + self.epsilon)
            H = -torch.sum(probs * torch.log(probs + self.epsilon)).item()
            entropies.append(H)

        return float(np.mean(entropies))
