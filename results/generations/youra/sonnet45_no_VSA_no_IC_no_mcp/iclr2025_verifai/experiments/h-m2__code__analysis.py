"""Analysis functions for h-m2 experiments."""

from ast_validator import compute_latency_stats


def analyze_latency(timings: list) -> dict:
    """
    Analyze latency statistics and check gate.

    Args:
        timings: List of parse times in milliseconds

    Returns:
        Dictionary with stats and gate pass status
    """
    stats = compute_latency_stats(timings)
    gate_pass = stats['mean'] < 50 and stats['p95'] < 100
    return {'stats': stats, 'gate_pass': gate_pass}


def analyze_ranking(logs: list) -> dict:
    """
    Analyze validity proportion in beam outputs.

    Args:
        logs: Beam output logs

    Returns:
        Dictionary with validity proportion and gate pass status
    """
    valid_count = sum(1 for log in logs if log['validity'])
    total = len(logs)

    proportion = valid_count / total if total > 0 else 0.0
    return {'correct_proportion': proportion, 'gate_pass': proportion >= 0.6}


def compare_ablation(results: dict) -> dict:
    """
    Identify optimal alpha/beta weights.

    Args:
        results: Dictionary mapping (alpha, beta) to metrics

    Returns:
        Dictionary with optimal pair and metrics by pair
    """
    optimal = None
    best_correctness = 0.0

    for (alpha, beta), metrics in results.items():
        if metrics['ranking_correctness'] > best_correctness:
            best_correctness = metrics['ranking_correctness']
            optimal = (alpha, beta)

    return {'optimal_pair': optimal, 'metrics_by_pair': results}


def compare_baselines(
    greedy_errors: float,
    pure_beam_errors: float,
    combined_errors: float
) -> dict:
    """
    Compare baseline error rates.

    Args:
        greedy_errors: Greedy sampling error rate
        pure_beam_errors: Pure log-likelihood beam search error rate
        combined_errors: Combined scoring error rate

    Returns:
        Dictionary with improvements and gate pass status
    """
    improvement_vs_pure = pure_beam_errors - combined_errors
    gate_pass = combined_errors < greedy_errors

    return {
        'improvement_vs_pure': improvement_vs_pure,
        'gate_pass': gate_pass,
        'greedy_error_rate': greedy_errors,
        'pure_beam_error_rate': pure_beam_errors,
        'combined_error_rate': combined_errors
    }
