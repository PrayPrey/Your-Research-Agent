"""Verification Module for SpecBridge.

This module implements:
1. Test-based verification against test cases
2. Specification validation using test scenarios
3. Counterexample extraction for refinement
"""

import ast
import traceback
from typing import Tuple, Optional

def verify_code_with_tests(code: str, test_cases: list, func_name: str) -> Tuple[bool, int, int, Optional[dict], str]:
    """Verify generated code against test cases.

    Returns:
        - success: Whether all tests pass
        - passed: Number of passed tests
        - total: Total number of tests
        - counterexample: First failing test case (if any)
        - error_msg: Error message (if any)
    """
    passed = 0
    total = len(test_cases)
    counterexample = None
    error_msg = ""

    if not test_cases:
        return True, 0, 0, None, ""

    # Create execution context
    exec_globals = {}

    try:
        # Execute the code to define the function
        exec(code, exec_globals)

        if func_name not in exec_globals:
            return False, 0, total, test_cases[0], f"Function {func_name} not defined"

        func = exec_globals[func_name]

        # Run each test case
        for test in test_cases:
            try:
                inputs = test["input"]
                expected = test["expected"]

                # Handle different input formats
                if isinstance(inputs, dict):
                    result = func(**inputs)
                else:
                    result = func(inputs)

                # Compare results
                if compare_results(result, expected):
                    passed += 1
                else:
                    if counterexample is None:
                        counterexample = {
                            "input": inputs,
                            "expected": expected,
                            "actual": result
                        }
                        error_msg = f"Expected {expected}, got {result}"
            except Exception as e:
                if counterexample is None:
                    counterexample = {
                        "input": inputs,
                        "expected": expected,
                        "error": str(e)
                    }
                    error_msg = f"Runtime error: {str(e)}"

    except SyntaxError as e:
        return False, 0, total, test_cases[0] if test_cases else None, f"Syntax error: {str(e)}"
    except Exception as e:
        return False, 0, total, test_cases[0] if test_cases else None, f"Execution error: {str(e)}"

    success = passed == total
    return success, passed, total, counterexample, error_msg

def compare_results(actual, expected) -> bool:
    """Compare actual and expected results with type flexibility."""
    # Direct equality
    if actual == expected:
        return True

    # Handle None
    if actual is None and expected is None:
        return True

    # Handle lists/sets (order may vary for some problems)
    if isinstance(actual, (list, set)) and isinstance(expected, (list, set)):
        try:
            if set(actual) == set(expected):
                return True
        except TypeError:
            pass

        # Try sorted comparison
        try:
            if sorted(actual) == sorted(expected):
                return True
        except TypeError:
            pass

    # Handle floating point
    if isinstance(actual, float) and isinstance(expected, (int, float)):
        if abs(actual - expected) < 1e-9:
            return True

    # Handle nested structures (like partition results)
    if isinstance(actual, list) and isinstance(expected, list):
        if len(actual) == len(expected):
            all_match = True
            for a, e in zip(actual, expected):
                if isinstance(a, list) and isinstance(e, list):
                    # For partitions, check if sets match
                    try:
                        if set(a) != set(e) and sorted(a) != sorted(e):
                            all_match = False
                            break
                    except TypeError:
                        if a != e:
                            all_match = False
                            break
                elif a != e:
                    all_match = False
                    break
            if all_match:
                return True

    return False

def validate_specification_syntax(spec: dict) -> Tuple[bool, str]:
    """Validate that specification is syntactically correct Python."""
    try:
        pre = spec.get("precondition", "True")
        post = spec.get("postcondition", "True")

        # Check if they parse as Python expressions
        ast.parse(pre, mode='eval')
        ast.parse(post, mode='eval')

        return True, ""
    except SyntaxError as e:
        return False, f"Specification syntax error: {str(e)}"

def check_specification_satisfiability(spec: dict, test_cases: list) -> Tuple[bool, str]:
    """Check if specification is satisfiable using test cases.

    Returns True if at least one test case satisfies the precondition.
    """
    pre = spec.get("precondition", "True")

    for test in test_cases:
        inputs = test["input"]
        try:
            # Create local context with input variables
            local_context = dict(inputs)
            result = eval(pre, {"__builtins__": {}}, local_context)
            if result:
                return True, "Specification is satisfiable"
        except Exception:
            continue

    return False, "No test case satisfies precondition"

class VerificationResult:
    """Container for verification results."""

    def __init__(self, success: bool, passed: int, total: int,
                 counterexample: Optional[dict] = None, error_msg: str = ""):
        self.success = success
        self.passed = passed
        self.total = total
        self.counterexample = counterexample
        self.error_msg = error_msg
        self.pass_rate = passed / total if total > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "passed": self.passed,
            "total": self.total,
            "pass_rate": self.pass_rate,
            "counterexample": self.counterexample,
            "error_msg": self.error_msg
        }
