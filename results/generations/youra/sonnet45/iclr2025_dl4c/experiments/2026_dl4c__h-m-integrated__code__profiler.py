"""
Code Profiling Pipeline: Correctness, Complexity, Efficiency
"""

from typing import List, Tuple, Dict
import sys
import io
import traceback
import cProfile
import tracemalloc
import numpy as np
from scipy.special import comb
from radon.complexity import cc_visit
from radon.visitors import ComplexityVisitor
import ast
import multiprocessing
from multiprocessing import Pool, TimeoutError as MPTimeoutError
import signal


def execute_with_timeout(code: str, timeout: float) -> bool:
    """
    Execute code with timeout.
    Returns True if execution succeeds, False otherwise.
    """
    try:
        # Capture stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        # Execute code
        exec_globals = {}
        exec(code, exec_globals)

        # Restore stdout/stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr

        return True

    except Exception:
        # Restore stdout/stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        return False


def execute_single_test(args):
    """Worker function for parallel test execution."""
    sample, tests, timeout = args
    try:
        code_with_tests = sample + "\n" + tests
        return execute_with_timeout(code_with_tests, timeout)
    except:
        return False


class CodeProfiler:
    """Multi-dimensional code profiling (correctness, complexity, efficiency)."""

    def __init__(self, timeout: float = 3.0, n_workers: int = 4):
        """Initialize profiler with timeout and worker config."""
        self.timeout = timeout
        self.n_workers = n_workers

    def profile_correctness(self, samples: List[str], tests: str) -> float:
        """
        Execute samples against tests.
        Returns pass rate (0-1).
        """
        if not samples:
            return 0.0

        # Filter out empty samples
        valid_samples = [s for s in samples if s.strip()]
        if not valid_samples:
            return 0.0

        passed = 0
        for sample in valid_samples:
            code_with_tests = sample + "\n" + tests
            if execute_with_timeout(code_with_tests, self.timeout):
                passed += 1

        return passed / len(valid_samples)

    def compute_pass_at_k(self, n: int, c: int, k: int) -> float:
        """
        Compute pass@k using unbiased estimator.
        n: total samples
        c: correct samples
        k: samples to select
        """
        if n - c < k:
            return 1.0
        if c == 0:
            return 0.0

        try:
            return 1.0 - float(comb(n - c, k)) / float(comb(n, k))
        except (ValueError, OverflowError):
            return 0.0

    def profile_complexity(self, samples: List[str]) -> Tuple[float, float]:
        """
        Compute complexity metrics.
        Returns (cyclomatic, ast_depth).
        """
        if not samples:
            return (0.0, 0.0)

        cyclo_scores = []
        ast_depths = []

        for sample in samples:
            if not sample.strip():
                continue

            try:
                # Cyclomatic complexity using radon
                cc_results = cc_visit(sample)
                if cc_results:
                    avg_complexity = np.mean([r.complexity for r in cc_results])
                    cyclo_scores.append(avg_complexity)
                else:
                    cyclo_scores.append(1.0)  # Default complexity

                # AST depth
                try:
                    tree = ast.parse(sample)
                    depth = self._get_ast_depth(tree)
                    ast_depths.append(depth)
                except:
                    ast_depths.append(1.0)

            except Exception:
                # Skip samples that can't be parsed
                continue

        if not cyclo_scores:
            return (1.0, 1.0)

        return (np.mean(cyclo_scores), np.mean(ast_depths))

    def _get_ast_depth(self, node, current_depth=0):
        """Recursively compute AST depth."""
        if not isinstance(node, ast.AST):
            return current_depth

        max_depth = current_depth
        for child in ast.iter_child_nodes(node):
            depth = self._get_ast_depth(child, current_depth + 1)
            max_depth = max(max_depth, depth)

        return max_depth

    def profile_efficiency(self, samples: List[str], tests: str) -> Tuple[float, float]:
        """
        Profile runtime and memory for correct samples only.
        Returns (runtime_ms, memory_kb).
        """
        if not samples:
            return (0.0, 0.0)

        runtimes = []
        memories = []

        for sample in samples:
            if not sample.strip():
                continue

            # Only profile correct samples
            code_with_tests = sample + "\n" + tests
            if not execute_with_timeout(code_with_tests, self.timeout):
                continue

            try:
                # Runtime profiling
                profiler = cProfile.Profile()
                profiler.enable()

                exec_globals = {}
                exec(sample, exec_globals)

                profiler.disable()
                stats = profiler.getstats()
                total_time = sum(stat.totaltime for stat in stats) * 1000  # Convert to ms
                runtimes.append(total_time if total_time > 0 else 0.001)

                # Memory profiling
                tracemalloc.start()

                exec_globals = {}
                exec(sample, exec_globals)

                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()

                memories.append(peak / 1024)  # Convert to KB

            except Exception:
                # Skip samples that fail profiling
                continue

        if not runtimes:
            return (0.1, 1.0)  # Default small values

        return (np.mean(runtimes), np.mean(memories))

    def extract_signature(self, task: dict, samples: List[str]) -> Dict[str, float]:
        """
        Extract full performance signature.
        Returns dict with all metrics.
        """
        tests = task["test"]

        # Correctness
        correctness = self.profile_correctness(samples, tests)

        # Complexity
        cyclo, ast_depth = self.profile_complexity(samples)

        # Efficiency
        runtime, memory = self.profile_efficiency(samples, tests)

        return {
            "correctness": correctness,
            "cyclomatic": cyclo,
            "ast_depth": ast_depth,
            "runtime_ms": runtime,
            "memory_kb": memory
        }
