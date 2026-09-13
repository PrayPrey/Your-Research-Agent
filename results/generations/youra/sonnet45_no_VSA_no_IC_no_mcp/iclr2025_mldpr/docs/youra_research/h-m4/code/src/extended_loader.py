"""Extended Instrumented Loader - h-m4 Module 10 (h-m3 integration)"""
import hashlib
import time
from typing import Dict, Any, Tuple
from datasets import load_dataset


class ExtendedInstrumentedLoader:
    """Extends h-m3 loader with h-m4 async telemetry and performance tracking."""

    def __init__(
        self,
        telemetry_logger: 'TelemetryLogger',
        performance_tracker: 'PerformanceTracker',
        deprecation_registry: Dict[str, str],
        ground_truth_generator: 'GroundTruthGenerator' = None
    ):
        """
        Initialize loader.

        Args:
            telemetry_logger: TelemetryLogger instance
            performance_tracker: PerformanceTracker instance
            deprecation_registry: {deprecated_name: successor_name}
            ground_truth_generator: optional ground truth recorder
        """
        self.telemetry_logger = telemetry_logger
        self.performance_tracker = performance_tracker
        self.deprecation_registry = deprecation_registry
        self.ground_truth_generator = ground_truth_generator

    def load_dataset_with_tracking(
        self,
        dataset_name: str,
        user_id: str,
        **kwargs
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Load dataset with telemetry and performance tracking.

        Args:
            dataset_name: dataset to load
            user_id: user identifier
            **kwargs: passed to load_dataset()

        Returns:
            (dataset, {
                'latency_ms': float,
                'memory_delta_mb': float,
                'cpu_percent': float,
                'group': str,
                'deprecated': bool,
                'successor': str
            })
        """
        # 1. Check deprecation
        deprecated = dataset_name in self.deprecation_registry
        successor = self.deprecation_registry.get(dataset_name)

        # 2. Assign user group (hash-based)
        group = self._assign_user_group(user_id)

        # 3. Track load performance (mock data for PoC)
        def mock_load():
            return {'data': [f'sample_{i}' for i in range(10)]}

        dataset, perf_metrics = self.performance_tracker.track_operation(
            mock_load
        )

        # 4. Log event (async)
        self._log_load_event(
            user_id,
            dataset_name,
            deprecated,
            successor,
            group,
            perf_metrics
        )

        # 5. Record ground truth (if enabled)
        if self.ground_truth_generator:
            self.ground_truth_generator.record_load_event(
                user_id,
                dataset_name,
                deprecated,
                successor,
                group
            )

        return dataset, {
            **perf_metrics,
            'group': group,
            'deprecated': deprecated,
            'successor': successor
        }

    def _assign_user_group(self, user_id: str) -> str:
        """
        Hash-based user group assignment.

        Args:
            user_id: user identifier

        Returns:
            'baseline' | 'instrumented'
        """
        hash_val = int(hashlib.sha256(user_id.encode()).hexdigest(), 16)
        return 'baseline' if hash_val % 2 == 0 else 'instrumented'

    def _log_load_event(
        self,
        user_id: str,
        dataset_name: str,
        deprecated: bool,
        successor: str,
        group: str,
        perf_metrics: Dict[str, float]
    ) -> None:
        """
        Log event via async queue.

        Args:
            user_id: user identifier
            dataset_name: dataset loaded
            deprecated: deprecation status
            successor: successor dataset (if deprecated)
            group: user group
            perf_metrics: {latency_ms, memory_delta_mb, cpu_percent}
        """
        event = {
            'user_id': user_id,
            'dataset_name': dataset_name,
            'deprecated': deprecated,
            'successor': successor,
            'user_group': group,
            'timestamp': time.time(),
            'latency_ms': perf_metrics.get('latency_ms'),
            'memory_delta_mb': perf_metrics.get('memory_delta_mb'),
            'cpu_percent': perf_metrics.get('cpu_percent')
        }

        self.telemetry_logger.log_event(event)
