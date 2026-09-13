"""
Variance Calculation Module (M3-4)
Computes coefficient of variation (CV) per benchmark with outlier filtering.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def filter_outliers(values: List[float], n_std: float = 3.0) -> Tuple[List[float], List[float]]:
    """
    Filter outliers using n-standard deviation rule.

    Args:
        values: List of performance values
        n_std: Number of standard deviations for outlier threshold

    Returns:
        Tuple of (filtered_values, outliers)
    """
    values = np.array(values)
    mean = np.mean(values)
    std = np.std(values, ddof=1)

    # Outlier mask: |value - mean| > n_std * std
    outlier_mask = np.abs(values - mean) > (n_std * std)

    filtered = values[~outlier_mask].tolist()
    outliers = values[outlier_mask].tolist()

    if len(outliers) > 0:
        logger.info(f"Filtered {len(outliers)} outliers out of {len(values)} values")

    return filtered, outliers


def calculate_cv(values: List[float], min_samples: int = 5) -> Optional[float]:
    """
    Calculate coefficient of variation (CV = σ/μ).

    Args:
        values: List of performance values
        min_samples: Minimum number of samples required

    Returns:
        CV value or None if insufficient samples
    """
    if len(values) < min_samples:
        logger.warning(f"Insufficient samples: {len(values)} < {min_samples}")
        return None

    mean = np.mean(values)
    std = np.std(values, ddof=1)

    if mean == 0:
        logger.warning("Mean is zero, CV undefined")
        return None

    cv = std / mean
    return float(cv)


def compute_benchmark_variance(df: pd.DataFrame, outlier_threshold: float = 3.0,
                               min_samples: int = 5) -> pd.DataFrame:
    """
    Compute CV for each benchmark with outlier filtering.

    Args:
        df: DataFrame with 'performance_values' column
        outlier_threshold: Number of standard deviations for outlier filtering
        min_samples: Minimum samples required after filtering

    Returns:
        DataFrame with 'cv', 'mean_performance', 'std_performance' columns
    """
    results = []

    for idx, row in df.iterrows():
        values = row["performance_values"]

        # Filter outliers
        filtered_values, outliers = filter_outliers(values, n_std=outlier_threshold)

        # Calculate CV
        cv = calculate_cv(filtered_values, min_samples=min_samples)

        if cv is not None:
            results.append({
                "benchmark_id": row["benchmark_id"],
                "benchmark_name": row.get("benchmark_name", ""),
                "artifact_group": row.get("artifact_group", ""),
                "artifact_count": row.get("artifact_count", 0),
                "num_results_original": len(values),
                "num_results_filtered": len(filtered_values),
                "num_outliers": len(outliers),
                "mean_performance": np.mean(filtered_values),
                "std_performance": np.std(filtered_values, ddof=1),
                "cv": cv
            })

    results_df = pd.DataFrame(results)
    logger.info(f"Computed CV for {len(results_df)} benchmarks")

    return results_df


def summarize_variance_by_group(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize CV statistics by artifact group.

    Args:
        df: DataFrame with 'cv' and 'artifact_group' columns

    Returns:
        Summary DataFrame with group statistics
    """
    summary = df.groupby("artifact_group")["cv"].agg([
        ("count", "count"),
        ("mean_cv", "mean"),
        ("median_cv", "median"),
        ("std_cv", "std"),
        ("min_cv", "min"),
        ("max_cv", "max")
    ]).reset_index()

    logger.info("\nVariance Summary by Artifact Group:")
    logger.info(summary.to_string(index=False))

    return summary


if __name__ == "__main__":
    import os

    # Load data
    data_path = "../outputs/benchmark_data.csv"
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")

    df = pd.read_csv(data_path)

    # Parse performance_values from string representation
    import ast
    df["performance_values"] = df["performance_values"].apply(ast.literal_eval)

    # Compute variance
    variance_df = compute_benchmark_variance(df)

    # Summarize by group
    summary = summarize_variance_by_group(variance_df)

    # Save results
    output_path = "../outputs/variance_results.csv"
    variance_df.to_csv(output_path, index=False)
    print(f"✓ Variance results saved to: {output_path}")

    summary_path = "../outputs/variance_summary.csv"
    summary.to_csv(summary_path, index=False)
    print(f"✓ Variance summary saved to: {summary_path}")
