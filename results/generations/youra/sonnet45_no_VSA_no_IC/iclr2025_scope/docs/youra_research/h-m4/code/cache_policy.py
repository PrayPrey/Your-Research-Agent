"""Provenance-aware tiered cache eviction with diversity scoring."""
import torch
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from mmr_diversity import MMRDiversityScorer


@dataclass
class ProvenanceCacheConfig:
    """Configuration for provenance-based tiered eviction."""
    cache_budget_ratio: float = 0.25
    tier_allocation_query: float = 0.10
    tier_allocation_high: float = 0.60
    tier_allocation_low: float = 0.30

    def __post_init__(self):
        total = self.tier_allocation_query + self.tier_allocation_high + self.tier_allocation_low
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Tier allocation must sum to 1.0, got {total}")


class ProvenanceCacheBase:
    """Base class for tiered eviction policies."""

    def __init__(self, config: ProvenanceCacheConfig):
        self.config = config
        self.provenance_metadata: Dict[int, Tuple[str, float]] = {}

    def register_provenance(
        self,
        token_indices: List[int],
        token_types: List[str],
        relevance_scores: List[float]
    ):
        """Register provenance metadata for tokens.

        Args:
            token_indices: Token position indices
            token_types: 'query' | 'passage_0' | 'passage_1' ...
            relevance_scores: Contriever scores for passages (0.0 for query)
        """
        for idx, typ, score in zip(token_indices, token_types, relevance_scores):
            self.provenance_metadata[idx] = (typ, score)

    def assign_tier(self, token_type: str, relevance_score: float, top_k_threshold: int = 5) -> int:
        """Assign tier based on provenance and relevance.

        Args:
            token_type: 'query' or 'passage_X'
            relevance_score: Contriever score
            top_k_threshold: How many passages qualify as high-relevance

        Returns:
            0 = query tokens (always retained)
            1 = high-relevance passages (top-k by score)
            2 = low-relevance passages (remaining)
        """
        if token_type == 'query':
            return 0
        # Tier 1/2 assignment based on relevance rank handled by select_passages_for_tier
        return 1 if relevance_score > 0 else 2

    def select_passages_for_tier(
        self,
        tier: int,
        passage_ids: List[str],
        passage_scores: Dict[str, float],
        budget_tokens: int,
        passage_embeddings: Optional[Dict[str, torch.Tensor]] = None,
        query_embedding: Optional[torch.Tensor] = None
    ) -> List[str]:
        """Select passages within tier budget (abstract method)."""
        raise NotImplementedError


class ProvenanceCacheFull(ProvenanceCacheBase):
    """Diversity-aware cache with MMR scoring."""

    def __init__(self, config: ProvenanceCacheConfig, diversity_scorer: MMRDiversityScorer):
        super().__init__(config)
        self.diversity_scorer = diversity_scorer

    def select_passages_for_tier(
        self,
        tier: int,
        passage_ids: List[str],
        passage_scores: Dict[str, float],
        budget_tokens: int,
        passage_embeddings: Optional[Dict[str, torch.Tensor]] = None,
        query_embedding: Optional[torch.Tensor] = None
    ) -> List[str]:
        """Select diverse passages using MMR."""
        if not passage_ids or passage_embeddings is None or query_embedding is None:
            return []

        # Stack embeddings
        emb_list = [passage_embeddings[pid] for pid in passage_ids]
        scores_list = [passage_scores[pid] for pid in passage_ids]

        passage_embs = torch.stack(emb_list)  # [N, 768]
        passage_score_tensor = torch.tensor(scores_list, dtype=torch.float32)  # [N]

        # MMR selection
        selected_indices, _ = self.diversity_scorer.select_diverse_passages(
            query_embedding,
            passage_embs,
            passage_score_tensor,
            budget_tokens
        )

        return [passage_ids[i] for i in selected_indices]


class ProvenanceCacheRelevanceOnly(ProvenanceCacheBase):
    """Relevance-only cache (ablation baseline)."""

    def select_passages_for_tier(
        self,
        tier: int,
        passage_ids: List[str],
        passage_scores: Dict[str, float],
        budget_tokens: int,
        passage_embeddings: Optional[Dict[str, torch.Tensor]] = None,
        query_embedding: Optional[torch.Tensor] = None
    ) -> List[str]:
        """Select passages by relevance score (greedy)."""
        if not passage_ids:
            return []

        # Sort by relevance descending
        sorted_passages = sorted(passage_ids, key=lambda p: passage_scores[p], reverse=True)

        # Greedily retain until budget
        avg_passage_len = 100  # Tokens per passage (estimated)
        max_passages = budget_tokens // avg_passage_len

        return sorted_passages[:max_passages]
