"""KV Cache Eviction Policies for H-M1 Experiment"""

import torch
from torch import Tensor
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class H2OCacheConfig:
    heavy_ratio: float = 0.125
    recent_ratio: float = 0.125
    n_sink: int = 4
    cache_budget_ratio: float = 0.25

@dataclass
class ProvenanceCacheConfig:
    cache_budget_ratio: float = 0.25
    top_k_passages: int = 5
    high_rel_count: int = 3
    tier_allocation_high: float = 0.5
    tier_allocation_low: float = 0.5

class FullKVCache:
    """No eviction baseline"""
    def evict(self, k: Tensor, v: Tensor) -> Tuple[Tensor, Tensor]:
        return k, v

class H2OCache:
    """H2O baseline: Heavy-hitter + recent tokens"""
    def __init__(self, config: H2OCacheConfig):
        self.heavy_ratio = config.heavy_ratio
        self.recent_ratio = config.recent_ratio
        self.n_sink = config.n_sink
        self.cache_budget_ratio = config.cache_budget_ratio
        self.accumulated_attention: Dict[int, float] = {}

    def update_attention_scores(self, attention_weights: Tensor) -> None:
        """attention_weights: [B, H, Lq, Lkv]"""
        token_importance = attention_weights.sum(dim=(1, 2))  # [B, Lkv]
        for idx in range(token_importance.shape[1]):
            if idx not in self.accumulated_attention:
                self.accumulated_attention[idx] = 0.0
            self.accumulated_attention[idx] += token_importance[0, idx].item()

    def evict(self, k: Tensor, v: Tensor, max_len: int) -> Tuple[Tensor, Tensor]:
        """k, v: [B, H, L, D]"""
        seq_len = k.shape[2]
        cache_budget = int(max_len * self.cache_budget_ratio)

        keep_mask = torch.zeros(seq_len, dtype=torch.bool, device=k.device)

        # Tier 0: Sinks
        keep_mask[:self.n_sink] = True

        # Tier 1: Heavy hitters
        n_heavy = int(cache_budget * self.heavy_ratio)
        if len(self.accumulated_attention) > 0:
            attention_scores = torch.tensor([
                self.accumulated_attention.get(i, 0.0) for i in range(seq_len)
            ], device=k.device)
            attention_scores[:self.n_sink] = -float('inf')
            heavy_indices = torch.topk(attention_scores, k=min(n_heavy, seq_len)).indices
            keep_mask[heavy_indices] = True

        # Tier 2: Recent
        n_recent = int(cache_budget * self.recent_ratio)
        keep_mask[-n_recent:] = True

        # Re-index tracker
        kept_indices = torch.where(keep_mask)[0].tolist()
        self.accumulated_attention = {
            new_idx: self.accumulated_attention[old_idx]
            for new_idx, old_idx in enumerate(kept_indices)
            if old_idx in self.accumulated_attention
        }

        return k[:, :, keep_mask, :], v[:, :, keep_mask, :]

class ProvenanceCache:
    """Provenance-aware tiered eviction"""
    def __init__(self, config: ProvenanceCacheConfig):
        self.cache_budget_ratio = config.cache_budget_ratio
        self.high_rel_count = config.high_rel_count
        self.tier_allocation_high = config.tier_allocation_high
        self.tier_allocation_low = config.tier_allocation_low
        self.provenance_metadata: Dict[int, Tuple[str, float]] = {}

    def register_provenance(
        self,
        token_indices: List[int],
        token_types: List[str],
        relevance_scores: List[float]
    ) -> None:
        """types: ['query', 'high_rel_passage', 'low_rel_passage']"""
        for idx, t_type, score in zip(token_indices, token_types, relevance_scores):
            self.provenance_metadata[idx] = (t_type, score)

    def evict(self, k: Tensor, v: Tensor, max_len: int) -> Tuple[Tensor, Tensor]:
        """k, v: [B, H, L, D]"""
        seq_len = k.shape[2]
        cache_budget = int(max_len * self.cache_budget_ratio)

        keep_mask = torch.zeros(seq_len, dtype=torch.bool, device=k.device)

        # Tier 0: Query tokens
        query_indices = [i for i, (t, _) in self.provenance_metadata.items() if t == "query"]
        keep_mask[query_indices] = True

        # Tier 1: High-rel passages
        high_rel = [(i, score) for i, (t, score) in self.provenance_metadata.items() if t == "high_rel_passage"]
        high_rel.sort(key=lambda x: x[1], reverse=True)
        n_high = min(len(high_rel), int(cache_budget * self.tier_allocation_high))
        keep_mask[[i for i, _ in high_rel[:n_high]]] = True

        # Tier 2: Low-rel passages
        low_rel = [(i, score) for i, (t, score) in self.provenance_metadata.items() if t == "low_rel_passage"]
        n_low = cache_budget - keep_mask.sum().item()
        if n_low > 0:
            keep_mask[[i for i, _ in low_rel[:n_low]]] = True

        return k[:, :, keep_mask, :], v[:, :, keep_mask, :]

class RandomCache:
    """Random eviction baseline"""
    def __init__(self, budget_ratio: float = 0.25):
        self.budget_ratio = budget_ratio

    def evict(self, k: Tensor, v: Tensor, max_len: int) -> Tuple[Tensor, Tensor]:
        seq_len = k.shape[2]
        cache_budget = int(max_len * self.budget_ratio)

        indices = torch.randperm(seq_len, device=k.device)[:cache_budget]
        indices = indices.sort()[0]

        return k[:, :, indices, :], v[:, :, indices, :]
