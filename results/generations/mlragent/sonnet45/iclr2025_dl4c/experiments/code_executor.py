"""
Code execution and test validation module.
"""

import ast
import sys
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, List, Tuple, Any
import signal


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException("Code execution timed out")


class CodeExecutor:
    """Execute Python code and validate against test cases."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def execute_code(self, code: str, test_cases: List[Dict]) -> Tuple[bool, List[Dict], str]:
        """
        Execute code and run test cases.

        Returns:
            - success: Whether all tests passed
            - results: List of test results
            - error_msg: Error message if any
        """
        results = []
        error_msg = ""

        try:
            # Parse and validate syntax
            ast.parse(code)

            # Create execution namespace
            exec_globals = {}
            exec_locals = {}

            # Execute the code
            exec(code, exec_globals, exec_locals)

            # Find the function
            function_name = None
            for name, obj in exec_locals.items():
                if callable(obj) and not name.startswith('_'):
                    function_name = name
                    break

            if not function_name:
                return False, [], "No function found in code"

            func = exec_locals[function_name]

            # Run test cases
            all_passed = True
            for i, test in enumerate(test_cases):
                try:
                    # Set timeout
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(self.timeout)

                    # Execute function
                    result = func(*test["input"])

                    # Cancel timeout
                    signal.alarm(0)

                    passed = result == test["expected"]
                    results.append({
                        "test_id": i,
                        "passed": passed,
                        "expected": test["expected"],
                        "actual": result,
                        "error": None
                    })
                    if not passed:
                        all_passed = False

                except TimeoutException:
                    signal.alarm(0)
                    results.append({
                        "test_id": i,
                        "passed": False,
                        "expected": test["expected"],
                        "actual": None,
                        "error": "Timeout"
                    })
                    all_passed = False

                except Exception as e:
                    signal.alarm(0)
                    results.append({
                        "test_id": i,
                        "passed": False,
                        "expected": test["expected"],
                        "actual": None,
                        "error": str(e)
                    })
                    all_passed = False

            return all_passed, results, error_msg

        except SyntaxError as e:
            error_msg = f"Syntax Error: {str(e)}"
            return False, [], error_msg
        except Exception as e:
            error_msg = f"Execution Error: {str(e)}\n{traceback.format_exc()}"
            return False, [], error_msg

    def get_execution_trace(self, code: str, test_case: Dict) -> Dict[str, Any]:
        """
        Get execution trace for debugging.

        Returns trace information including variables, control flow, etc.
        """
        trace_info = {
            "variables": {},
            "control_flow": [],
            "error_location": None
        }

        try:
            exec_globals = {}
            exec_locals = {}
            exec(code, exec_globals, exec_locals)

            # Find function
            function_name = None
            for name, obj in exec_locals.items():
                if callable(obj) and not name.startswith('_'):
                    function_name = name
                    break

            if function_name:
                func = exec_locals[function_name]
                try:
                    result = func(*test_case["input"])
                    trace_info["result"] = result
                except Exception as e:
                    trace_info["error"] = str(e)
                    trace_info["traceback"] = traceback.format_exc()

        except Exception as e:
            trace_info["error"] = str(e)

        return trace_info
