"""
Curriculum Data Loader with Dynamic Domain Scheduling
Implements diversity-ranked, reversed, shuffled, and static sampling strategies.
"""

import torch
import numpy as np
from typing import Dict, Iterator, List
from torch.utils.data import Dataset, DataLoader


class CurriculumDataLoader:
    """
    Dynamic curriculum scheduler for multi-domain language model training.

    Supports 4 conditions:
    - static: Uniform 16.67% per domain throughout training
    - diversity_ranked: High→Low diversity (Gaussian peaks)
    - reversed: Low→High diversity (inverted Gaussian)
    - shuffled: Random domain order with Gaussian scheduling
    """

    def __init__(
        self,
        domain_data: Dict[str, Dataset],
        diversity_scores: Dict[str, float],
        condition: str,
        batch_size: int,
        total_steps: int,
        sequence_length: int = 2048,
        gaussian_width: float = 0.3,
        min_weight: float = 0.05,
        seed: int = 42
    ):
        """
        Args:
            domain_data: Dict mapping domain name to PyTorch Dataset
            diversity_scores: Dict mapping domain to diversity score [0, 1]
            condition: One of ["static", "diversity_ranked", "reversed", "shuffled"]
            batch_size: Number of sequences per batch
            total_steps: Total training steps
            sequence_length: Tokens per sequence
            gaussian_width: Width of Gaussian transition
            min_weight: Minimum sampling weight per domain
            seed: Random seed for reproducibility
        """
        self.domain_data = domain_data
        self.diversity_scores = diversity_scores
        self.condition = condition
        self.batch_size = batch_size
        self.total_steps = total_steps
        self.sequence_length = sequence_length
        self.gaussian_width = gaussian_width
        self.min_weight = min_weight
        self.seed = seed

        # Rank domains by diversity
        self.ranked_domains = sorted(
            diversity_scores.keys(),
            key=lambda d: diversity_scores[d],
            reverse=True  # High to low
        )

        # For shuffled condition
        self.rng = np.random.RandomState(seed)
        if condition == "shuffled":
            self.shuffled_order = self.rng.permutation(self.ranked_domains).tolist()

        self.current_step = 0

    def get_domain_weights(self, training_progress: float) -> Dict[str, float]:
        """
        Calculate domain sampling weights based on training progress.

        Args:
            training_progress: Float in [0.0, 1.0] representing fraction complete

        Returns:
            Dict mapping domain name to sampling weight (sum to 1.0)
        """
        if self.condition == "static":
            # Uniform weights throughout training
            n_domains = len(self.ranked_domains)
            return {d: 1.0 / n_domains for d in self.ranked_domains}

        # Determine domain order based on condition
        if self.condition == "diversity_ranked":
            domain_order = self.ranked_domains  # High to low
        elif self.condition == "reversed":
            domain_order = self.ranked_domains[::-1]  # Low to high
        elif self.condition == "shuffled":
            domain_order = self.shuffled_order
        else:
            raise ValueError(f"Unknown condition: {self.condition}")

        # Gaussian weighting
        weights = {}
        for i, domain in enumerate(domain_order):
            # Peak weight at domain's scheduled time
            domain_peak_time = i / len(domain_order)

            # Gaussian centered at peak time
            weight = np.exp(-((training_progress - domain_peak_time) / self.gaussian_width) ** 2)
            weights[domain] = weight

        # Normalize to sum to 1.0 first
        total = sum(weights.values())
        normalized = {d: w / total for d, w in weights.items()}

        # Then apply minimum weight floor
        final_weights = {d: max(w, self.min_weight) for d, w in normalized.items()}

        # Re-normalize after applying min_weight
        total = sum(final_weights.values())
        return {d: w / total for d, w in final_weights.items()}

    def sample_batch(self, step: int) -> Dict[str, torch.Tensor]:
        """
        Sample a batch according to curriculum schedule.

        Args:
            step: Current training step

        Returns:
            Dict with keys:
                - input_ids: (batch_size, sequence_length) token indices
                - labels: (batch_size, sequence_length) target tokens
                - domain_ids: (batch_size,) domain indices
        """
        training_progress = step / self.total_steps
        domain_weights = self.get_domain_weights(training_progress)

        # Sample domains according to weights
        domain_list = list(domain_weights.keys())
        weight_list = [domain_weights[d] for d in domain_list]

        sampled_domains = self.rng.choice(
            domain_list,
            size=self.batch_size,
            p=weight_list
        )

        # Create batch (simplified - assumes pre-tokenized data)
        input_ids = []
        labels = []
        domain_ids = []

        for domain in sampled_domains:
            # Sample random sequence from domain
            dataset = self.domain_data[domain]
            idx = self.rng.randint(0, len(dataset))
            sample = dataset[idx]

            input_ids.append(sample['input_ids'])
            labels.append(sample['labels'])
            domain_ids.append(domain_list.index(domain))

        return {
            'input_ids': torch.stack(input_ids),
            'labels': torch.stack(labels),
            'domain_ids': torch.tensor(domain_ids, dtype=torch.long)
        }

    def __iter__(self) -> Iterator[Dict[str, torch.Tensor]]:
        """Iterate through batches with dynamic domain mixing."""
        for step in range(self.total_steps):
            yield self.sample_batch(step)
            self.current_step = step + 1
