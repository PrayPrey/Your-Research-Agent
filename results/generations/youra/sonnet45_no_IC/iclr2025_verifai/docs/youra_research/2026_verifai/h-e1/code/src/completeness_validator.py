"""Completeness Validator - Field presence and NL content validation."""

from typing import Dict, Tuple


class CompletenessValidator:
    """Validate tool call completeness."""

    def __init__(self, min_word_count: int = 10):
        """Initialize validator with minimum word count threshold."""
        self.min_word_count = min_word_count

    def count_words(self, text: str) -> int:
        """Count words in text string.

        Args:
            text: Input text

        Returns:
            Word count
        """
        if not isinstance(text, str):
            return 0
        return len(text.split())

    def extract_nl_content(self, obj) -> str:
        """Extract natural language content from nested dict/list/str.

        Args:
            obj: Object to extract text from (dict, list, str, or other)

        Returns:
            Concatenated string of all text content
        """
        if obj is None:
            return ""

        if isinstance(obj, str):
            return obj

        if isinstance(obj, dict):
            texts = []
            for value in obj.values():
                texts.append(self.extract_nl_content(value))
            return " ".join(texts)

        if isinstance(obj, list):
            texts = []
            for item in obj:
                texts.append(self.extract_nl_content(item))
            return " ".join(texts)

        # Numbers, booleans, etc -> convert to string
        return str(obj)

    def validate_tool_call(self, tool_call: Dict) -> bool:
        """Validate a single tool call for completeness.

        Args:
            tool_call: Tool call dict

        Returns:
            True if complete (has required fields + NL content)
        """
        # Check required fields present
        required_fields = ['tool_name', 'parameters', 'result']
        for field in required_fields:
            if field not in tool_call or tool_call[field] is None:
                return False

        # Check parameters not empty
        params = tool_call['parameters']
        if not params or (isinstance(params, dict) and len(params) == 0):
            return False

        # Check result not empty
        result = tool_call['result']
        if not result:
            return False

        # Extract natural language content
        params_text = self.extract_nl_content(params)
        result_text = self.extract_nl_content(result)

        # Count total words
        total_words = self.count_words(params_text) + self.count_words(result_text)

        return total_words >= self.min_word_count
