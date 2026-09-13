"""
Execution Feedback Module for ExePlay
Handles code execution and structured execution feedback (SEF) collection
"""
import subprocess
import sys
import traceback
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
import ast
import signal
import contextlib
import io


@dataclass
class ExecutionResult:
    """Structured Execution Feedback (SEF)"""
    compilation_status: bool = False
    test_results: List[bool] = field(default_factory=list)
    outputs: List[Any] = field(default_factory=list)
    expected_outputs: List[Any] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    coverage: float = 0.0
    runtime_ms: float = 0.0
    passed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "compilation_status": self.compilation_status,
            "test_results": self.test_results,
            "outputs": [str(o) for o in self.outputs],
            "expected_outputs": [str(e) for e in self.expected_outputs],
            "error_messages": self.error_messages,
            "coverage": self.coverage,
            "runtime_ms": self.runtime_ms,
            "passed": self.passed
        }


class TimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutError("Execution timed out")


def execute_code_with_tests(code: str, test_cases: List[Dict[str, Any]], timeout: int = 5) -> ExecutionResult:
    """
    Execute code with test cases and collect execution feedback.

    Args:
        code: The code to execute
        test_cases: List of dicts with 'input' and 'expected_output' keys
        timeout: Maximum execution time in seconds

    Returns:
        ExecutionResult with structured execution feedback
    """
    result = ExecutionResult()

    # Check syntax/compilation
    try:
        ast.parse(code)
        result.compilation_status = True
    except SyntaxError as e:
        result.compilation_status = False
        result.error_messages.append(f"SyntaxError: {str(e)}")
        return result

    # Execute with each test case
    for test in test_cases:
        test_input = test.get('input', '')
        expected = test.get('expected_output', None)
        entry_point = test.get('entry_point', None)

        result.expected_outputs.append(expected)

        try:
            # Create execution environment
            exec_globals = {}

            # Execute the code to define functions
            exec(code, exec_globals)

            # Run the test
            if entry_point and entry_point in exec_globals:
                func = exec_globals[entry_point]
                if isinstance(test_input, tuple):
                    output = func(*test_input)
                elif isinstance(test_input, dict):
                    output = func(**test_input)
                else:
                    output = func(test_input)
            else:
                # Try to find a function in the code
                for name, obj in exec_globals.items():
                    if callable(obj) and not name.startswith('_'):
                        if isinstance(test_input, tuple):
                            output = obj(*test_input)
                        elif isinstance(test_input, dict):
                            output = obj(**test_input)
                        else:
                            output = obj(test_input)
                        break
                else:
                    output = None

            result.outputs.append(output)

            # Check if output matches expected
            if expected is not None:
                test_passed = output == expected
            else:
                test_passed = True  # No expected output to compare

            result.test_results.append(test_passed)

        except Exception as e:
            result.outputs.append(None)
            result.test_results.append(False)
            result.error_messages.append(f"{type(e).__name__}: {str(e)}")

    # Calculate coverage (simplified: based on test pass rate)
    if result.test_results:
        result.coverage = sum(result.test_results) / len(result.test_results)

    # Determine overall pass
    result.passed = all(result.test_results) if result.test_results else False

    return result


def compute_execution_quality_score(
    result: ExecutionResult,
    reference_solution: Optional[str] = None,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Compute the Execution Quality Score (EQS) for a solution.

    EQS = alpha * test_pass_rate + beta * coverage + gamma * error_proximity + delta * behavior_similarity

    Args:
        result: ExecutionResult from code execution
        reference_solution: Optional reference solution for comparison
        weights: Optional custom weights for EQS components

    Returns:
        Float EQS score between 0 and 1
    """
    if weights is None:
        weights = {
            "test_pass_rate": 0.4,
            "coverage": 0.2,
            "error_proximity": 0.2,
            "behavior_similarity": 0.2
        }

    # Test pass rate
    if result.test_results:
        test_pass_rate = sum(result.test_results) / len(result.test_results)
    else:
        test_pass_rate = 0.0

    # Coverage score
    coverage = result.coverage

    # Error proximity (simplified: lower score for more/severe errors)
    if not result.compilation_status:
        error_proximity = 0.0
    elif result.error_messages:
        # Fewer errors = higher score
        error_proximity = max(0, 1 - len(result.error_messages) * 0.2)
    else:
        error_proximity = 1.0

    # Behavior similarity (simplified: based on output matching)
    if result.outputs and result.expected_outputs:
        matching_outputs = sum(
            1 for o, e in zip(result.outputs, result.expected_outputs)
            if o == e
        )
        behavior_similarity = matching_outputs / len(result.expected_outputs)
    else:
        behavior_similarity = 0.0

    # Compute weighted EQS
    eqs = (
        weights["test_pass_rate"] * test_pass_rate +
        weights["coverage"] * coverage +
        weights["error_proximity"] * error_proximity +
        weights["behavior_similarity"] * behavior_similarity
    )

    return eqs


def extract_code_from_response(response: str) -> str:
    """Extract code from LLM response, handling markdown code blocks."""
    # Try to find code block
    code_pattern = r'```(?:python)?\n?(.*?)```'
    matches = re.findall(code_pattern, response, re.DOTALL)

    if matches:
        return matches[0].strip()

    # If no code block, return the response as-is (might be raw code)
    return response.strip()


def generate_critique(
    code: str,
    result: ExecutionResult,
    problem_description: str
) -> str:
    """
    Generate a natural language critique of failed code.
    This is a simplified version - in full implementation, this would use the LLM.

    Args:
        code: The failed code
        result: ExecutionResult with error information
        problem_description: The original problem

    Returns:
        Natural language critique
    """
    critique_parts = []

    if not result.compilation_status:
        critique_parts.append("The code has a syntax error and cannot be compiled.")
        if result.error_messages:
            critique_parts.append(f"Error: {result.error_messages[0]}")
    else:
        if result.error_messages:
            critique_parts.append("The code has runtime errors:")
            for err in result.error_messages[:3]:  # Limit to first 3 errors
                critique_parts.append(f"  - {err}")

        if result.test_results and not all(result.test_results):
            failed_tests = [i for i, passed in enumerate(result.test_results) if not passed]
            critique_parts.append(f"Failed test cases: {failed_tests}")

            for i in failed_tests[:2]:  # Show first 2 failures
                if i < len(result.outputs) and i < len(result.expected_outputs):
                    critique_parts.append(
                        f"  Test {i}: Got {result.outputs[i]}, expected {result.expected_outputs[i]}"
                    )

    if not critique_parts:
        return "The code appears to be correct."

    return "\n".join(critique_parts)
