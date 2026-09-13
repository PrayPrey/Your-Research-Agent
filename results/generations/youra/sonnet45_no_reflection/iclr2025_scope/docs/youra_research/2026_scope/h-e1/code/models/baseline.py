"""
Baseline model: Frozen Mixtral-8x7B with native MoE routing.
"""
import torch
import torch.nn as nn
from typing import Dict, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import ModelConfig


class BaselineModel(nn.Module):
    """Frozen Mixtral-8x7B baseline model."""

    def __init__(self, config: ModelConfig):
        """
        Initialize baseline with frozen weights.

        Args:
            config: ModelConfig instance
        """
        super().__init__()
        self.config = config
        self.model = None
        self.tokenizer = None

    def load_pretrained(self, device_map: str = "auto") -> None:
        """
        Load pretrained Mixtral-8x7B and freeze weights.

        Args:
            device_map: Device mapping strategy
        """
        print(f"Loading baseline model: {self.config.model_name}")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            torch_dtype=torch.bfloat16,
            device_map=device_map,
            use_cache=False,
            trust_remote_code=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)

        # Freeze all parameters
        for param in self.model.parameters():
            param.requires_grad = False

        print("Baseline model loaded and frozen")

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass.

        Args:
            input_ids: Input token IDs [B, S]
            attention_mask: Attention mask [B, S]
            labels: Optional labels for loss [B, S]

        Returns:
            Dictionary with loss, logits, hidden_states
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_pretrained() first.")

        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
            output_hidden_states=True
        )

        return {
            'loss': outputs.loss if labels is not None else None,
            'logits': outputs.logits,
            'hidden_states': outputs.hidden_states[-1] if outputs.hidden_states else None
        }
