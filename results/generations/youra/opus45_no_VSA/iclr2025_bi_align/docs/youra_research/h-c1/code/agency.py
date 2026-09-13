import hc1_config as config

AGENCY_PATTERNS = {
    "clarifying": ["clarify", "understand", "mean", "asking", "question", "sure"],
    "deferring": ["prefer", "choice", "decide", "up to you", "your call", "depends"],
    "hedging": ["might", "perhaps", "possibly", "could be", "uncertain", "not sure"],
    "option_enum": ["option", "alternatively", "or", "either", "choices", "ways"],
}


def classify_cluster_as_agency(topic_keywords, threshold=None):
    """
    Check if cluster keywords match agency patterns.
    Returns (is_agency, match_count).
    """
    if threshold is None:
        threshold = config.AGENCY_MATCH_THRESHOLD

    keywords_lower = topic_keywords.lower()
    matches = 0

    for pattern_name, keywords in AGENCY_PATTERNS.items():
        if any(kw in keywords_lower for kw in keywords):
            matches += 1

    return matches >= threshold, matches
