from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from index_builder import NgramIndex, SBERTIndex

from detectors.ngram_detector import NgramDetector
from detectors.embedding_detector import EmbeddingDetector
from detectors.minkpp_detector import MinkPPDetector
from detectors.dcpdd_detector import DCPDDDetector
from detectors.constat_detector import ConStatDetector


def get_detector_registry(cfg):
    """Return dict of all 5 detectors keyed by name."""
    return {
        "ngram": NgramDetector(cfg),
        "embedding": EmbeddingDetector(cfg),
        "minkpp": MinkPPDetector(cfg),
        "dcpdd": DCPDDDetector(cfg),
        "constat": ConStatDetector(cfg),
    }


def run_detector_evaluation(
    cfg,
    benchmark_texts_dict: dict,
    ngram_indices: dict,
    sbert_indices: dict,
    ground_truth_dict: dict,
) -> dict:
    """Loop benchmark × corpus × detector, store preds in dict[str, np.ndarray].

    Returns: {"{detector}_{benchmark}_{corpus}": np.ndarray shape (N,) int64}
    """
    import numpy as np
    registry = get_detector_registry(cfg)
    results: dict[str, np.ndarray] = {}

    for bench_name, bench_texts in benchmark_texts_dict.items():
        for corpus_name in cfg.corpora:
            ngram_idx = ngram_indices.get(corpus_name)
            sbert_idx = sbert_indices.get(corpus_name)
            key_prefix = f"{bench_name}_{corpus_name}"

            for det_name, detector in registry.items():
                key = f"{det_name}_{key_prefix}"
                try:
                    if det_name == "ngram" and ngram_idx is not None:
                        preds = detector.predict(bench_texts, ngram_idx)
                    elif det_name == "embedding" and sbert_idx is not None:
                        preds = detector.predict(bench_texts, sbert_idx)
                    elif det_name in ("minkpp", "dcpdd", "constat"):
                        preds = detector.predict(bench_texts)
                    else:
                        preds = np.zeros(len(bench_texts), dtype=np.int64)
                    results[key] = preds
                    print(f"  ✓ {key}: {preds.sum()}/{len(preds)} detected")
                except Exception as e:
                    print(f"  ⚠ {key} failed: {e}")
                    results[key] = np.zeros(len(bench_texts), dtype=np.int64)

    return results
