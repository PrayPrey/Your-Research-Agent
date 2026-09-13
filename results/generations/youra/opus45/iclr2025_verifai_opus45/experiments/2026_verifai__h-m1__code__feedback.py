"""Feedback formatting module for H-M1: Granularity-controlled error feedback."""

from config import GRANULARITY_LEVELS


def format_feedback(error_info: dict, level: str) -> str:
    """Format error feedback at specified granularity level.

    Granularity Levels:
        G0: "Test failed." (pass/fail only)
        G1: "Test failed: {error_type}"
        G2: "Test failed: {error_type}: {message}"
        G3: "Test failed: {error_type}: {message} at line {line}"
        G4: Full traceback

    Args:
        error_info: Dict with {type, message, line, traceback}
        level: One of G0, G1, G2, G3, G4

    Returns:
        Formatted feedback string
    """
    if level not in GRANULARITY_LEVELS:
        raise ValueError(f"Invalid granularity level: {level}. Must be one of {GRANULARITY_LEVELS}")

    error_type = error_info.get("type", "Error")
    error_message = error_info.get("message", "")
    error_line = error_info.get("line")
    traceback = error_info.get("traceback", "")

    if level == "G0":
        return "Test failed."

    elif level == "G1":
        return f"Test failed: {error_type}"

    elif level == "G2":
        if error_message:
            return f"Test failed: {error_type}: {error_message}"
        return f"Test failed: {error_type}"

    elif level == "G3":
        base = f"Test failed: {error_type}"
        if error_message:
            base += f": {error_message}"
        if error_line is not None:
            base += f" at line {error_line}"
        return base

    elif level == "G4":
        if traceback:
            return f"Test failed:\n{traceback}"
        # Fallback to G3 format if no traceback
        return format_feedback(error_info, "G3")

    return "Test failed."


def construct_repair_prompt(
    code: str,
    task_text: str,
    error_info: dict,
    granularity: str,
) -> str:
    """Build Self-Debug style repair prompt with controlled granularity.

    The prompt includes [BEGIN] marker for code extraction by CodeGenerator.

    Args:
        code: Buggy generated code from H-E1
        task_text: MBPP problem description
        error_info: Parsed error dict from parse_error_info()
        granularity: G0, G1, G2, G3, or G4

    Returns:
        Formatted prompt string ready for model.generate()
    """
    feedback = format_feedback(error_info, granularity)

    prompt = f"""You are a Python expert. The following code has a bug that causes it to fail.

Task: {task_text}

Buggy code:
```python
{code}
```

Execution feedback:
{feedback}

Please fix the bug and provide the corrected code. Only output the fixed Python code.
[BEGIN]
"""
    return prompt
