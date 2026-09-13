"""
Code Execution Sandbox for Runtime and Error Data Collection
Executes benchmark test cases to extract real runtime and error statistics
Based on 03_logic.md and 03_architecture.md specifications
"""
import subprocess
import time
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import traceback


class CodeExecutor:
    """
    Safe execution environment for code generation benchmarks.
    Measures runtime and categorizes errors from actual test execution.
    """

    def __init__(self, timeout: int = 30, max_output_kb: int = 1024):
        self.timeout = timeout
        self.max_output_kb = max_output_kb

    def execute_with_test(self, code: str, test_case: str) -> Dict:
        """
        Execute code with a test case and measure runtime/errors.

        Args:
            code: Generated code solution
            test_case: Test assertion(s) to run

        Returns:
            Dict with keys: passed, runtime_ms, error_type, error_msg
        """
        result = {
            'passed': False,
            'runtime_ms': None,
            'error_type': None,
            'error_msg': None
        }

        # Create temporary file for execution
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Combine code and test
            full_code = f"{code}\n\n{test_case}"
            f.write(full_code)
            temp_path = f.name

        try:
            # Measure execution time
            start_time = time.time()

            proc = subprocess.run(
                ['python3', temp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            end_time = time.time()
            runtime_ms = (end_time - start_time) * 1000

            if proc.returncode == 0:
                # Successful execution
                result['passed'] = True
                result['runtime_ms'] = runtime_ms
            else:
                # Execution failed - categorize error
                result['passed'] = False
                result['error_type'] = self._categorize_error(proc.stderr)
                result['error_msg'] = proc.stderr[:500]  # Truncate long errors

        except subprocess.TimeoutExpired:
            result['passed'] = False
            result['error_type'] = 'timeout'
            result['error_msg'] = f'Execution exceeded {self.timeout}s timeout'

        except Exception as e:
            result['passed'] = False
            result['error_type'] = 'runtime'
            result['error_msg'] = str(e)

        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass

        return result

    def _categorize_error(self, stderr: str) -> str:
        """
        Categorize error based on stderr output.

        Categories:
        - syntax: SyntaxError, IndentationError
        - runtime: NameError, TypeError, ValueError, AssertionError, etc.
        - timeout: Execution exceeded time limit
        """
        stderr_lower = stderr.lower()

        # Syntax errors
        if 'syntaxerror' in stderr_lower or 'indentationerror' in stderr_lower:
            return 'syntax'

        # Everything else is runtime error
        return 'runtime'

    def execute_benchmark_problem(
        self,
        code: str,
        test_cases: List[str],
        max_tests: int = 10
    ) -> Dict:
        """
        Execute code on multiple test cases from a benchmark problem.

        Args:
            code: Generated solution code
            test_cases: List of test assertions
            max_tests: Maximum number of tests to run (for efficiency)

        Returns:
            Dict with aggregated results:
            - n_passed: Number of tests passed
            - n_failed: Number of tests failed
            - runtimes_ms: List of runtimes for passing tests
            - error_types: List of error types for failing tests
        """
        results = {
            'n_passed': 0,
            'n_failed': 0,
            'runtimes_ms': [],
            'error_types': []
        }

        # Limit number of tests for efficiency
        test_subset = test_cases[:max_tests]

        for test in test_subset:
            exec_result = self.execute_with_test(code, test)

            if exec_result['passed']:
                results['n_passed'] += 1
                results['runtimes_ms'].append(exec_result['runtime_ms'])
            else:
                results['n_failed'] += 1
                results['error_types'].append(exec_result['error_type'])

        return results


def extract_runtime_and_errors_from_benchmark(
    benchmark_loader,
    model_name: str,
    sample_size: int = 50
) -> Tuple[List[Dict], List[Dict]]:
    """
    Extract real runtime and error data from benchmark execution.

    For EXISTENCE hypothesis: We demonstrate the capability by sampling
    problems from the benchmark and executing placeholder solutions.

    Args:
        benchmark_loader: Loaded benchmark dataset
        model_name: Model name (for logging)
        sample_size: Number of problems to sample

    Returns:
        (passing_solutions, failed_solutions) with runtime/error data
    """
    passing = []
    failed = []

    # For EXISTENCE proof: Use benchmark problems with reference solutions
    # In production: This would execute actual model-generated code

    dataset = benchmark_loader.dataset
    if dataset is None:
        # No dataset available - return empty
        return [], []

    # Get test split
    test_split = dataset.get('test', dataset.get('validation', None))
    if test_split is None:
        return [], []

    # Sample problems
    import random
    problems = list(test_split)
    random.shuffle(problems)
    sampled_problems = problems[:min(sample_size, len(problems))]

    executor = CodeExecutor()

    for problem in sampled_problems:
        # Extract problem components based on dataset format
        code = None
        test = None

        if 'prompt' in problem and 'canonical_solution' in problem:
            # HumanEval format
            code = problem.get('prompt', '') + '\n' + problem.get('canonical_solution', '')
            test = problem.get('test', '')
        elif 'text' in problem and 'code' in problem:
            # MBPP format
            code = problem['code']
            test_list = problem.get('test_list', [])
            test = '\n'.join(test_list) if test_list else ''
        else:
            continue

        if not code or not test:
            continue

        # Execute the test
        result = executor.execute_with_test(code, test)

        if result['passed']:
            passing.append({
                'runtime_ms': result['runtime_ms']
            })
        else:
            failed.append({
                'error_type': result['error_type']
            })

    return passing, failed
