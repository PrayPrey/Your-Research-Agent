"""AST-based ground truth bug line heuristics for H-M2."""
import ast
import re
import random
from typing import List, Dict, Optional

from config import U_LINE_ERRORS, U_IGNORE_ERRORS, SEED


def parse_traceback_line(traceback_str: str) -> Optional[int]:
    """Extract last line number from traceback."""
    if not traceback_str:
        return None
    matches = re.findall(r'line (\d+)', traceback_str)
    return int(matches[-1]) if matches else None


def _extract_identifier_from_traceback(traceback_str: str, error_type: str) -> Optional[str]:
    """Extract undefined identifier from error message."""
    if error_type == "NameError":
        match = re.search(r"name '(\w+)'", traceback_str)
        return match.group(1) if match else None
    elif error_type == "AttributeError":
        match = re.search(r"has no attribute '(\w+)'", traceback_str)
        return match.group(1) if match else None
    return None


def _find_name_or_attr_line(tree: ast.Module, tb_line: int, traceback_str: str, error_type: str) -> Optional[int]:
    """Find Name/Attribute node matching undefined identifier."""
    target_id = _extract_identifier_from_traceback(traceback_str, error_type)
    if not target_id:
        return tb_line

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == target_id:
            return node.lineno
        if isinstance(node, ast.Attribute) and node.attr == target_id:
            return node.lineno
    return tb_line


def _find_subscript_line(tree: ast.Module, tb_line: int) -> Optional[int]:
    """Find Subscript node near traceback line."""
    candidates = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and hasattr(node, 'lineno'):
            candidates.append(node.lineno)

    if not candidates:
        return tb_line
    return min(candidates, key=lambda x: abs(x - tb_line))


def _find_binop_or_call_line(tree: ast.Module, tb_line: int) -> Optional[int]:
    """Find BinOp/Call node near traceback line."""
    candidates = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.BinOp, ast.Call)) and hasattr(node, 'lineno'):
            candidates.append(node.lineno)

    if not candidates:
        return tb_line
    return min(candidates, key=lambda x: abs(x - tb_line))


def _find_syntax_line(traceback_str: str) -> Optional[int]:
    """SyntaxError/IndentationError - parse from traceback directly."""
    return parse_traceback_line(traceback_str)


def _find_stack_heuristic_line(tree: ast.Module, tb_line: int, error_type: str) -> Optional[int]:
    """U_ignore errors - heuristic based on loop/recursion detection."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)) and hasattr(node, 'lineno'):
            return node.lineno
        if isinstance(node, ast.FunctionDef) and hasattr(node, 'lineno'):
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call):
                    if isinstance(inner.func, ast.Name) and inner.func.id == node.name:
                        return inner.lineno
    return tb_line


def _get_error_type_from_traceback(traceback_str: str) -> str:
    """Extract exception class name from traceback."""
    all_errors = U_LINE_ERRORS | U_IGNORE_ERRORS
    for err in all_errors:
        if err in traceback_str:
            return err
    return "UnknownError"


def find_bug_line_ast(code: str, error_type: str, traceback_str: str) -> Optional[int]:
    """Heuristic ground-truth bug line via AST analysis."""
    tb_line = parse_traceback_line(traceback_str)
    if tb_line is None:
        return None

    if error_type in {'SyntaxError', 'IndentationError'}:
        return _find_syntax_line(traceback_str)

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return tb_line

    if error_type in {'NameError', 'AttributeError'}:
        return _find_name_or_attr_line(tree, tb_line, traceback_str, error_type)

    if error_type in {'IndexError', 'KeyError'}:
        return _find_subscript_line(tree, tb_line)

    if error_type in {'TypeError', 'ValueError', 'ZeroDivisionError'}:
        return _find_binop_or_call_line(tree, tb_line)

    return _find_stack_heuristic_line(tree, tb_line, error_type)


def annotate_ground_truth(samples: List[Dict]) -> List[Dict]:
    """Add actual_bug_line to each sample (skip if already present)."""
    for sample in samples:
        error_type = _get_error_type_from_traceback(sample.get("traceback", ""))
        sample["error_type_specific"] = error_type
        if sample.get("actual_bug_line") is None:
            actual_line = find_bug_line_ast(
                sample.get("code", ""),
                error_type,
                sample.get("traceback", "")
            )
            sample["actual_bug_line"] = actual_line
    return samples


def spot_check_sample(samples: List[Dict], n: int = 50, seed: int = SEED) -> List[Dict]:
    """Return random subset for manual validation."""
    random.seed(seed)
    valid_samples = [s for s in samples if s.get("actual_bug_line") is not None]
    n = min(n, len(valid_samples))
    return random.sample(valid_samples, n)
