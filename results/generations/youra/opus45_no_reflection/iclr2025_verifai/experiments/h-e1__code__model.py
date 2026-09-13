"""H-E1 AS Component Extractors and Signal Generators"""

import re
from dataclasses import dataclass

@dataclass
class ASComponents:
    AS_loc: int      # 1 if file:line present, else 0
    AS_state: int    # count of var=value pairs
    AS_causal: int   # count of traceback frames

    def is_valid(self) -> bool:
        return self.AS_loc >= 0 and self.AS_state >= 0 and self.AS_causal >= 0

# Regex patterns for AS extraction
FILE_LINE_PATTERN = re.compile(r'File "([^"]+)", line (\d+)')
VARIABLE_VALUE_PATTERN = re.compile(r"(\w+)\s*=\s*(['\"]?[\w\d\.\-\[\]{}]+['\"]?)")
TRACEBACK_FRAME_PATTERN = re.compile(
    r'^\s+File "([^"]+)", line (\d+), in (\w+)',
    re.MULTILINE
)

def extract_AS_loc(signal_text: str) -> int:
    """Extract localization component (binary)."""
    match = FILE_LINE_PATTERN.search(signal_text)
    return 1 if match else 0

def extract_AS_state(signal_text: str) -> int:
    """Extract state exposure component (count of variable=value pairs)."""
    matches = VARIABLE_VALUE_PATTERN.findall(signal_text)
    excluded = {'File', 'line', 'in', 'Error', 'Exception', 'Traceback', 'most', 'recent', 'call', 'last'}
    valid_matches = [m for m in matches if m[0] not in excluded and len(m[0]) > 1]
    return len(valid_matches)

def extract_AS_causal(signal_text: str) -> int:
    """Extract causal context component (trace depth)."""
    frames = TRACEBACK_FRAME_PATTERN.findall(signal_text)
    return len(frames)

def extract_all_components(signal_text: str) -> ASComponents:
    """Extract all AS components from verification signal."""
    return ASComponents(
        AS_loc=extract_AS_loc(signal_text),
        AS_state=extract_AS_state(signal_text),
        AS_causal=extract_AS_causal(signal_text)
    )

def truncate_trace(trace_output: str, max_frames: int = 3) -> str:
    """Keep only first max_frames traceback frames."""
    lines = trace_output.split('\n')
    result = []
    frame_count = 0
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith('File "'):
            if frame_count < max_frames:
                result.append(lines[i])
                if i + 1 < len(lines) and not lines[i + 1].strip().startswith('File "'):
                    result.append(lines[i + 1])
                    i += 1
            frame_count += 1
        elif frame_count == 0 or frame_count >= max_frames:
            if not lines[i].strip().startswith('File "'):
                result.append(lines[i])
        i += 1
    return '\n'.join(result)

def mask_values(trace_output: str) -> str:
    """Replace variable=value pairs with var=<masked>."""
    return VARIABLE_VALUE_PATTERN.sub(r'\1=<masked>', trace_output)

def extract_error_only(error_output: str) -> str:
    """Return last line matching error pattern."""
    pattern = re.compile(r'(\w+(?:Error|Exception)): .+')
    lines = error_output.strip().split('\n')
    for line in reversed(lines):
        if pattern.search(line):
            return line.strip()
    return ""

def extract_syntax_error(error_output: str) -> str:
    """Return SyntaxError line only, or empty if none."""
    if 'SyntaxError' in error_output:
        pattern = re.compile(r'SyntaxError: .+')
        match = pattern.search(error_output)
        if match:
            return match.group(0)
    return ""

def generate_signal_variants(error_output: str, trace_output: str) -> dict:
    """Generate 6 signal variants with controlled AS levels."""
    full_signal = trace_output if trace_output else error_output
    return {
        'C1': full_signal,
        'C2': truncate_trace(full_signal, max_frames=3),
        'C3': mask_values(full_signal),
        'C4': extract_error_only(error_output if error_output else full_signal),
        'C5': "",  # Static analysis placeholder
        'C6': extract_syntax_error(error_output if error_output else full_signal),
    }
