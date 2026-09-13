import random
from errors import StructuredError

def to_sections(error: StructuredError, original_code: str) -> list:
    """Build 4-section list: [(PROBLEM, ...), (LOCATION, ...), (CONTEXT, ...), (ROOT_CAUSE, ...)]."""
    problem_content = f"{error.error_type}: {error.error_message}"
    location_content = f"Line {error.line_number}" if error.line_number > 0 else "Unknown location"
    context_content = "\n".join(error.code_context) if error.code_context else "No context available"
    root_cause_content = f"The {error.error_type} occurred likely due to: {error.error_message}"

    return [
        ("PROBLEM", problem_content),
        ("LOCATION", location_content),
        ("CONTEXT", context_content),
        ("ROOT_CAUSE", root_cause_content),
    ]

def format_sections(sections: list) -> str:
    """Format list of (header, content) tuples into markdown-style text."""
    parts = []
    for header, content in sections:
        parts.append(f"## {header}\n{content}")
    return "\n\n".join(parts)

def scramble_sections(sections: list, seed: int) -> list:
    """Random shuffle copy; preserves content, reorders only."""
    rng = random.Random(seed)
    shuffled = list(sections)
    rng.shuffle(shuffled)
    return shuffled

def format_structured_prompt(error: StructuredError, original_code: str) -> str:
    """Format error as structured 4-section prompt (canonical order)."""
    sections = to_sections(error, original_code)
    error_info = format_sections(sections)
    return f"""Fix the following code that produced an error.

{error_info}

## ORIGINAL CODE
```python
{original_code}
```

Provide only the corrected Python code:"""

def format_scrambled_prompt(error: StructuredError, original_code: str, seed: int) -> str:
    """Format error with randomly-ordered sections (same content)."""
    sections = to_sections(error, original_code)
    scrambled = scramble_sections(sections, seed)
    error_info = format_sections(scrambled)
    return f"""Fix the following code that produced an error.

{error_info}

## ORIGINAL CODE
```python
{original_code}
```

Provide only the corrected Python code:"""
