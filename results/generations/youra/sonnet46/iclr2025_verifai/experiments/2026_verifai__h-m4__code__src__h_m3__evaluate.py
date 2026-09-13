"""evaluate.py — gate metrics, secondary statistics, verified results builder."""
from __future__ import annotations

import logging

import numpy as np
from scipy.stats import pointbiserialr

from h_m3.config import (
    STD_GATE_THRESHOLD,
    VERIFIED_RESULTS_SCHEMA_VERSION,
    MetricsConfig,
    MODEL_SHORT_NAMES,
)

logger = logging.getLogger(__name__)


def compute_gate_metrics(
    confidence_scores_by_model: dict[str, list[float]],
) -> dict[str, dict]:
    """Compute std(c) and mean(c) per model.

    Returns:
        {model_short: {std_c, mean_c, n_pairs, gate_pass}}
    """
    gate_metrics: dict[str, dict] = {}
    for model_short, scores in confidence_scores_by_model.items():
        if not scores:
            gate_metrics[model_short] = {
                "std_c": 0.0,
                "mean_c": 0.0,
                "n_pairs": 0,
                "gate_pass": False,
            }
            continue
        std_c = float(np.std(scores))
        mean_c = float(np.mean(scores))
        gate_pass = std_c > STD_GATE_THRESHOLD
        gate_metrics[model_short] = {
            "std_c": std_c,
            "mean_c": mean_c,
            "n_pairs": len(scores),
            "gate_pass": gate_pass,
        }
        logger.info(
            f"{model_short}: std(c)={std_c:.4f}, mean(c)={mean_c:.4f}, "
            f"n={len(scores)}, gate_pass={gate_pass}"
        )
    return gate_metrics


def evaluate_gate(
    gate_metrics: dict[str, dict],
    threshold: float = STD_GATE_THRESHOLD,
) -> tuple[bool, dict]:
    """MUST_WORK gate: std(c) > threshold for ALL 3 models.

    Returns:
        (gate_pass: bool, detail: dict)
    """
    gate_pass = all(v["gate_pass"] for v in gate_metrics.values())
    passing_models = [m for m, v in gate_metrics.items() if v["gate_pass"]]
    failing_models = [m for m, v in gate_metrics.items() if not v["gate_pass"]]

    detail = {
        "threshold": threshold,
        "models_passing": len(passing_models),
        "models_total": len(gate_metrics),
        "passing_models": passing_models,
        "failing_models": failing_models,
        "gate_pass": gate_pass,
    }
    logger.info(
        f"Gate evaluation: PASS={gate_pass} "
        f"({len(passing_models)}/{len(gate_metrics)} models passing)"
    )
    return gate_pass, detail


def compute_secondary_metrics(
    confidence_scores_by_model: dict[str, list[float]],
    correctness_by_model: dict[str, list[int]],
    tiers_by_model: dict[str, list[str]],
) -> dict[str, dict]:
    """Compute min/max(c), 20-bin histogram, tier-stratified mean/std, point-biserial correlation.

    Returns:
        {model_short: {min_c, max_c, histogram, tier_stats, correlation, p_value}}
    """
    cfg = MetricsConfig()
    secondary: dict[str, dict] = {}

    for model_short, scores in confidence_scores_by_model.items():
        if not scores:
            secondary[model_short] = {}
            continue

        scores_arr = np.array(scores)
        correctness_arr = np.array(correctness_by_model.get(model_short, [0] * len(scores)))
        tiers = tiers_by_model.get(model_short, ["unknown"] * len(scores))

        min_c = float(np.min(scores_arr))
        max_c = float(np.max(scores_arr))

        hist, edges = np.histogram(scores_arr, bins=cfg.histogram_bins, range=(0, 1))

        # Tier-stratified stats
        hard_scores = [s for s, t in zip(scores, tiers) if t == "hard"]
        easy_scores = [s for s, t in zip(scores, tiers) if t == "easy"]
        tier_stats = {
            "hard": {
                "mean_c": float(np.mean(hard_scores)) if hard_scores else None,
                "std_c": float(np.std(hard_scores)) if hard_scores else None,
                "n": len(hard_scores),
            },
            "easy": {
                "mean_c": float(np.mean(easy_scores)) if easy_scores else None,
                "std_c": float(np.std(easy_scores)) if easy_scores else None,
                "n": len(easy_scores),
            },
        }

        # Point-biserial correlation
        corr, pval = None, None
        if len(scores) > 2 and len(set(correctness_arr)) > 1:
            try:
                corr_result = pointbiserialr(correctness_arr, scores_arr)
                corr = float(corr_result.correlation)
                pval = float(corr_result.pvalue)
            except Exception as e:
                logger.warning(f"Point-biserial correlation failed for {model_short}: {e}")

        secondary[model_short] = {
            "min_c": min_c,
            "max_c": max_c,
            "histogram": hist.tolist(),
            "histogram_edges": edges.tolist(),
            "tier_stats": tier_stats,
            "correlation": corr,
            "p_value": pval,
        }

    return secondary


def build_verified_results(
    gate_metrics: dict[str, dict],
    gate_pass: bool,
    gate_detail: dict,
    secondary_metrics: dict,
) -> dict:
    """Assemble ptrue_hm3_verified.json payload (FR-10.1 schema)."""
    models_data: dict[str, dict] = {}
    for model_short, metrics in gate_metrics.items():
        models_data[model_short] = {
            "std_c": metrics["std_c"],
            "mean_c": metrics["mean_c"],
            "n_pairs": metrics["n_pairs"],
            "gate_pass": metrics["gate_pass"],
        }

    return {
        "schema_version": VERIFIED_RESULTS_SCHEMA_VERSION,
        "hypothesis_id": "h-m3",
        "gate": {
            "type": "MUST_WORK",
            "condition": "std(c) > 0.05 for ALL 3 models",
            "satisfied": gate_pass,
            "detail": gate_detail,
        },
        "models": models_data,
        "secondary_metrics": secondary_metrics,
    }
