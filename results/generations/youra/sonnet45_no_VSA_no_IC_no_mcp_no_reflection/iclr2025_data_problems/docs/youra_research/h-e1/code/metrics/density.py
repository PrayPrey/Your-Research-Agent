"""Information density computation."""
from typing import List
from collections import Counter
import math
import zlib
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class InformationDensityComputer:
    def __init__(self, embedder_name: str = "all-MiniLM-L6-v2"):
        """Load sentence embedder."""
        self.embedder = SentenceTransformer(embedder_name)

    def compute_token_entropy(self, texts: List[str]) -> float:
        """Unigram/bigram/trigram Shannon entropy. Returns: normalized H(X)."""
        tokens = ' '.join(texts).split()
        token_counts = Counter(tokens)
        total_tokens = sum(token_counts.values())

        if total_tokens == 0:
            return 0.0

        entropy = -sum((count / total_tokens) * math.log2(count / total_tokens)
                       for count in token_counts.values())

        # Normalize by max entropy
        max_entropy = math.log2(len(token_counts)) if len(token_counts) > 0 else 1
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def compute_ngram_redundancy(self, texts: List[str]) -> float:
        """LZ77 compression ratio. Returns: 1 - (compressed / original)."""
        text_bytes = ' '.join(texts).encode('utf-8')
        compressed_size = len(zlib.compress(text_bytes))
        original_size = len(text_bytes)

        return 1 - (compressed_size / original_size) if original_size > 0 else 0.0

    def compute_semantic_diversity(self, texts: List[str], sample_size: int = 1000) -> float:
        """Pairwise embedding diversity. Returns: mean(1 - cosine_sim)."""
        sampled_texts = texts[:sample_size] if len(texts) > sample_size else texts

        if len(sampled_texts) < 2:
            return 0.0

        embeddings = self.embedder.encode(sampled_texts)
        pairwise_sim = cosine_similarity(embeddings)

        # Exclude diagonal (self-similarity)
        np.fill_diagonal(pairwise_sim, 0)

        return 1 - pairwise_sim.mean()

    def compute_combined_density(self, texts: List[str]) -> float:
        """Aggregate density score. Returns: (entropy + (1-redundancy) + diversity) / 3."""
        entropy = self.compute_token_entropy(texts)
        redundancy = self.compute_ngram_redundancy(texts)
        diversity = self.compute_semantic_diversity(texts)

        return (entropy + (1 - redundancy) + diversity) / 3
