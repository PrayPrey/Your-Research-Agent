"""Statistical aggregation of alpha results."""
import numpy as np
from collections import defaultdict
from config import CONFIG


def aggregate_statistics(results: list[dict]) -> dict:
    """Aggregate alpha statistics from measurement results."""
    if not results:
        return {"error": "No results to aggregate"}

    all_alphas = [r["alpha_mean"] for r in results]

    mean_alpha = float(np.mean(all_alphas))
    median_alpha = float(np.median(all_alphas))
    sigma_alpha = float(np.std(all_alphas))
    alpha_range = [float(np.min(all_alphas)), float(np.max(all_alphas))]

    by_family = defaultdict(list)
    for r in results:
        by_family[r["family"]].append(r["alpha_mean"])

    family_stats = {}
    for family, alphas in by_family.items():
        family_stats[family] = {
            "mean_alpha": float(np.mean(alphas)),
            "sigma_alpha": float(np.std(alphas)),
            "n": len(alphas)
        }

    return {
        "mean_alpha": mean_alpha,
        "median_alpha": median_alpha,
        "sigma_alpha": sigma_alpha,
        "range": alpha_range,
        "n_models_processed": len(results),
        "gate_passed": sigma_alpha < CONFIG.sigma_gate_threshold,
        "by_family": family_stats
    }


if __name__ == "__main__":
    test_results = [
        {"model_id": "a", "family": "google", "alpha_mean": 2.5},
        {"model_id": "b", "family": "google", "alpha_mean": 2.7},
        {"model_id": "c", "family": "facebook", "alpha_mean": 2.3},
    ]
    stats = aggregate_statistics(test_results)
    print(f"sigma_alpha: {stats['sigma_alpha']:.4f}")
    print(f"gate_passed: {stats['gate_passed']}")
