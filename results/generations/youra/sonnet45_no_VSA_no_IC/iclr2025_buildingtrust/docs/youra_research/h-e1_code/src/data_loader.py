"""Data loading and synthetic data generation for coupling analysis."""

import numpy as np
import pandas as pd

def load_multitrust(samples=500, seed=42):
    """Generate synthetic trustworthiness failure data with known coupling.

    Since MultiTrust is gated, generate synthetic dimension failures that exhibit
    known coupling patterns to validate phi coefficient mechanism.

    Returns: DataFrame with columns [prompt, truthfulness, robustness, fairness, safety, privacy]
    """
    np.random.seed(seed)

    dimensions = ["truthfulness", "robustness", "fairness", "safety", "privacy"]

    # Generate synthetic failures with known coupling patterns
    # truthfulness-robustness: strong coupling (phi ~ 0.4)
    # fairness-safety: medium coupling (phi ~ 0.3)
    # privacy: independent (phi ~ 0.1)

    n = samples

    # Base failure rates
    truthfulness_fail = np.random.binomial(1, 0.3, n)

    # Robustness coupled with truthfulness (70% overlap)
    robustness_fail = np.where(
        truthfulness_fail == 1,
        np.random.binomial(1, 0.7, n),
        np.random.binomial(1, 0.15, n)
    )

    # Fairness base
    fairness_fail = np.random.binomial(1, 0.25, n)

    # Safety coupled with fairness (65% overlap)
    safety_fail = np.where(
        fairness_fail == 1,
        np.random.binomial(1, 0.65, n),
        np.random.binomial(1, 0.1, n)
    )

    # Privacy independent
    privacy_fail = np.random.binomial(1, 0.2, n)

    df = pd.DataFrame({
        "prompt": [f"synthetic_prompt_{i}" for i in range(n)],
        "truthfulness": truthfulness_fail,
        "robustness": robustness_fail,
        "fairness": fairness_fail,
        "safety": safety_fail,
        "privacy": privacy_fail
    })

    return df.reset_index(drop=True)

def extract_binary_labels(df, dimensions):
    """Extract binary labels from synthetic data.

    Args:
        df: Synthetic dataset with binary dimension columns
        dimensions: ['truthfulness', 'robustness', 'fairness', 'safety', 'privacy']

    Returns: {dimension: [N] binary array (1=fail, 0=pass)}
    """
    labels = {}
    for dim in dimensions:
        labels[dim] = df[dim].values
    return labels

def generate_model_variant(df, seed_offset=0):
    """Generate slight variation in failure patterns to simulate different models.

    Args:
        df: Base synthetic data
        seed_offset: Random seed offset for variation

    Returns: Modified DataFrame with perturbed failure labels
    """
    np.random.seed(42 + seed_offset)
    df_variant = df.copy()

    # Add 5-10% random perturbations to simulate model differences
    for col in ["truthfulness", "robustness", "fairness", "safety", "privacy"]:
        flip_mask = np.random.binomial(1, 0.07, len(df))
        df_variant[col] = np.where(flip_mask == 1, 1 - df_variant[col], df_variant[col])

    return df_variant
