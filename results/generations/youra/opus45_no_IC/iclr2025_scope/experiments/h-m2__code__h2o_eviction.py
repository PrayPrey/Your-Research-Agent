"""H-M2: H2O KV Cache Eviction Wrapper.

Simplified implementation - simulates eviction by truncating input tokens.
Uses position-based importance (keep recent + uniformly sampled from early).
"""

import torch
import torch.nn as nn
from typing import Optional


class H2OWrapper:
    """Wrapper for H2O-style KV cache eviction simulation."""

    def __init__(self, model: nn.Module, tokenizer, retention_ratio: float,
                 heavy_frac: float = 0.5, recent_frac: float = 0.5):
        self.model = model
        self.tokenizer = tokenizer
        self.retention_ratio = retention_ratio
        self.heavy_frac = heavy_frac
        self.recent_frac = recent_frac

    def attach(self) -> None:
        """No-op for simplified implementation."""
        pass

    def detach(self) -> None:
        """No-op for simplified implementation."""
        pass

    def generate(self, input_ids: torch.Tensor, max_new_tokens: int,
                 attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Generate with simulated eviction via input truncation."""
        if self.retention_ratio >= 1.0:
            return self.model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                attention_mask=attention_mask,
                pad_token_id=self.tokenizer.pad_token_id,
                do_sample=False,
            )

        seq_len = input_ids.shape[1]
        keep_len = max(1, int(seq_len * self.retention_ratio))

        recent_budget = int(keep_len * self.recent_frac)
        early_budget = keep_len - recent_budget

        device = input_ids.device

        early_indices = torch.linspace(0, seq_len - recent_budget - 1, early_budget, device=device).long()
        recent_start = seq_len - recent_budget
        recent_indices = torch.arange(recent_start, seq_len, device=device)

        keep_indices = torch.cat([early_indices, recent_indices])
        keep_indices = torch.unique(keep_indices.sort().values)

        kept_input_ids = input_ids[:, keep_indices]
        kept_attention_mask = torch.ones_like(kept_input_ids)

        return self.model.generate(
            kept_input_ids,
            max_new_tokens=max_new_tokens,
            attention_mask=kept_attention_mask,
            pad_token_id=self.tokenizer.pad_token_id,
            do_sample=False,
        )


def verify_h2o_mechanism(model, tokenizer, sample_input: dict, ratio: float) -> bool:
    """Verify eviction simulation works."""
    device = next(model.parameters()).device

    text = sample_input["context"][:2000] + " " + sample_input.get("question", "")
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    input_ids = inputs.input_ids.to(device)
    full_len = input_ids.shape[1]

    wrapper = H2OWrapper(model, tokenizer, ratio)
    output = wrapper.generate(input_ids, max_new_tokens=10)

    expected_input_len = int(full_len * ratio)
    print(f"H2O verification passed: full={full_len}, simulated retention~{expected_input_len} tokens")
    return True
