from __future__ import annotations
import logging
import os
import time
from typing import Optional, TYPE_CHECKING

from datasketch import MinHash, MinHashLSH

if TYPE_CHECKING:
    from config import Config
    from ngram_extractor import NgramExtractor

logger = logging.getLogger(__name__)


class PileQuery:
    def __init__(self, config: "Config", extractor: "NgramExtractor"):
        self.config = config
        self.extractor = extractor
        self._mode: str = "wimbd" if self._use_wimbd() else "fallback_minhash"
        self._lsh: Optional[MinHashLSH] = None

    def _use_wimbd(self) -> bool:
        """Returns True if WIMBD_ES_HOST env var is set and non-empty."""
        return bool(os.environ.get("WIMBD_ES_HOST", "").strip())

    def _init_minhash_lsh(self) -> MinHashLSH:
        """Lazy-init MinHashLSH(threshold=0.5, num_perm=128) for fallback mode."""
        if self._lsh is None:
            self._lsh = MinHashLSH(
                threshold=self.config.minhash_threshold,
                num_perm=self.config.minhash_num_perm,
            )
        return self._lsh

    def _query_wimbd_with_retry(self, ngram: str) -> bool:
        """Query wimbd with 3 attempts, exponential backoff (1s, 2s, 4s).
        Returns True if ngram found in Pile index."""
        from wimbd.es import has_ngram
        for attempt in range(self.config.retry_attempts):
            try:
                return has_ngram(ngram, n=self.config.ngram_n, index=self.config.pile_index)
            except Exception as e:
                if attempt == self.config.retry_attempts - 1:
                    logger.warning(f"wimbd query failed after {self.config.retry_attempts} attempts: {e}")
                    return False
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
        return False

    def _query_minhash(self, ngrams: list[str]) -> bool:
        """MinHash LSH fallback: check if any ngram shingle matches LSH index.
        Returns True if Jaccard similarity >= threshold with any indexed document."""
        lsh = self._init_minhash_lsh()
        m = MinHash(num_perm=self.config.minhash_num_perm)
        for ng in ngrams:
            m.update(ng.encode("utf8"))
        results = lsh.query(m)
        return len(results) > 0

    def is_contaminated(self, text: str) -> int:
        """Returns 1 if any 13-gram matches Pile index, 0 otherwise."""
        ngrams = self.extractor.extract(text)
        if not ngrams:
            return 0
        if self._mode == "wimbd":
            return int(any(self._query_wimbd_with_retry(ng) for ng in ngrams))
        else:
            return int(self._query_minhash(ngrams))

    def query_subtask(self, name: str, texts: list[str]) -> list[int]:
        """Returns per-item contamination labels [0/1] for one sub-task with logging."""
        labels = [self.is_contaminated(text) for text in texts]
        count = sum(labels)
        rate = count / len(labels) if labels else 0.0
        logger.info(
            f"Querying wimbd for sub-task {name}: "
            f"{count}/{len(labels)} items contaminated ({rate:.3f})"
        )
        return labels

    def query_all(self, subtask_texts: dict[str, list[str]]) -> dict[str, list[int]]:
        """Returns {subtask_name: [0/1, ...]} for all 59 sub-tasks."""
        return {name: self.query_subtask(name, texts) for name, texts in subtask_texts.items()}

    @property
    def mode(self) -> str:
        """Returns 'wimbd' or 'fallback_minhash'."""
        return self._mode
