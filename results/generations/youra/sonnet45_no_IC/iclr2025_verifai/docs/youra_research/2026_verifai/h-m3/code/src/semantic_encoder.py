"""Encode texts using sentence transformers."""

import torch
from typing import List, Tuple
from sentence_transformers import SentenceTransformer, util

class SemanticEncoder:
    """Encode texts using sentence transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize encoder."""
        self.model = SentenceTransformer(model_name)

    def encode_texts(self, texts: List[str], batch_size: int = 32) -> torch.Tensor:
        """Batch encode texts."""
        return self.model.encode(texts, batch_size=batch_size, convert_to_tensor=True)

    def compute_similarity_matrix(
        self,
        embeddings1: torch.Tensor,
        embeddings2: torch.Tensor
    ) -> torch.Tensor:
        """Compute cosine similarity."""
        return util.cos_sim(embeddings1, embeddings2)

    def encode_assumptions_and_claims(
        self,
        assumptions: List[dict],
        claims: List[dict]
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Encode both assumptions and claims."""
        assumption_texts = [a["text"] for a in assumptions]
        claim_texts = [c["text"] for c in claims]

        assumption_embeddings = self.encode_texts(assumption_texts)
        claim_embeddings = self.encode_texts(claim_texts)

        return assumption_embeddings, claim_embeddings
