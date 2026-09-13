"""Final output selector for h-m4."""

import sys
sys.path.insert(0, '../../h-m3/code')

import numpy as np
from scoring import combined_score


class FinalOutputSelector:
    """Select best beam from k candidates using combined scoring."""

    def __init__(self, alpha: float = 0.7, beta: float = 0.3):
        self.alpha = alpha
        self.beta = beta

    def select_final_output(
        self,
        beams: list[str],
        log_likelihoods: list[float]
    ) -> tuple[str, int, list[float]]:
        """
        Select beam with highest final_score.

        Args:
            beams: [k] code strings
            log_likelihoods: [k] log probabilities

        Returns:
            (selected_beam, beam_idx, all_scores)
        """
        final_scores = []
        for beam, log_likelihood in zip(beams, log_likelihoods):
            score, _, _ = combined_score(log_likelihood, beam, self.alpha, self.beta)
            final_scores.append(score)

        best_idx = int(np.argmax(final_scores))
        return beams[best_idx], best_idx, final_scores
