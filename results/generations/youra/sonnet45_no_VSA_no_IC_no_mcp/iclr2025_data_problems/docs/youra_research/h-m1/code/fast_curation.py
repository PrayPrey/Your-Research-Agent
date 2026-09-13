"""
Fast Curation for h-m1 PoC
Exact-match hash dedup (O(n) vs LSH O(n²)) per 03_prd.md NFR2
"""
from typing import List, Dict, Tuple
import hashlib
import logging

logger = logging.getLogger(__name__)


class FastDeduplicationFilter:
    """Exact-match hash dedup (PoC simplification)"""

    def __init__(self, threshold: float = 0.8):
        """Threshold unused for exact-match (kept for API compat)"""
        self.threshold = threshold

    def filter_dataset(self, samples: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Deduplicate using exact-match hash.

        Args:
            samples: [{"instruction": str, "input": str, "output": str}]

        Returns:
            (filtered_samples, stats)
        """
        if not samples:
            return [], {"original": 0, "unique": 0, "removed": 0}

        seen_hashes = set()
        unique_samples = []

        for sample in samples:
            text = f"{sample.get('instruction', '')} {sample.get('input', '')} {sample.get('output', '')}"
            text_hash = hashlib.sha256(text.encode()).hexdigest()

            if text_hash not in seen_hashes:
                seen_hashes.add(text_hash)
                unique_samples.append(sample)

        stats = {
            "original": len(samples),
            "unique": len(unique_samples),
            "removed": len(samples) - len(unique_samples)
        }
        return unique_samples, stats


class PerplexityFilter:
    """Proxy perplexity filter (same as h-e1)"""

    def __init__(self, cutoff: float = 100.0):
        self.cutoff = cutoff
        logger.warning("PoC mode: Using length-based perplexity proxy")

    def compute_perplexity(self, text: str) -> float:
        if not text:
            return float('inf')
        return max(10.0, 1000.0 / len(text))

    def filter_dataset(self, samples: List[Dict]) -> Tuple[List[Dict], Dict]:
        if not samples:
            return [], {"original": 0, "passed": 0, "removed": 0, "mean_ppl": 0.0}

        filtered = []
        perplexities = []

        for sample in samples:
            text = f"{sample.get('instruction', '')} {sample.get('input', '')} {sample.get('output', '')}"
            ppl = self.compute_perplexity(text)
            perplexities.append(ppl)

            if ppl <= self.cutoff:
                filtered.append(sample)

        stats = {
            "original": len(samples),
            "passed": len(filtered),
            "removed": len(samples) - len(filtered),
            "mean_ppl": sum(perplexities) / len(perplexities) if perplexities else 0.0
        }
        return filtered, stats
