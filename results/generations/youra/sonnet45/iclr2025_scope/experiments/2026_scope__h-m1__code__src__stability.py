"""Context Stability Testing Module for Mechanism Validation (h-m1)."""

from typing import List, Callable, Dict, Any, Tuple
import numpy as np
import torch
from torch.utils.data import DataLoader

from .analyzer import LowRankAnalyzer


class ContextStabilityTester:
    """Tests stability of effective rank and operator entropy across context lengths."""

    def __init__(
        self,
        analyzer: LowRankAnalyzer,
        context_lengths: List[int] = None
    ):
        """
        Initialize stability tester.

        Args:
            analyzer: LowRankAnalyzer instance from h-e1
            context_lengths: List of context lengths to test (e.g., [8192, 16384, 32768, 65536, 131072])
        """
        self.analyzer = analyzer
        self.context_lengths = context_lengths or [8192, 16384, 32768, 65536, 131072]

    def test_context_stability(
        self,
        dataloader_factory: Callable[[int], DataLoader],
        num_samples_per_length: int = 10
    ) -> Dict[str, Any]:
        """
        Test stability across context lengths.

        Args:
            dataloader_factory: Function that creates DataLoader for given context length
            num_samples_per_length: Number of samples to analyze per context length

        Returns:
            Dictionary with structure:
            {
                'context_lengths': [...],
                'rank_by_context': {context_len: {layer_idx: r_eff, ...}, ...},
                'entropy_by_context': {context_len: {layer_idx: entropy, ...}, ...}
            }
        """
        rank_by_context = {}
        entropy_by_context = {}

        for context_len in self.context_lengths:
            print(f"Testing context length: {context_len}")

            # Create dataloader for this context length
            dataloader = dataloader_factory(context_len)

            # Run analysis
            results = self.analyzer.analyze_layers(dataloader, num_samples=num_samples_per_length)

            # Extract rank and entropy per layer
            rank_by_layer = {layer_idx: result['effective_rank']
                           for layer_idx, result in results.items()}
            entropy_by_layer = {layer_idx: result['operator_entropy']
                              for layer_idx, result in results.items()}

            rank_by_context[context_len] = rank_by_layer
            entropy_by_context[context_len] = entropy_by_layer

            # Clear cache to avoid OOM
            torch.cuda.empty_cache()

        return {
            'context_lengths': self.context_lengths,
            'rank_by_context': rank_by_context,
            'entropy_by_context': entropy_by_context
        }

    def compute_variance_metrics(self, stability_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute variance metrics across context lengths.

        Args:
            stability_results: Output from test_context_stability()

        Returns:
            Dictionary with structure:
            {
                'rank_variance': {layer_idx: variance, ...},
                'entropy_variance': {layer_idx: variance, ...},
                'max_rank_variance': float,
                'max_entropy_variance': float
            }
        """
        rank_by_context = stability_results['rank_by_context']
        entropy_by_context = stability_results['entropy_by_context']

        # Get layer indices from first context length
        first_context = list(rank_by_context.keys())[0]
        layer_indices = list(rank_by_context[first_context].keys())

        rank_variance = {}
        entropy_variance = {}

        for layer_idx in layer_indices:
            # Collect values across all context lengths
            rank_values = [rank_by_context[ctx][layer_idx] for ctx in self.context_lengths
                          if layer_idx in rank_by_context.get(ctx, {})]
            entropy_values = [entropy_by_context[ctx][layer_idx] for ctx in self.context_lengths
                            if layer_idx in entropy_by_context.get(ctx, {})]

            # Compute variance
            rank_variance[layer_idx] = np.var(rank_values) if rank_values else 0.0
            entropy_variance[layer_idx] = np.var(entropy_values) if entropy_values else 0.0

        return {
            'rank_variance': rank_variance,
            'entropy_variance': entropy_variance,
            'max_rank_variance': max(rank_variance.values()) if rank_variance else 0.0,
            'max_entropy_variance': max(entropy_variance.values()) if entropy_variance else 0.0
        }

    def validate_stability(
        self,
        variance_metrics: Dict[str, Any],
        baseline_variance: float,
        threshold: float = 1.2
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate that variance is within threshold.

        Args:
            variance_metrics: Output from compute_variance_metrics()
            baseline_variance: Baseline variance for comparison
            threshold: Maximum allowed variance multiplier (default: 1.2)

        Returns:
            Tuple of (is_valid, validation_details)
        """
        max_rank_var = variance_metrics['max_rank_variance']
        max_entropy_var = variance_metrics['max_entropy_variance']

        # Check if variance is within threshold
        rank_valid = max_rank_var <= baseline_variance * threshold
        entropy_valid = max_entropy_var <= baseline_variance * threshold

        is_valid = rank_valid and entropy_valid

        validation_details = {
            'rank_valid': rank_valid,
            'entropy_valid': entropy_valid,
            'max_rank_variance': max_rank_var,
            'max_entropy_variance': max_entropy_var,
            'baseline_variance': baseline_variance,
            'threshold': threshold,
            'threshold_value': baseline_variance * threshold
        }

        return is_valid, validation_details
