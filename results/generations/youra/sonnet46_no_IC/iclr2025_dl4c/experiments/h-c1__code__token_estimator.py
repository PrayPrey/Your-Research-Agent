"""Token estimation for H-C1."""


def estimate_tokens(source: str) -> int:
    """Approximate token count: word count * 1.3."""
    return int(len(source.split()) * 1.3)


def sum_tokens(sources: list) -> float:
    """Total estimated tokens for a list of source strings."""
    return sum(estimate_tokens(s) for s in sources)
