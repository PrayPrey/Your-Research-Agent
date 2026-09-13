import torch
from torch import Tensor
from transformers import AutoTokenizer, AutoModel
from typing import Optional
import numpy as np


class HiddenStateExtractor:
    """Extract hidden states from transformer model."""

    def __init__(self, model_name: str = "bert-base-uncased", device: str = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
        self.hidden_dim = self.model.config.hidden_size

    def extract(self, texts: list[str], max_length: int = 128, batch_size: int = 32) -> Tensor:
        """Extract hidden states [N, seq, hidden_dim] from texts."""
        all_hidden = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]

            inputs = self.tokenizer(
                batch_texts,
                padding="max_length",
                truncation=True,
                max_length=max_length,
                return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs, output_hidden_states=True)
                hidden = outputs.last_hidden_state

            all_hidden.append(hidden.cpu())

        return torch.cat(all_hidden, dim=0)

    def extract_pooled(self, texts: list[str], max_length: int = 128, batch_size: int = 32) -> Tensor:
        """Extract mean-pooled hidden states [N, hidden_dim]."""
        hidden = self.extract(texts, max_length, batch_size)
        return hidden.mean(dim=1)


def cache_hidden_states(extractor: HiddenStateExtractor, texts: list[str],
                        cache_path: str, batch_size: int = 32) -> Tensor:
    """Extract and cache hidden states."""
    import os
    if os.path.exists(cache_path):
        return torch.load(cache_path)

    hidden = extractor.extract(texts, batch_size=batch_size)
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    torch.save(hidden, cache_path)
    return hidden
