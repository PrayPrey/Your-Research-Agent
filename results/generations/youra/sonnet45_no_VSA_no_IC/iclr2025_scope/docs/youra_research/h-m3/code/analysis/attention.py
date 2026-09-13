"""Query-token attention extraction and stratified analysis."""
import torch
import numpy as np
from typing import Tuple


class QueryTokenAttentionExtractor:
    def __init__(self, tokenizer):
        """Store tokenizer for query token boundary detection."""
        self.tokenizer = tokenizer

    def locate_query_tokens(self, full_input_ids: torch.Tensor, query: str) -> Tuple[int, int]:
        """Find query token positions in full input.

        Returns: (start_idx, end_idx)
        """
        query_ids = self.tokenizer.encode(query, add_special_tokens=False)
        query_len = len(query_ids)
        # Query assumed at start of prompt after special tokens
        # For LongBench format: "Context: ... Question: {query} Answer:"
        # We need to find the query tokens in the full input
        full_ids_list = full_input_ids[0].tolist() if full_input_ids.dim() > 1 else full_input_ids.tolist()

        # Simple search for query token sequence
        for i in range(len(full_ids_list) - len(query_ids) + 1):
            if full_ids_list[i:i+len(query_ids)] == query_ids:
                return (i, i + len(query_ids))

        # Fallback: assume query near middle (after "Question:")
        mid = len(full_ids_list) // 2
        return (mid, mid + len(query_ids))

    def extract_concentration(
        self,
        query: str,
        attentions: tuple,  # From model output
        input_ids: torch.Tensor
    ) -> float:
        """Query attention mass / total attention mass.

        attentions: tuple of [B, H, S, S] per layer
        Returns: float in [0, 1]
        """
        last_layer_attn = attentions[-1][0]  # [H, S, S], batch=0
        avg_heads = last_layer_attn.mean(dim=0)  # [S, S]

        query_start, query_end = self.locate_query_tokens(input_ids, query)

        # Sum attention to query tokens
        query_attn_mass = avg_heads[:, query_start:query_end].sum().item()
        total_attn_mass = avg_heads.sum().item()

        return query_attn_mass / total_attn_mass if total_attn_mass > 0 else 0.0
