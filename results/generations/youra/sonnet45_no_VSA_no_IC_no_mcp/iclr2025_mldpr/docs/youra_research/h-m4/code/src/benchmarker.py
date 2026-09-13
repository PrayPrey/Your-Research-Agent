"""Performance Benchmarker - h-m4 Modules 4 & 5"""
import time
from typing import Dict, Any, List
from datasets import load_dataset


class PerformanceBenchmarker:
    """Baseline and instrumented performance benchmarks."""

    def __init__(self, performance_tracker: 'PerformanceTracker' = None):
        """
        Initialize benchmarker.

        Args:
            performance_tracker: PerformanceTracker instance (for instrumented mode)
        """
        self.performance_tracker = performance_tracker

    def run_baseline_benchmark(
        self,
        dataset_configs: List[Dict[str, Any]],
        runs_per_dataset: int = 100
    ) -> Dict[str, Dict[str, float]]:
        """
        Run baseline benchmarks (native load_dataset).

        Args:
            dataset_configs: [{'name': str, 'config': str, 'split': str, 'size': str}]
            runs_per_dataset: number of runs per dataset

        Returns:
            {
                'small': {'mean_ms': float, 'std_ms': float, 'runs': int},
                'medium': {...},
                ...
            }
        """
        results = {}

        for config in dataset_configs:
            size = config['size']  # 'small', 'medium', 'large', 'xlarge'
            dataset_name = config['name']
            dataset_config = config.get('config')
            split = config.get('split', 'train[:100]')

            latencies = []

            for _ in range(runs_per_dataset):
                start = time.time()
                if dataset_config:
                    load_dataset(dataset_name, dataset_config, split=split)
                else:
                    load_dataset(dataset_name, split=split)
                latency = (time.time() - start) * 1000  # ms
                latencies.append(latency)

            mean_lat = sum(latencies) / len(latencies)
            std_lat = (sum((x - mean_lat) ** 2 for x in latencies) / len(latencies)) ** 0.5

            results[size] = {
                'mean_ms': mean_lat,
                'std_ms': std_lat,
                'runs': runs_per_dataset,
                'dataset': dataset_name
            }

        return results

    def run_instrumented_benchmark(
        self,
        dataset_configs: List[Dict[str, Any]],
        runs_per_dataset: int = 100
    ) -> Dict[str, Dict[str, float]]:
        """
        Run instrumented benchmarks (with PerformanceTracker).

        Args:
            dataset_configs: [{'name': str, 'config': str, 'split': str, 'size': str}]
            runs_per_dataset: number of runs per dataset

        Returns:
            {
                'small': {'mean_ms': float, 'std_ms': float, 'overhead_pct': float, 'runs': int},
                ...
            }
        """
        if not self.performance_tracker:
            raise ValueError("PerformanceTracker required for instrumented benchmark")

        results = {}

        for config in dataset_configs:
            size = config['size']
            dataset_name = config['name']
            dataset_config = config.get('config')
            split = config.get('split', 'train[:100]')

            # Reset tracker metrics
            self.performance_tracker.metrics = []

            for _ in range(runs_per_dataset):
                if dataset_config:
                    self.performance_tracker.track_operation(
                        load_dataset,
                        dataset_name,
                        dataset_config,
                        split=split
                    )
                else:
                    self.performance_tracker.track_operation(
                        load_dataset,
                        dataset_name,
                        split=split
                    )

            # Get aggregate metrics
            agg = self.performance_tracker.get_metrics()

            results[size] = {
                'mean_ms': agg['latency_ms']['mean'],
                'std_ms': agg['latency_ms']['std'],
                'p95_ms': agg['latency_ms']['p95'],
                'memory_delta_mb': agg['memory_delta_mb']['mean'],
                'cpu_percent': agg['cpu_percent']['mean'],
                'runs': runs_per_dataset,
                'dataset': dataset_name
            }

        return results

    def compute_overhead(
        self,
        baseline: Dict[str, Dict[str, float]],
        instrumented: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Compute overhead percentage.

        Args:
            baseline: baseline results
            instrumented: instrumented results

        Returns:
            {'small': overhead_pct, 'medium': overhead_pct, ...}
        """
        overhead = {}

        for size in baseline.keys():
            if size in instrumented:
                base_mean = baseline[size]['mean_ms']
                inst_mean = instrumented[size]['mean_ms']
                overhead[size] = ((inst_mean - base_mean) / base_mean) * 100

        return overhead
