from __future__ import annotations
import logging
import pickle
import random
import time
from pathlib import Path
from typing import TYPE_CHECKING

from datasketch import MinHashLSH
from datasets import load_dataset

if TYPE_CHECKING:
    from config import Config
    from ngram_extractor import NgramExtractor

logger = logging.getLogger(__name__)


class StreamingError(RuntimeError):
    pass


class CorpusIndexer:
    def __init__(self, config: "Config", extractor: "NgramExtractor"):
        self.config = config
        self.extractor = extractor
        self._sampled_flag: dict[str, bool] = {}

    def load_or_build(self, corpus_name: str) -> MinHashLSH:
        """Load existing index if path exists; otherwise call build()."""
        index_path = getattr(self.config, f"{corpus_name}_index_path")
        if Path(index_path).exists():
            logger.info(f"Loading existing {corpus_name} index from {index_path}")
            return self.load(index_path)
        logger.info(f"No existing index for {corpus_name}, building...")
        return self.build(corpus_name)

    def build(self, corpus_name: str) -> MinHashLSH:
        """Stream HF corpus, build MinHash LSH, checkpoint every 500k docs."""
        index_path = getattr(self.config, f"{corpus_name}_index_path")
        lsh = MinHashLSH(threshold=self.config.lsh_threshold, num_perm=self.config.num_perm)

        stream = self._stream_corpus(corpus_name)
        _using_fallback = False

        def _safe_stream():
            nonlocal _using_fallback
            try:
                yield from stream
            except StreamingError:
                logger.warning(f"Streaming failed for {corpus_name}; falling back to {self.config.sample_fraction*100:.0f}% sample")
                _using_fallback = True
                yield from self._fallback_sample(corpus_name)

        for doc_id, text in enumerate(_safe_stream()):
            if not text or not text.strip():
                continue
            minhash = self.extractor.text_to_minhash(text)
            lsh.insert(f"d{doc_id}", minhash)
            if (doc_id + 1) % self.config.checkpoint_interval == 0:
                self.checkpoint(lsh, corpus_name, doc_id + 1)
                logger.info(f"Building {corpus_name} index: {doc_id+1:,} docs processed")

        if _using_fallback:
            self._sampled_flag[corpus_name] = True
        Path(index_path).parent.mkdir(parents=True, exist_ok=True)
        self.save(lsh, index_path)
        logger.info(f"Saved {corpus_name} index to {index_path}")
        return lsh

    def _stream_corpus(self, corpus_name: str):
        """Yield text strings with exponential-backoff retry (3 attempts)."""
        hf_path = self.config.corpus_configs[corpus_name]["hf_path"]
        hf_cfg = self.config.corpus_configs[corpus_name]["config"]

        for attempt in range(self.config.retry_attempts):
            try:
                import aiohttp
                kwargs = dict(streaming=True, split="train",
                              storage_options={"client_kwargs": {"timeout": aiohttp.ClientTimeout(total=60)}})
                if hf_cfg is not None:
                    ds = load_dataset(hf_path, hf_cfg, **kwargs)
                else:
                    ds = load_dataset(hf_path, **kwargs)
                for doc in ds:
                    yield doc.get("text", "")
                return
            except Exception as e:
                wait = 2 ** attempt
                logger.warning(f"Stream attempt {attempt+1} failed for {corpus_name}: {e}. Retrying in {wait}s")
                time.sleep(wait)

        raise StreamingError(f"All {self.config.retry_attempts} attempts failed for {corpus_name}")

    def _fallback_sample(self, corpus_name: str):
        """Yield text from a random sample_fraction of the corpus (non-streaming)."""
        hf_path = self.config.corpus_configs[corpus_name]["hf_path"]
        hf_cfg = self.config.corpus_configs[corpus_name]["config"]
        try:
            import aiohttp
            timeout_obj = aiohttp.ClientTimeout(total=60)
            if hf_cfg is not None:
                ds = load_dataset(hf_path, hf_cfg, split="train",
                                  storage_options={"client_kwargs": {"timeout": timeout_obj}})
            else:
                ds = load_dataset(hf_path, split="train",
                                  storage_options={"client_kwargs": {"timeout": timeout_obj}})
            n = len(ds)
            random.seed(self.config.seed)
            sample_ids = sorted(random.sample(range(n), int(n * self.config.sample_fraction)))
            for idx in sample_ids:
                yield ds[idx].get("text", "")
        except Exception as e:
            logger.error(f"Fallback sample also failed for {corpus_name}: {e}")

    def checkpoint(self, lsh: MinHashLSH, corpus_name: str, doc_id: int) -> None:
        """Save incremental checkpoint to indices/{corpus_name}_ckpt_{doc_id}.pkl."""
        path = Path(self.config.indices_dir) / f"{corpus_name}_ckpt_{doc_id}.pkl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(lsh, f, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info(f"Checkpoint saved: {path}")

    def save(self, lsh: MinHashLSH, path: str) -> None:
        """Serialize MinHashLSH to pickle file."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(lsh, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self, path: str) -> MinHashLSH:
        """Deserialize MinHashLSH from pickle file."""
        with open(path, "rb") as f:
            return pickle.load(f)

    def is_sampled(self, corpus_name: str) -> bool:
        return self._sampled_flag.get(corpus_name, False)
