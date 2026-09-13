"""Diversity measurement for beam search outputs."""


def measure_diversity(outputs: list[str]) -> dict:
    """
    Measure uniqueness of k beam outputs.
    Returns: {unique_count, diversity_ratio, unique_outputs}
    """
    unique = set(outputs)
    return {
        'unique_count': len(unique),
        'diversity_ratio': len(unique) / len(outputs) if outputs else 0.0,
        'unique_outputs': list(unique)
    }
