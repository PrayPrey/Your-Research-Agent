"""Error taxonomy for H-C1: classifies execution errors into schema classes."""
from enum import Enum
import re


class ErrorClass(Enum):
    COMPILE_ERROR = "CompileError"
    RUNTIME_ERROR = "RuntimeError"
    FAILED_TEST = "FailedTest"
    PASSED_TEST = "PassedTest"


def classify_error(error_msg: str, pass_rate: float) -> ErrorClass:
    """Classify error message + pass_rate into one of 4 error classes.

    CodeRL taxonomy:
    - CompileError: SyntaxError, IndentationError, NameError (undefined), ImportError
    - RuntimeError: TypeError, ValueError, AttributeError, IndexError, KeyError, ZeroDivision, Timeout
    - FailedTest: AssertionError (test failed but code executed)
    - PassedTest: pass_rate == 1.0
    """
    if pass_rate == 1.0:
        return ErrorClass.PASSED_TEST

    if not error_msg or error_msg.strip() == "":
        return ErrorClass.FAILED_TEST

    error_lower = error_msg.lower()

    # Compile errors: parsing/name resolution issues before execution
    compile_patterns = [
        "syntaxerror", "indentationerror", "taberror",
        "nameerror", "importerror", "modulenotfounderror",
        "invalid syntax", "unexpected indent", "expected an indented block",
        "is not defined", "name '", "no module named",
    ]
    for pattern in compile_patterns:
        if pattern in error_lower:
            return ErrorClass.COMPILE_ERROR

    # Runtime errors: execution-time exceptions
    runtime_patterns = [
        "typeerror", "valueerror", "attributeerror", "indexerror",
        "keyerror", "zerodivisionerror", "recursionerror", "memoryerror",
        "overflow", "timeout", "runtimeerror", "stopiteration",
        "unsupported operand", "object is not", "out of range",
        "division by zero", "maximum recursion",
    ]
    for pattern in runtime_patterns:
        if pattern in error_lower:
            return ErrorClass.RUNTIME_ERROR

    # Test failed (e.g. AssertionError)
    if "assertionerror" in error_lower or "assert" in error_lower:
        return ErrorClass.FAILED_TEST

    # Default: if test didn't pass but no clear error, treat as RuntimeError
    if pass_rate < 1.0:
        return ErrorClass.FAILED_TEST

    return ErrorClass.RUNTIME_ERROR
