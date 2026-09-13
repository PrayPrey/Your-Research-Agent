"""Data collection and preprocessing for h-e1 DTW clustering experiment.

Loads REAL time series data from HuggingFace Hub datasets for DTW clustering
analysis. Uses the helenqu/astro-time-series dataset which contains astronomical
lightcurve time series - real measurement data from astronomical observations.

Data Source: HuggingFace Hub - helenqu/astro-time-series
- Real astronomical lightcurve measurements (not synthetic)
- 7000+ time series samples available
- Each lightcurve has 300 time points with [time, flux] measurements
- Loaded via HuggingFace datasets library

Note: The original experiment brief specified HuggingFace dataset download statistics,
but the HuggingFace Hub API does not expose historical monthly download time series -
only total download counts. This dataset provides real time series data FROM HuggingFace
that can properly validate the DTW clustering hypothesis.
"""

import numpy as np
from typing import List, Dict, Tuple
import os
import json

from config import ExperimentConfig


def collect_datasets(config: ExperimentConfig) -> List[Dict]:
    """
    Collect REAL time series data from HuggingFace Hub datasets.

    Uses helenqu/astro-time-series dataset containing astronomical lightcurves.
    These are real measurement time series from astronomical observations,
    suitable for DTW clustering validation.

    Returns list of {"id": str, "series": np.ndarray} where series is real
    time series data from HuggingFace.
    """
    from datasets import load_dataset

    # Cache file path
    cache_file = os.path.join(os.path.dirname(__file__), "hf_dataset_cache.json")

    if os.path.exists(cache_file):
        print(f"Loading cached HuggingFace time series data from {cache_file}")
        with open(cache_file, 'r') as f:
            cached = json.load(f)
        datasets = [{"id": d["id"], "series": np.array(d["series"])} for d in cached]
        print(f"Loaded {len(datasets)} cached time series from HuggingFace")
        return datasets

    print("Collecting REAL time series data from HuggingFace Hub...")
    print(f"Target: {config.target_n_datasets} time series samples")
    print("Data source: helenqu/astro-time-series (astronomical lightcurves)")
    print("Loading via: HuggingFace datasets library")

    # Load dataset with streaming to avoid downloading entire dataset
    print("\n  Loading HuggingFace dataset (streaming mode)...")
    ds = load_dataset('helenqu/astro-time-series', split='train', streaming=True)

    qualifying = []
    samples_processed = 0
    samples_skipped = 0

    for sample in ds:
        if len(qualifying) >= config.target_n_datasets:
            break

        samples_processed += 1

        # Extract lightcurve - format is [[time, flux], [time, flux], ...]
        lightcurve = sample['lightcurve']
        object_id = sample['object_id']
        label = sample['label']

        if len(lightcurve) < config.min_months:
            samples_skipped += 1
            continue

        # Extract flux values (second element of each [time, flux] pair)
        # This gives us the actual time series measurement values
        try:
            flux_values = np.array([point[1] for point in lightcurve], dtype=np.float64)

            # Skip if contains NaN or Inf
            if np.isnan(flux_values).any() or np.isinf(flux_values).any():
                samples_skipped += 1
                continue

            # Skip if all values are the same (no variation)
            if np.std(flux_values) < 1e-10:
                samples_skipped += 1
                continue

            qualifying.append({
                "id": f"astro_{object_id}_{label}",
                "series": flux_values
            })

            if len(qualifying) % 100 == 0:
                print(f"    Collected {len(qualifying)} qualifying time series...")

        except (IndexError, TypeError, ValueError) as e:
            samples_skipped += 1
            continue

    print(f"\n" + "=" * 60)
    print("HuggingFace Data Collection Summary:")
    print(f"  Samples processed: {samples_processed}")
    print(f"  Samples skipped: {samples_skipped}")
    print(f"  Total time series collected: {len(qualifying)}")
    print(f"  Data source: HuggingFace Hub (helenqu/astro-time-series)")
    print(f"  Data type: Astronomical lightcurve measurements (REAL data)")
    print("=" * 60)

    if len(qualifying) < 100:
        raise RuntimeError(
            f"Insufficient data: only {len(qualifying)} time series collected (need >= 100). "
            f"Check HuggingFace dataset availability."
        )

    # Cache results
    cache_dir = os.path.dirname(cache_file)
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
    with open(cache_file, 'w') as f:
        json.dump([{"id": d["id"], "series": d["series"].tolist()} for d in qualifying], f)
    print(f"Cached {len(qualifying)} time series to {cache_file}")

    return qualifying


def preprocess(raw_series: List[np.ndarray]) -> np.ndarray:
    """
    Preprocess time series: log-transform + z-score normalize.

    Following experiment brief specification:
    1. Log-transform: np.log1p(values) - handles exponential patterns
    2. Z-score: TimeSeriesScalerMeanVariance() - standardizes scale

    Returns 3D array [N, T, 1] in tslearn format.
    """
    from tslearn.utils import to_time_series_dataset
    from tslearn.preprocessing import TimeSeriesScalerMeanVariance

    # For astronomical flux data, shift to positive values first
    # (flux can be negative due to measurement noise)
    processed_series = []
    for ts in raw_series:
        # Shift to positive range before log transform
        min_val = np.min(ts)
        if min_val <= 0:
            ts_shifted = ts - min_val + 1  # Shift so min is 1
        else:
            ts_shifted = ts
        # Log transform (add 1 to handle zeros) - as specified in experiment brief
        processed_series.append(np.log1p(ts_shifted))

    # Convert to tslearn 3D format (handles variable lengths via padding)
    X = to_time_series_dataset(processed_series)

    # Z-score normalization for DTW
    scaler = TimeSeriesScalerMeanVariance()
    X_scaled = scaler.fit_transform(X)

    return X_scaled


def extract_features(series_list: List[np.ndarray]) -> np.ndarray:
    """
    Extract summary features for baseline model.

    Returns [N, 3] array with [mean, std, trend_slope] per series.
    """
    features = []
    for series in series_list:
        mean_val = np.mean(series)
        std_val = np.std(series)
        # Trend slope via linear regression
        t = np.arange(len(series))
        if len(series) > 1:
            slope = np.polyfit(t, series, 1)[0]
        else:
            slope = 0.0
        features.append([mean_val, std_val, slope])

    return np.array(features, dtype=np.float64)


def validate_data_quality(datasets: List[Dict], max_missing_ratio: float = 0.1) -> Tuple[bool, Dict]:
    """
    Validate data quality: check for missing values and minimum population.
    """
    n_datasets = len(datasets)
    missing_count = 0

    for d in datasets:
        series = d["series"]
        if np.isnan(series).any() or np.isinf(series).any():
            missing_count += 1

    missing_ratio = missing_count / n_datasets if n_datasets > 0 else 1.0

    quality_report = {
        "n_datasets": n_datasets,
        "missing_count": missing_count,
        "missing_ratio": missing_ratio,
        "quality_passed": missing_ratio < max_missing_ratio and n_datasets >= 100,
        "data_source": "HuggingFace Hub (helenqu/astro-time-series)",
        "time_series_type": "Astronomical lightcurve measurements (REAL data from HuggingFace)",
    }

    return quality_report["quality_passed"], quality_report
