"""
Base-rate calculation and majority vote utilities.
"""
from typing import Tuple
import pandas as pd
import numpy as np
from statsmodels.stats.proportion import proportion_confint


def majority_vote(
    annotations: pd.DataFrame,
    n_annotators: int = 3
) -> np.ndarray:
    """
    Determine final labels using majority vote from 3 annotators.

    Args:
        annotations: DataFrame with columns [sample_id, annotator_id, judgment]
        n_annotators: Number of annotators (default 3)

    Returns:
        np.ndarray: Binary array (1=violation, 0=marginal)
        Shape: (500,)
    """
    # Pivot to rating matrix
    rating_matrix = annotations.pivot(
        index="sample_id",
        columns="annotator_id",
        values="judgment"
    )

    # Convert boolean to int
    rating_matrix = rating_matrix.astype(int)

    # Sum votes per sample (0-3 range)
    vote_sums = rating_matrix.sum(axis=1)

    # Majority rule: ≥2 votes for violation → 1
    final_labels = (vote_sums >= 2).astype(int).values

    return final_labels


def calculate_base_rate(
    final_labels: np.ndarray,
    confidence_level: float = 0.95
) -> Tuple[float, Tuple[float, float]]:
    """
    Calculate base-rate of genuine violations with confidence interval.

    Args:
        final_labels: Binary array (1=violation, 0=marginal) from majority vote
        confidence_level: CI confidence level (default 0.95)

    Returns:
        Tuple[float, Tuple[float, float]]:
            - Base-rate p (proportion of violations)
            - 95% confidence interval (lower, upper)

    Shape:
        - Input: (500,) binary array
        - Output: scalar + (lower, upper) tuple
    """
    n = len(final_labels)
    k = np.sum(final_labels)  # Count violations
    p = k / n  # Base-rate

    # Wilson score interval for binomial proportion
    ci_lower, ci_upper = proportion_confint(
        count=k,
        nobs=n,
        alpha=1 - confidence_level,
        method='wilson'
    )

    return p, (ci_lower, ci_upper)
