import re
from dataclasses import dataclass
from typing import List

@dataclass
class StructuredError:
    line_number: int
    error_type: str
    error_message: str
    code_context: List[str]

def parse_compiler_output(raw_output: str, source_code: str) -> StructuredError:
    line_match = re.search(r'line (\d+)', raw_output, re.IGNORECASE)
    line_number = int(line_match.group(1)) if line_match else 0

    error_type_match = re.search(r'(\w+Error|\w+Exception)', raw_output)
    error_type = error_type_match.group(1) if error_type_match else "UnknownError"

    msg_match = re.search(rf'{re.escape(error_type)}:\s*(.+?)(?:\n|$)', raw_output)
    error_message = msg_match.group(1).strip() if msg_match else raw_output.strip()[:200]

    lines = source_code.split('\n')
    start = max(0, line_number - 3)
    end = min(len(lines), line_number + 2)
    code_context = [f"{i+1}: {lines[i]}" for i in range(start, end)]

    return StructuredError(
        line_number=line_number,
        error_type=error_type,
        error_message=error_message,
        code_context=code_context
    )
