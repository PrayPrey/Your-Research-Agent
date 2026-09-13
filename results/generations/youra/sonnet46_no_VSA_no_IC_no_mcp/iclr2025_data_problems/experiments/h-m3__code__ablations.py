"""ablations.py — A-3: Four ablation studies on the correlation analysis."""
from typing import Optional
import numpy as np
try:
    from .correlation import CorrelationResult, pearson_spearman
    from .data_loader import BENCHMARKS, MODEL_SIZES, build_analysis_vectors
except ImportError:
    from correlation import CorrelationResult, pearson_spearman
    from data_loader import BENCHMARKS, MODEL_SIZES, build_analysis_vectors


def ablation_estimator_comparison(
    acc_diff: dict[str, dict[str, float]],
    cont_13gram: dict[str, float],
    mink_diff: Optional[dict[str, float]],
) -> dict:
    """Compare 13-gram overlap vs min-k% as contamination predictor."""
    cont_vec, diff_flat, _ = build_analysis_vectors(acc_diff, cont_13gram)
    result_13gram = pearson_spearman(cont_vec, diff_flat)

    if mink_diff is None:
        return {
            "13gram": result_13gram.to_dict(),
            "mink": None,
            "r_difference": None,
            "estimators_disagree": None,
            "note": "H-M2 min-k% results unavailable — skipped",
        }

    mink_vec = np.array([mink_diff[b] for b in BENCHMARKS])
    mink_repeated = np.tile(mink_vec, len(MODEL_SIZES))
    result_mink = pearson_spearman(mink_repeated, diff_flat)

    r_diff = abs(result_13gram.pearson_r - result_mink.pearson_r)
    return {
        "13gram": result_13gram.to_dict(),
        "mink": result_mink.to_dict(),
        "r_difference": float(r_diff),
        "estimators_disagree": bool(r_diff > 0.3),
    }


def ablation_aggregation_strategy(
    cont_vec: np.ndarray,
    diff_matrix: np.ndarray,
) -> dict:
    """Compare n=16 flattened vs n=4 benchmark-level aggregation."""
    cont_repeated = np.tile(cont_vec, len(MODEL_SIZES))  # (16,)
    diff_flat = diff_matrix.flatten()  # (16,)
    result_n16 = pearson_spearman(cont_repeated, diff_flat)

    diff_mean = diff_matrix.mean(axis=0)  # (4,)
    result_n4 = pearson_spearman(cont_vec, diff_mean)

    return {
        "n16": result_n16.to_dict(),
        "n4": result_n4.to_dict(),
        "note": "n=4 requires r>=0.95 for p<0.05; n=16 is the valid primary choice",
    }


def ablation_token_vs_step(
    acc_diff_token: dict[str, dict[str, float]],
    acc_diff_step: Optional[dict[str, dict[str, float]]],
    cont_vec: np.ndarray,
) -> dict:
    """Compare correlation under token-count vs step-count checkpoint matching."""
    cont_repeated = np.tile(cont_vec, len(MODEL_SIZES))
    cont_dict = dict(zip(BENCHMARKS, cont_vec.tolist()))
    _, diff_flat_token, _ = build_analysis_vectors(acc_diff_token, cont_dict)
    result_token = pearson_spearman(cont_repeated, diff_flat_token)

    if acc_diff_step is None:
        return {
            "token": result_token.to_dict(),
            "step": None,
            "note": "Step-matched results not available from H-E1",
        }

    _, diff_flat_step, _ = build_analysis_vectors(acc_diff_step, cont_dict)
    result_step = pearson_spearman(cont_repeated, diff_flat_step)
    return {"token": result_token.to_dict(), "step": result_step.to_dict()}


def ablation_per_model_size(
    acc_diff: dict[str, dict[str, float]],
    cont_vec: np.ndarray,
) -> dict[str, dict]:
    """Run Pearson separately for each model size (n=4 per size)."""
    results = {}
    for model_size in MODEL_SIZES:
        diff_vec = np.array([acc_diff[model_size][b] for b in BENCHMARKS])
        result = pearson_spearman(cont_vec, diff_vec)
        results[model_size] = result.to_dict()
    return results
