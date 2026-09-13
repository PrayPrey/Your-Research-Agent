"""Telemetry Logger with Retry - h-m4 Module 2"""
from typing import Dict, Any
import time
import json
from pathlib import Path


class TelemetryLogger:
    """Logger with exponential backoff retry and JSONL fallback."""

    def __init__(
        self,
        async_queue: 'AsyncTelemetryQueue',
        fallback_dir: str = "logs/fallback"
    ):
        """
        Initialize logger.

        Args:
            async_queue: AsyncTelemetryQueue instance
            fallback_dir: directory for fallback JSONL files
        """
        self.async_queue = async_queue
        self.fallback_dir = Path(fallback_dir)
        self.fallback_dir.mkdir(parents=True, exist_ok=True)

    def log_event(
        self,
        event: Dict[str, Any],
        max_retries: int = 3
    ) -> bool:
        """
        Log with exponential backoff retry.

        Args:
            event: {user_id, dataset_name, deprecated, ...}
            max_retries: max retry attempts

        Returns:
            True if logged (queue or fallback), False otherwise
        """
        for attempt in range(max_retries):
            if self.async_queue.put(event):
                return True

            # Exponential backoff
            backoff = self._exponential_backoff(attempt)
            time.sleep(backoff)

        # All retries failed → write to fallback
        self._write_to_fallback(event)
        return False

    def _write_to_fallback(self, event: Dict[str, Any]) -> None:
        """
        Write to local JSONL file if queue fails.

        Args:
            event: event dict
        """
        fallback_file = self.fallback_dir / f"fallback_{int(time.time())}.jsonl"

        with open(fallback_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

    def _exponential_backoff(self, attempt: int) -> float:
        """
        Calculate backoff delay: 2^attempt seconds.

        Args:
            attempt: retry attempt number (0-indexed)

        Returns:
            delay in seconds
        """
        return 2 ** attempt
