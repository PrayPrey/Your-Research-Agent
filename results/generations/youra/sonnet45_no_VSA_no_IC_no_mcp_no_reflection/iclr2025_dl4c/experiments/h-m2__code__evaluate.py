"""Evaluation metrics for fix-impact comparison."""

from typing import List, Dict
from agent import FixResult


def measure_proportion_high_impact(
    fix_results: List[FixResult],
    threshold: int = 2
) -> float:
    """
    Calculate proportion of high-impact fixes.

    Args:
        fix_results: [FixResult]
        threshold: Minimum delta for high-impact

    Returns:
        proportion: float ∈ [0,1]
    """
    if len(fix_results) == 0:
        return 0.0

    high_impact_count = sum(
        1 for fr in fix_results
        if fr.delta_passing >= threshold
    )

    return high_impact_count / len(fix_results)


def compare_agents(
    baseline_results: List[List[FixResult]],
    proposed_results: List[List[FixResult]],
    threshold: int = 2
) -> Dict:
    """
    Compare baseline vs proposed agents.

    Args:
        baseline_results: [[FixResult]] per problem
        proposed_results: [[FixResult]] per problem
        threshold: High-impact threshold

    Returns:
        comparison: {
            "baseline_proportion": float,
            "proposed_proportion": float,
            "improvement": float,
            "gate_pass": bool
        }
    """
    # Flatten all fix results
    baseline_flat = [fr for problem_results in baseline_results for fr in problem_results]
    proposed_flat = [fr for problem_results in proposed_results for fr in problem_results]

    # Calculate proportions
    baseline_prop = measure_proportion_high_impact(baseline_flat, threshold)
    proposed_prop = measure_proportion_high_impact(proposed_flat, threshold)

    # Check gate (MUST_WORK: proposed > baseline)
    gate_pass = proposed_prop > baseline_prop

    return {
        "baseline_proportion": baseline_prop,
        "proposed_proportion": proposed_prop,
        "improvement": proposed_prop - baseline_prop,
        "gate_pass": gate_pass,
        "baseline_count": len(baseline_flat),
        "proposed_count": len(proposed_flat),
    }
