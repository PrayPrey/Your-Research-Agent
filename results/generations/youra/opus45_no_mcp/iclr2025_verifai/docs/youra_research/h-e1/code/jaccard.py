"""A-5: Jaccard similarity and categorization."""
from typing import Literal

Category = Literal["static_only", "exec_only", "both", "neither"]

def compute_jaccard(set_a: set, set_b: set) -> float:
    """Compute Jaccard similarity: |A ∩ B| / |A ∪ B|."""
    if not set_a and not set_b:
        return 0.0
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)

def categorize(static_errors: set, exec_errors: set) -> Category:
    """Categorize problem by error source."""
    if static_errors and exec_errors:
        return "both"
    if static_errors:
        return "static_only"
    if exec_errors:
        return "exec_only"
    return "neither"
