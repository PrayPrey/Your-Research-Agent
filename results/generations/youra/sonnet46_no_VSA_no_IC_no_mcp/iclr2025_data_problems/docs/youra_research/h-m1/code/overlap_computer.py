"""A-5: Overlap Computer — parallel per-doc 13-gram overlap computation."""
import json
import os
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from config import NGRAM_SIZE, N_WORKERS, BENCHMARKS, CHECKPOINT_DIR
from sampler import DocWithMeta


def _compute_single(args: tuple) -> dict[str, float]:
    """Worker: compute char n-gram overlap between one doc and benchmark ngram sets."""
    text, ngram_sets_items, n = args
    # Rebuild frozensets from items passed as lists (multiprocessing serialization)
    doc_ngrams = frozenset(text[i:i + n] for i in range(len(text) - n + 1))
    if not doc_ngrams:
        return {b: 0.0 for b, _ in ngram_sets_items}
    return {b: len(doc_ngrams & frozenset(ngs)) / len(doc_ngrams)
            for b, ngs in ngram_sets_items}


def compute_overlap_batch(
    docs: list[DocWithMeta],
    ngram_sets: dict[str, frozenset],
    n: int = NGRAM_SIZE,
    n_workers: int = N_WORKERS,
    chunk_size: int = 100,
) -> np.ndarray:
    """Parallel 13-gram overlap for all docs.

    Returns np.ndarray shape [len(docs), len(ngram_sets)],
    columns ordered by sorted(ngram_sets.keys()).
    """
    benchmarks = sorted(ngram_sets.keys())
    # Convert frozensets to lists for multiprocessing pickle
    ngram_sets_items = [(b, list(ngram_sets[b])) for b in benchmarks]

    args = [(doc.text, ngram_sets_items, n) for doc in docs]

    results: list[dict[str, float]] = []
    with Pool(n_workers) as pool:
        for res in pool.imap(_compute_single, args, chunksize=chunk_size):
            results.append(res)

    arr = np.array([[r[b] for b in benchmarks] for r in results], dtype=np.float32)
    return arr  # shape [N_docs, len(benchmarks)]


def save_overlap_checkpoint(
    removed_arr: np.ndarray,
    retained_arr: np.ndarray,
    benchmark_names: list[str],
    checkpoint_path: Path,
) -> None:
    """Save overlap arrays as JSON."""
    payload = {
        "benchmarks": benchmark_names,
        "removed": removed_arr.tolist(),
        "retained": retained_arr.tolist(),
    }
    tmp = checkpoint_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload))
    os.replace(tmp, checkpoint_path)


def load_overlap_checkpoint(
    checkpoint_path: Path,
) -> tuple[np.ndarray, np.ndarray, list[str]] | None:
    """Returns (removed_arr, retained_arr, benchmark_names) or None if missing."""
    if not checkpoint_path.exists():
        return None
    d = json.loads(checkpoint_path.read_text())
    return (
        np.array(d["removed"], dtype=np.float32),
        np.array(d["retained"], dtype=np.float32),
        d["benchmarks"],
    )


def compute_all_overlaps(
    sampled_docs: dict[str, list[DocWithMeta]],
    ngram_sets: dict[str, frozenset],
    checkpoint_path: Path = CHECKPOINT_DIR / "overlap_scores.json",
    n: int = NGRAM_SIZE,
    n_workers: int = N_WORKERS,
) -> dict[str, dict[str, list[float]]]:
    """Return {"removed": {bench: [floats]}, "retained": {bench: [floats]}}.

    Benchmarks ordered by sorted keys. Checkpointed.
    """
    cached = load_overlap_checkpoint(checkpoint_path)
    if cached is not None:
        removed_arr, retained_arr, benchmarks = cached
        print(f"✓ Overlap scores loaded from checkpoint")
        result = {"removed": {}, "retained": {}}
        for i, b in enumerate(benchmarks):
            result["removed"][b] = removed_arr[:, i].tolist()
            result["retained"][b] = retained_arr[:, i].tolist()
        return result

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    benchmarks = sorted(ngram_sets.keys())
    removed_docs = sampled_docs["removed"]
    retained_docs = sampled_docs["retained"]

    print(f"Computing overlaps for {len(removed_docs)} removed docs...")
    removed_arr = compute_overlap_batch(removed_docs, ngram_sets, n=n, n_workers=n_workers)
    print(f"Computing overlaps for {len(retained_docs)} retained docs...")
    retained_arr = compute_overlap_batch(retained_docs, ngram_sets, n=n, n_workers=n_workers)

    save_overlap_checkpoint(removed_arr, retained_arr, benchmarks, checkpoint_path)
    print(f"✓ Overlap scores saved to {checkpoint_path}")

    result = {"removed": {}, "retained": {}}
    for i, b in enumerate(benchmarks):
        result["removed"][b] = removed_arr[:, i].tolist()
        result["retained"][b] = retained_arr[:, i].tolist()
    return result
