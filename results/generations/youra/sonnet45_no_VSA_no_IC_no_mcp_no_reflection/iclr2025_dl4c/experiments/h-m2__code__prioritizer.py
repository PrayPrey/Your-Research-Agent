"""Root cause prioritization by error clustering."""

import sys
import os
from typing import List, Dict
from collections import defaultdict

# Import H-M1 utilities
H_M1_CODE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "h-m1", "code")
sys.path.insert(0, H_M1_CODE_PATH)

from utils import ErrorType


class RootCausePrioritizer:
    """Prioritize fixes by error cluster size."""

    def __init__(self):
        pass

    def cluster_errors(self, error_messages: Dict[str, str]) -> Dict[ErrorType, List[str]]:
        """
        Group tests by error type.

        Args:
            error_messages: {test_id: error_msg}

        Returns:
            {ErrorType: [test_ids]}
        """
        clusters = defaultdict(list)

        for test_id, error_msg in error_messages.items():
            error_type = self._classify_error(error_msg)
            clusters[error_type].append(test_id)

        return dict(clusters)

    def _classify_error(self, error_msg: str) -> ErrorType:
        """Map error message to ErrorType."""
        msg_lower = error_msg.lower()

        if "syntax" in msg_lower or "parse" in msg_lower:
            return ErrorType.SYNTAX
        elif "runtime" in msg_lower or "exception" in msg_lower:
            return ErrorType.RUNTIME
        elif "edge" in msg_lower or "boundary" in msg_lower:
            return ErrorType.EDGE_CASE
        else:
            return ErrorType.LOGIC

    def prioritize(self, clusters: Dict[ErrorType, List[str]]) -> List[str]:
        """
        Sort tests by cluster size (descending).

        Args:
            clusters: {ErrorType: [test_ids]}

        Returns:
            priority_order: [test_ids] (largest cluster first)
        """
        # Sort clusters by size descending
        sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)

        # Flatten to priority order
        priority_order = []
        for error_type, test_ids in sorted_clusters:
            priority_order.extend(test_ids)

        return priority_order
