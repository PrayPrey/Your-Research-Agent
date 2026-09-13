"""
Inter-annotator agreement calculation using Cohen's kappa.
"""
from typing import Tuple
import pandas as pd
import numpy as np
from itertools import combinations


def compute_cohens_kappa(
    annotations: pd.DataFrame,
    n_annotators: int = 3
) -> Tuple[float, pd.DataFrame]:
    """
    Calculate Cohen's kappa for multi-rater agreement.

    Args:
        annotations: DataFrame with columns [sample_id, annotator_id, judgment]
        n_annotators: Number of annotators (default 3)

    Returns:
        Tuple[float, pd.DataFrame]:
            - Overall multi-rater kappa (float)
            - Pairwise kappa matrix (3×3 DataFrame)

    Shape:
        - Input: (1500, 3)  [500 samples × 3 annotators]
        - Output: scalar + (3, 3) matrix
    """
    # Step 1: Pivot to rating matrix
    rating_matrix = annotations.pivot(
        index="sample_id",
        columns="annotator_id",
        values="judgment"
    )

    # Convert boolean to int for calculation
    rating_matrix = rating_matrix.astype(int)

    # Step 2: Pairwise kappa
    annotator_ids = sorted(rating_matrix.columns)
    pairwise_kappas = pd.DataFrame(
        index=annotator_ids,
        columns=annotator_ids,
        dtype=float
    )

    # Set diagonal to 1.0 (perfect self-agreement)
    for annotator in annotator_ids:
        pairwise_kappas.loc[annotator, annotator] = 1.0

    # Compute pairwise kappas
    kappa_values = []
    for i, j in combinations(annotator_ids, 2):
        rater1 = rating_matrix[i].values
        rater2 = rating_matrix[j].values

        kappa = cohen_kappa_score(rater1, rater2)
        pairwise_kappas.loc[i, j] = kappa
        pairwise_kappas.loc[j, i] = kappa
        kappa_values.append(kappa)

    # Step 3: Overall kappa (average of pairwise)
    overall_kappa = np.mean(kappa_values)

    return overall_kappa, pairwise_kappas


def cohen_kappa_score(rater1: np.ndarray, rater2: np.ndarray) -> float:
    """
    Calculate Cohen's kappa between two raters.

    Args:
        rater1: Binary ratings from rater 1
        rater2: Binary ratings from rater 2

    Returns:
        Cohen's kappa coefficient
    """
    # Observed agreement
    p_o = np.mean(rater1 == rater2)

    # Expected agreement by chance
    p1_yes = np.mean(rater1 == 1)
    p1_no = np.mean(rater1 == 0)
    p2_yes = np.mean(rater2 == 1)
    p2_no = np.mean(rater2 == 0)

    p_e = (p1_yes * p2_yes) + (p1_no * p2_no)

    # Cohen's kappa
    if p_e == 1.0:
        return 1.0  # Perfect agreement

    kappa = (p_o - p_e) / (1 - p_e)
    return kappa
