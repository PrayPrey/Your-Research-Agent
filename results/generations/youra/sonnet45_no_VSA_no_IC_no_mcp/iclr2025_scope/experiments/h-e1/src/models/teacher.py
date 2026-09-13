import torch
import torch.nn as nn
from transformers import GPT2Model
from typing import Tuple


class TeacherModel(nn.Module):
    """GPT-2 Small teacher model wrapper."""

    def __init__(self, model_name: str = "gpt2"):
        super().__init__()
        self.model = GPT2Model.from_pretrained(model_name)
        self.model.eval()
        self.model.requires_grad_(False)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor
    ) -> Tuple[torch.Tensor, ...]:
        """
        Args:
            input_ids: [batch, seq_len]
            attention_mask: [batch, seq_len]

        Returns:
            Tuple of 13 tensors [batch, seq_len, 768]
        """
        with torch.no_grad():
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_hidden_states=True
            )
        return outputs.hidden_states
