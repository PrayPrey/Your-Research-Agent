import numpy as np
import sys
from pathlib import Path

h_m1_code = Path(__file__).parent.parent.parent / "h-m1" / "code"
sys.path.insert(0, str(h_m1_code))

from detect import get_ngrams


def per_example_ccr(corpus: list[str], benchmark: list[dict], n: int = 8) -> np.ndarray:
    """CCR score per training example (fraction of its n-grams matching benchmark)."""
    benchmark_ngrams = set()
    for sample in benchmark:
        text = f"{sample['question']} {sample['choices'][sample['answer']]}"
        benchmark_ngrams.update(get_ngrams(text, n))

    if not benchmark_ngrams:
        return np.zeros(len(corpus))

    scores = np.zeros(len(corpus))
    for i, doc in enumerate(corpus):
        doc_ngrams = get_ngrams(doc, n)
        if doc_ngrams:
            overlap = len(doc_ngrams & benchmark_ngrams)
            scores[i] = overlap / len(benchmark_ngrams)
    return scores


class RemovalIntervention:
    def __init__(self, ccr_scores: np.ndarray, removal_fraction: float):
        self.ccr_scores = ccr_scores
        self.removal_fraction = removal_fraction
        self.n_remove = max(1, int(len(ccr_scores) * removal_fraction))
        self.high_ccr_threshold = np.percentile(ccr_scores, 100 * (1 - removal_fraction))

    def get_high_ccr_mask(self) -> np.ndarray:
        """Top removal_fraction% by CCR score."""
        mask = np.zeros(len(self.ccr_scores), dtype=bool)
        top_indices = np.argsort(self.ccr_scores)[-self.n_remove:]
        mask[top_indices] = True
        return mask

    def get_random_mask(self, seed: int) -> np.ndarray:
        """Random removal of same fraction."""
        rng = np.random.default_rng(seed)
        indices = rng.choice(len(self.ccr_scores), self.n_remove, replace=False)
        mask = np.zeros(len(self.ccr_scores), dtype=bool)
        mask[indices] = True
        return mask

    def apply(self, corpus: list[str], mask: np.ndarray) -> list[str]:
        """Return corpus with masked examples removed."""
        return [doc for i, doc in enumerate(corpus) if not mask[i]]
