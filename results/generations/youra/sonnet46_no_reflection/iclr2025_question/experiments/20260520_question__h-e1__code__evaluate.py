import json
import logging
import os
import pickle
from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.metrics import roc_auc_score

from config import ExperimentConfig

logger = logging.getLogger(__name__)


def compute_auroc(
    uncertainty_scores: np.ndarray,
    correctness_labels: np.ndarray,
) -> float:
    """Compute AUROC via sklearn. Higher uncertainty -> lower correctness."""
    # Invert scores: higher uncertainty = predicts incorrectness = label 0
    return roc_auc_score(correctness_labels, -uncertainty_scores)


def bootstrap_auroc_ci(
    uncertainty_scores: np.ndarray,
    correctness_labels: np.ndarray,
    n_resamples: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """Percentile bootstrap CI for AUROC. Returns (mean_auroc, ci_low, ci_high)."""
    rng = np.random.default_rng(seed)
    Q = len(correctness_labels)
    bootstrap_aurocs = []
    for _ in range(n_resamples):
        idx = rng.integers(0, Q, size=Q)
        labels_b = correctness_labels[idx]
        scores_b = uncertainty_scores[idx]
        # Skip if only one class present
        if len(np.unique(labels_b)) < 2:
            continue
        try:
            auroc_b = roc_auc_score(labels_b, -scores_b)
            bootstrap_aurocs.append(auroc_b)
        except Exception:
            continue

    if not bootstrap_aurocs:
        auroc_point = compute_auroc(uncertainty_scores, correctness_labels)
        return auroc_point, auroc_point, auroc_point

    bootstrap_aurocs = np.array(bootstrap_aurocs)
    ci_low = float(np.percentile(bootstrap_aurocs, 100 * alpha / 2))
    ci_high = float(np.percentile(bootstrap_aurocs, 100 * (1 - alpha / 2)))
    mean_auroc = float(np.mean(bootstrap_aurocs))
    return mean_auroc, ci_low, ci_high


def _bootstrap_diff_ci(
    se_scores: np.ndarray,
    tp_scores: np.ndarray,
    labels: np.ndarray,
    n_resamples: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """Bootstrap CI for AUROC(SE) - AUROC(TP) difference."""
    rng = np.random.default_rng(seed)
    Q = len(labels)
    diff_samples = []
    for _ in range(n_resamples):
        idx = rng.integers(0, Q, size=Q)
        labs = labels[idx]
        if len(np.unique(labs)) < 2:
            continue
        try:
            se_a = roc_auc_score(labs, -se_scores[idx])
            tp_a = roc_auc_score(labs, -tp_scores[idx])
            diff_samples.append(se_a - tp_a)
        except Exception:
            continue
    if not diff_samples:
        return 0.0, -1.0, 1.0
    diff_arr = np.array(diff_samples)
    return (
        float(np.mean(diff_arr)),
        float(np.percentile(diff_arr, 100 * alpha / 2)),
        float(np.percentile(diff_arr, 100 * (1 - alpha / 2))),
    )


def run_gate_check(
    auroc_results: Dict[str, Any],
    uq_scores_all: Dict[str, Dict[str, Dict[str, np.ndarray]]],
    correctness_labels_all: Dict[str, np.ndarray],
    n_resamples: int = 1000,
) -> Tuple[bool, Dict[str, bool]]:
    """Check all 4 MUST_WORK gate conditions.

    Conditions:
      1. SE AUROC_8B_trivia > TP AUROC_8B_trivia AND diff CI excludes zero
      2. SE AUROC_70B_trivia > TP AUROC_70B_trivia AND diff CI excludes zero
      3. SE AUROC_8B_nq > TP AUROC_8B_nq AND diff CI excludes zero
      4. SE AUROC_70B_nq > TP AUROC_70B_nq AND diff CI excludes zero
    """
    model_keys = {"8b": "small", "70b": "large"}
    dataset_keys = {"trivia": "trivia_qa", "nq": "natural_questions"}
    condition_results = {}

    for scale_key, model_key in model_keys.items():
        for ds_key, ds_name in dataset_keys.items():
            cond_name = f"{scale_key}_{ds_key}"
            try:
                se_scores = uq_scores_all[model_key][ds_name]["semantic_entropy"]
                tp_scores = uq_scores_all[model_key][ds_name]["token_prob"]
                labels = correctness_labels_all[ds_name]

                mean_diff, ci_low, ci_high = _bootstrap_diff_ci(
                    se_scores, tp_scores, labels, n_resamples=n_resamples
                )
                condition_results[cond_name] = bool(mean_diff > 0 and ci_low > 0)
                logger.info(
                    f"Gate {cond_name}: diff={mean_diff:.4f} CI=[{ci_low:.4f}, {ci_high:.4f}] "
                    f"-> {'PASS' if condition_results[cond_name] else 'FAIL'}"
                )
            except KeyError as e:
                logger.warning(f"Gate check missing data for {cond_name}: {e}")
                condition_results[cond_name] = False

    gate_pass = all(condition_results.values())
    return gate_pass, condition_results


def evaluate_all(
    uq_scores: Dict[str, np.ndarray],
    correctness_labels: np.ndarray,
    cfg: ExperimentConfig,
    dataset_name: str,
    model_key: str,
) -> Dict[str, Any]:
    """Run bootstrap_auroc_ci for each method. Returns nested results dict."""
    results = {}
    for method, scores in uq_scores.items():
        # Skip NaN-only arrays (e.g., seps when no probe)
        valid = ~np.isnan(scores)
        if valid.sum() < 10:
            logger.warning(f"Skipping {method}: insufficient valid scores ({valid.sum()})")
            results[method] = {"auroc": None, "ci_low": None, "ci_high": None, "n_valid": int(valid.sum())}
            continue
        valid_scores = scores[valid]
        valid_labels = correctness_labels[valid]
        if len(np.unique(valid_labels)) < 2:
            logger.warning(f"Skipping {method}: only one class in labels")
            results[method] = {"auroc": None, "ci_low": None, "ci_high": None, "n_valid": int(valid.sum())}
            continue
        mean_auroc, ci_low, ci_high = bootstrap_auroc_ci(
            valid_scores,
            valid_labels,
            n_resamples=cfg.evaluation.bootstrap_resamples,
            alpha=cfg.evaluation.alpha,
        )
        results[method] = {
            "auroc": mean_auroc,
            "ci_low": ci_low,
            "ci_high": ci_high,
            "n_valid": int(valid.sum()),
        }
        logger.info(
            f"[{model_key}/{dataset_name}] {method}: AUROC={mean_auroc:.4f} "
            f"CI=[{ci_low:.4f}, {ci_high:.4f}]"
        )
    return results


def save_results(
    auroc_results: Dict[str, Any],
    uq_scores: Dict[str, np.ndarray],
    correctness_labels: np.ndarray,
    dataset_name: str,
    model_key: str,
    output_dir: str,
) -> None:
    """Save auroc_results.json, uncertainty_scores pickle, correctness_labels pickle."""
    os.makedirs(output_dir, exist_ok=True)

    # Save JSON
    json_path = os.path.join(output_dir, "auroc_results.json")
    # Load existing if present
    existing = {}
    if os.path.exists(json_path):
        with open(json_path) as f:
            existing = json.load(f)
    existing.setdefault(model_key, {})[dataset_name] = auroc_results
    with open(json_path, "w") as f:
        json.dump(existing, f, indent=2)

    # Save pickle files
    scores_path = os.path.join(output_dir, f"uncertainty_scores_{model_key}_{dataset_name}.pkl")
    with open(scores_path, "wb") as f:
        pickle.dump(uq_scores, f)

    labels_path = os.path.join(output_dir, f"correctness_labels_{dataset_name}.pkl")
    with open(labels_path, "wb") as f:
        pickle.dump(correctness_labels, f)

    logger.info(f"Results saved to {output_dir}")
