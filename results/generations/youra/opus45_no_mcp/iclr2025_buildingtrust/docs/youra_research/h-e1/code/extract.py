"""Response extraction for confidence and answer."""
import re
from typing import Optional
from config import CONFIG


def extract_confidence(response_text: str) -> Optional[float]:
    """Extract confidence percentage from response."""
    match = re.search(CONFIG.experiment.confidence_regex, response_text, re.IGNORECASE)
    if match:
        value = int(match.group(1))
        if 0 <= value <= 100:
            return value / 100.0
    return None


def extract_answer(response_text: str, num_choices: int) -> Optional[str]:
    """Extract answer letter from response."""
    match = re.search(CONFIG.experiment.answer_regex, response_text, re.IGNORECASE)
    if match:
        letter = match.group(1).upper()
        if ord(letter) - ord("A") < num_choices:
            return letter
    return None
