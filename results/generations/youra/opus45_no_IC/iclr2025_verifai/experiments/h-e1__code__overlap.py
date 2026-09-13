"""Jaccard overlap analysis for error class independence."""

import config


def jaccard_index(set_a: set, set_b: set) -> float:
    """Compute Jaccard index: |A∩B| / |A∪B|."""
    union = set_a | set_b
    if len(union) == 0:
        return 0.0
    return len(set_a & set_b) / len(union)


def compute_jaccard_overlap(sets: dict[str, set]) -> dict[str, float]:
    """Compute pairwise Jaccard indices for grammar/static/smt sets."""
    pairs = [
        ("grammar", "static"),
        ("grammar", "smt"),
        ("static", "smt"),
    ]

    results = {}
    for a, b in pairs:
        key = f"{a}_vs_{b}"
        results[key] = jaccard_index(sets.get(a, set()), sets.get(b, set()))

    pairwise_values = list(results.values())
    results["mean"] = sum(pairwise_values) / len(pairwise_values) if pairwise_values else 0.0

    return results


def gate_check(overlaps: dict[str, float], threshold: float = config.JACCARD_THRESHOLD) -> bool:
    """Check if all pairwise Jaccard indices are below threshold.

    Returns True if gate PASSES (all overlaps < threshold).
    """
    for key, value in overlaps.items():
        if key == "mean":
            continue
        if value >= threshold:
            return False
    return True
