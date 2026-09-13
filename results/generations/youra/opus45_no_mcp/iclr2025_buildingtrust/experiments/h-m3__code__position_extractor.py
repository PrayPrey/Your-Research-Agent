"""Position extraction module for H-M3."""

import re
from typing import Tuple, List

HEDGING_MARKERS = [
    'might', 'possibly', 'could', 'perhaps', 'may', 'likely',
    'unlikely', 'however', 'uncertain', 'although', 'but',
    'difficult to determine', 'not certain', 'hard to say',
    'alternatively', 'on the other hand', 'it depends'
]


def extract_confidence_position(output: str) -> Tuple[int, int]:
    """Extract confidence statement position and value."""
    patterns = [
        r'(?:My\s+)?[Cc]onfidence[:\s]+(\d+)%?',
        r'[Cc]onfidence:\s*(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            return match.start(), int(match.group(1))
    return -1, -1


def extract_hedging_positions(output: str) -> List[Tuple[str, int]]:
    """Find all hedging markers and their positions."""
    markers_found = []
    for marker in HEDGING_MARKERS:
        pattern = rf'\b{re.escape(marker)}\b'
        for match in re.finditer(pattern, output, re.IGNORECASE):
            markers_found.append((marker, match.start()))
    return sorted(markers_found, key=lambda x: x[1])
