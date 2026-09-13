"""Hedging marker detection and reasoning chain extraction."""
import re
from config import CONFIG

HEDGING_MARKERS = CONFIG["hedging"]["markers"]
EXTENDED_HEDGING_MARKERS = HEDGING_MARKERS + CONFIG["hedging"]["extended_markers"]
CONFIDENCE_SPLIT_MARKERS = CONFIG["hedging"]["confidence_split_markers"]


def extract_reasoning_chain(output: str) -> str:
    """Extract reasoning text before confidence statement.

    Args:
        output: Full model output text.

    Returns:
        Reasoning portion only, excluding confidence statement.
    """
    lower = output.lower()
    for marker in CONFIDENCE_SPLIT_MARKERS:
        idx = lower.find(marker)
        if idx != -1:
            return output[:idx]
    return output


def extract_confidence(text: str) -> float | None:
    """Extract confidence value, normalized to [0,1].

    Args:
        text: Text containing confidence statement.

    Returns:
        Confidence value in [0,1], or None if not found.
    """
    match = re.search(r'confidence:?\s*(\d{1,3})', text, re.IGNORECASE)
    if match:
        val = int(match.group(1))
        if 0 <= val <= 100:
            return val / 100.0
    return None


def count_hedging_markers(text: str, markers: list[str] = None) -> dict:
    """Count marker occurrences (case-insensitive substring).

    Args:
        text: Text to analyze.
        markers: List of markers to count. Defaults to HEDGING_MARKERS.

    Returns:
        Dict with markers_found, total_count, has_hedging.
    """
    if markers is None:
        markers = HEDGING_MARKERS

    text_lower = text.lower()
    counts = {}
    total = 0
    for marker in markers:
        c = text_lower.count(marker)
        if c > 0:
            counts[marker] = c
            total += c
    return {"markers_found": counts, "total_count": total, "has_hedging": total > 0}


def analyze_hedging(cot_output: str) -> dict:
    """Extract reasoning and count hedging markers.

    Args:
        cot_output: Full CoT model output.

    Returns:
        Dict with reasoning_text and hedging analysis results.
    """
    reasoning = extract_reasoning_chain(cot_output)
    result = count_hedging_markers(reasoning)
    return {"reasoning_text": reasoning, **result}
