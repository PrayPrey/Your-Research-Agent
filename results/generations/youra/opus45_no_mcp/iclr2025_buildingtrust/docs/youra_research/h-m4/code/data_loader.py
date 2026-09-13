"""H-M4 Data Loader: Load and extract hedging-confidence pairs from H-M2 cache."""
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def load_h_m2_cache(cache_path: Path) -> List[Dict[str, Any]]:
    """Load H-M2 results from JSON file."""
    with open(cache_path, 'r') as f:
        data = json.load(f)
    return data


def validate_cache_format(data: Any) -> bool:
    """Validate H-M2 cache is a flat list of dicts."""
    if not isinstance(data, list):
        return False
    if len(data) == 0:
        return False
    sample = data[0]
    return isinstance(sample, dict)


def extract_pairs(data: List[Dict[str, Any]]) -> Tuple[List[int], List[float]]:
    """Extract (hedging_count, confidence_score) pairs.

    Handles field name variants:
    - hedging_count / total_count / num_hedging_markers
    - confidence / confidence_score (0-1 or 0-100 scale)

    Returns:
        Tuple of (hedging_counts, confidence_scores) lists.
    """
    hedging_counts = []
    confidence_scores = []

    for item in data:
        hedging = item.get('hedging_count') or item.get('total_count') or item.get('num_hedging_markers')
        confidence = item.get('confidence') or item.get('confidence_score')

        if hedging is not None and confidence is not None:
            hedging_counts.append(int(hedging))
            conf_val = float(confidence)
            if conf_val <= 1.0:
                conf_val *= 100
            confidence_scores.append(conf_val)

    return hedging_counts, confidence_scores
