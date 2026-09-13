from dataclasses import dataclass
from typing import Dict
from errors import StructuredError

@dataclass
class HintAnalysis:
    general_strategy: str
    specific_pattern: str
    exact_fix: str

ERROR_HINT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "IndexError": {
        "strategy": "Check array/list bounds before accessing elements",
        "pattern": "Add bounds check or use try-except for IndexError near line {line}"
    },
    "TypeError": {
        "strategy": "Verify variable types match expected operations",
        "pattern": "Check type compatibility or add type conversion near line {line}"
    },
    "NameError": {
        "strategy": "Ensure all variables are defined before use",
        "pattern": "Define variable or check spelling near line {line}"
    },
    "ValueError": {
        "strategy": "Validate input values before processing",
        "pattern": "Add input validation or handle invalid values near line {line}"
    },
    "KeyError": {
        "strategy": "Check dictionary key existence before access",
        "pattern": "Use .get() or check 'in' before accessing key near line {line}"
    },
    "AttributeError": {
        "strategy": "Verify object has the attribute before calling",
        "pattern": "Check object type or use hasattr() near line {line}"
    },
    "ZeroDivisionError": {
        "strategy": "Check divisor is non-zero before division",
        "pattern": "Add zero check before division near line {line}"
    },
    "SyntaxError": {
        "strategy": "Fix syntax issues like missing colons, brackets, or quotes",
        "pattern": "Check syntax near line {line} for missing/mismatched tokens"
    },
    "UnknownError": {
        "strategy": "Review the error message and trace carefully",
        "pattern": "Debug the logic near line {line}"
    },
}

def _heuristic_patch(target_line: str, error_type: str) -> str:
    if error_type == "IndexError":
        return f"if 0 <= idx < len(arr): {target_line.strip()}"
    elif error_type == "ZeroDivisionError":
        return f"if divisor != 0: {target_line.strip()}"
    elif error_type == "KeyError":
        return target_line.replace("[", ".get(").replace("]", ", None)")
    return target_line.strip() + "  # TODO: fix"

def _build_exact_fix(error: StructuredError, source_code: str) -> str:
    lines = source_code.split('\n')
    if 0 < error.line_number <= len(lines):
        target_line = lines[error.line_number - 1]
        patch = _heuristic_patch(target_line, error.error_type)
        return f"Change line {error.line_number} to: {patch}"
    return f"Review and fix line {error.line_number}: {error.error_message}"

def analyze_error(error: StructuredError, source_code: str) -> HintAnalysis:
    template = ERROR_HINT_TEMPLATES.get(error.error_type, ERROR_HINT_TEMPLATES["UnknownError"])
    general_strategy = template["strategy"]
    specific_pattern = template["pattern"].format(line=error.line_number)
    exact_fix = _build_exact_fix(error, source_code)
    return HintAnalysis(general_strategy, specific_pattern, exact_fix)

def generate_hint(error: StructuredError, source_code: str, level: int) -> str:
    if level == 0:
        return ""
    analysis = analyze_error(error, source_code)
    return {1: analysis.general_strategy, 2: analysis.specific_pattern, 3: analysis.exact_fix}[level]

def demo():
    from errors import StructuredError
    err = StructuredError(line_number=2, error_type="IndexError",
                          error_message="list index out of range", code_context=["1: x = []", "2: y = x[10]"])
    code = "x = []\ny = x[10]"
    assert generate_hint(err, code, 0) == ""
    assert "bounds" in generate_hint(err, code, 1).lower()
    assert "line 2" in generate_hint(err, code, 2)
    assert "Change line 2" in generate_hint(err, code, 3)
    print("hints.py demo PASS")

if __name__ == "__main__":
    demo()
