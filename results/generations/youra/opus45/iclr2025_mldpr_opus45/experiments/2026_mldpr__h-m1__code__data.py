"""Data loading and preprocessing for h-m1 PELT changepoint detection experiment.

Reuses time series data cached by h-e1 (HuggingFace astro-time-series).
Preprocessing adapted for ruptures PELT: returns List[np.ndarray] (1D per series).
"""

import numpy as np
from typing import List, Dict, Tuple
import os
import json

from config import ExperimentConfig


def load_series(config: ExperimentConfig) -> List[Dict]:
    """
    Load time series from h-e1 cache or local cache.

    Returns list of {"id": str, "series": np.ndarray} where series is 1D.
    """
    # Try local cache first (copied from h-e1)
    cache_file = os.path.join(os.path.dirname(__file__), config.cache_path)

    if os.path.exists(cache_file):
        print(f"Loading cached time series data from {cache_file}")
        with open(cache_file, 'r') as f:
            cached = json.load(f)
        datasets = [{"id": d["id"], "series": np.array(d["series"])} for d in cached]
        print(f"Loaded {len(datasets)} cached time series")
        return datasets

    # Try h-e1 cache as fallback
    h_e1_cache = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code", "hf_dataset_cache.json")
    if os.path.exists(h_e1_cache):
        print(f"Loading from h-e1 cache: {h_e1_cache}")
        with open(h_e1_cache, 'r') as f:
            cached = json.load(f)
        datasets = [{"id": d["id"], "series": np.array(d["series"])} for d in cached]
        print(f"Loaded {len(datasets)} time series from h-e1 cache")
        return datasets

    raise FileNotFoundError(
        f"No cache file found at {cache_file} or {h_e1_cache}. "
        "Run h-e1 experiment first to collect data."
    )


def preprocess_for_pelt(raw_series: List[np.ndarray]) -> List[np.ndarray]:
    """
    Preprocess time series for PELT changepoint detection.

    Applies log-transform + z-score normalization per series.
    Returns List[np.ndarray] (1D per series) for ruptures compatibility.

    Note: Unlike h-e1's preprocess() which returns [N, T, 1] tslearn format,
    this returns List[np.ndarray] as required by ruptures.Pelt.
    """
    processed = []

    for ts in raw_series:
        # Ensure 1D
        ts = np.asarray(ts).flatten()

        # Shift to positive values before log transform
        min_val = np.min(ts)
        if min_val <= 0:
            ts_shifted = ts - min_val + 1  # Shift so min is 1
        else:
            ts_shifted = ts

        # Log transform (handles exponential patterns)
        ts_log = np.log1p(ts_shifted)

        # Z-score normalization
        mu = np.mean(ts_log)
        sigma = np.std(ts_log)

        # Guard against constant series
        if sigma < 1e-10:
            sigma = 1.0

        ts_normalized = (ts_log - mu) / sigma

        processed.append(ts_normalized)

    return processed


def validate_series(datasets: List[Dict], config: ExperimentConfig = None) -> Tuple[bool, Dict]:
    """
    Validate time series data quality.

    Checks:
    - Minimum series length
    - No NaN or Inf values
    - Sufficient dataset count

    Returns (passed: bool, report: Dict).
    """
    min_length = config.min_series_length if config else 12

    n_total = len(datasets)
    n_valid = 0
    n_too_short = 0
    n_invalid = 0
    series_lengths = []

    for d in datasets:
        series = d["series"]
        length = len(series)
        series_lengths.append(length)

        if length < min_length:
            n_too_short += 1
            continue

        if np.isnan(series).any() or np.isinf(series).any():
            n_invalid += 1
            continue

        n_valid += 1

    passed = n_valid >= 100 and n_valid >= n_total * 0.9

    report = {
        "n_total": n_total,
        "n_valid": n_valid,
        "n_too_short": n_too_short,
        "n_invalid": n_invalid,
        "valid_ratio": n_valid / n_total if n_total > 0 else 0.0,
        "min_length": int(np.min(series_lengths)) if series_lengths else 0,
        "max_length": int(np.max(series_lengths)) if series_lengths else 0,
        "mean_length": float(np.mean(series_lengths)) if series_lengths else 0.0,
        "passed": passed,
    }

    return passed, report
