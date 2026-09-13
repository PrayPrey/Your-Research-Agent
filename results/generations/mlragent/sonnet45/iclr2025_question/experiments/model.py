"""
Semantic Consistency Graph (SCG) model implementation.
"""

import numpy as np
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import networkx as nx
from typing import List, Dict, Tuple
import re

import config


class ClaimExtractor:
    """Extract atomic claims from text."""

    def __init__(self):
        self.sentence_pattern = re.compile(r'[^.!?]+[.!?]')

    def extract_claims(self, text: str) -> List[str]:
        """Extract atomic claims from text."""
        # Simple sentence splitting
        sentences = self.sentence_pattern.findall(text)
        claims = []

        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 10:  # Filter very short sentences
                # Split compound sentences
                if ' and ' in sent.lower() or ' but ' in sent.lower():
                    parts = re.split(r'\s+(?:and|but)\s+', sent, flags=re.IGNORECASE)
                    claims.extend([p.strip() for p in parts if len(p.strip()) > 10])
                else:
                    claims.append(sent)

        return claims


class SemanticConsistencyGraph:
    """Build and analyze semantic consistency graph."""

    def __init__(self):
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.embedding_model.to(config.DEVICE)

        # Load NLI cross-encoder model
        try:
            from sentence_transformers import CrossEncoder
            self.nli_model = CrossEncoder(config.NLI_MODEL)
            self.use_cross_encoder = True
        except Exception as e:
            print(f"Warning: Could not load NLI model: {e}")
            self.nli_model = None
            self.use_cross_encoder = False

        self.claim_extractor = ClaimExtractor()
        self.graph = nx.DiGraph()
        self.claims = []
        self.claim_embeddings = []
        self.claim_turns = []  # Track which turn each claim came from

    def add_response(self, response: str, turn: int):
        """Add a response to the graph."""
        # Extract claims
        new_claims = self.claim_extractor.extract_claims(response)

        if not new_claims:
            return

        # Get embeddings
        new_embeddings = self.embedding_model.encode(
            new_claims,
            convert_to_tensor=True,
            device=config.DEVICE
        )

        # Add nodes
        start_idx = len(self.claims)
        for i, claim in enumerate(new_claims):
            node_id = start_idx + i
            self.graph.add_node(node_id, claim=claim, turn=turn)
            self.claims.append(claim)
            self.claim_turns.append(turn)

        self.claim_embeddings.append(new_embeddings)

        # Update edges
        self._update_edges(start_idx, len(new_claims))

    def _update_edges(self, start_idx: int, num_new_claims: int):
        """Update graph edges with new claims."""
        if start_idx == 0:
            return  # First claims, no edges to add

        # Combine all embeddings
        all_embeddings = torch.cat(self.claim_embeddings, dim=0)

        # Compute edges between new claims and existing claims
        for i in range(start_idx, start_idx + num_new_claims):
            for j in range(start_idx):
                # Compute edge weight
                weight = self._compute_edge_weight(i, j, all_embeddings)
                if abs(weight) > 0.1:  # Threshold for edge creation
                    self.graph.add_edge(j, i, weight=weight)

    def _compute_edge_weight(self, i: int, j: int, embeddings: torch.Tensor) -> float:
        """Compute edge weight between two claims."""
        # Semantic similarity
        sim_score = torch.cosine_similarity(
            embeddings[i].unsqueeze(0),
            embeddings[j].unsqueeze(0)
        ).item()

        # NLI score
        nli_score = self._compute_nli(self.claims[i], self.claims[j])

        # Combined weight
        weight = config.ALPHA * sim_score + (1 - config.ALPHA) * nli_score
        return weight

    def _compute_nli(self, claim1: str, claim2: str) -> float:
        """Compute NLI score between two claims."""
        if not self.use_cross_encoder or self.nli_model is None:
            return 0.0

        try:
            # Use cross-encoder for NLI
            # The model predicts: contradiction, entailment, neutral
            score = self.nli_model.predict([(claim1, claim2)])[0]
            # Cross-encoder outputs a score where higher means more similar/entailment
            # We normalize to [-1, 1] range
            normalized_score = np.tanh(score / 2.0)
            return normalized_score

        except Exception as e:
            # Fallback to semantic similarity only
            return 0.0

    def detect_contradictions(self) -> List[Tuple[int, int, float]]:
        """Detect contradictory claim pairs."""
        contradictions = []

        for edge in self.graph.edges(data=True):
            source, target, data = edge
            weight = data['weight']

            if weight < -config.CONTRADICTION_THRESHOLD:
                contradictions.append((source, target, weight))

        return contradictions

    def compute_claim_uncertainty(self, claim_id: int) -> float:
        """Compute uncertainty score for a specific claim."""
        if claim_id not in self.graph:
            return 0.0

        # Dirichlet energy (variation from neighbors)
        neighbors = list(self.graph.predecessors(claim_id)) + list(self.graph.successors(claim_id))
        if not neighbors:
            return 0.0

        embeddings = torch.cat(self.claim_embeddings, dim=0)
        claim_emb = embeddings[claim_id]

        dirichlet_energy = 0.0
        for neighbor in neighbors:
            edge_data = self.graph.get_edge_data(claim_id, neighbor) or self.graph.get_edge_data(neighbor, claim_id)
            if edge_data:
                weight = edge_data['weight']
                neighbor_emb = embeddings[neighbor]
                diff = torch.norm(claim_emb - neighbor_emb).item()
                dirichlet_energy += weight * diff ** 2

        dirichlet_energy /= len(neighbors)

        # Count contradictions
        num_contradictions = sum(
            1 for n in neighbors
            if (self.graph.get_edge_data(claim_id, n) or self.graph.get_edge_data(n, claim_id))['weight'] < -config.CONTRADICTION_THRESHOLD
        )
        contradiction_ratio = num_contradictions / len(self.claims) if self.claims else 0

        # Edge weight entropy
        edge_weights = [
            abs((self.graph.get_edge_data(claim_id, n) or self.graph.get_edge_data(n, claim_id))['weight'])
            for n in neighbors
        ]
        if edge_weights:
            edge_weights = np.array(edge_weights)
            edge_weights = edge_weights / (edge_weights.sum() + 1e-8)
            entropy = -np.sum(edge_weights * np.log(edge_weights + 1e-8))
        else:
            entropy = 0.0

        # Combine with learned weights
        uncertainty = (
            config.BETA_WEIGHTS[0] * dirichlet_energy +
            config.BETA_WEIGHTS[1] * contradiction_ratio +
            config.BETA_WEIGHTS[2] * entropy
        )

        return uncertainty

    def compute_turn_uncertainty(self, turn: int) -> float:
        """Compute uncertainty for a specific turn."""
        turn_claims = [i for i, t in enumerate(self.claim_turns) if t == turn]

        if not turn_claims:
            return 0.0

        uncertainties = [self.compute_claim_uncertainty(c) for c in turn_claims]
        mean_uncertainty = np.mean(uncertainties)
        max_uncertainty = np.max(uncertainties)

        return mean_uncertainty + config.GAMMA * max_uncertainty

    def compute_conversation_uncertainty(self) -> float:
        """Compute overall conversation uncertainty."""
        if not self.claim_turns:
            return 0.0

        max_turn = max(self.claim_turns)
        turn_uncertainties = [
            self.compute_turn_uncertainty(t)
            for t in range(max_turn + 1)
        ]

        mean_uncertainty = np.mean(turn_uncertainties)

        # Detect contradiction clusters
        contradictions = self.detect_contradictions()
        contradiction_ratio = len(contradictions) / len(self.claims) if self.claims else 0

        return mean_uncertainty + config.DELTA * contradiction_ratio


class SCGDetector:
    """Hallucination detector using SCG."""

    def __init__(self):
        pass

    def predict(self, conversation: List[Dict]) -> Dict:
        """Predict hallucination for a conversation."""
        scg = SemanticConsistencyGraph()

        # Build graph from conversation
        for msg in conversation:
            if msg["speaker"] == "assistant":
                scg.add_response(msg["text"], msg["turn"])

        # Compute uncertainty
        conversation_uncertainty = scg.compute_conversation_uncertainty()
        contradictions = scg.detect_contradictions()

        # Binary prediction based on threshold (lowered for better sensitivity)
        has_hallucination = conversation_uncertainty > 0.3 or len(contradictions) > 0

        return {
            "has_hallucination": has_hallucination,
            "uncertainty_score": conversation_uncertainty,
            "num_contradictions": len(contradictions),
            "contradictions": contradictions
        }
