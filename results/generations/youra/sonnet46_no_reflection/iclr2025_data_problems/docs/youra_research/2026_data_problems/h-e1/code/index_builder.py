from __future__ import annotations
import os
import pickle
import hashlib
import struct
from pathlib import Path
from typing import Iterator, Optional

import numpy as np
from config import ExperimentConfig


def _ngrams(text: str, n: int) -> list[str]:
    words = text.lower().split()
    return [" ".join(words[i:i+n]) for i in range(len(words) - n + 1)]


class NgramIndex:
    """Inverted n-gram index stored as a set for fast lookup."""

    def __init__(self, ngram_set: set[str], n: int = 13):
        self._set = ngram_set
        self.n = n

    def max_overlap(self, text: str, n: int = 13) -> int:
        """Return max consecutive n-gram match count (0 if none)."""
        grams = _ngrams(text, n)
        if not grams:
            return 0
        count = sum(1 for g in grams if g in self._set)
        return count

    def is_contaminated(self, text: str, threshold: int = 1) -> bool:
        return self.max_overlap(text, self.n) >= threshold


class NgramIndexBuilder:
    def __init__(self, cfg: ExperimentConfig):
        self.cfg = cfg
        self.index_dir = Path(cfg.index_dir)

    def build_index(
        self,
        corpus_name: str,
        corpus_stream: Iterator[str],
        max_docs: Optional[int] = None,
    ) -> None:
        """Stream corpus, extract n-grams, save index to disk."""
        out_path = self.index_dir / corpus_name
        out_path.mkdir(parents=True, exist_ok=True)
        ngram_set: set[str] = set()
        n = self.cfg.ngram_n
        count = 0
        for text in corpus_stream:
            if max_docs and count >= max_docs:
                break
            ngram_set.update(_ngrams(text, n))
            count += 1
            if count % 10_000 == 0:
                print(f"  [{corpus_name}] Processed {count} docs, {len(ngram_set)} n-grams")
        index_file = out_path / "ngram_index.pkl"
        with open(index_file, "wb") as f:
            pickle.dump(ngram_set, f)
        print(f"✓ N-gram index saved: {index_file} ({len(ngram_set)} n-grams, {count} docs)")

    def load_index(self, corpus_name: str) -> NgramIndex:
        index_file = self.index_dir / corpus_name / "ngram_index.pkl"
        if not index_file.exists():
            raise FileNotFoundError(f"N-gram index not found: {index_file}. Run build_index first.")
        with open(index_file, "rb") as f:
            ngram_set = pickle.load(f)
        return NgramIndex(ngram_set, n=self.cfg.ngram_n)


class SBERTIndex:
    """FAISS IndexFlatIP wrapper for cosine similarity search."""

    def __init__(self, index, model, batch_size: int = 256):
        self._index = index
        self._model = model
        self._batch_size = batch_size

    def search(
        self,
        query_texts: list[str],
        k: int = 1,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return (distances shape (Q,k) float32, indices shape (Q,k) int64)."""
        import torch
        query_embs = self._model.encode(
            query_texts,
            normalize_embeddings=True,
            batch_size=self._batch_size,
            show_progress_bar=False,
        ).astype(np.float32)
        distances, indices = self._index.search(query_embs, k)
        return distances, indices


class SBERTIndexBuilder:
    def __init__(self, cfg: ExperimentConfig):
        self.cfg = cfg
        self.index_dir = Path(cfg.index_dir)
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.cfg.sbert_model)
        return self._model

    def build_index(
        self,
        corpus_name: str,
        corpus_texts: list[str],
    ) -> None:
        """Encode corpus, build FAISS IndexFlatIP, save to disk."""
        import faiss
        out_path = self.index_dir / corpus_name
        out_path.mkdir(parents=True, exist_ok=True)
        model = self._get_model()
        print(f"  [{corpus_name}] Encoding {len(corpus_texts)} docs with SBERT...")
        embeddings = model.encode(
            corpus_texts,
            normalize_embeddings=True,
            batch_size=self.cfg.sbert_batch_size,
            show_progress_bar=True,
        ).astype(np.float32)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)
        faiss.write_index(index, str(out_path / "sbert_index.faiss"))
        print(f"✓ SBERT index saved: {out_path / 'sbert_index.faiss'} ({len(corpus_texts)} vecs)")

    def load_index(self, corpus_name: str) -> SBERTIndex:
        import faiss
        index_file = self.index_dir / corpus_name / "sbert_index.faiss"
        if not index_file.exists():
            raise FileNotFoundError(f"SBERT index not found: {index_file}. Run build_index first.")
        index = faiss.read_index(str(index_file))
        model = self._get_model()
        return SBERTIndex(index, model, self.cfg.sbert_batch_size)
