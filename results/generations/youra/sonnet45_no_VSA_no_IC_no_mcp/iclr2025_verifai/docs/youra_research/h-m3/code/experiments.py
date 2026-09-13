"""Experiment runners for invalid beam pruning tracking."""

from beam_search_tracked import run_beam_search_with_tracking


def experiment_a_tracking(
    model,
    tokenizer,
    dataset: list[dict],
    k: int = 5,
    alpha: float = 0.7,
    beta: float = 0.3
) -> dict:
    """Track invalid proportion across full HumanEval-164."""
    results = []

    for problem in dataset:
        outputs, tracking_data = run_beam_search_with_tracking(
            model, tokenizer, problem['prompt'], k, alpha, beta, max_tokens=512
        )

        final_valid_count = sum(tracking_data['final_validity'])
        results.append({
            'problem_id': problem['task_id'],
            'reduction_rate': tracking_data['reduction_rate'],
            'final_valid_count': final_valid_count,
            'temporal_log': tracking_data['temporal_log']
        })

    return {'experiments': results}


def experiment_b_final_validity(tracking_results: dict) -> dict:
    """Analyze final beam validity distribution."""
    import numpy as np

    experiments = tracking_results['experiments']
    k = 5

    valid_proportions = [e['final_valid_count'] / k for e in experiments]
    problems_3plus = sum(1 for e in experiments if e['final_valid_count'] >= 3)

    dist = [0] * 6
    for e in experiments:
        count = e['final_valid_count']
        dist[count] += 1

    return {
        'mean_valid_proportion': float(np.mean(valid_proportions)),
        'problems_with_3plus_valid': problems_3plus,
        'problems_with_3plus_valid_pct': problems_3plus / len(experiments),
        'valid_count_distribution': dist
    }


def experiment_c_temporal_dynamics(tracking_results: dict) -> dict:
    """Compute phase-wise statistics."""
    return {
        'note': 'Per-step tracking unavailable with HuggingFace generate()',
        'alternative': 'Use final validity distribution as proxy'
    }


def baseline_comparison(
    model,
    tokenizer,
    dataset: list[dict],
    k: int = 5
) -> dict:
    """Run pure log-likelihood (alpha=1.0, beta=0.0) with tracking."""
    return experiment_a_tracking(
        model, tokenizer, dataset, k, alpha=1.0, beta=0.0
    )
