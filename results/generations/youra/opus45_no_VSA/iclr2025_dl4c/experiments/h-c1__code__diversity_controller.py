"""Feedback diversity controller for H-C1: entropy-based batch filtering."""
import math
import random
from collections import Counter
from typing import List, Dict, Any

from error_taxonomy import ErrorClass


class FeedbackDiversityController:
    """Controls feedback diversity during RL training via batch resampling."""

    def __init__(self, mode: str = "high", target_high: float = 2.5, target_low: float = 1.5):
        self.mode = mode
        self.target_high = target_high
        self.target_low = target_low

    def compute_entropy(self, samples: List[Dict[str, Any]]) -> float:
        """H(ErrorClass) - Shannon entropy of error type distribution in bits."""
        if not samples:
            return 0.0

        error_counts = Counter(s.get("error_type", ErrorClass.FAILED_TEST) for s in samples)
        total = sum(error_counts.values())
        if total == 0:
            return 0.0

        probs = [c / total for c in error_counts.values() if c > 0]
        return -sum(p * math.log2(p) for p in probs)

    def filter_batch(self, samples: List[Dict[str, Any]], batch_size: int = None) -> List[Dict[str, Any]]:
        """Filter samples to achieve target entropy based on mode.

        - mode="high": oversample minority error types to maximize diversity
        - mode="low": concentrate on dominant error type to minimize diversity
        """
        if not samples:
            return samples

        if batch_size is None:
            batch_size = len(samples)

        if self.mode == "high":
            return self._resample_for_diversity(samples, batch_size)
        else:  # mode == "low"
            return self._resample_for_concentration(samples, batch_size)

    def _resample_for_diversity(self, samples: List[Dict[str, Any]], batch_size: int) -> List[Dict[str, Any]]:
        """Oversample minority error types to increase H towards target_high."""
        by_type = self._group_by_error_type(samples)
        if not by_type:
            return samples[:batch_size]

        # Sample uniformly from each error type (equal weight)
        result = []
        types = list(by_type.keys())
        per_type = max(1, batch_size // len(types))

        for error_type in types:
            pool = by_type[error_type]
            sampled = random.choices(pool, k=min(per_type, batch_size - len(result)))
            result.extend(sampled)
            if len(result) >= batch_size:
                break

        # Fill remaining with uniform random from all types
        while len(result) < batch_size and samples:
            remaining = batch_size - len(result)
            all_pools = [s for pool in by_type.values() for s in pool]
            extra = random.choices(all_pools, k=min(remaining, len(all_pools)))
            result.extend(extra)
            break

        return result[:batch_size]

    def _resample_for_concentration(self, samples: List[Dict[str, Any]], batch_size: int) -> List[Dict[str, Any]]:
        """Concentrate on dominant error type to decrease H towards target_low."""
        by_type = self._group_by_error_type(samples)
        if not by_type:
            return samples[:batch_size]

        # Find dominant type
        dominant_type = max(by_type.keys(), key=lambda t: len(by_type[t]))
        dominant_pool = by_type[dominant_type]

        # 80% from dominant, 20% from others
        dominant_count = int(batch_size * 0.8)
        other_count = batch_size - dominant_count

        result = random.choices(dominant_pool, k=min(dominant_count, len(dominant_pool)))

        # Add some from other types
        other_pool = [s for t, pool in by_type.items() if t != dominant_type for s in pool]
        if other_pool and other_count > 0:
            result.extend(random.choices(other_pool, k=min(other_count, len(other_pool))))

        return result[:batch_size]

    def _group_by_error_type(self, samples: List[Dict[str, Any]]) -> Dict[ErrorClass, List[Dict[str, Any]]]:
        """Group samples by error_type field."""
        by_type = {}
        for s in samples:
            error_type = s.get("error_type", ErrorClass.FAILED_TEST)
            if error_type not in by_type:
                by_type[error_type] = []
            by_type[error_type].append(s)
        return by_type

    def log_entropy(self, samples: List[Dict[str, Any]], target: float) -> None:
        """Log current entropy vs target."""
        H = self.compute_entropy(samples)
        print(f"Feedback entropy: {H:.3f} bits (target: {target}), samples: {len(samples)}")
