"""Combined scoring function for beam search."""

from typing import Tuple
import numpy as np
from ast_validator import validate_syntax_timed


def combined_score(
    log_likelihood: float,
    code: str,
    alpha: float = 0.7,
    beta: float = 0.3
) -> Tuple[float, bool, float]:
    """
    Compute combined score from log-likelihood and syntax validity.

    Formula: final_score = alpha * log_likelihood + beta * syntax_validity_score

    Args:
        log_likelihood: Model's log probability for this sequence
        code: Generated code string
        alpha: Weight for log-likelihood term (default 0.7)
        beta: Weight for syntax validity term (default 0.3)

    Returns:
        (final_score, validity, elapsed_ms): Combined score, validity flag, AST parse time
    """
    validity, elapsed_ms = validate_syntax_timed(code)
    validity_score = 1.0 if validity else 0.0
    final_score = alpha * log_likelihood + beta * validity_score
    return final_score, validity, elapsed_ms


def rank_beams(scores: list) -> list:
    """
    Rank beam candidates by score (descending).

    Args:
        scores: List of final scores

    Returns:
        List of rank indices (0 = highest score)
    """
    return np.argsort(scores)[::-1].tolist()
