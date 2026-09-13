"""MMR-based diversity scoring for passage selection."""
import torch
import torch.nn.functional as F
from typing import List, Tuple


class MMRDiversityScorer:
    """Greedy MMR selection with relevance-diversity tradeoff."""

    def __init__(self, lambda_param: float = 0.5):
        """Initialize MMR scorer.

        Args:
            lambda_param: Relevance weight (0=pure diversity, 1=pure relevance)
        """
        if not 0.0 <= lambda_param <= 1.0:
            raise ValueError(f"lambda_param must be in [0, 1], got {lambda_param}")
        self.lambda_param = lambda_param

    def select_diverse_passages(
        self,
        query_embedding: torch.Tensor,
        passage_embeddings: torch.Tensor,
        passage_scores: torch.Tensor,
        budget_tokens: int,
        avg_passage_len: int = 100
    ) -> Tuple[List[int], List[float]]:
        """Greedily select diverse passages within token budget.

        Args:
            query_embedding: Query vector [768]
            passage_embeddings: Passage vectors [N, 768]
            passage_scores: Contriever relevance scores [N]
            budget_tokens: Maximum tokens to retain
            avg_passage_len: Avg tokens per passage (for budget conversion)

        Returns:
            (selected_indices, mmr_scores)
        """
        n_passages = passage_embeddings.shape[0]
        max_passages = budget_tokens // avg_passage_len

        selected = []
        selected_scores = []
        candidates = set(range(n_passages))

        for _ in range(min(max_passages, n_passages)):
            if not candidates:
                break

            best_score = float('-inf')
            best_idx = None

            for idx in candidates:
                mmr = self.compute_mmr_score(
                    idx,
                    query_embedding,
                    passage_embeddings,
                    passage_scores,
                    selected
                )

                if mmr > best_score:
                    best_score = mmr
                    best_idx = idx

            selected.append(best_idx)
            selected_scores.append(best_score)
            candidates.remove(best_idx)

        return selected, selected_scores

    def compute_mmr_score(
        self,
        candidate_idx: int,
        query_embedding: torch.Tensor,
        passage_embeddings: torch.Tensor,
        passage_scores: torch.Tensor,
        selected_indices: List[int]
    ) -> float:
        """Compute MMR = λ * relevance - (1-λ) * max_similarity.

        Args:
            candidate_idx: Index of candidate passage
            query_embedding: Query vector [768]
            passage_embeddings: Passage vectors [N, 768]
            passage_scores: Contriever relevance scores [N]
            selected_indices: Already selected passage indices

        Returns:
            MMR score (float)
        """
        # Relevance term (normalized to [0, 1])
        relevance = float(passage_scores[candidate_idx])

        # Diversity term
        if not selected_indices:
            max_sim = 0.0
        else:
            candidate_emb = passage_embeddings[candidate_idx].unsqueeze(0)  # [1, 768]
            selected_embs = passage_embeddings[selected_indices]  # [k, 768]

            # Batch cosine similarity
            sims = F.cosine_similarity(candidate_emb, selected_embs, dim=1)  # [k]
            max_sim = float(sims.max())

        # MMR formula
        mmr = self.lambda_param * relevance - (1 - self.lambda_param) * max_sim
        return mmr
