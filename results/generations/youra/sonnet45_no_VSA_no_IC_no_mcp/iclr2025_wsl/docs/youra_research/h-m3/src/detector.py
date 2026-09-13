"""Confound detection via keyword pattern matching."""

from typing import Dict, List, Optional, Tuple


class ConfoundDetector:
    """Cross-domain confound pattern detector."""

    def __init__(self, pattern_db: Dict[str, List[Dict]]):
        self.patterns = pattern_db

    def detect(self, hypothesis_text: str) -> Tuple[str, Optional[str]]:
        """Detect confound in hypothesis. Returns: ('confounded', pattern_name) or ('unconfounded', None)."""
        text_lower = hypothesis_text.lower()

        for domain, patterns in self.patterns.items():
            for pattern in patterns:
                if self._match_keywords(text_lower, pattern["keywords"]):
                    return ("confounded", pattern["description"])

        return ("unconfounded", None)

    def _match_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if ALL keywords appear in text (case-insensitive). Returns: bool."""
        return all(kw.lower() in text for kw in keywords)
