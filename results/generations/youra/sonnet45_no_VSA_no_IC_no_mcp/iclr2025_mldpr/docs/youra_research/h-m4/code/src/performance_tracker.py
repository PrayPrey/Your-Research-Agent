"""Performance Tracker - h-m4 Module 3"""
import time
import psutil
from typing import Callable, Any, Dict, List, Tuple
from statistics import mean, stdev


class PerformanceTracker:
    """Track load operation metrics (latency, memory, CPU)."""

    def __init__(self):
        """Initialize tracker."""
        self.metrics: List[Dict[str, float]] = []
        self.process = psutil.Process()

    def track_operation(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Tuple[Any, Dict[str, float]]:
        """
        Track load operation metrics.

        Args:
            func: function to track (e.g., load_dataset)
            *args, **kwargs: function arguments

        Returns:
            (result, metrics_dict)
            metrics_dict: {latency_ms, memory_delta_mb, cpu_percent}
        """
        mem_before = self._measure_memory()
        start = time.time()

        result = func(*args, **kwargs)

        latency = (time.time() - start) * 1000  # ms
        mem_after = self._measure_memory()
        cpu = psutil.cpu_percent(interval=0.1)

        metrics = {
            'latency_ms': latency,
            'memory_delta_mb': (mem_after - mem_before) / 1024 / 1024,
            'cpu_percent': cpu
        }

        self.metrics.append(metrics)

        return result, metrics

    def get_metrics(self) -> Dict[str, Any]:
        """
        Return aggregate metrics.

        Returns:
            {
                'latency_ms': {'mean': float, 'std': float, 'p50': float, 'p95': float},
                'memory_delta_mb': {'mean': float, 'std': float},
                'cpu_percent': {'mean': float}
            }
        """
        if not self.metrics:
            return {}

        latencies = [m['latency_ms'] for m in self.metrics]
        memories = [m['memory_delta_mb'] for m in self.metrics]
        cpus = [m['cpu_percent'] for m in self.metrics]

        return {
            'latency_ms': {
                'mean': mean(latencies),
                'std': stdev(latencies) if len(latencies) > 1 else 0,
                'p50': self._compute_percentile(latencies, 50),
                'p95': self._compute_percentile(latencies, 95)
            },
            'memory_delta_mb': {
                'mean': mean(memories),
                'std': stdev(memories) if len(memories) > 1 else 0
            },
            'cpu_percent': {
                'mean': mean(cpus)
            }
        }

    def _measure_memory(self) -> int:
        """
        Current process memory in bytes.

        Returns:
            memory usage in bytes
        """
        return self.process.memory_info().rss

    def _compute_percentile(self, values: List[float], percentile: int) -> float:
        """
        Compute percentile without numpy.

        Args:
            values: list of values
            percentile: 0-100

        Returns:
            percentile value
        """
        sorted_vals = sorted(values)
        if not sorted_vals:
            return 0.0

        idx = int(len(sorted_vals) * percentile / 100)
        idx = min(idx, len(sorted_vals) - 1)

        return sorted_vals[idx]
