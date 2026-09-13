"""Analysis module: aggregate results, check non-monotonicity."""
import json
import numpy as np
from typing import Dict, List, Tuple
from config import DEDUP_LEVELS

def load_sweep_results(results_path: str = "./results/sweep_results.json") -> Dict:
    """Load sweep results from JSON."""
    with open(results_path) as f:
        return json.load(f)

def aggregate_results(results: Dict) -> Dict[str, Dict]:
    """Aggregate results across seeds for each level."""
    aggregated = {}
    tasks = ["hellaswag", "arc_easy", "piqa", "winogrande"]
    levels_order = [cfg.level for cfg in DEDUP_LEVELS]

    for level in levels_order:
        if level not in results:
            continue

        seed_data = results[level]
        task_scores = {t: [] for t in tasks}
        losses = []

        for seed, data in seed_data.items():
            scores = data.get("scores", {})
            for t in tasks:
                if t in scores:
                    task_scores[t].append(scores[t])
            if data.get("final_loss") is not None:
                losses.append(data["final_loss"])

        aggregated[level] = {
            "mean_scores": {t: np.mean(v) if v else 0.0 for t, v in task_scores.items()},
            "std_scores": {t: np.std(v) if len(v) > 1 else 0.0 for t, v in task_scores.items()},
            "ensemble_mean": np.mean([np.mean(v) for v in task_scores.values() if v]),
            "ensemble_std": np.std([np.mean(v) for v in task_scores.values() if v]) if len(task_scores) > 1 else 0.0,
            "mean_loss": np.mean(losses) if losses else None,
            "n_seeds": len(seed_data)
        }

    return aggregated

def check_non_monotonicity(aggregated: Dict) -> Tuple[bool, Dict]:
    """Check if intermediate levels outperform strictest."""
    levels_order = [cfg.level for cfg in DEDUP_LEVELS]
    ensemble_scores = {}

    for level in levels_order:
        if level in aggregated:
            ensemble_scores[level] = aggregated[level]["ensemble_mean"]

    if len(ensemble_scores) < 2:
        return False, {"reason": "insufficient data"}

    strictest = "exact_plus_fuzzy"
    if strictest not in ensemble_scores:
        strictest = levels_order[-1]

    strictest_score = ensemble_scores.get(strictest, 0.0)

    # Find best intermediate level (not "none" or strictest)
    intermediate_levels = ["fuzzy_0.7", "fuzzy_0.85", "exact"]
    intermediate_scores = {l: ensemble_scores.get(l, 0.0) for l in intermediate_levels if l in ensemble_scores}

    if not intermediate_scores:
        return False, {"reason": "no intermediate levels available"}

    best_intermediate = max(intermediate_scores.items(), key=lambda x: x[1])
    best_level, best_score = best_intermediate

    non_monotonic = best_score > strictest_score

    return non_monotonic, {
        "strictest_level": strictest,
        "strictest_score": strictest_score,
        "best_intermediate_level": best_level,
        "best_intermediate_score": best_score,
        "delta": best_score - strictest_score,
        "non_monotonic": non_monotonic
    }

def compute_effect_size(aggregated: Dict, level_a: str, level_b: str) -> float:
    """Compute effect size (difference) between two levels."""
    if level_a not in aggregated or level_b not in aggregated:
        return 0.0

    score_a = aggregated[level_a]["ensemble_mean"]
    score_b = aggregated[level_b]["ensemble_mean"]
    return score_a - score_b

def generate_analysis_summary(results: Dict) -> Dict:
    """Generate complete analysis summary."""
    aggregated = aggregate_results(results)
    non_monotonic, details = check_non_monotonicity(aggregated)

    # Effect sizes
    effect_sizes = {}
    levels = [cfg.level for cfg in DEDUP_LEVELS]
    for i, level_a in enumerate(levels):
        for level_b in levels[i+1:]:
            key = f"{level_a}_vs_{level_b}"
            effect_sizes[key] = compute_effect_size(aggregated, level_a, level_b)

    return {
        "aggregated": aggregated,
        "non_monotonicity": details,
        "hypothesis_supported": non_monotonic and details.get("delta", 0) > 0.005,  # >0.5% threshold
        "effect_sizes": effect_sizes
    }

def print_analysis(analysis: Dict):
    """Print analysis summary."""
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)

    print("\nPer-level ensemble scores (mean ± std):")
    for level, data in analysis["aggregated"].items():
        print(f"  {level}: {data['ensemble_mean']:.4f} ± {data['ensemble_std']:.4f} (n={data['n_seeds']})")

    nm = analysis["non_monotonicity"]
    print(f"\nNon-monotonicity check:")
    print(f"  Strictest ({nm['strictest_level']}): {nm['strictest_score']:.4f}")
    print(f"  Best intermediate ({nm['best_intermediate_level']}): {nm['best_intermediate_score']:.4f}")
    print(f"  Delta: {nm['delta']:.4f}")
    print(f"  Non-monotonic: {nm['non_monotonic']}")

    print(f"\nHypothesis supported: {analysis['hypothesis_supported']}")
