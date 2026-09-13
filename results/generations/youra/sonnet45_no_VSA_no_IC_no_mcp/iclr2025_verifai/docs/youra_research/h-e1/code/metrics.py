import time
import ast
from typing import Callable, Any

def time_generation(fn: Callable) -> tuple[Any, float]:
    """Time a generation function execution."""
    start = time.time()
    result = fn()
    elapsed = time.time() - start
    return result, elapsed

def measure_ast_latency(candidates: list[list[str]]) -> dict:
    """Measure AST parse latency statistics."""
    latencies = []

    for prompt_candidates in candidates:
        for code in prompt_candidates:
            start = time.time()
            try:
                ast.parse(code)
            except SyntaxError:
                pass
            elapsed_ms = (time.time() - start) * 1000
            latencies.append(elapsed_ms)

    return {
        'mean': sum(latencies) / len(latencies) if latencies else 0,
        'min': min(latencies) if latencies else 0,
        'max': max(latencies) if latencies else 0,
        'all': latencies
    }

def compute_gate_metrics(time_sec: float, latency_ms: float, time_target: int, latency_target: int) -> dict:
    """Compute gate pass/fail status."""
    time_pass = time_sec < time_target
    latency_pass = latency_ms < latency_target

    return {
        'time_target': time_target,
        'time_actual': time_sec,
        'time_pass': time_pass,
        'latency_target': latency_target,
        'latency_actual': latency_ms,
        'latency_pass': latency_pass,
        'gate_pass': time_pass and latency_pass
    }
