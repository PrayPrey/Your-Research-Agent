"""Pile corpus n-gram indexer."""

import pickle
from typing import Iterable
from tqdm import tqdm
from ngram_utils import extract_ngram_hashes
from config import NGRAM_SIZE


class PileIndexer:
    """Build hash-set index from Pile corpus subset."""

    def __init__(self, ngram_size: int = NGRAM_SIZE):
        self.ngram_size = ngram_size
        self.index: set[int] = set()

    def build_from_stream(self, doc_iter: Iterable[str], max_docs: int | None = None) -> None:
        """Stream docs, extract ngram hashes, union into index."""
        for i, doc_text in enumerate(tqdm(doc_iter, total=max_docs, desc="Indexing Pile")):
            if max_docs and i >= max_docs:
                break
            self.index |= extract_ngram_hashes(doc_text, self.ngram_size)

    def save(self, path: str) -> None:
        """Persist index to pickle file."""
        with open(path, "wb") as f:
            pickle.dump(self.index, f)

    def load(self, path: str) -> None:
        """Load index from pickle file."""
        with open(path, "rb") as f:
            self.index = pickle.load(f)
