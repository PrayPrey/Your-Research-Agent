"""Experiment runners for h-m2."""

from ast_validator import validate_syntax_timed, compute_latency_stats
from beam_search_custom import run_beam_search_scored
from beam_search import run_beam_search, validate_syntax


def experiment_a_latency(
    model,
    tokenizer,
    dataset: list,
    k: int = 5
) -> dict:
    """
    Experiment A: Measure AST parse latency across dataset.

    Args:
        model: HuggingFace model
        tokenizer: HuggingFace tokenizer
        dataset: List of problem dictionaries
        k: Beam width

    Returns:
        Dictionary with timings and statistics
    """
    all_timings = []

    for problem in dataset:
        candidates, _ = run_beam_search_scored(
            model, tokenizer, problem['prompt'], k, 0.7, 0.3, 64
        )
        for cand in candidates:
            _, elapsed_ms = validate_syntax_timed(cand)
            all_timings.append(elapsed_ms)

    stats = compute_latency_stats(all_timings)
    return {'timings': all_timings, 'stats': stats}


def experiment_b_ranking(
    model,
    tokenizer,
    dataset: list,
    alpha: float = 0.7,
    beta: float = 0.3
) -> dict:
    """
    Experiment B: Verify valid beams exist in outputs.

    Args:
        model: HuggingFace model
        tokenizer: HuggingFace tokenizer
        dataset: List of problem dictionaries
        alpha: Log-likelihood weight
        beta: Syntax validity weight

    Returns:
        Dictionary with logs and validity proportion
    """
    all_logs = []
    valid_count = 0
    total_beams = 0

    for problem in dataset:
        _, logs = run_beam_search_scored(
            model, tokenizer, problem['prompt'], 5, alpha, beta, 64
        )
        all_logs.extend(logs)

        # Count valid beams
        for log in logs:
            total_beams += 1
            if log['validity']:
                valid_count += 1

    return {
        'logs': all_logs,
        'correct_proportion': valid_count / total_beams if total_beams > 0 else 0.0
    }


def experiment_c_ablation(
    model,
    tokenizer,
    subset: list,
    weight_pairs: list
) -> dict:
    """
    Experiment C: Test alpha/beta weight combinations.

    Args:
        model: HuggingFace model
        tokenizer: HuggingFace tokenizer
        subset: Stratified subset of problems
        weight_pairs: List of (alpha, beta) tuples

    Returns:
        Dictionary mapping (alpha, beta) to metrics
    """
    results = {}

    for alpha, beta in weight_pairs:
        logs = []
        valid_count = 0
        total_beams = 0

        for problem in subset:
            _, beam_logs = run_beam_search_scored(
                model, tokenizer, problem['prompt'], 5, alpha, beta, 64
            )
            logs.extend(beam_logs)

            for log in beam_logs:
                total_beams += 1
                if log['validity']:
                    valid_count += 1

        results[(alpha, beta)] = {
            'ranking_correctness': valid_count / total_beams if total_beams > 0 else 0.0,
            'logs': logs
        }

    return results


def baseline_comparison(
    model,
    tokenizer,
    dataset: list
) -> dict:
    """
    Baseline comparison: Greedy and pure log-likelihood beam search.

    Args:
        model: HuggingFace model
        tokenizer: HuggingFace tokenizer
        dataset: List of problem dictionaries

    Returns:
        Dictionary with error rates and improvement
    """
    # Pure log-likelihood beam search (alpha=1.0, beta=0.0)
    pure_beam_results = []
    for problem in dataset:
        outputs = run_beam_search(
            model, tokenizer, [problem['prompt']], k=5, max_new_tokens=64
        )
        pure_beam_results.extend(outputs[0])

    pure_errors = sum(1 for code in pure_beam_results if not validate_syntax(code))
    pure_error_rate = pure_errors / len(pure_beam_results)

    # Combined scoring (alpha=0.7, beta=0.3)
    combined_results = []
    for problem in dataset:
        outputs, _ = run_beam_search_scored(
            model, tokenizer, problem['prompt'], 5, 0.7, 0.3, 64
        )
        combined_results.extend(outputs)

    combined_errors = sum(1 for code in combined_results if not validate_syntax(code))
    combined_error_rate = combined_errors / len(combined_results)

    return {
        'pure_beam_error_rate': pure_error_rate,
        'combined_error_rate': combined_error_rate,
        'improvement': pure_error_rate - combined_error_rate
    }
