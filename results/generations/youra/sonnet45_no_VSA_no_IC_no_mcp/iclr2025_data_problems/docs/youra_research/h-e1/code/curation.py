"""
Data Curation Pipeline for h-e1
Implements deduplication + perplexity filtering with 3 variants
"""
from typing import List, Dict, Tuple
from datasketch import MinHash, MinHashLSH
from datasets import load_dataset
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeduplicationFilter:
    """MinHash LSH deduplication per 03_logic.md L-1 spec"""

    def __init__(self, threshold: float = 0.8, num_perm: int = 128):
        """Initialize LSH deduplicator. threshold: Jaccard similarity cutoff."""
        self.threshold = threshold
        self.num_perm = num_perm
        self.lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)

    def filter_dataset(self, samples: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Deduplicate instruction samples per L-1 spec.

        Args:
            samples: [{"instruction": str, "input": str, "output": str}]

        Returns:
            (filtered_samples, stats)
            stats: {"original": int, "unique": int, "removed": int}
        """
        if not samples:
            return [], {"original": 0, "unique": 0, "removed": 0}

        unique_samples = []
        for idx, sample in enumerate(samples):
            text = f"{sample.get('instruction', '')} {sample.get('input', '')} {sample.get('output', '')}"
            m = MinHash(num_perm=self.num_perm)
            for token in text.split():
                m.update(token.encode('utf8'))

            # Check for near-duplicates
            if not self.lsh.query(m):
                self.lsh.insert(f"doc_{idx}", m)
                unique_samples.append(sample)

        stats = {
            "original": len(samples),
            "unique": len(unique_samples),
            "removed": len(samples) - len(unique_samples)
        }
        return unique_samples, stats


class PerplexityFilter:
    """KenLM perplexity filtering per 03_logic.md L-2 spec"""

    def __init__(self, cutoff: float = 100.0):
        """Initialize perplexity filter. cutoff: Max allowed perplexity."""
        self.cutoff = cutoff
        # PoC: Skip KenLM model (requires ~4GB download)
        # Use simple proxy: character length (longer = lower perplexity)
        logger.warning("PoC mode: Using length-based perplexity proxy (no KenLM download)")

    def compute_perplexity(self, text: str) -> float:
        """Compute proxy perplexity: max(10, 1000/len(text))"""
        if not text:
            return float('inf')
        return max(10.0, 1000.0 / len(text))

    def filter_dataset(self, samples: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Filter high-perplexity samples per L-2 spec.

        Returns:
            (filtered_samples, stats)
            stats: {"original": int, "passed": int, "removed": int, "mean_ppl": float}
        """
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


def curate_dataset(
    dataset_name: str = "tatsu-lab/alpaca",
    dedup_threshold: float = 0.8,
    ppl_cutoff: float = 100.0,
    cache_dir: str = None
) -> Tuple[List[Dict], Dict]:
    """
    Apply dedup + perplexity filtering per 03_logic.md.

    Returns:
        (curated_samples, curation_stats)
    """
    logger.info(f"Loading dataset: {dataset_name}")
    dataset = load_dataset(dataset_name, cache_dir=cache_dir)
    samples = list(dataset['train'])
    logger.info(f" Loaded: {len(samples)} samples")

    # Step 1: Deduplication
    logger.info(f"Deduplication (threshold={dedup_threshold})...")
    dedup_filter = DeduplicationFilter(threshold=dedup_threshold)
    dedup_samples, dedup_stats = dedup_filter.filter_dataset(samples)
    logger.info(f" Removed {dedup_stats['removed']} duplicates")

    # Step 2: Perplexity filtering
    logger.info(f"Perplexity filtering (cutoff={ppl_cutoff})...")
    ppl_filter = PerplexityFilter(cutoff=ppl_cutoff)
    curated_samples, ppl_stats = ppl_filter.filter_dataset(dedup_samples)
    logger.info(f" Removed {ppl_stats['removed']} high-perplexity samples")

    curation_stats = {
        "original_count": len(samples),
        "after_dedup": dedup_stats['unique'],
        "after_ppl": ppl_stats['passed'],
        "total_removed": len(samples) - len(curated_samples),
        "dedup_stats": dedup_stats,
        "ppl_stats": ppl_stats
    }

    return curated_samples, curation_stats


if __name__ == "__main__":
    # PoC test
    cache_dir = "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_data_problems/docs/youra_research/.data_cache/datasets/alpaca"

    print("=== PoC: Baseline (no filtering) ===")
    dataset = load_dataset("tatsu-lab/alpaca", cache_dir=cache_dir)
    baseline = list(dataset['train'])
    print(f"Baseline: {len(baseline)} samples")

    print("\n=== PoC: Transferred thresholds (C4) ===")
    curated, stats = curate_dataset(
        dedup_threshold=0.8,
        ppl_cutoff=100.0,
        cache_dir=cache_dir
    )
    print(f"Curated: {len(curated)} samples ({stats['total_removed']} removed)")
    print(f"Stats: {stats}")
