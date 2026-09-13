"""
CorpusFilter: load, score, filter, and save DCLM corpus slices.

Uses pre-computed fasttext score field when available.
"""

import itertools
import logging
import os
import random
from pathlib import Path
from typing import Dict, List, Optional

import jsonlines
import numpy as np

logger = logging.getLogger(__name__)


class CorpusFilter:
    """Load DCLM documents, apply quality filters, and persist corpora."""

    def __init__(self, fasttext_model_path: str, seed: int = 42):
        self.fasttext_model_path = fasttext_model_path
        self.seed = seed
        self._model = None  # lazy-loaded only when needed
        random.seed(seed)
        np.random.seed(seed)

    @property
    def model(self):
        if self._model is None:
            import fasttext
            logger.info("Loading fasttext model from %s", self.fasttext_model_path)
            self._model = fasttext.load_model(self.fasttext_model_path)
        return self._model

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def load_and_sample(self, dataset_id: str, n_docs: int) -> List[dict]:
        """Stream DCLM dataset and collect n_docs documents."""
        from datasets import load_dataset

        logger.info("Streaming %d docs from %s", n_docs, dataset_id)
        ds = load_dataset(
            dataset_id,
            split="train",
            streaming=True,
            trust_remote_code=True,
        )
        docs = list(itertools.islice(ds, n_docs))
        logger.info("Collected %d documents", len(docs))
        return docs

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    PRECOMPUTED_FIELD = "fasttext_openhermes_reddit_eli5_vs_rw_v2_bigram_200k_train_prob"

    def score_documents(self, docs: List[dict]) -> np.ndarray:
        """Return quality scores for all docs.

        Prefers the pre-computed score field in the dataset.
        Falls back to running the fasttext model.
        """
        if docs and self.PRECOMPUTED_FIELD in docs[0]:
            logger.info("Using pre-computed fasttext scores from field '%s'", self.PRECOMPUTED_FIELD)
            return np.array([float(d.get(self.PRECOMPUTED_FIELD, 0.5)) for d in docs])

        logger.info("Computing fasttext scores from model")
        scores = []
        for d in docs:
            text = d.get("text", "") or ""
            text = text.replace("\n", " ").strip()
            if not text:
                scores.append(0.5)
                continue
            try:
                labels, probs = self.model.predict(text)
                prob = float(probs[0])
                score = prob if labels[0] == "__label__hq" else 1.0 - prob
            except Exception:
                score = 0.5
            scores.append(score)
        return np.array(scores)

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def apply_fasttext_filter(
        self,
        docs: List[dict],
        scores: np.ndarray,
        percentile: float,
    ) -> List[dict]:
        """Keep docs whose score is >= the given percentile threshold."""
        if percentile <= 0:
            return docs
        threshold = float(np.percentile(scores, percentile))
        filtered = [d for d, s in zip(docs, scores) if s >= threshold]
        logger.info(
            "fasttext filter @pct=%s: %d → %d docs (threshold=%.4f)",
            percentile, len(docs), len(filtered), threshold,
        )
        return filtered

    def apply_doremi_reweight(
        self,
        docs: List[dict],
        domain_key: str = "source",
    ) -> List[dict]:
        """Inverse-frequency domain reweighting (DoReMi-style)."""
        from collections import Counter

        domain_counts: Counter = Counter(d.get(domain_key, "unknown") for d in docs)
        total = len(docs)
        # Inverse frequency weights
        weights = np.array(
            [1.0 / domain_counts[d.get(domain_key, "unknown")] for d in docs],
            dtype=float,
        )
        weights /= weights.sum()
        indices = np.random.choice(len(docs), size=total, replace=True, p=weights)
        reweighted = [docs[i] for i in indices]
        logger.info("DoReMi reweight: %d docs, %d domains", total, len(domain_counts))
        return reweighted

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    @staticmethod
    def _sanitize_doc(doc: dict) -> dict:
        """Convert non-JSON-serializable values (e.g., datetime) to strings."""
        import datetime
        result = {}
        for k, v in doc.items():
            if isinstance(v, (datetime.datetime, datetime.date)):
                result[k] = v.isoformat()
            elif isinstance(v, dict):
                result[k] = CorpusFilter._sanitize_doc(v)
            elif isinstance(v, (list, tuple)):
                result[k] = [
                    CorpusFilter._sanitize_doc(i) if isinstance(i, dict) else
                    (i.isoformat() if isinstance(i, (datetime.datetime, datetime.date)) else i)
                    for i in v
                ]
            else:
                result[k] = v
        return result

    def save_corpus(self, docs: List[dict], config_id: str, data_dir: str) -> str:
        """Write corpus to {data_dir}/corpora/{config_id}.jsonl"""
        out_path = Path(data_dir) / "corpora" / f"{config_id}.jsonl"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        sanitized = [self._sanitize_doc(d) for d in docs]
        with jsonlines.open(str(out_path), mode="w") as writer:
            writer.write_all(sanitized)
        logger.info("Saved %d docs to %s", len(docs), out_path)
        return str(out_path)

    def load_corpus(self, config_id: str, data_dir: str) -> List[dict]:
        """Read corpus from {data_dir}/corpora/{config_id}.jsonl"""
        path = Path(data_dir) / "corpora" / f"{config_id}.jsonl"
        with jsonlines.open(str(path)) as reader:
            docs = list(reader)
        logger.info("Loaded %d docs from %s", len(docs), path)
        return docs

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    def build_all_corpora(
        self,
        data_dir: str,
        dataset_id: str = "mlfoundations/dclm-baseline-1.0",
        n_docs: int = 10_000_000,
        configurations: Optional[list] = None,
    ) -> Dict[str, str]:
        """Build C0-C6 corpora, skipping any that already exist."""
        from config import CONFIG

        if configurations is None:
            configurations = CONFIG["configurations"]

        corpora_dir = Path(data_dir) / "corpora"
        corpora_dir.mkdir(parents=True, exist_ok=True)

        # Check if all corpora exist already
        all_exist = all(
            (corpora_dir / f"{c['id']}.jsonl").exists() for c in configurations
        )

        if all_exist:
            logger.info("All corpora already exist; skipping load.")
            paths = {c["id"]: str(corpora_dir / f"{c['id']}.jsonl") for c in configurations}
            return paths

        # Load base docs once
        logger.info("Loading base corpus (%d docs)…", n_docs)
        docs = self.load_and_sample(dataset_id, n_docs)
        scores = self.score_documents(docs)

        paths: Dict[str, str] = {}
        for cfg in configurations:
            cid = cfg["id"]
            out_path = corpora_dir / f"{cid}.jsonl"

            if out_path.exists():
                logger.info("Corpus %s exists, skipping.", cid)
                paths[cid] = str(out_path)
                continue

            filter_type = cfg["filter_type"]
            percentile = cfg.get("percentile")

            if filter_type == "unfiltered":
                filtered = docs
            elif filter_type == "fasttext":
                filtered = self.apply_fasttext_filter(docs, scores, percentile)
            elif filter_type == "doremi":
                filtered = self.apply_doremi_reweight(docs)
            else:
                logger.warning("Unknown filter_type '%s'; using unfiltered.", filter_type)
                filtered = docs

            path = self.save_corpus(filtered, cid, data_dir)
            paths[cid] = path

        return paths
