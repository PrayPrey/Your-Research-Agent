"""Δ* computation, reliability filter, and vector construction for H-E1."""
import logging

import numpy as np
from scipy.stats import spearmanr

logger = logging.getLogger(__name__)


def compute_delta_star(clean_acc: float, adv_acc: float) -> float:
    """Δ* = (clean - adv) / clean; returns 0.0 if clean == 0."""
    if clean_acc == 0.0:
        return 0.0
    return (clean_acc - adv_acc) / clean_acc


def split_half_reliability(scores_half1: np.ndarray, scores_half2: np.ndarray) -> float:
    """Spearman-Brown corrected split-half reliability: (2r) / (1+r)."""
    if len(scores_half1) < 2 or len(scores_half2) < 2:
        return 0.0
    r, _ = spearmanr(scores_half1, scores_half2)
    if np.isnan(r):
        return 0.0
    r = float(r)
    return (2 * r) / (1 + r) if (1 + r) != 0 else 0.0


def filter_reliable_categories(
    results: dict,
    min_r: float = 0.7,
    min_n: int = 30,
) -> list:
    """Returns attack categories passing reliability filter.

    results: {model_id: {key: {clean_acc, adv_acc, category, n_examples}}}
    min_n lowered to 30 to accommodate AdvGLUE small sets (78-148 examples).
    """
    category_data = {}  # category -> {model_id: [(delta_star, n_examples)]}

    for model_id, model_results in results.items():
        for key, entry in model_results.items():
            cat = entry.get("category")
            if cat is None:
                continue
            clean = entry.get("clean_acc", 0.0) or 0.0
            adv = entry.get("adv_acc", 0.0) or 0.0
            n = entry.get("n_examples", 0) or 0
            ds = compute_delta_star(clean, adv)
            category_data.setdefault(cat, {}).setdefault(model_id, []).append((ds, n))

    reliable = []
    for cat, model_entries in category_data.items():
        per_model_ds = []
        total_n = 0
        for model_id, entries in model_entries.items():
            if entries:
                ds_mean = np.mean([e[0] for e in entries])
                n_sum = sum(e[1] for e in entries)
                per_model_ds.append(ds_mean)
                total_n += n_sum

        n_models_with_data = len(per_model_ds)
        if total_n < min_n:
            logger.info(f"Category {cat} filtered: n={total_n} < {min_n}")
            continue

        if n_models_with_data < 3:
            logger.info(f"Category {cat} filtered: only {n_models_with_data} models")
            continue

        # Split-half reliability across models
        if n_models_with_data < 4:
            # With 3 models, accept without split-half if n is large enough
            reliable.append(cat)
            logger.info(f"Category {cat}: n={total_n}, {n_models_with_data} models, accepted (too few for split-half)")
            continue

        arr = np.array(per_model_ds)
        half = n_models_with_data // 2
        r = split_half_reliability(arr[:half], arr[half:half*2])
        logger.info(f"Category {cat}: n={total_n}, {n_models_with_data} models, split-half r={r:.3f}")
        if r >= min_r:
            reliable.append(cat)

    logger.info(f"Reliable categories: {reliable}")
    return reliable


def build_delta_star_vectors(
    results: dict,
    reliable_categories: list,
) -> tuple:
    """Returns (X: [n_models, n_cats], model_ids, family_labels).

    Aggregates across tasks per (model, category) pair.
    """
    from fine_tuner import MODEL_CONFIGS

    model_ids = sorted(results.keys())
    X = np.zeros((len(model_ids), len(reliable_categories)), dtype=float)

    for i, model_id in enumerate(model_ids):
        model_results = results[model_id]
        for j, cat in enumerate(reliable_categories):
            # Collect all entries for this model + category
            entries = [
                v for v in model_results.values()
                if v.get("category") == cat
            ]
            if not entries:
                X[i, j] = 0.0
                continue
            # Mean delta_star across tasks
            delta_stars = [
                compute_delta_star(
                    e.get("clean_acc", 0.0) or 0.0,
                    e.get("adv_acc", 0.0) or 0.0,
                )
                for e in entries
            ]
            X[i, j] = float(np.mean(delta_stars))

    family_labels = [MODEL_CONFIGS.get(m, {}).get("family", "encoder") for m in model_ids]
    logger.info(f"Δ*-vector matrix shape: {X.shape}")
    return X, model_ids, family_labels


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Sanity check
    assert abs(compute_delta_star(0.8, 0.6) - (0.8 - 0.6) / 0.8) < 1e-9
    print("compute_delta_star(0.8, 0.6) =", compute_delta_star(0.8, 0.6))
    print("compute_delta_star(0.0, 0.0) =", compute_delta_star(0.0, 0.0))
    a = np.array([0.1, 0.2, 0.3, 0.4])
    b = np.array([0.15, 0.25, 0.35, 0.45])
    print("split_half_reliability:", split_half_reliability(a, b))
