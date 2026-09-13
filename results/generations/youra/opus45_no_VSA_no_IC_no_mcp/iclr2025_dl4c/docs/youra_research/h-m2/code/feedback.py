from sandbox import ExecResult

def format_detailed_feedback(result: ExecResult) -> str:
    """Full error trace with localization for targeted edits."""
    if result.passed:
        return "Test passed."

    lines = []
    if result.error_type:
        loc = f" at line {result.line_number}" if result.line_number else ""
        lines.append(f"Error: {result.error_type}{loc}")

    if result.expected and result.actual:
        lines.append(f"Expected: {result.expected}")
        lines.append(f"Actual: {result.actual}")

    if result.stderr:
        tb_lines = result.stderr.strip().splitlines()[-3:]
        if tb_lines:
            lines.append("Traceback: " + " | ".join(tb_lines))

    return "\n".join(lines) if lines else "Execution failed"

def format_binary_feedback(result: ExecResult) -> str:
    """Pass/fail only, no localization - forces global rewrites."""
    return "Test passed." if result.passed else "Test failed."
