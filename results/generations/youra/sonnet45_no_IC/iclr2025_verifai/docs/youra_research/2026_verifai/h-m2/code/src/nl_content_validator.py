"""Natural Language Content Validator for H-M1.

Validates NL word presence in MCP trace tool calls using regex-based
word counting with recursive text extraction.
"""

import re
from typing import Tuple, Any


class NLContentValidator:
    """Validate natural language content in tool calls."""

    NL_WORD_PATTERN = r'\b[a-zA-Z]{2,}\b'

    def __init__(self, min_word_count: int = 10):
        """Initialize validator.

        Args:
            min_word_count: Minimum NL words for presence (default: 10)
        """
        self.min_word_count = min_word_count
        self.pattern = re.compile(self.NL_WORD_PATTERN)

    def count_nl_words(self, text: str) -> int:
        """Count NL words (≥2 alphabetic chars).

        Args:
            text: String to analyze

        Returns:
            Word count
        """
        if not isinstance(text, str):
            return 0
        return len(self.pattern.findall(text))

    def extract_text_from_dict(self, obj: Any) -> str:
        """Recursively extract strings from nested structures.

        Excludes JSON keys, preserves values only.

        Args:
            obj: dict, list, or primitive value

        Returns:
            Concatenated text content
        """
        if obj is None:
            return ""
        if isinstance(obj, str):
            return obj
        if isinstance(obj, dict):
            return " ".join(self.extract_text_from_dict(v) for v in obj.values())
        if isinstance(obj, list):
            return " ".join(self.extract_text_from_dict(item) for item in obj)
        return str(obj)

    def validate_nl_presence(self, tool_call: dict) -> Tuple[bool, int, int]:
        """Validate NL content in params and results.

        Args:
            tool_call: Tool call dict with 'parameters' and 'result' keys

        Returns:
            (is_valid, query_words, result_words)
        """
        params_text = self.extract_text_from_dict(tool_call.get('parameters', {}))
        result_text = self.extract_text_from_dict(tool_call.get('result', ''))

        query_words = self.count_nl_words(params_text)
        result_words = self.count_nl_words(result_text)
        total_words = query_words + result_words

        return (total_words >= self.min_word_count, query_words, result_words)

    def get_source_type(self, query_words: int, result_words: int) -> str:
        """Classify NL source type.

        Args:
            query_words: Word count in query parameters
            result_words: Word count in results

        Returns:
            'both', 'query_only', 'result_only', or 'neither'
        """
        has_query = query_words >= 5
        has_result = result_words >= 5

        if has_query and has_result:
            return "both"
        elif has_query:
            return "query_only"
        elif has_result:
            return "result_only"
        else:
            return "neither"
