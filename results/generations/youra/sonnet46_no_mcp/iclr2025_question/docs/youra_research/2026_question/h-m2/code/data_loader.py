import sys
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from tqdm import tqdm

from config import ExperimentConfig


def load_labels(cfg: ExperimentConfig) -> np.ndarray:
    """Load hallucination labels from halueval_qa_2k.json. Returns shape (2000,) int array."""
    path = Path(cfg.dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    with open(path) as f:
        data = json.load(f)
    labels = np.array([int(record.get("hallucination", record.get("label", 0))) for record in data], dtype=int)
    return labels


def load_cluster_counts_from_se_json(se_path: str) -> Optional[np.ndarray]:
    """Attempt to extract per-example cluster_count from semantic_entropy.json.

    semantic_entropy.json stores {str_id: float} entropy scores, NOT cluster counts.
    Returns None (expected — float scores only, not cluster counts).
    """
    path = Path(se_path)
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    # Check if values are dicts containing cluster_count
    sample = next(iter(data.values())) if data else None
    if isinstance(sample, dict) and "cluster_count" in sample:
        counts = []
        for key in sorted(data.keys(), key=lambda x: int(x)):
            counts.append(int(data[key]["cluster_count"]))
        return np.array(counts, dtype=int)
    # Values are floats (entropy scores) — cluster counts not stored
    return None


def validate_cluster_counts(cluster_counts: np.ndarray, n: int = 2000) -> np.ndarray:
    """Assert len==n, clamp values to [1,5], warn on out-of-range."""
    if len(cluster_counts) != n:
        raise ValueError(f"cluster_counts length {len(cluster_counts)} != expected {n}")
    out_of_range = np.sum((cluster_counts < 1) | (cluster_counts > 5))
    if out_of_range > 0:
        print(f"⚠ {out_of_range} cluster counts out of [1,5] range — clamping")
    return np.clip(cluster_counts, 1, 5).astype(int)


def load_stochastic_samples(path: str) -> List[Dict[str, Any]]:
    """Load stochastic_samples.jsonl. Returns list of {id, samples: List[str]}."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"stochastic_samples.jsonl not found at {path}. "
            "Ensure H-E1 experiment has been run."
        )
    records = []
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _get_nli_pipeline_for_recluster(cfg: ExperimentConfig):
    """Inject h-e1/code to sys.path, load NLI pipeline."""
    h_e1_dir = str(Path(cfg.h_e1_code_dir).resolve())
    if h_e1_dir not in sys.path:
        sys.path.insert(0, h_e1_dir)
    from uq_signals import load_nli_pipeline  # noqa: E402
    return load_nli_pipeline(cfg)


def _cluster_count_for_example(
    samples: List[str],
    nli_pipeline,
    batch_size: int = 16,
) -> int:
    """Run cluster_by_nli, return len(set(cluster_ids.values()))."""
    if len(samples) <= 1:
        return 1
    h_e1_dir = None
    for p in sys.path:
        if "h-e1" in p and Path(p).exists():
            h_e1_dir = p
            break
    if h_e1_dir and h_e1_dir not in sys.path:
        sys.path.insert(0, h_e1_dir)
    from uq_signals import cluster_by_nli  # noqa: E402
    cluster_ids = cluster_by_nli(samples, nli_pipeline, batch_size=batch_size)
    return len(set(cluster_ids.values()))


def load_cluster_counts_from_stochastic_samples(
    samples_path: str,
    nli_pipeline,
    cfg: ExperimentConfig,
) -> np.ndarray:
    """Fallback: re-run NLI clustering on stochastic_samples.jsonl.

    Returns shape (2000,) int array, values in [1, 5].
    """
    records = load_stochastic_samples(samples_path)
    records = sorted(records, key=lambda r: r["id"])
    counts = []
    for record in tqdm(records, desc="NLI re-clustering"):
        samples = record["samples"][: cfg.n_samples_per_example]
        count = _cluster_count_for_example(samples, nli_pipeline, batch_size=16)
        counts.append(max(1, min(5, count)))
    return np.array(counts, dtype=int)


def load_cluster_counts(cfg: ExperimentConfig) -> Tuple[np.ndarray, str]:
    """Priority loader:
      1. Try load_cluster_counts_from_se_json()
      2. Try H-M1 experiment_results.json cluster_distribution field
      3. Fallback: re-run NLI clustering via load_cluster_counts_from_stochastic_samples()
    Returns (cluster_counts array, source_description string).
    """
    # Priority 1: semantic_entropy.json (expected to return None)
    counts = load_cluster_counts_from_se_json(cfg.se_scores_path)
    if counts is not None:
        print("✓ Cluster counts loaded from semantic_entropy.json")
        return counts, "se_json"

    # Priority 2: H-M1 experiment_results.json cluster_distribution
    hm1_path = Path(cfg.hm1_results_path)
    if hm1_path.exists():
        with open(hm1_path) as f:
            hm1_data = json.load(f)
        raw = hm1_data.get("cluster_distribution", {}).get("cluster_counts")
        if raw is not None and len(raw) == 2000:
            print("✓ Cluster counts loaded from H-M1 experiment_results.json")
            return np.array(raw, dtype=int), "hm1_summary"

    # Priority 3: NLI re-clustering fallback
    samples_path = cfg.stochastic_samples_path
    if not Path(samples_path).exists():
        raise FileNotFoundError(
            f"stochastic_samples.jsonl not found at {samples_path}. "
            "Cannot load cluster counts from any source."
        )
    print("⚠ Falling back to NLI re-clustering from stochastic_samples.jsonl")
    nli_pipeline = _get_nli_pipeline_for_recluster(cfg)
    counts = load_cluster_counts_from_stochastic_samples(samples_path, nli_pipeline, cfg)
    return counts, "nli_recluster"
