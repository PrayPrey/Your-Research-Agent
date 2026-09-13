"""Data loading module for H-M3."""

import json
from pathlib import Path
from typing import List, Dict, Any


def load_h_m2_cache(cache_path: Path) -> List[Dict[str, Any]]:
    """Load cached H-M2 experiment outputs."""
    if not cache_path.exists():
        raise FileNotFoundError(f"H-M2 cache not found: {cache_path}")

    with open(cache_path, 'r') as f:
        data = json.load(f)

    if not validate_cache_format(data):
        raise ValueError("Invalid H-M2 cache format")

    return data


def validate_cache_format(data: Any) -> bool:
    """Validate cache has required fields."""
    if not isinstance(data, list):
        return False
    if len(data) == 0:
        return False
    sample = data[0]
    return 'raw_output' in sample or 'output_text' in sample or 'response' in sample or 'output' in sample
