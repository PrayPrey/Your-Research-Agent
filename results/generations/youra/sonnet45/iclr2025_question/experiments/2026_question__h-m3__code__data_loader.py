"""Data loading module for H-M3 Bootstrap CI Stability Analysis.

Task: T-EPIC-02 (A-2: Data Loading from h-e1)
"""

import pandas as pd
import numpy as np
from typing import Dict
from pathlib import Path


# Expected data format
EXPECTED_COLUMNS = ["dataset", "architecture", "seed", "test_accuracy", "device", "error"]
EXPECTED_SAMPLES_PER_CONDITION = 30
VALID_DATASETS = ["mnist", "fashion_mnist"]
VALID_ARCHITECTURES = ["1layer", "2layer"]

# Data validation
ACCURACY_MIN = 0.0
ACCURACY_MAX = 100.0


def load_h_e1_test_accuracies(csv_path: str) -> Dict[str, np.ndarray]:
    """Load test accuracies from h-e1 experiment logs.

    Args:
        csv_path: Path to h-e1 experiment_logs.csv

    Returns:
        Dictionary mapping condition names to numpy arrays of test accuracies (shape: (30,))

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If data validation fails
    """
    # Check file exists
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"h-e1 results file not found: {csv_path}")

    # Load CSV
    df = pd.read_csv(csv_path)

    # Validate columns
    missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing columns in CSV: {missing_cols}")

    # Extract condition data (skip conditions with missing data)
    conditions_data = {}
    skipped_conditions = []

    for dataset in VALID_DATASETS:
        for architecture in VALID_ARCHITECTURES:
            condition_name = f"{architecture}_{dataset}"
            try:
                condition_data = extract_condition_data(df, dataset, architecture)
                conditions_data[condition_name] = condition_data
            except ValueError as e:
                skipped_conditions.append((condition_name, str(e)))
                print(f"  ⚠ Skipping {condition_name}: {e}")

    # Validate extracted data
    validate_condition_data(conditions_data)

    print(f"✓ Loaded test accuracies from {csv_path}")
    print(f"✓ Extracted {len(conditions_data)} conditions with {EXPECTED_SAMPLES_PER_CONDITION} samples each")
    if skipped_conditions:
        print(f"  ⚠ Skipped {len(skipped_conditions)} conditions due to missing/invalid data")

    # Ensure we have at least some conditions
    if len(conditions_data) == 0:
        raise ValueError("No valid conditions found in experiment logs")

    return conditions_data


def extract_condition_data(df: pd.DataFrame, dataset: str, architecture: str) -> np.ndarray:
    """Extract 30 test accuracies for one condition.

    Args:
        df: Full experiment logs dataframe
        dataset: Dataset name (mnist or fashion_mnist)
        architecture: Architecture name (1layer or 2layer)

    Returns:
        Array of test accuracies (shape: (30,))

    Raises:
        ValueError: If not exactly 30 samples found or if data contains NaN/missing values
    """
    # Filter for condition
    mask = (df['dataset'] == dataset) & (df['architecture'] == architecture)
    filtered = df[mask]

    # Extract test_accuracy column
    test_accuracies = filtered['test_accuracy'].values

    # Validate sample count
    if len(test_accuracies) != EXPECTED_SAMPLES_PER_CONDITION:
        raise ValueError(
            f"Expected {EXPECTED_SAMPLES_PER_CONDITION} samples, got {len(test_accuracies)}"
        )

    # Check for NaN values (missing data)
    if np.any(np.isnan(test_accuracies)):
        nan_count = np.sum(np.isnan(test_accuracies))
        raise ValueError(f"Contains {nan_count} missing values")

    return test_accuracies


def validate_condition_data(data: Dict[str, np.ndarray], expected_samples: int = 30) -> None:
    """Validate data shape, check for NaN/Inf, verify range [0, 100].

    Args:
        data: Dictionary mapping condition names to test accuracy arrays
        expected_samples: Expected number of samples per condition

    Raises:
        ValueError: If validation fails
    """
    for condition_name, condition_data in data.items():
        # Check shape
        if condition_data.shape != (expected_samples,):
            raise ValueError(
                f"Invalid shape for {condition_name}: {condition_data.shape}, "
                f"expected ({expected_samples},)"
            )

        # Check for NaN/Inf
        if np.any(np.isnan(condition_data)):
            raise ValueError(f"NaN values found in {condition_name}")
        if np.any(np.isinf(condition_data)):
            raise ValueError(f"Inf values found in {condition_name}")

        # Check range [0, 100]
        if np.any(condition_data < ACCURACY_MIN) or np.any(condition_data > ACCURACY_MAX):
            raise ValueError(
                f"Values out of range [0, 100] in {condition_name}: "
                f"min={condition_data.min()}, max={condition_data.max()}"
            )

    print(f"✓ Data validation passed for all {len(data)} conditions")
