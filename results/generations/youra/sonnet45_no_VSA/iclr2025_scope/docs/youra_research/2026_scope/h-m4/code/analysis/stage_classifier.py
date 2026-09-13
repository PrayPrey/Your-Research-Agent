"""Classify failure stage from CI logs."""

import re
from typing import List, Optional


class StageClassifier:
    """Classify failure stage from CI logs."""

    def __init__(self):
        """Initialize stage classifier."""
        self.environment_patterns = [
            'contract', 'validation', 'setup', 'dependencies',
            'pip install', 'import error', 'module not found',
            'Validate API Contracts'
        ]
        self.training_patterns = [
            'train.py', 'training', 'Run training', 'epoch', 'batch',
            'loss', 'accuracy', 'model.forward'
        ]

    def classify_from_logs(self, step_logs: List[str]) -> str:
        """Classify failure stage from step logs."""
        for log in step_logs:
            # Check for contract validation failure
            if 'Validate API Contracts' in log and 'failure' in log.lower():
                return 'environment'

            # Check for setup failures
            if any(pattern in log.lower() for pattern in ['setup', 'install dependencies']):
                if 'failure' in log.lower():
                    return 'environment'

            # Check for training failures
            if any(pattern in log.lower() for pattern in ['run training', 'train.py']):
                if 'failure' in log.lower():
                    return 'training'

        return 'unknown'

    def is_environment_failure(self, log: str) -> bool:
        """Check if log indicates environment-stage failure."""
        for pattern in self.environment_patterns:
            if pattern.lower() in log.lower():
                return True
        return False

    def is_training_failure(self, log: str) -> bool:
        """Check if log indicates training-stage failure."""
        for pattern in self.training_patterns:
            if pattern.lower() in log.lower():
                return True
        return False
