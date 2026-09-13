"""Safe execution of generated Python code against test cases."""

import subprocess
import tempfile
import os
from typing import List, Tuple


class CodeExecutor:
    """Safe execution of generated Python code against test cases."""

    def __init__(self, timeout: float = 5.0):
        """
        Args:
            timeout: Max execution time per test (seconds)
        """
        self.timeout = timeout
        self.restricted_imports = {'os', 'subprocess', 'sys', 'eval', 'exec', '__import__'}

    def execute_test(
        self,
        code: str,
        test_case: str,
        setup_code: str = ""
    ) -> bool:
        """
        Execute code against single test case.

        Args:
            code: Generated Python function
            test_case: Assert statement (e.g., "assert f(1) == 2")
            setup_code: Import statements

        Returns:
            success: True if test passes, False otherwise
        """
        # Validate no restricted imports
        if self._has_restricted_imports(code):
            return False

        # Combine setup, code, test
        full_code = f"{setup_code}\n{code}\n{test_case}"

        try:
            # Execute in subprocess with timeout
            result = subprocess.run(
                ['python3', '-c', full_code],
                timeout=self.timeout,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False

    def evaluate_problem(
        self,
        code: str,
        test_list: List[str],
        setup_code: str = ""
    ) -> Tuple[bool, int]:
        """
        Evaluate code against all test cases.

        Args:
            code: Generated solution
            test_list: List of assert statements
            setup_code: Import dependencies

        Returns:
            is_correct: True if ALL tests pass
            num_passed: Number of tests passed
        """
        num_passed = 0
        for test_case in test_list:
            if self.execute_test(code, test_case, setup_code):
                num_passed += 1

        is_correct = (num_passed == len(test_list))
        return is_correct, num_passed

    def _has_restricted_imports(self, code: str) -> bool:
        """Check for dangerous imports."""
        code_lower = code.lower()
        for module in self.restricted_imports:
            if f"import {module}" in code_lower or f"from {module}" in code_lower:
                return True
        return False

    def batch_evaluate(
        self,
        codes: List[str],
        test_lists: List[List[str]],
        setup_codes: List[str]
    ) -> List[Tuple[bool, int]]:
        """
        Evaluate multiple code samples.

        Args:
            codes: List of generated solutions
            test_lists: List of test case lists
            setup_codes: List of setup code strings

        Returns:
            results: List of (is_correct, num_passed) tuples
        """
        results = []
        for code, test_list, setup_code in zip(codes, test_lists, setup_codes):
            is_correct, num_passed = self.evaluate_problem(code, test_list, setup_code)
            results.append((is_correct, num_passed))
        return results
