import random
from sandbox import ExecResult

RANDOM_TEMPLATES = [
    "Try a different approach",
    "Check your logic",
    "Review the code",
    "Consider edge cases",
    "Think about the problem again",
]

def format_execution_feedback(result: ExecResult) -> str:
    parts = []
    if result.error_type:
        parts.append(f"Error: {result.error_type}")
    if result.line_number:
        parts.append(f"at line {result.line_number}")
    if result.expected and result.actual:
        parts.append(f"\nExpected: {result.expected}\nActual: {result.actual}")
    if result.stderr and len(parts) == 0:
        parts.append(f"Output: {result.stderr[:500]}")
    return " ".join(parts) if parts else "Execution failed"

def generate_random_feedback() -> str:
    return random.choice(RANDOM_TEMPLATES)
