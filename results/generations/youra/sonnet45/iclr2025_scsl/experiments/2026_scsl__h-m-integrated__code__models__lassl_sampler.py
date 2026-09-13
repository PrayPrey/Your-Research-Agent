"""Learning-speed aware sampler for LA-SSL training.

Implements inverse sampling proportional to learning speed (loss trajectory slope).
Fast learners (steep negative slope) get lower sampling probability.
"""

import torch
import numpy as np
from typing import Iterator, Optional


class LASSLSampler(torch.utils.data.Sampler):
    """Learning-speed aware sampler for LA-SSL training.

    Tracks per-sample loss history and samples inversely proportional to learning speed.
    Fast learners are undersampled to focus on slow learners.

    Args:
        dataset_size: Total number of samples in dataset
        alpha: Temperature for probability smoothing (0=uniform, 1=inverse)
        window_size: Number of epochs for loss history tracking
        generator: Optional random generator for reproducibility
    """

    def __init__(
        self,
        dataset_size: int,
        alpha: float = 0.5,
        window_size: int = 10,
        generator: Optional[torch.Generator] = None
    ):
        self.dataset_size = dataset_size
        self.alpha = alpha
        self.window_size = window_size
        self.generator = generator

        # Circular buffer: [dataset_size, window_size]
        self.loss_history = np.zeros((dataset_size, window_size), dtype=np.float32)
        self.epoch_counter = 0

    def update_losses(
        self,
        sample_indices: torch.Tensor,
        losses: torch.Tensor
    ) -> None:
        """Update loss history for batch samples.

        Args:
            sample_indices: Tensor of sample indices [B]
            losses: Tensor of per-sample losses [B]
        """
        # Convert to numpy
        indices = sample_indices.cpu().numpy()
        loss_values = losses.detach().cpu().numpy()

        # Circular buffer index
        current_idx = self.epoch_counter % self.window_size

        # Update history
        self.loss_history[indices, current_idx] = loss_values

    def compute_sampling_probs(self) -> torch.Tensor:
        """Compute sampling probabilities based on learning speed.

        Returns:
            Normalized probabilities [dataset_size]
        """
        # Count valid epochs for each sample (non-zero entries)
        valid_counts = (self.loss_history > 0).sum(axis=1)
        valid_mask = valid_counts >= 2  # Need at least 2 epochs for slope

        # Initialize uniform probabilities
        raw_probs = np.ones(self.dataset_size, dtype=np.float32)

        # Compute learning speed for samples with sufficient history
        if valid_mask.sum() > 0:
            for i in range(self.dataset_size):
                if valid_mask[i]:
                    # Get recent losses (non-zero entries)
                    recent_losses = self.loss_history[i][self.loss_history[i] > 0]

                    # Compute learning speed: negative slope (fast learner = steep negative)
                    # Use mean of pairwise differences
                    if len(recent_losses) >= 2:
                        diffs = np.diff(recent_losses)
                        learning_speed = -np.mean(diffs)  # Positive for decreasing loss

                        # Inverse probability: slow learners (low speed) get higher prob
                        # Add epsilon to avoid division by zero
                        eps = 1e-8
                        raw_probs[i] = 1.0 / (learning_speed + eps) ** self.alpha

        # Handle invalid values (inf, nan)
        raw_probs = np.nan_to_num(raw_probs, nan=1.0, posinf=1.0, neginf=1.0)

        # Normalize to sum to 1
        normalized_probs = raw_probs / raw_probs.sum()

        return torch.from_numpy(normalized_probs).float()

    def __iter__(self) -> Iterator[int]:
        """Generate sample indices for epoch."""
        # Compute sampling probabilities
        probs = self.compute_sampling_probs()

        # Sample with replacement using multinomial
        indices = torch.multinomial(
            probs,
            num_samples=self.dataset_size,
            replacement=True,
            generator=self.generator
        )

        # Increment epoch counter for circular buffer
        self.epoch_counter += 1

        return iter(indices.tolist())

    def __len__(self) -> int:
        """Return dataset size."""
        return self.dataset_size
