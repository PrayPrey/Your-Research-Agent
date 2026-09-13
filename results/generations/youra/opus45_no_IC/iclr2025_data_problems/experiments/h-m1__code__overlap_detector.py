"""Overlap detection between benchmark items and Pile index."""

from ngram_utils import extract_ngram_hashes
from config import NGRAM_SIZE


class OverlapDetector:
    """Compute n-gram overlap ratio."""

    def __init__(self, pile_index: set[int], ngram_size: int = NGRAM_SIZE):
        self.pile_index = pile_index
        self.ngram_size = ngram_size

    def compute_item_overlap(self, text: str) -> dict:
        """Compute overlap for single item."""
        item_hashes = extract_ngram_hashes(text, self.ngram_size)
        if not item_hashes:
            return {"overlap": 0.0, "matched": 0, "total": 0}
        matched = len(item_hashes & self.pile_index)
        total = len(item_hashes)
        return {"overlap": matched / total, "matched": matched, "total": total}

    def compute_benchmark_overlap(self, items: list[dict]) -> list[dict]:
        """Compute overlap for all items in benchmark."""
        return [{**self.compute_item_overlap(item["text"]), "id": item["id"]} for item in items]
