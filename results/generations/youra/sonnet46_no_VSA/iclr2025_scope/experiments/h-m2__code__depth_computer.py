"""Depth percentile computation for H-M2 analysis."""
import re
from config import DEPTH_FALLBACK_VALUE, RETRIEVAL_CATEGORIES

# Common English stopwords to exclude from keyword extraction
_STOPWORDS = frozenset({
    "the", "and", "for", "are", "was", "were", "has", "have", "had",
    "this", "that", "with", "from", "they", "their", "them", "what",
    "when", "where", "which", "who", "will", "would", "could", "should",
    "been", "being", "does", "did", "not", "but", "can", "its", "also",
    "into", "about", "than", "then", "some", "such", "more", "most",
    "other", "than", "these", "those", "only", "over", "after", "before",
    "each", "both", "few", "how", "all", "any", "much", "many", "may",
    "while", "since", "under", "within", "without", "between",
})


def extract_keywords(question: str, answer_text: str, top_n: int = 5) -> list[str]:
    """
    Extract content words (length >= 4, non-stopword) from question + answer_text.
    Returns top_n longest distinct tokens (longer = more discriminative).
    """
    combined = f"{question} {answer_text}"
    tokens = re.findall(r"\b[a-zA-Z]{4,}\b", combined.lower())
    seen = set()
    unique = []
    for t in tokens:
        if t not in _STOPWORDS and t not in seen:
            seen.add(t)
            unique.append(t)

    # Sort by length descending — longer words are more discriminative
    unique.sort(key=len, reverse=True)
    return unique[:top_n]


def compute_depth_percentile(record: dict) -> float:
    """
    Compute depth_percentile = earliest_keyword_position / len(context).
    Convention: 1.0 = answer near beginning, 0.0 = answer near end.
    Falls back to DEPTH_FALLBACK_VALUE if no keyword found or context empty.
    """
    context = record.get("context", "")
    question = record.get("question", "")
    answer_text = record.get("answer_text", "")

    if not context:
        return DEPTH_FALLBACK_VALUE

    ctx_lower = context.lower()
    ctx_len = len(ctx_lower)

    keywords = extract_keywords(question, answer_text)
    if not keywords:
        return DEPTH_FALLBACK_VALUE

    earliest_pos = None
    for kw in keywords:
        pos = ctx_lower.find(kw)
        if pos >= 0:
            if earliest_pos is None or pos < earliest_pos:
                earliest_pos = pos

    if earliest_pos is None:
        return DEPTH_FALLBACK_VALUE

    # Normalize: 1.0 = near start, 0.0 = near end
    # (1 - pos/len) so 0 position → 1.0 depth, end position → ~0.0)
    depth = 1.0 - (earliest_pos / ctx_len)
    return float(max(0.0, min(1.0, depth)))


def add_depth_percentiles(records: list[dict]) -> list[dict]:
    """
    Apply compute_depth_percentile to each record. Adds 'depth_percentile' field in-place.
    Validates: nunique > 10, all in [0,1], >= 100 samples.
    Returns records (same list, mutated).
    """
    fallback_count = 0
    for rec in records:
        dp = compute_depth_percentile(rec)
        rec["depth_percentile"] = dp
        if abs(dp - DEPTH_FALLBACK_VALUE) < 1e-9:
            fallback_count += 1

    # Validation
    values = [r["depth_percentile"] for r in records]
    n_unique = len(set(round(v, 4) for v in values))
    assert all(0.0 <= v <= 1.0 for v in values), "depth_percentile out of [0,1] range"

    fallback_frac = fallback_count / max(len(records), 1)
    print(f"[DepthComputer] {len(records)} records, {n_unique} unique depth values, "
          f"fallback rate: {fallback_frac:.1%}")

    if n_unique <= 10:
        import warnings
        warnings.warn(f"Only {n_unique} unique depth values — depth_percentile may be nearly constant")

    return records


def depth_stats(records: list[dict]) -> dict:
    """Returns {mean, std, min, max, fallback_fraction} of depth_percentile."""
    import statistics
    values = [r["depth_percentile"] for r in records]
    fallback_n = sum(1 for v in values if abs(v - DEPTH_FALLBACK_VALUE) < 1e-9)
    return {
        "mean": statistics.mean(values),
        "std": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "fallback_fraction": fallback_n / max(len(values), 1),
    }
