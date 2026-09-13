"""H-M1: Structural error categorization for pylint+mypy errors."""
from typing import Set, List, Tuple

STRUCTURAL_ERROR_CODES: dict = {
    # pylint structural errors
    "E0001": "syntax-error",
    "E0102": "function-redefined",
    "E0602": "undefined-variable",
    "E0603": "undefined-all-variable",
    "E1101": "no-member",
    "E1120": "no-value-for-parameter",
    "E1121": "too-many-function-args",
    "W0612": "unused-variable",
    "W0611": "unused-import",
    # mypy substring keys -> category
    "incompatible": "type-mismatch",
    "arg-type": "argument-type-error",
    "return": "return-type-error",
    "name": "undefined-name",
}

def categorize_static_errors(static_errors: Set[str]) -> Tuple[List[Tuple[str, str]], List[str]]:
    """Split run_static_analysis() output into (structural, other).

    static_errors: set of "pylint:CODE" or "mypy:message" strings
    Returns: (structural: [(code, category)], other: [raw strings])
    """
    structural = []
    other = []

    for err in static_errors:
        if err.startswith("pylint:"):
            code = err.split("pylint:", 1)[1]
            if code in STRUCTURAL_ERROR_CODES:
                structural.append((code, STRUCTURAL_ERROR_CODES[code]))
            else:
                other.append(err)
        elif err.startswith("mypy:"):
            msg = err.split("mypy:", 1)[1].lower()
            matched = False
            for key in ("incompatible", "arg-type", "return", "name"):
                if key in msg:
                    structural.append((key, STRUCTURAL_ERROR_CODES[key]))
                    matched = True
                    break
            if not matched:
                other.append(err)
        else:
            other.append(err)

    return structural, other

def has_structural_error(static_errors: Set[str]) -> bool:
    """True if categorize_static_errors returns any structural entries."""
    structural, _ = categorize_static_errors(static_errors)
    return len(structural) > 0
