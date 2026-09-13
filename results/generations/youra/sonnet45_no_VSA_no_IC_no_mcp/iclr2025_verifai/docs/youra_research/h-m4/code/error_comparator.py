"""Error rate comparison between greedy and beam search."""

import sys
sys.path.insert(0, '../../h-m3/code')

from ast_validator import validate_syntax_timed


def compute_error_reduction(
    greedy_outputs: list[str],
    beam_outputs: list[str]
) -> dict:
    """
    Compare greedy vs beam search syntax error rates.

    Args:
        greedy_outputs: [N] greedy generated code
        beam_outputs: [N] beam-selected code

    Returns:
        {
            'greedy_error_rate': float,
            'beam_error_rate': float,
            'absolute_reduction': float,
            'relative_reduction': float  # percentage
        }
    """
    greedy_errors = sum(1 for code in greedy_outputs if not validate_syntax_timed(code)[0])
    beam_errors = sum(1 for code in beam_outputs if not validate_syntax_timed(code)[0])

    greedy_error_rate = greedy_errors / len(greedy_outputs)
    beam_error_rate = beam_errors / len(beam_outputs)

    absolute_reduction = greedy_error_rate - beam_error_rate
    relative_reduction = (absolute_reduction / greedy_error_rate * 100) if greedy_error_rate > 0 else 0.0

    return {
        'greedy_error_rate': greedy_error_rate,
        'beam_error_rate': beam_error_rate,
        'absolute_reduction': absolute_reduction,
        'relative_reduction': relative_reduction
    }
