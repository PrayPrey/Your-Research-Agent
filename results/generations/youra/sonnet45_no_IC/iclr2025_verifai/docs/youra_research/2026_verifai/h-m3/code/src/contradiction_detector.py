"""Detect contradictions via similarity threshold."""

import torch
import json
from pathlib import Path
from typing import List, Dict

class ContradictionDetector:
    """Detect contradictions via similarity threshold."""

    def __init__(self, similarity_threshold: float = 0.3):
        """Initialize detector."""
        self.similarity_threshold = similarity_threshold

    def detect_contradictions(
        self,
        similarity_matrix: torch.Tensor,
        pairs: List[Dict]
    ) -> List[Dict]:
        """Flag pairs below threshold."""
        contradictions = []
        num_assumptions = similarity_matrix.shape[0]
        num_claims = similarity_matrix.shape[1]

        for i in range(num_assumptions):
            for j in range(num_claims):
                sim_score = similarity_matrix[i, j].item()
                if sim_score < self.similarity_threshold:
                    pair = pairs[i * num_claims + j]
                    flagged = self.flag_mismatches(pair, sim_score)
                    contradictions.append(flagged)

        return contradictions

    def flag_mismatches(self, pair: Dict, similarity: float) -> Dict:
        """Add metadata."""
        return {
            "assumption": pair["assumption"],
            "claim": pair["claim"],
            "similarity": similarity,
            "mismatch": True,
            "threshold": self.similarity_threshold
        }

    def save_contradictions(self, contradictions: List[Dict], output_path: Path) -> None:
        """Save results."""
        with open(output_path, 'w') as f:
            json.dump(contradictions, f, indent=2)
