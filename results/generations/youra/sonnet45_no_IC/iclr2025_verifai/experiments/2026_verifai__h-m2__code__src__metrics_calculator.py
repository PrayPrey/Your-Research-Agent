"""Metrics Calculator for H-M1 NL Content Validation.

Calculates NL presence rate, source breakdown, tool type breakdown,
and word count distribution.
"""

from typing import List, Dict
from .nl_content_validator import NLContentValidator


class MetricsCalculator:
    """Calculate NL content metrics."""

    def __init__(self, validator: NLContentValidator):
        """Initialize with validator instance.

        Args:
            validator: NLContentValidator instance
        """
        self.validator = validator

    def calculate_nl_presence_rate(self, traces: List[Dict]) -> float:
        """Calculate NL presence rate.

        Args:
            traces: List of trace dicts

        Returns:
            Rate [0.0, 1.0]
        """
        total_calls = 0
        calls_with_nl = 0

        for trace in traces:
            for tool_call in trace['tool_calls']:
                total_calls += 1
                is_valid, _, _ = self.validator.validate_nl_presence(tool_call)
                if is_valid:
                    calls_with_nl += 1

        if total_calls == 0:
            return 0.0
        return calls_with_nl / total_calls

    def calculate_source_breakdown(self, traces: List[Dict]) -> Dict[str, int]:
        """Count calls by source type.

        Returns:
            Dict with keys: query_only, result_only, both, neither
        """
        breakdown = {"query_only": 0, "result_only": 0, "both": 0, "neither": 0}

        for trace in traces:
            for tool_call in trace['tool_calls']:
                _, query_words, result_words = self.validator.validate_nl_presence(tool_call)
                source_type = self.validator.get_source_type(query_words, result_words)
                breakdown[source_type] += 1

        return breakdown

    def calculate_tool_type_breakdown(self, traces: List[Dict]) -> Dict[str, Dict]:
        """Calculate NL presence by tool type.

        Returns:
            Dict with keys: research, data_processing
            (each with total, with_nl, rate)
        """
        research_tools = ['rag_search', 'rag_read', 'mcp__archon']

        stats = {
            "research": {"total": 0, "with_nl": 0, "rate": 0.0},
            "data_processing": {"total": 0, "with_nl": 0, "rate": 0.0}
        }

        for trace in traces:
            for tool_call in trace['tool_calls']:
                tool_name = tool_call.get('tool_name', '')
                is_valid, _, _ = self.validator.validate_nl_presence(tool_call)

                is_research = any(rt in tool_name for rt in research_tools)
                category = "research" if is_research else "data_processing"

                stats[category]["total"] += 1
                if is_valid:
                    stats[category]["with_nl"] += 1

        # Calculate rates
        for category in stats:
            if stats[category]["total"] > 0:
                stats[category]["rate"] = stats[category]["with_nl"] / stats[category]["total"]

        return stats

    def calculate_word_count_distribution(self, traces: List[Dict]) -> Dict[str, int]:
        """Bin word counts.

        Returns:
            Dict with keys: 0-5, 5-10, 10-20, 20-50, 50+
        """
        bins = {"0-5": 0, "5-10": 0, "10-20": 0, "20-50": 0, "50+": 0}

        for trace in traces:
            for tool_call in trace['tool_calls']:
                _, query_words, result_words = self.validator.validate_nl_presence(tool_call)
                total_words = query_words + result_words

                if total_words < 5:
                    bins["0-5"] += 1
                elif total_words < 10:
                    bins["5-10"] += 1
                elif total_words < 20:
                    bins["10-20"] += 1
                elif total_words < 50:
                    bins["20-50"] += 1
                else:
                    bins["50+"] += 1

        return bins
