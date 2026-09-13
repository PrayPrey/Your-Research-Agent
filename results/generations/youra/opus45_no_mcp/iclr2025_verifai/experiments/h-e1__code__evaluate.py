"""A-7: Gate evaluation."""
from typing import Tuple

def evaluate_gate(results: dict, jaccard_gate: float = 0.3, non_overlap_gate: float = 0.7) -> Tuple[bool, str]:
    """Check if MUST_WORK gate passes."""
    mean_jaccard = results.get("mean_jaccard", 1.0)
    non_overlapping = results.get("non_overlapping_pct", 0.0)

    gate_passed = mean_jaccard < jaccard_gate
    msg = f"Jaccard={mean_jaccard:.3f} ({'PASS' if gate_passed else 'FAIL'}, threshold={jaccard_gate})"

    secondary_passed = non_overlapping >= non_overlap_gate
    msg += f", Non-overlapping={non_overlapping:.1%} ({'PASS' if secondary_passed else 'FAIL'}, threshold={non_overlap_gate:.0%})"

    return gate_passed, msg
