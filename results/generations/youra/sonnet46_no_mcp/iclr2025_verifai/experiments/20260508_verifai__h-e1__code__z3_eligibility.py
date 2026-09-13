import ast
import json
import re
from typing import Dict, List, Tuple

import z3


class Z3EligibilityChecker:
    def __init__(self, timeout_ms: int = 2000) -> None:
        self.timeout_ms = timeout_ms

    def extract_postconditions(self, problem: dict) -> List[str]:
        """Extract assert expressions from contract field or prompt."""
        # Prefer the contract field (EvalPlus) which has structured assert statements
        contract = problem.get("contract", "")
        if contract:
            asserts = re.findall(r"assert\s+(.+?)(?:#.*)?(?:\n|$)", contract)
            candidates = [a.strip() for a in asserts if a.strip()]
            if candidates:
                return candidates
        # Fallback: scan full prompt for assert statements
        prompt = problem.get("prompt", "")
        asserts = re.findall(r"assert\s+(.+?)(?:\n|$)", prompt)
        return [a.strip() for a in asserts if a.strip()]

    def _extract_var_names(self, expr_str: str) -> List[str]:
        """Extract variable names from an expression string."""
        try:
            tree = ast.parse(expr_str, mode="eval")
        except SyntaxError:
            return []
        names = []
        for node in ast.walk(tree.body):
            if isinstance(node, ast.Name):
                names.append(node.id)
        return list(set(names))

    def _build_lia_formula(
        self,
        assert_exprs: List[str],
        var_names: List[str],
    ) -> Tuple[bool, object]:
        """Walk AST; accept BinOp(+,-), Compare, int Constant, Name only.
        Returns (True, z3_formula) or (False, None) if non-LIA ops found.
        """
        z3_vars = {name: z3.Int(name) for name in var_names}
        z3_vars["result"] = z3.Int("result")

        formulas = []
        for expr_str in assert_exprs:
            try:
                tree = ast.parse(expr_str, mode="eval")
            except SyntaxError:
                return False, None

            try:
                formula = self._ast_to_z3(tree.body, z3_vars)
                if formula is None:
                    return False, None
                formulas.append(formula)
            except Exception:
                return False, None

        if not formulas:
            return False, None

        combined = formulas[0] if len(formulas) == 1 else z3.And(*formulas)
        return True, combined

    def _ast_to_z3(self, node: ast.AST, z3_vars: dict):
        """Convert AST node to Z3 expression. Returns None for non-LIA ops."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, bool)):
                return z3.IntVal(int(node.value))
            return None
        elif isinstance(node, ast.Name):
            name = node.id
            if name not in z3_vars:
                z3_vars[name] = z3.Int(name)
            return z3_vars[name]
        elif isinstance(node, ast.BinOp):
            left = self._ast_to_z3(node.left, z3_vars)
            right = self._ast_to_z3(node.right, z3_vars)
            if left is None or right is None:
                return None
            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, (ast.Mult,)):
                # Multiplication by constant is LIA; general mult is not
                if isinstance(node.right, ast.Constant):
                    return left * node.right.value
                if isinstance(node.left, ast.Constant):
                    return node.left.value * right
                return None
            return None
        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                operand = self._ast_to_z3(node.operand, z3_vars)
                return -operand if operand is not None else None
            return None
        elif isinstance(node, ast.Compare):
            left = self._ast_to_z3(node.left, z3_vars)
            if left is None:
                return None
            formulas = []
            prev = left
            for op, comparator in zip(node.ops, node.comparators):
                right = self._ast_to_z3(comparator, z3_vars)
                if right is None:
                    return None
                if isinstance(op, ast.Eq):
                    formulas.append(prev == right)
                elif isinstance(op, ast.NotEq):
                    formulas.append(prev != right)
                elif isinstance(op, ast.Lt):
                    formulas.append(prev < right)
                elif isinstance(op, ast.LtE):
                    formulas.append(prev <= right)
                elif isinstance(op, ast.Gt):
                    formulas.append(prev > right)
                elif isinstance(op, ast.GtE):
                    formulas.append(prev >= right)
                else:
                    return None
                prev = right
            return z3.And(*formulas) if len(formulas) > 1 else formulas[0]
        elif isinstance(node, ast.BoolOp):
            values = [self._ast_to_z3(v, z3_vars) for v in node.values]
            if any(v is None for v in values):
                return None
            if isinstance(node.op, ast.And):
                return z3.And(*values)
            elif isinstance(node.op, ast.Or):
                return z3.Or(*values)
        return None

    def has_integer_output_assertions(self, problem: dict) -> bool:
        """Check if the test field contains simple integer-equality assertions
        (e.g., assert func(args) == 5). These indicate Z3 can encode output
        constraints as integer equality formulas."""
        test_code = problem.get("test", "")
        # EvalPlus tests use `candidate(args) == value`; look for integer equality
        pattern = r"assert\s+candidate\s*\([^)]*\)\s*==\s*-?\d+"
        return bool(re.search(pattern, test_code))

    def check_problem(self, problem: dict) -> Tuple[bool, str]:
        """Check Z3 eligibility for one problem.
        Returns (is_eligible, reason).

        A problem is eligible if:
        1. Its contract has LIA-encodable conditions, OR
        2. Its test field contains integer-equality assertions (Z3 can verify output)
        """
        # Check test field for integer output assertions (broader eligibility)
        if self.has_integer_output_assertions(problem):
            return True, "integer_output_assertions"

        postconds = self.extract_postconditions(problem)
        if not postconds:
            return False, "no_assertions"

        var_names = []
        for expr in postconds:
            var_names.extend(self._extract_var_names(expr))
        var_names = list(set(var_names))

        try:
            ok, formula = self._build_lia_formula(postconds, var_names)
        except Exception:
            return False, "parse_error"

        if not ok:
            return False, "non_lia_ops"

        try:
            solver = z3.Solver()
            solver.set("timeout", self.timeout_ms)
            solver.add(formula)
            result = solver.check()
            if result == z3.unknown:
                return False, "z3_timeout"
            return True, "lia_encodable"
        except Exception:
            return False, "parse_error"

    def check_all(
        self,
        problems: Dict[str, dict],
        output_path: str,
    ) -> Dict[str, bool]:
        """Run check_problem on all problems; serialize JSON to output_path."""
        eligibility: Dict[str, bool] = {}

        for task_id, problem in problems.items():
            is_eligible, reason = self.check_problem(problem)
            eligibility[task_id] = is_eligible

        eligible_count = sum(1 for v in eligibility.values() if v)
        rate = eligible_count / len(eligibility) if eligibility else 0.0
        print(f"  Z3 eligibility: {eligible_count}/{len(eligibility)} = {rate:.2%}")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(eligibility, f, indent=2)

        return eligibility
