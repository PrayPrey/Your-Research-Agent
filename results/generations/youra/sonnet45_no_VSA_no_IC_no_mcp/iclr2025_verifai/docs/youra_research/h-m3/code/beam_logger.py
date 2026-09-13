"""Beam count logging callback for HuggingFace Transformers."""

import torch


class BeamCountLogger:
    """Log active beam count at each generation step."""

    def __init__(self):
        self.counts = []

    def __call__(self, input_ids: torch.Tensor, scores: torch.Tensor, **kwargs) -> bool:
        """
        Callback invoked at each generation step.
        input_ids: [num_beams, seq_len]
        """
        self.counts.append(input_ids.shape[0])
        return False  # Never stop early

    def get_counts(self):
        return self.counts

    def beam_maintained(self, expected_k: int) -> bool:
        """Check if all steps maintained k beams."""
        return all(c == expected_k for c in self.counts)

    def reset(self):
        """Clear counts for next problem."""
        self.counts = []
