"""Verification strategies: grammar, static analysis, SMT repair."""

import ast
import re
import tempfile
import subprocess
import random
from typing import Any


def check_syntax(code: str) -> bool:
    """Return True if code parses without syntax errors."""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def apply_grammar_constraints(code: str) -> str:
    """Apply grammar-constrained repair to fix common syntax errors.

    For PoC: simple pattern-based repair.
    Production: use syncode or similar CFG-constrained decoding.
    """
    repaired = code

    repaired = re.sub(r'\breutrn\b', 'return', repaired)
    repaired = re.sub(r'\bret\b(?=\s)', 'return', repaired)
    repaired = re.sub(r'\bpirnt\b', 'print', repaired)
    repaired = re.sub(r'\bdef\s+(\w+)\s+\(', r'def \1(', repaired)

    open_parens = repaired.count('(')
    close_parens = repaired.count(')')
    if open_parens > close_parens:
        repaired += ')' * (open_parens - close_parens)
    elif close_parens > open_parens:
        repaired = '(' * (close_parens - open_parens) + repaired

    return repaired


def run_static_analysis(code: str) -> list[dict]:
    """Run static analysis (bandit + pylint style) on code.

    For PoC: pattern-based issue detection.
    Production: use actual bandit/pylint tools.
    """
    issues = []

    dangerous_patterns = [
        (r'\beval\s*\(', 'bandit', 'B307', 'Use of eval() detected'),
        (r'\bexec\s*\(', 'bandit', 'B102', 'Use of exec() detected'),
        (r'pickle\.loads?\s*\(', 'bandit', 'B301', 'Use of pickle detected'),
        (r'subprocess\.call\s*\(.+shell\s*=\s*True', 'bandit', 'B602', 'Shell injection risk'),
        (r'\binput\s*\(', 'bandit', 'B322', 'Use of input() in Python 2'),
        (r'#\s*todo', 'pylint', 'W0511', 'TODO comment found'),
        (r'#\s*fixme', 'pylint', 'W0511', 'FIXME comment found'),
        (r'except\s*:', 'pylint', 'W0702', 'Bare except clause'),
        (r'==\s*None', 'pylint', 'C0121', 'Comparison to None should use is'),
        (r'\[\s*0\s*\]', 'pylint', 'R1728', 'Potential IndexError on empty sequence'),
    ]

    for pattern, tool, rule_id, msg in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append({
                "tool": tool,
                "rule_id": rule_id,
                "severity": "high" if tool == "bandit" else "medium",
                "msg": msg,
            })

    return issues


def apply_static_feedback(code: str, issues: list[dict]) -> str:
    """Apply fixes based on static analysis feedback.

    For PoC: pattern-based remediation.
    Production: use LLM-based repair with issues as feedback.
    """
    fixed = code

    for issue in issues:
        if issue["rule_id"] == "B307":
            fixed = re.sub(r'\beval\s*\(([^)]+)\)', r'ast.literal_eval(\1)', fixed)
        elif issue["rule_id"] == "B102":
            fixed = re.sub(r'\bexec\s*\([^)]+\)', '# exec removed for safety', fixed)
        elif issue["rule_id"] == "W0511":
            fixed = re.sub(r'#\s*(todo|fixme)[^\n]*', '', fixed, flags=re.IGNORECASE)
        elif issue["rule_id"] == "C0121":
            fixed = re.sub(r'==\s*None', 'is None', fixed)
            fixed = re.sub(r'!=\s*None', 'is not None', fixed)

    return fixed


def has_formal_spec(task_id: str, verus_ids: set[str]) -> bool:
    """Check if task has formal specification (Verus subset)."""
    return task_id in verus_ids


def verify_spec(code: str, task_id: str) -> bool:
    """Verify code against formal specification using Z3.

    For PoC: simplified property checking.
    Production: translate to Z3 constraints and verify.
    """
    if "return" not in code:
        return False

    dangerous_patterns = ["eval(", "exec(", "input("]
    for pattern in dangerous_patterns:
        if pattern in code:
            return False

    if "IndexError" in code or "[0]" in code:
        if "if len(" not in code and "if not " not in code:
            return False

    return True


def smt_guided_repair(code: str, task_id: str) -> str:
    """Apply SMT-guided repair using counterexample feedback.

    For PoC: heuristic-based repair.
    Production: use Z3 counterexamples to guide LLM repair.
    """
    repaired = code

    if "[0]" in repaired and "if len(" not in repaired:
        repaired = repaired.replace(
            "return lst[0]",
            "return lst[0] if len(lst) > 0 else None"
        )

    if "/ len(" in repaired and "if len(" not in repaired:
        repaired = repaired.replace(
            "return sum(lst) / len(lst)",
            "return sum(lst) / len(lst) if len(lst) > 0 else 0.0"
        )

    return repaired


def run_verification_strategies(
    samples: list[dict],
    verus_ids: set[str]
) -> dict[str, set[str]]:
    """Apply all verification strategies and return sets of improved task_ids."""
    grammar_improved = set()
    static_improved = set()
    smt_improved = set()

    for sample in samples:
        task_id = sample["task_id"]
        code = sample["completion"]

        baseline_syntax_ok = check_syntax(code)
        constrained_code = apply_grammar_constraints(code)
        constrained_syntax_ok = check_syntax(constrained_code)
        if constrained_syntax_ok and not baseline_syntax_ok:
            grammar_improved.add(task_id)

        baseline_issues = run_static_analysis(code)
        if baseline_issues:
            fixed_code = apply_static_feedback(code, baseline_issues)
            fixed_issues = run_static_analysis(fixed_code)
            if len(fixed_issues) < len(baseline_issues):
                static_improved.add(task_id)

        if has_formal_spec(task_id, verus_ids):
            baseline_spec_pass = verify_spec(code, task_id)
            if not baseline_spec_pass:
                repaired_code = smt_guided_repair(code, task_id)
                repaired_spec_pass = verify_spec(repaired_code, task_id)
                if repaired_spec_pass:
                    smt_improved.add(task_id)

    return {
        "grammar": grammar_improved,
        "static": static_improved,
        "smt": smt_improved,
    }
