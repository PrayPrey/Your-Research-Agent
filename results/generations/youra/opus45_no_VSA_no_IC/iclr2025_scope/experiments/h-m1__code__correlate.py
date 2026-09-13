"""Correlation analysis for optimal rank vs model size."""
import numpy as np
from scipy.stats import pearsonr
from config import MODEL_PARAMS, RANKS


def find_optimal_rank(f1_scores: list[float], ranks: list[int] = RANKS) -> int:
    best_idx = int(np.argmax(f1_scores))
    return ranks[best_idx]


def compute_correlation(results: dict, model_params: dict = MODEL_PARAMS) -> dict:
    """Correlation between attention entropy at optimal rank and model size."""
    entropies_at_optimal = []
    sizes = []

    for size, data in results.items():
        f1_list = [data[r]["f1"] for r in RANKS]
        optimal_rank = find_optimal_rank(f1_list)
        optimal_entropy = data[optimal_rank]["entropy"]
        entropies_at_optimal.append(optimal_entropy)
        sizes.append(model_params[size])

    r, p = pearsonr(sizes, entropies_at_optimal)
    return {
        "pearson_r": float(r),
        "p_value": float(p),
        "pass": bool(r > 0.6 and p < 0.05),
        "entropies_at_optimal": entropies_at_optimal,
        "model_sizes": sizes,
    }
