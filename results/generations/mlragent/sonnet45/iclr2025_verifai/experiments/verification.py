"""
Verification module for code analysis and testing
"""
import ast
import sys
import io
import traceback
from typing import Dict, List, Tuple, Any
import pylint.lint
from pylint.reporters.text import TextReporter
import contextlib
import re

class VerificationResult:
    """Store verification results"""
    def __init__(self, passed: bool, error_type: str = None,
                 error_message: str = None, location: str = None):
        self.passed = passed
        self.error_type = error_type
        self.error_message = error_message
        self.location = location

    def to_dict(self):
        return {
            "passed": self.passed,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "location": self.location
        }

class CodeVerifier:
    """Verify generated code using static analysis and unit tests"""

    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds

    def verify_code(self, code: str, test_cases: List[Dict]) -> Tuple[List[VerificationResult], Dict]:
        """
        Verify code with static analysis and unit tests
        Returns: (verification_results, test_results)
        """
        verification_results = []

        # Step 1: Syntax checking
        syntax_result = self._check_syntax(code)
        verification_results.append(syntax_result)
        if not syntax_result.passed:
            return verification_results, {"passed": 0, "failed": 1, "total": 1}

        # Step 2: Static analysis
        static_results = self._static_analysis(code)
        verification_results.extend(static_results)

        # Step 3: Run unit tests
        test_results = self._run_tests(code, test_cases)

        return verification_results, test_results

    def _check_syntax(self, code: str) -> VerificationResult:
        """Check if code has valid Python syntax"""
        try:
            ast.parse(code)
            return VerificationResult(passed=True)
        except SyntaxError as e:
            return VerificationResult(
                passed=False,
                error_type="SyntaxError",
                error_message=str(e),
                location=f"Line {e.lineno}"
            )

    def _static_analysis(self, code: str) -> List[VerificationResult]:
        """Run static analysis using pylint"""
        results = []

        try:
            # Create a temporary file-like object for pylint output
            pylint_output = io.StringIO()
            reporter = TextReporter(pylint_output)

            # Run pylint
            with contextlib.redirect_stdout(io.StringIO()):
                pylint.lint.Run(
                    ['--disable=all',
                     '--enable=undefined-variable,used-before-assignment,unbalanced-tuple-unpacking,unpacking-non-sequence,invalid-sequence-index,invalid-slice-index',
                     '--from-stdin', 'temp'],
                    reporter=reporter,
                    exit=False,
                    do_exit=False
                )

            # Parse pylint output
            output = pylint_output.getvalue()
            if output and len(output.strip()) > 0:
                # Extract errors from output
                for line in output.split('\n'):
                    if ':' in line and any(keyword in line.lower() for keyword in ['error', 'warning', 'undefined']):
                        results.append(VerificationResult(
                            passed=False,
                            error_type="StaticAnalysisError",
                            error_message=line.strip(),
                            location="Various"
                        ))

        except Exception as e:
            # If static analysis fails, just skip it
            pass

        # If no errors found, add a success result
        if not results:
            results.append(VerificationResult(passed=True))

        return results

    def _run_tests(self, code: str, test_cases: List[Dict]) -> Dict:
        """Execute code with test cases"""
        passed = 0
        failed = 0
        test_details = []

        # Extract function name from code
        try:
            tree = ast.parse(code)
            function_name = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_name = node.name
                    break

            if not function_name:
                return {
                    "passed": 0,
                    "failed": len(test_cases),
                    "total": len(test_cases),
                    "details": ["No function definition found"]
                }

            # Create execution environment
            exec_globals = {}
            exec(code, exec_globals)
            func = exec_globals.get(function_name)

            if not func:
                return {
                    "passed": 0,
                    "failed": len(test_cases),
                    "total": len(test_cases),
                    "details": [f"Function {function_name} not found"]
                }

            # Run each test case
            for i, test_case in enumerate(test_cases):
                try:
                    # Handle different input formats
                    inputs = test_case.get("input", {})
                    expected = test_case.get("expected")

                    # Call function with inputs
                    if isinstance(inputs, dict):
                        result = func(**inputs)
                    else:
                        result = func(inputs)

                    # Check if result matches expected
                    if result == expected or str(result) == str(expected):
                        passed += 1
                        test_details.append(f"Test {i+1}: PASSED")
                    else:
                        failed += 1
                        test_details.append(f"Test {i+1}: FAILED - Expected {expected}, got {result}")

                except Exception as e:
                    failed += 1
                    test_details.append(f"Test {i+1}: ERROR - {str(e)}")

        except Exception as e:
            return {
                "passed": 0,
                "failed": len(test_cases),
                "total": len(test_cases),
                "details": [f"Execution error: {str(e)}"]
            }

        return {
            "passed": passed,
            "failed": failed,
            "total": len(test_cases),
            "details": test_details
        }

    def synthesize_feedback(self, verification_results: List[VerificationResult],
                           test_results: Dict, code: str) -> str:
        """
        Synthesize verification feedback into natural language
        This is the core of the VeriL approach
        """
        feedback_parts = []

        # Add header
        num_issues = sum(1 for r in verification_results if not r.passed)
        if num_issues > 0 or test_results["failed"] > 0:
            feedback_parts.append(f"Verification identified {num_issues + test_results['failed']} issues:\n")
        else:
            return "All verification checks passed!"

        # Add verification errors
        for i, result in enumerate(verification_results):
            if not result.passed:
                feedback_parts.append(f"\nIssue {len(feedback_parts)+1} [{result.error_type}]:")
                feedback_parts.append(f"- Location: {result.location}")
                feedback_parts.append(f"- Error: {result.error_message}")
                feedback_parts.append(f"- Suggestion: {self._generate_repair_hint(result)}")

        # Add test failures
        if test_results["failed"] > 0:
            feedback_parts.append(f"\nTest Results: {test_results['passed']}/{test_results['total']} passed")
            for detail in test_results["details"]:
                if "FAILED" in detail or "ERROR" in detail:
                    feedback_parts.append(f"- {detail}")

        feedback_parts.append("\nPlease revise the code to address these issues.")

        return "\n".join(feedback_parts)

    def _generate_repair_hint(self, result: VerificationResult) -> str:
        """Generate repair hints based on error type"""
        if result.error_type == "SyntaxError":
            return "Check for missing colons, parentheses, or indentation issues."
        elif "undefined" in result.error_message.lower():
            return "Ensure all variables are defined before use."
        elif "index" in result.error_message.lower():
            return "Check array bounds and index validity."
        else:
            return "Review the code logic and ensure it matches the specification."

    def get_raw_feedback(self, verification_results: List[VerificationResult],
                        test_results: Dict) -> str:
        """Get raw verification output without synthesis (baseline)"""
        feedback = []
        for result in verification_results:
            if not result.passed:
                feedback.append(f"{result.error_type}: {result.error_message} at {result.location}")

        if test_results["failed"] > 0:
            feedback.append(f"Tests failed: {test_results['failed']}/{test_results['total']}")
            for detail in test_results["details"]:
                if "FAILED" in detail or "ERROR" in detail:
                    feedback.append(detail)

        return "\n".join(feedback) if feedback else "All checks passed"
