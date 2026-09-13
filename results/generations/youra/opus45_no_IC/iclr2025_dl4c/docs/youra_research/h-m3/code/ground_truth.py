"""GroundTruthGenerator: AST-based executable line analysis + coverage cross-validation."""

import ast
from typing import Set, Optional


class GroundTruthGenerator:
    """Generates ground truth executable line sets using AST analysis."""

    def __init__(self):
        pass

    def ast_executable_lines(self, code_str: str) -> Set[int]:
        """Parse code_str, return line numbers of executable statement nodes.

        Excludes:
        - ClassDef/FunctionDef signature-only lines
        - Docstring-only Expr(Constant(str))
        - Comments, blank lines
        """
        try:
            tree = ast.parse(code_str)
        except SyntaxError:
            return set()

        lines = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.stmt):
                if isinstance(node, ast.Expr):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        continue

                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    continue

                lines.add(node.lineno)

                if hasattr(node, "end_lineno") and node.end_lineno and node.end_lineno > node.lineno:
                    lines.update(range(node.lineno, node.end_lineno + 1))

        return lines

    def coverage_cross_validate(self, code_str: str, test_input: str = "") -> Set[int]:
        """Run code under coverage.py and return executed line set.

        Optional cross-check. Returns empty set if coverage not available.
        """
        try:
            import coverage
        except ImportError:
            return set()

        full_code = code_str + "\n" + test_input if test_input else code_str

        try:
            code_obj = compile(full_code, "<gt>", "exec")
        except SyntaxError:
            return set()

        cov = coverage.Coverage()
        cov.start()

        try:
            exec(code_obj, {"__builtins__": __builtins__}, {})
        except Exception:
            pass
        finally:
            cov.stop()

        try:
            data = cov.get_data()
            lines = data.lines("<gt>") or []
            return set(lines)
        except Exception:
            return set()

    def generate(self, code_str: str, test_input: str = "") -> Set[int]:
        """Generate ground truth: AST executable lines intersected with coverage (if available).

        Falls back to AST-only if coverage unavailable.
        """
        ast_lines = self.ast_executable_lines(code_str)
        cov_lines = self.coverage_cross_validate(code_str, test_input)

        if cov_lines:
            return ast_lines & cov_lines
        return ast_lines
