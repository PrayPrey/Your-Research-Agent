"""Experiment runners for h-m4."""

import sys
sys.path.insert(0, '../../h-m3/code')

import json
from ast_validator import validate_syntax_timed
from beam_search_tracked import run_beam_search_with_tracking
from selector import FinalOutputSelector
from greedy_sampler import run_greedy_baseline
from selection_analyzer import SelectionAnalyzer
from strategy_comparator import StrategyComparator
from error_comparator import compute_error_reduction


def experiment_a_final_validity(
    model,
    tokenizer,
    dataset: list[dict],
    k: int = 5,
    alpha: float = 0.7,
    beta: float = 0.3
) -> dict:
    """Run beam search, select final output, validate syntax."""
    selector = FinalOutputSelector(alpha, beta)
    results = {
        'selected_outputs': [],
        'selected_indices': [],
        'final_scores': [],
        'all_beams': [],
        'validity_labels': []
    }

    for problem in dataset:
        prompt = problem['prompt']
        beams, tracking_data = run_beam_search_with_tracking(
            model, tokenizer, prompt, k, alpha, beta, 512
        )

        # Use dummy log_likelihoods (h-m3 scoring uses 0.0, relies on validity only)
        log_likelihoods = [0.0] * len(beams)

        selected, idx, scores = selector.select_final_output(beams, log_likelihoods)
        is_valid, _ = validate_syntax_timed(selected)

        results['selected_outputs'].append(selected)
        results['selected_indices'].append(idx)
        results['final_scores'].append(scores)
        results['all_beams'].append(beams)
        results['validity_labels'].append(is_valid)

    # Compute validity rate
    total = len(results['validity_labels'])
    valid = sum(results['validity_labels'])
    results['syntax_validity_rate'] = valid / total if total > 0 else 0.0
    results['syntax_error_rate'] = 1.0 - results['syntax_validity_rate']

    return results


def experiment_b_greedy_baseline(
    model,
    tokenizer,
    dataset: list[dict]
) -> dict:
    """Run greedy sampling, validate syntax, compare error rates."""
    prompts = [p['prompt'] for p in dataset]
    greedy_outputs = run_greedy_baseline(model, tokenizer, prompts)

    validity_labels = [validate_syntax_timed(code)[0] for code in greedy_outputs]

    total = len(validity_labels)
    valid = sum(validity_labels)
    syntax_error_rate = 1.0 - (valid / total) if total > 0 else 0.0

    return {
        'greedy_outputs': greedy_outputs,
        'validity_labels': validity_labels,
        'syntax_error_rate': syntax_error_rate
    }


def experiment_c_selection_quality(
    beam_results: dict
) -> dict:
    """Analyze selection accuracy by beam availability strata."""
    analyzer = SelectionAnalyzer()
    return analyzer.compute_selection_accuracy(
        beam_results['all_beams'],
        beam_results['selected_indices']
    )


def experiment_d_strategy_comparison(
    beam_results: dict
) -> dict:
    """Compare argmax vs validity-first vs random-valid selection."""
    comparator = StrategyComparator()
    return comparator.compare_strategies(
        beam_results['all_beams'],
        beam_results['final_scores']
    )
