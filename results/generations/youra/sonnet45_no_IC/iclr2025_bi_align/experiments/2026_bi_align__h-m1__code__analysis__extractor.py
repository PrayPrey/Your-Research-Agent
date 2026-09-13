"""
Hidden State Extractor
Extracts layer 47 hidden states from GPT-2 XL models
"""

import torch
import torch.nn as nn
from typing import Optional
from pathlib import Path

class HiddenStateExtractor:
    """Extract hidden states from final transformer layer."""

    def __init__(self, model: nn.Module, device: str = "cuda"):
        self.model = model
        self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()

    def extract_from_batch(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor
    ) -> torch.Tensor:
        """
        Extract hidden states from a batch.

        Args:
            input_ids: [B, L] input token IDs
            attention_mask: [B, L] attention mask

        Returns:
            [B, H=1600] mean-pooled hidden states
        """
        with torch.no_grad():
            input_ids = input_ids.to(self.device)
            attention_mask = attention_mask.to(self.device)

            # Forward pass with hidden states
            outputs = self.model.model(
                input_ids,
                attention_mask=attention_mask,
                output_hidden_states=True
            )

            # Get final layer hidden states
            last_hidden = outputs.hidden_states[-1]  # [B, L, H=1600]

            # Mean pooling over sequence dimension
            pooled = last_hidden.mean(dim=1)  # [B, H]

            return pooled.cpu()

    def extract_from_dataset(self, dataloader) -> torch.Tensor:
        """
        Extract hidden states from entire dataset.

        Args:
            dataloader: PyTorch DataLoader

        Returns:
            [N, H] tensor of hidden states
        """
        all_hidden = []

        for batch in dataloader:
            hidden = self.extract_from_batch(
                batch['input_ids'],
                batch['attention_mask']
            )
            all_hidden.append(hidden)

        return torch.cat(all_hidden, dim=0)

    def save_hidden_states(self, hidden_states: torch.Tensor, save_path: str):
        """Save hidden states to disk."""
        torch.save(hidden_states, save_path)
