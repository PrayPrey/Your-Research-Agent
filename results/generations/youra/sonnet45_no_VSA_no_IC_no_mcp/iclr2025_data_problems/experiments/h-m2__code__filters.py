"""Curation filters for h-m2."""

import hashlib
from typing import List, Dict, Tuple
from collections import defaultdict
import numpy as np

class DeduplicationFilter:
    """MinHash-based deduplication (simplified n-gram hash version)."""

    def __init__(self, n_gram_size: int = 13, similarity_threshold: float = 0.8):
        self.n_gram_size = n_gram_size
        self.similarity_threshold = similarity_threshold

    def _get_ngrams(self, text: str) -> set:
        """Extract character n-grams."""
        return {text[i:i+self.n_gram_size] for i in range(len(text) - self.n_gram_size + 1)}

    def apply(self, samples: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Remove near-duplicates."""
        seen_hashes = set()
        unique_samples = []
        duplicates = 0

        for sample in samples:
            text = sample.get("instruction", "") + " " + sample.get("response", "")
            text_hash = hashlib.md5(text.encode()).hexdigest()[:16]

            if text_hash not in seen_hashes:
                seen_hashes.add(text_hash)
                unique_samples.append(sample)
            else:
                duplicates += 1

        stats = {
            "original_count": len(samples),
            "unique_count": len(unique_samples),
            "duplicates_removed": duplicates
        }
        return unique_samples, stats


class PerplexityFilter:
    """Mock perplexity filter (length-based proxy for PoC)."""

    def __init__(self, cutoff: float = 1000):
        self.cutoff = cutoff

    def apply(self, samples: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Filter by mock perplexity (use length as proxy)."""
        # Mock: remove samples with response length > cutoff/10
        max_length = int(self.cutoff / 10)
        filtered = [s for s in samples if len(s.get("response", "")) <= max_length]

        stats = {
            "original_count": len(samples),
            "filtered_count": len(filtered),
            "removed": len(samples) - len(filtered)
        }
        return filtered, stats


class InstructionQualityFilter:
    """Objective-dependent filter: instruction quality heuristics."""

    def __init__(self, min_diversity: float = 0.5, min_length: int = 10):
        self.min_diversity = min_diversity
        self.min_length = min_length

    def _compute_diversity(self, text: str) -> float:
        """Trigram diversity score."""
        if len(text) < 3:
            return 0.0
        trigrams = [text[i:i+3] for i in range(len(text) - 2)]
        if not trigrams:
            return 0.0
        return len(set(trigrams)) / len(trigrams)

    def apply(self, samples: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Filter by instruction quality."""
        filtered = []
        for sample in samples:
            instruction = sample.get("instruction", "")
            diversity = self._compute_diversity(instruction)
            if len(instruction) >= self.min_length and diversity >= self.min_diversity:
                filtered.append(sample)

        stats = {
            "original_count": len(samples),
            "filtered_count": len(filtered),
            "removed": len(samples) - len(filtered)
        }
        return filtered, stats


def apply_independent_filters(
    samples: List[Dict],
    dedup_threshold: float,
    ppl_cutoff: float
) -> Tuple[List[Dict], Dict]:
    """Apply objective-independent filters."""
    dedup = DeduplicationFilter(similarity_threshold=dedup_threshold)
    ppl = PerplexityFilter(cutoff=ppl_cutoff)

    samples, dedup_stats = dedup.apply(samples)
    samples, ppl_stats = ppl.apply(samples)

    return samples, {"dedup": dedup_stats, "perplexity": ppl_stats}


def apply_dependent_filters(
    samples: List[Dict],
    min_diversity: float
) -> Tuple[List[Dict], Dict]:
    """Apply objective-dependent filters."""
    quality_filter = InstructionQualityFilter(min_diversity=min_diversity)
    return quality_filter.apply(samples)
