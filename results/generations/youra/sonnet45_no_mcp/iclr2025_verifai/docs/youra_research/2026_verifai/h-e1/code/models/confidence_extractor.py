"""
Confidence Trajectory Extractor
Extracts confidence derivatives from LeanDojo proof search
"""

from typing import List, Tuple
import numpy as np
from scipy.stats import entropy


class ConfidenceTrajectoryExtractor:
    """Extract confidence derivatives from LeanDojo proof search trajectories."""

    def __init__(self, window_size: int = 15):
        """
        Initialize confidence extractor.

        Args:
            window_size: Number of proof steps to monitor for entropy trajectory
        """
        self.window_size = window_size

    def extract_confidence_trajectory(self, proof_session) -> Tuple[float, List[float]]:
        """
        Extract confidence derivative from proof search session.

        Args:
            proof_session: LeanDojo Dojo session with get_tactics() method

        Returns:
            confidence_derivative: std dev of entropy trajectory (scalar)
            entropies: entropy values for each step (list of floats, length ≤ window_size)
        """
        entropies = []

        for step_num in range(self.window_size):
            try:
                # Get tactics with log probabilities from LeanDojo
                tactics_with_logprobs = proof_session.get_tactics()

                if not tactics_with_logprobs:
                    print(f"  WARNING: No tactics available at step {step_num}")
                    break

                # Extract log probabilities and convert to normalized softmax
                logprobs = np.array([logprob for _, logprob in tactics_with_logprobs])
                probs = np.exp(logprobs)
                probs = probs / probs.sum()  # Normalize

                # Compute Shannon entropy for current step
                step_entropy = self.compute_entropy(probs)
                entropies.append(step_entropy)

                # Early termination if proof completes
                if proof_session.is_done():
                    print(f"  Proof completed at step {step_num + 1}")
                    break

            except Exception as e:
                print(f"  WARNING: Error at step {step_num}: {e}")
                break

        # Compute confidence derivative (std dev)
        if len(entropies) == 0:
            return 0.0, []

        confidence_derivative = self.compute_derivative(entropies)
        return confidence_derivative, entropies

    def compute_entropy(self, probabilities: np.ndarray) -> float:
        """
        Compute Shannon entropy from probability distribution.

        Args:
            probabilities: softmax probabilities, shape [num_tactics]

        Returns:
            entropy_value: Shannon entropy (scalar)
        """
        # Use scipy.stats.entropy for robust calculation
        return float(entropy(probabilities))

    def compute_derivative(self, entropies: List[float]) -> float:
        """
        Compute confidence derivative as std dev of entropy trajectory.

        Args:
            entropies: entropy values over time, list of floats

        Returns:
            derivative: std dev of entropies (scalar)
        """
        if len(entropies) <= 1:
            return 0.0
        return float(np.std(entropies))
