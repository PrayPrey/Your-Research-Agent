"""Statistical analysis for H-M3 convergence comparison."""

import numpy as np
from typing import List, Dict, Tuple, Any


def steps_to_target_ratio(fgo_steps: int, standard_steps: int) -> float:
    """FGO/Standard steps ratio. Success if < 0.6."""
    if standard_steps == 0:
        return float('inf')
    return fgo_steps / standard_steps


def learning_curve_slope(curve: List[Tuple[int, float]]) -> float:
    """Average pass@1 improvement per eval interval."""
    if len(curve) < 2:
        return 0.0
    deltas = [curve[i+1][1] - curve[i][1] for i in range(len(curve) - 1)]
    return np.mean(deltas)


def sample_efficiency(curve: List[Tuple[int, float]], batch_size: int = 16) -> float:
    """Pass@1 gain per 1000 samples."""
    if len(curve) < 2:
        return 0.0
    total_delta = curve[-1][1] - curve[0][1]
    total_steps = curve[-1][0] - curve[0][0]
    total_samples = total_steps * batch_size
    if total_samples == 0:
        return 0.0
    return total_delta / (total_samples / 1000)


def aggregate_seeds(results: List[Dict]) -> Dict[str, Any]:
    """Aggregate metrics across multiple seed runs."""
    if not results:
        return {}

    steps = [r["steps_to_target"] for r in results]
    pass1s = [r["final_pass1"] for r in results]

    return {
        "steps_to_target_mean": np.mean(steps),
        "steps_to_target_std": np.std(steps),
        "final_pass1_mean": np.mean(pass1s),
        "final_pass1_std": np.std(pass1s),
        "n_seeds": len(results),
    }


def compute_gate_verdict(
    fgo_results: Dict,
    standard_results: Dict,
    ratio_threshold: float = 0.6
) -> Dict[str, Any]:
    """Compute SHOULD_WORK gate verdict."""
    ratio = steps_to_target_ratio(
        int(fgo_results["steps_to_target_mean"]),
        int(standard_results["steps_to_target_mean"])
    )

    fgo_better_steps = ratio < ratio_threshold
    fgo_better_pass1 = fgo_results["final_pass1_mean"] > standard_results["final_pass1_mean"]

    gate_passed = fgo_better_steps or fgo_better_pass1

    return {
        "gate_type": "SHOULD_WORK",
        "passed": gate_passed,
        "steps_ratio": ratio,
        "steps_threshold": ratio_threshold,
        "fgo_steps_mean": fgo_results["steps_to_target_mean"],
        "standard_steps_mean": standard_results["steps_to_target_mean"],
        "fgo_pass1_mean": fgo_results["final_pass1_mean"],
        "standard_pass1_mean": standard_results["final_pass1_mean"],
        "criteria": {
            "faster_convergence": fgo_better_steps,
            "higher_final_pass1": fgo_better_pass1,
        }
    }
