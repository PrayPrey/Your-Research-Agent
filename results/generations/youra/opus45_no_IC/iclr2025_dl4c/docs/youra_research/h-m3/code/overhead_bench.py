"""OverheadBenchmark: Measure trace collection overhead vs baseline execution."""

import time
import statistics
from typing import Dict, List, Tuple, Any
from trace_collector import ExecutionTraceCollector


class OverheadBenchmark:
    """Benchmark trace collection overhead against baseline execution."""

    def __init__(self, collector: ExecutionTraceCollector = None):
        self.collector = collector or ExecutionTraceCollector()

    def measure(self, code_str: str, test_input: str = "", timeout: float = 5.0) -> Dict[str, float]:
        """Measure overhead for a single code sample.

        Returns:
            Dict with trace_time, baseline_time, overhead ratio.
        """
        start = time.perf_counter()
        self.collector.collect_trace(code_str, test_input, timeout)
        trace_time = time.perf_counter() - start

        full_code = code_str + "\n" + test_input if test_input else code_str
        try:
            code_obj = compile(full_code, "<baseline>", "exec")
        except SyntaxError:
            return {"trace_time": trace_time, "baseline_time": 0.0, "overhead": float("inf")}

        start = time.perf_counter()
        try:
            exec(code_obj, {"__builtins__": __builtins__}, {})
        except Exception:
            pass
        baseline_time = time.perf_counter() - start

        if baseline_time < 1e-9:
            baseline_time = 1e-9

        return {
            "trace_time": trace_time,
            "baseline_time": baseline_time,
            "overhead": trace_time / baseline_time
        }

    def run_batch(
        self,
        samples: List[Tuple[str, str]],
        timeout: float = 5.0
    ) -> Dict[str, Any]:
        """Run benchmark on multiple samples, compute aggregate stats.

        Args:
            samples: List of (code_str, test_input) tuples
            timeout: Per-sample timeout

        Returns:
            Dict with mean, median, p95 overhead and individual results.
        """
        results = []
        overheads = []

        for code_str, test_input in samples:
            result = self.measure(code_str, test_input, timeout)
            results.append(result)
            if result["overhead"] < float("inf"):
                overheads.append(result["overhead"])

        if not overheads:
            return {
                "mean": float("inf"),
                "median": float("inf"),
                "p95": float("inf"),
                "min": float("inf"),
                "max": float("inf"),
                "num_samples": len(samples),
                "valid_samples": 0,
                "results": results
            }

        overheads_sorted = sorted(overheads)
        p95_idx = int(len(overheads_sorted) * 0.95)

        return {
            "mean": statistics.mean(overheads),
            "median": statistics.median(overheads),
            "p95": overheads_sorted[min(p95_idx, len(overheads_sorted) - 1)],
            "min": min(overheads),
            "max": max(overheads),
            "num_samples": len(samples),
            "valid_samples": len(overheads),
            "results": results
        }
