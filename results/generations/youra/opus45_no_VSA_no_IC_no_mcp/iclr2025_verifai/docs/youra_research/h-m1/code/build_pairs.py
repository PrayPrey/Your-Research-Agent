"""Build error pairs dataset by generating buggy code and capturing tracebacks."""
import json
import os
import random
import traceback
from dataclasses import asdict
from typing import List, Dict, Any

from errors import StructuredError, parse_compiler_output


# Templates for generating buggy code snippets
BUGGY_TEMPLATES = {
    "NameError": [
        "x = undefined_variable + 1",
        "result = foo_bar_undefined()",
        "print(nonexistent_var)",
        "value = some_undefined * 2",
    ],
    "TypeError": [
        "x = 'hello' + 5",
        "result = len(42)",
        "x = None + 1",
        "result = 'str' - 'str'",
    ],
    "IndexError": [
        "lst = [1, 2, 3]\nx = lst[10]",
        "arr = []\nfirst = arr[0]",
        "data = [1]\nval = data[-5]",
    ],
    "KeyError": [
        "d = {'a': 1}\nval = d['missing']",
        "data = {}\nresult = data['key']",
    ],
    "ZeroDivisionError": [
        "x = 10 / 0",
        "result = 100 // 0",
        "val = 5 % 0",
    ],
    "ValueError": [
        "x = int('not_a_number')",
        "val = float('invalid')",
        "nums = [1, 2, 3]\nidx = nums.index(99)",
    ],
    "AttributeError": [
        "x = None\nx.append(1)",
        "s = 'hello'\ns.nonexistent_method()",
        "n = 42\nn.upper()",
    ],
    "SyntaxError": [
        "eval('def f( :')",
        "exec('if True')",
        "compile('x = ', '<string>', 'exec')",
    ],
}


def generate_buggy_snippets(n: int = 500) -> List[Dict[str, str]]:
    """Generate n buggy code snippets across error types."""
    snippets = []
    error_types = list(BUGGY_TEMPLATES.keys())

    for i in range(n):
        error_type = error_types[i % len(error_types)]
        templates = BUGGY_TEMPLATES[error_type]
        template = random.choice(templates)

        # Add some variation with prefix/suffix
        prefix_lines = random.randint(0, 3)
        prefix = "\n".join([f"# Line {j+1}" for j in range(prefix_lines)])
        if prefix:
            prefix += "\n"

        snippets.append({
            "source_code": prefix + template,
            "expected_error_type": error_type,
        })

    return snippets


def capture_raw_error(source_code: str) -> str:
    """Execute source code and capture traceback on exception."""
    try:
        exec(source_code, {"__builtins__": __builtins__}, {})
        return ""  # No error
    except Exception:
        return traceback.format_exc()


def build_error_pairs(n_samples: int = 500) -> List[Dict[str, Any]]:
    """Generate error pairs: raw traceback + structured error for each sample."""
    snippets = generate_buggy_snippets(n_samples)
    pairs = []

    for snippet in snippets:
        source_code = snippet["source_code"]
        raw_error = capture_raw_error(source_code)

        if not raw_error:
            continue  # Skip if no error occurred

        structured = parse_compiler_output(raw_error, source_code)

        pairs.append({
            "raw_error": raw_error,
            "structured_error": asdict(structured),
            "source_code": source_code,
        })

    return pairs


def save_pairs(pairs: List[Dict[str, Any]], out_path: str) -> None:
    """Save pairs to JSON file."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(pairs, f, indent=2)


def load_or_build_error_pairs(out_path: str, n_samples: int = 500) -> List[Dict[str, Any]]:
    """Load pairs from file if exists, otherwise build and save."""
    if os.path.exists(out_path):
        with open(out_path, "r") as f:
            return json.load(f)

    pairs = build_error_pairs(n_samples)
    save_pairs(pairs, out_path)
    return pairs


if __name__ == "__main__":
    from config import CONFIG
    pairs = load_or_build_error_pairs(CONFIG["error_pairs_path"], CONFIG["min_samples"])
    print(f"Built/loaded {len(pairs)} error pairs")
