"""
Baseline uncertainty quantification methods for comparison.
"""

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import openai

import config


class PerplexityBaseline:
    """Perplexity-based uncertainty estimation."""

    def __init__(self):
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.embedding_model.to(config.DEVICE)

    def predict(self, conversation: List[Dict]) -> Dict:
        """Predict based on semantic coherence."""
        assistant_responses = [
            msg["text"] for msg in conversation if msg["speaker"] == "assistant"
        ]

        if len(assistant_responses) < 2:
            return {
                "has_hallucination": False,
                "uncertainty_score": 0.0,
                "num_contradictions": 0
            }

        # Compute embeddings
        embeddings = self.embedding_model.encode(
            assistant_responses,
            convert_to_tensor=True,
            device=config.DEVICE
        )

        # Compute pairwise similarities
        similarities = torch.cosine_similarity(
            embeddings.unsqueeze(1),
            embeddings.unsqueeze(0),
            dim=2
        )

        # Compute average similarity (high similarity = low uncertainty)
        # Exclude diagonal
        mask = ~torch.eye(len(assistant_responses), dtype=bool, device=config.DEVICE)
        avg_similarity = similarities[mask].mean().item()

        # Convert to uncertainty (low similarity = high uncertainty)
        uncertainty = 1.0 - avg_similarity

        # Detect potential contradictions (very low similarity)
        low_similarity_pairs = (similarities < 0.3) & mask
        num_contradictions = low_similarity_pairs.sum().item() // 2  # Divide by 2 for symmetry

        has_hallucination = uncertainty > 0.5 or num_contradictions > 0

        return {
            "has_hallucination": has_hallucination,
            "uncertainty_score": uncertainty,
            "num_contradictions": num_contradictions
        }


class SelfCheckGPTBaseline:
    """Self-consistency checking baseline."""

    def __init__(self):
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.embedding_model.to(config.DEVICE)

    def predict(self, conversation: List[Dict]) -> Dict:
        """Predict using self-consistency."""
        assistant_responses = [
            msg["text"] for msg in conversation if msg["speaker"] == "assistant"
        ]

        if len(assistant_responses) < 2:
            return {
                "has_hallucination": False,
                "uncertainty_score": 0.0,
                "num_contradictions": 0
            }

        # For each response, check consistency with others
        embeddings = self.embedding_model.encode(
            assistant_responses,
            convert_to_tensor=True,
            device=config.DEVICE
        )

        inconsistencies = []
        for i in range(len(assistant_responses)):
            # Compare with all other responses
            similarities = torch.cosine_similarity(
                embeddings[i].unsqueeze(0),
                embeddings,
                dim=1
            )

            # Exclude self-similarity
            similarities[i] = 1.0

            # Check for inconsistencies
            min_similarity = similarities.min().item()
            inconsistencies.append(1.0 - min_similarity)

        # Average inconsistency
        avg_inconsistency = np.mean(inconsistencies)

        # Count contradictions (high inconsistency)
        num_contradictions = sum(1 for inc in inconsistencies if inc > 0.7)

        has_hallucination = avg_inconsistency > 0.5

        return {
            "has_hallucination": has_hallucination,
            "uncertainty_score": avg_inconsistency,
            "num_contradictions": num_contradictions
        }


class SemanticEmbeddingBaseline:
    """Semantic embedding-based uncertainty from Grewal et al. (2024)."""

    def __init__(self):
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.embedding_model.to(config.DEVICE)

    def predict(self, conversation: List[Dict]) -> Dict:
        """Predict using semantic embedding variance."""
        assistant_responses = [
            msg["text"] for msg in conversation if msg["speaker"] == "assistant"
        ]

        if len(assistant_responses) < 2:
            return {
                "has_hallucination": False,
                "uncertainty_score": 0.0,
                "num_contradictions": 0
            }

        # Compute embeddings
        embeddings = self.embedding_model.encode(
            assistant_responses,
            convert_to_tensor=True,
            device=config.DEVICE
        )

        # Compute variance in embedding space
        mean_embedding = embeddings.mean(dim=0)
        distances = torch.norm(embeddings - mean_embedding, dim=1)
        uncertainty = distances.mean().item()

        # Normalize to [0, 1]
        uncertainty = min(uncertainty / 2.0, 1.0)

        # Detect contradictions based on large distances
        num_contradictions = (distances > distances.mean() + distances.std()).sum().item()

        has_hallucination = uncertainty > 0.5

        return {
            "has_hallucination": has_hallucination,
            "uncertainty_score": uncertainty,
            "num_contradictions": num_contradictions
        }
