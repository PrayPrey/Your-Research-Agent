"""High-precision timing benchmark"""

import time
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import Dict, Callable, List
import logging

logger = logging.getLogger(__name__)


class TimingBenchmark:
    """High-precision timing measurement for extraction methods"""

    def __init__(self, warmup_runs: int = 1):
        self.warmup_runs = warmup_runs

    def measure_extraction_time(self, extractor_fn: Callable, model_names: List[str]) -> Dict:
        """
        Measure extraction time with warmup.

        Args:
            extractor_fn: Callable extraction function (extract_batch)
            model_names: Model list

        Returns:
            {
                'total_time': float,
                'avg_time': float,
                'median_time': float,
                'p90_time': float,
                'per_model': dict[str, float]
            }
        """
        # Warmup runs (not counted in results)
        if self.warmup_runs > 0:
            warmup_models = model_names[:self.warmup_runs]
            logger.info(f"Running warmup with {len(warmup_models)} model(s)")
            _ = extractor_fn(warmup_models)

        # Actual measurement
        start_time = time.perf_counter()
        results = extractor_fn(model_names)
        end_time = time.perf_counter()

        total_time = results.get('total_time', end_time - start_time)
        per_model_times = results.get('per_model_times', {})

        # Compute statistics
        times_list = list(per_model_times.values())
        if times_list:
            avg_time = np.mean(times_list)
            median_time = np.median(times_list)
            p90_time = np.percentile(times_list, 90)
        else:
            avg_time = median_time = p90_time = 0.0

        timing_results = {
            'total_time': total_time,
            'avg_time': avg_time,
            'median_time': median_time,
            'p90_time': p90_time,
            'per_model': per_model_times
        }

        logger.info(f"Extraction timing: total={total_time:.2f}s, avg={avg_time:.2f}s, median={median_time:.2f}s, p90={p90_time:.2f}s")

        return timing_results

    def compare_methods(self, checkpoint_results: Dict, forward_results: Dict) -> Dict:
        """
        Compute speedup between checkpoint-only and forward-pass.

        Returns:
            {
                'speedup_factor': float,
                'checkpoint_time': float,
                'forward_time': float,
                'per_model_speedup': dict[str, float]
            }
        """
        checkpoint_time = checkpoint_results['total_time']
        forward_time = forward_results['total_time']

        speedup_factor = forward_time / checkpoint_time if checkpoint_time > 0 else 0.0

        # Per-model speedup
        per_model_speedup = {}
        for model_name in checkpoint_results['per_model'].keys():
            if model_name in forward_results['per_model']:
                checkpoint_model_time = checkpoint_results['per_model'][model_name]
                forward_model_time = forward_results['per_model'][model_name]
                per_model_speedup[model_name] = forward_model_time / checkpoint_model_time if checkpoint_model_time > 0 else 0.0

        speedup_results = {
            'speedup_factor': speedup_factor,
            'checkpoint_time': checkpoint_time,
            'forward_time': forward_time,
            'per_model_speedup': per_model_speedup
        }

        logger.info(f"Speedup: {speedup_factor:.2f}x (checkpoint={checkpoint_time:.2f}s, forward={forward_time:.2f}s)")

        return speedup_results

    def plot_timing_comparison(self, results: Dict, output_path: str):
        """Generate bar chart: checkpoint vs forward-pass timing"""
        checkpoint_time = results['checkpoint_time']
        forward_time = results['forward_time']

        fig, ax = plt.subplots(figsize=(10, 6))

        methods = ['Checkpoint-Only', 'Forward-Pass']
        times = [checkpoint_time, forward_time]
        colors = ['#2ca02c', '#d62728']

        bars = ax.bar(methods, times, color=colors, width=0.6)

        ax.set_ylabel('Total Extraction Time (seconds)', fontsize=12)
        ax.set_title('Extraction Time Comparison: Checkpoint-Only vs Forward-Pass', fontsize=14)
        ax.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bar, time_val in zip(bars, times):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{time_val:.1f}s',
                   ha='center', va='bottom', fontsize=11)

        # Add speedup annotation
        speedup = results['speedup_factor']
        ax.text(0.5, max(times) * 0.9,
               f'Speedup: {speedup:.2f}x',
               ha='center', fontsize=13, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()

        logger.info(f"Timing comparison plot saved to {output_path}")

    def save_timing_report(self, results: Dict, output_path: str):
        """Save timing metrics to JSON"""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Timing report saved to {output_path}")
