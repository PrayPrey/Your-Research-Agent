"""LlmFix 19-cause taxonomy classifier for H-M3.

Based on LlmFix paper (arXiv:2409.00676) - 19 error causes across 3 tiers.
"""

from typing import Dict, List, Optional, Tuple

from config import LLMFIX_TAXONOMY, ALL_FINE_CAUSES, COARSE_CATEGORIES


# Coarse-level error matching strings (lowercase, from h-e1 pattern)
COARSE_SYNTAX_ERRORS = [
    "syntaxerror", "indentationerror", "importerror", "modulenotfounderror"
]
COARSE_RUNTIME_ERRORS = [
    "typeerror", "nameerror", "attributeerror", "indexerror", "keyerror",
    "valueerror", "zerodivisionerror", "recursionerror", "timeout", "memoryerror",
    "runtimeerror", "stopiteration", "overflowerror", "filenotfounderror"
]
COARSE_ASSERTION_ERRORS = ["assertionerror", "expected", "wrong answer"]

# Fine-cause mapping: (substring_to_match -> fine_cause_label)
FINE_SYNTAX_MAP = [
    ("indentationerror", "indentation_error"),
    ("syntaxerror", "syntax_error"),
    ("importerror", "missing_import"),
    ("modulenotfounderror", "missing_import"),
]

FINE_RUNTIME_MAP = [
    ("nameerror", "name_error"),
    ("typeerror", "type_error"),
    ("attributeerror", "attribute_error"),
    ("indexerror", "index_error"),
    ("keyerror", "key_error"),
    ("valueerror", "value_error"),
    ("zerodivisionerror", "zero_division"),
    ("recursionerror", "recursion_error"),
    ("timeout", "timeout"),
    ("memoryerror", "memory_error"),
    ("runtimeerror", "timeout"),  # Often timeout-related
    ("overflowerror", "memory_error"),
]


def classify_error_coarse(error_trace: Optional[str]) -> str:
    """Classify error at coarse 3-tier level.

    Args:
        error_trace: Error traceback string or None for pass

    Returns:
        One of: 'syntax', 'runtime', 'assertion', 'other', 'pass'
    """
    if error_trace is None:
        return "pass"

    error_lower = error_trace.lower()

    # Syntax errors (parse-time failures) - check first
    for err in COARSE_SYNTAX_ERRORS:
        if err in error_lower:
            return "syntax"

    # Assertion errors (code runs but wrong output)
    for err in COARSE_ASSERTION_ERRORS:
        if err in error_lower:
            return "assertion"

    # Runtime errors (execution-time failures before assertion)
    for err in COARSE_RUNTIME_ERRORS:
        if err in error_lower:
            return "runtime"

    return "other"


def classify_error_fine(error_trace: Optional[str], coarse: str) -> str:
    """Classify error at fine-grained 19-cause level.

    Args:
        error_trace: Error traceback string
        coarse: Coarse category ('syntax', 'runtime', 'assertion', 'other', 'pass')

    Returns:
        One of 19 LlmFix cause labels or 'unknown'
    """
    if error_trace is None or coarse == "pass":
        return "pass"

    if coarse == "other":
        return "unknown"

    error_lower = error_trace.lower()

    if coarse == "syntax":
        for pattern, cause in FINE_SYNTAX_MAP:
            if pattern in error_lower:
                return cause
        return "syntax_error"  # Default syntax cause

    if coarse == "runtime":
        for pattern, cause in FINE_RUNTIME_MAP:
            if pattern in error_lower:
                return cause
        return "timeout"  # Default runtime cause (conservative)

    if coarse == "assertion":
        # Assertion fine-causes require output analysis
        return _classify_assertion_fine(error_trace)

    return "unknown"


def _classify_assertion_fine(error_trace: str) -> str:
    """Classify assertion errors into fine-grained causes.

    Uses heuristics based on error message patterns.

    Args:
        error_trace: Error traceback string

    Returns:
        One of: 'wrong_output', 'partial_output', 'missing_output',
                'wrong_type', 'off_by_one', 'boundary_error'
    """
    error_lower = error_trace.lower()

    # Type mismatch patterns
    if any(p in error_lower for p in ["type", "isinstance", "not a ", "expected type"]):
        return "wrong_type"

    # Missing/empty output patterns
    if any(p in error_lower for p in ["none", "empty", "null", "missing", "no output"]):
        return "missing_output"

    # Partial match patterns
    if any(p in error_lower for p in ["partial", "truncated", "incomplete"]):
        return "partial_output"

    # Off-by-one patterns (numeric differences)
    if any(p in error_lower for p in ["off by", "±1", "+1", "-1", "one less", "one more"]):
        return "off_by_one"

    # Boundary condition patterns
    if any(p in error_lower for p in ["boundary", "edge", "limit", "overflow", "underflow"]):
        return "boundary_error"

    # Default: wrong output (most common assertion failure)
    return "wrong_output"


def classify_error_llmfix(
    error_trace: Optional[str],
    output: Optional[str] = None,
) -> Tuple[str, str]:
    """Classify error at both coarse and fine granularity levels.

    Args:
        error_trace: Error traceback string or None
        output: Generated code output (optional, for assertion analysis)

    Returns:
        (coarse_category, fine_cause) tuple
    """
    coarse = classify_error_coarse(error_trace)
    fine = classify_error_fine(error_trace, coarse)
    return coarse, fine


def classify_batch(results: List[dict]) -> List[dict]:
    """Add classification labels to each result dict.

    Modifies dicts in-place, adding 'coarse_category' and 'fine_cause' keys.

    Args:
        results: List of execution result dicts with 'error_trace' key

    Returns:
        Same list with classification keys added
    """
    for r in results:
        error_trace = r.get("error_trace")
        output = r.get("completion")
        coarse, fine = classify_error_llmfix(error_trace, output)
        r["coarse_category"] = coarse
        r["fine_cause"] = fine

    return results
