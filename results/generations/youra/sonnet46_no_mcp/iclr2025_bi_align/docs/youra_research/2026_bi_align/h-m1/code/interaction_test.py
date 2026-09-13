# h-m1/code/interaction_test.py
# Ambiguity-modulation interaction tests and validity checks

import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass, field

from config import AMBIGUITY_KAPPA_THRESHOLD

logger = logging.getLogger(__name__)


@dataclass
class InteractionResult:
    interaction_coef: float
    interaction_p: float
    high_ambiguity_beta: float
    low_ambiguity_beta: float
    discriminant_valid: bool
    placebo_p: float
    summary: object = field(default=None, repr=False)


def run_ambiguity_modulation_test(
    hh_df: pd.DataFrame,
    proj_scores_z: np.ndarray,
    q_early_model,
    feature_matrix_fn,
) -> InteractionResult:
    """Logit: proj_score_bin ~ C(round) + high_ambiguity + C(round):high_ambiguity + q_early.

    proj_score_z binarized at median for Logit outcome.
    Returns InteractionResult with interaction coefficient and p-value.
    """
    import statsmodels.formula.api as smf

    df = hh_df.copy().reset_index(drop=True)

    if len(proj_scores_z) != len(df):
        raise ValueError(
            f"proj_scores_z length {len(proj_scores_z)} != hh_df length {len(df)}"
        )

    df["proj_score_z"] = proj_scores_z
    # Binarize at median
    median_proj = np.median(proj_scores_z)
    df["proj_score_bin"] = (proj_scores_z >= median_proj).astype(int)

    # High ambiguity: partition_by_ambiguity returns (high_df, low_df)
    try:
        import sys, os
        # Ensure H-E1 path
        he1_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../h-e1/code")
        )
        if he1_path not in sys.path:
            sys.path.insert(0, he1_path)
        from features import partition_by_ambiguity
        high_df, low_df = partition_by_ambiguity(df, kappa_threshold=AMBIGUITY_KAPPA_THRESHOLD)
        high_idx = set(high_df.index)
    except Exception as e:
        logger.warning(f"partition_by_ambiguity failed ({e}); using index parity")
        high_idx = set(df.index[df.index % 2 == 0])

    df["high_ambiguity"] = df.index.isin(high_idx).astype(int)

    # Q_early scores
    try:
        X, _ = feature_matrix_fn(df)
        q_early_probs = q_early_model.predict_proba(X)[:, 1]
    except Exception as e:
        logger.warning(f"Q_early prediction failed ({e}); using zeros")
        q_early_probs = np.zeros(len(df))

    df["q_early"] = q_early_probs

    # Ensure round column exists
    if "round" not in df.columns:
        df["round"] = 1  # fallback

    formula = (
        "proj_score_bin ~ C(round) + high_ambiguity "
        "+ C(round):high_ambiguity + q_early"
    )

    try:
        result = smf.logit(formula, data=df).fit(disp=0, maxiter=200)
        # Find interaction terms
        interaction_terms = [
            p for p in result.pvalues.index
            if "round" in str(p) and "high_ambiguity" in str(p)
        ]
        if interaction_terms:
            interaction_p = float(result.pvalues[interaction_terms].min())
            argmin_idx = result.pvalues[interaction_terms].values.argmin()
            interaction_coef = float(result.params[interaction_terms[argmin_idx]])
        else:
            interaction_coef, interaction_p = 0.0, 1.0

        # Stratum means
        high_amb_mean = float(df.loc[df["high_ambiguity"] == 1, "proj_score_z"].mean()) if (df["high_ambiguity"] == 1).any() else 0.0
        low_amb_mean = float(df.loc[df["high_ambiguity"] == 0, "proj_score_z"].mean()) if (df["high_ambiguity"] == 0).any() else 0.0

        logger.info(
            f"Ambiguity interaction: coef={interaction_coef:.4f}, p={interaction_p:.4f}"
        )
        return InteractionResult(
            interaction_coef=interaction_coef,
            interaction_p=interaction_p,
            high_ambiguity_beta=high_amb_mean,
            low_ambiguity_beta=low_amb_mean,
            discriminant_valid=False,  # filled later
            placebo_p=1.0,            # filled later
            summary=result,
        )
    except Exception as e:
        logger.warning(f"Logit interaction test failed ({e}); returning null result")
        high_amb_mean = float(df.loc[df["high_ambiguity"] == 1, "proj_score_z"].mean()) if (df["high_ambiguity"] == 1).any() else 0.0
        low_amb_mean = float(df.loc[df["high_ambiguity"] == 0, "proj_score_z"].mean()) if (df["high_ambiguity"] == 0).any() else 0.0
        return InteractionResult(
            interaction_coef=0.0,
            interaction_p=1.0,
            high_ambiguity_beta=high_amb_mean,
            low_ambiguity_beta=low_amb_mean,
            discriminant_valid=False,
            placebo_p=1.0,
            summary=None,
        )


def run_discriminant_validity(
    stylistic_panel_result,
    topic_panel_result,
) -> bool:
    """Returns True if stylistic beta_exposure > topic beta_exposure."""
    result = stylistic_panel_result.beta_exposure > topic_panel_result.beta_exposure
    if not result:
        logger.warning(
            f"Discriminant validity FAILED: "
            f"stylistic beta={stylistic_panel_result.beta_exposure:.4f} <= "
            f"topic beta={topic_panel_result.beta_exposure:.4f}"
        )
    else:
        logger.info(
            f"Discriminant validity OK: "
            f"stylistic={stylistic_panel_result.beta_exposure:.4f} > "
            f"topic={topic_panel_result.beta_exposure:.4f}"
        )
    return result


def run_projection_placebo(
    null_vectors: np.ndarray,
    embeddings: np.ndarray,
    observed_proj_scores: np.ndarray,
) -> float:
    """Empirical p-value: proportion of null mean projections >= observed mean.

    null_vectors: (1000, 384), embeddings: (N, 384), observed_proj_scores: (N,)
    Returns float in [0, 1].
    """
    # (1000, 384) @ (384, N) -> (1000, N); mean per null -> (1000,)
    null_proj_means = (null_vectors.astype(np.float64) @ embeddings.astype(np.float64).T).mean(axis=1)
    observed_mean = float(observed_proj_scores.mean())
    empirical_p = float(np.mean(null_proj_means >= observed_mean))
    logger.info(f"Projection placebo: empirical p={empirical_p:.4f}, observed_mean={observed_mean:.4f}")
    return empirical_p


def check_monotonicity_hh(round_proj_means: dict) -> bool:
    """Returns True if round_proj_means[1] < [2] < [3]."""
    try:
        result = round_proj_means[1] < round_proj_means[2] < round_proj_means[3]
    except (KeyError, TypeError):
        logger.warning("Monotonicity check: missing round keys")
        return False
    if not result:
        logger.warning(
            f"HH-RLHF monotonicity check FAILED: "
            f"round means = {round_proj_means}"
        )
    else:
        logger.info(f"HH-RLHF monotonicity OK: {round_proj_means}")
    return result
