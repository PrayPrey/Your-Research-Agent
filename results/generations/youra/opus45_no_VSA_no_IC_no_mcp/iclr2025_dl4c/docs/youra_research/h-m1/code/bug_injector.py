"""Bug injection for H-M1: syntax, logic, type, off-by-one bugs."""
import ast
import random
import re

BUG_TYPES = ("syntax", "logic", "type", "off_by_one")

class InjectionError(Exception):
    pass

class BugInjector:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)

    def inject_syntax_bug(self, correct_code: str) -> tuple[str, int, str]:
        """Remove colon, paren, or shift indentation."""
        lines = correct_code.split("\n")
        candidates = []
        for i, line in enumerate(lines):
            if re.match(r'^\s*(def|if|for|while|class|elif|else|try|except|with|finally).+:\s*$', line):
                candidates.append((i, "colon", line))
            elif "(" in line and ")" in line:
                candidates.append((i, "paren", line))
        if not candidates:
            raise InjectionError("No syntax mutation candidates")
        idx, mutation, line = self.rng.choice(candidates)
        if mutation == "colon":
            new_line = line.rstrip().rstrip(":")
        else:
            new_line = line.replace("(", "", 1)
        lines[idx] = new_line
        buggy = "\n".join(lines)
        try:
            ast.parse(buggy)
            raise InjectionError("Bug did not cause syntax error")
        except SyntaxError:
            pass
        return buggy, idx + 1, f"{mutation} removed at line {idx + 1}"

    def inject_logic_bug(self, correct_code: str) -> tuple[str, int, str]:
        """Flip comparison or boolean operator."""
        try:
            tree = ast.parse(correct_code)
        except SyntaxError:
            raise InjectionError("Cannot parse code")
        ops_map = {
            ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt,
            ast.Eq: ast.NotEq, ast.NotEq: ast.Eq
        }
        bool_map = {ast.And: ast.Or, ast.Or: ast.And}
        candidates = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                for i, op in enumerate(node.ops):
                    if type(op) in ops_map:
                        candidates.append(("compare", node, i, type(op), ops_map[type(op)]))
            elif isinstance(node, ast.BoolOp):
                if type(node.op) in bool_map:
                    candidates.append(("bool", node, 0, type(node.op), bool_map[type(node.op)]))
        if not candidates:
            raise InjectionError("No logic mutation candidates")
        kind, node, idx, old_op, new_op = self.rng.choice(candidates)
        if kind == "compare":
            node.ops[idx] = new_op()
        else:
            node.op = new_op()
        buggy = ast.unparse(tree)
        lineno = getattr(node, "lineno", 1)
        return buggy, lineno, f"{old_op.__name__} -> {new_op.__name__} at line {lineno}"

    def inject_type_bug(self, correct_code: str) -> tuple[str, int, str]:
        """Change int() to str() or vice versa."""
        try:
            tree = ast.parse(correct_code)
        except SyntaxError:
            raise InjectionError("Cannot parse code")
        type_map = {"int": "str", "str": "int", "float": "str", "list": "tuple"}
        candidates = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in type_map:
                    candidates.append((node, node.func.id, type_map[node.func.id]))
        if not candidates:
            raise InjectionError("No type mutation candidates")
        node, old_type, new_type = self.rng.choice(candidates)
        node.func.id = new_type
        buggy = ast.unparse(tree)
        lineno = getattr(node, "lineno", 1)
        return buggy, lineno, f"{old_type} -> {new_type} at line {lineno}"

    def inject_off_by_one_bug(self, correct_code: str) -> tuple[str, int, str]:
        """Change range endpoint or index boundary."""
        try:
            tree = ast.parse(correct_code)
        except SyntaxError:
            raise InjectionError("Cannot parse code")
        candidates = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.BinOp):
                if isinstance(node.slice.op, ast.Sub) and isinstance(node.slice.right, ast.Constant):
                    if node.slice.right.value == 1:
                        candidates.append(("subscript", node))
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "range" and len(node.args) >= 1:
                    candidates.append(("range", node))
        if not candidates:
            raise InjectionError("No off-by-one candidates")
        kind, node = self.rng.choice(candidates)
        lineno = getattr(node, "lineno", 1)
        if kind == "subscript":
            node.slice.right.value = 0
            desc = f"index -1 -> -0 at line {lineno}"
        else:
            if len(node.args) == 1:
                arg = node.args[0]
                if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                    arg.op = ast.Sub()
                elif isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Sub):
                    arg.op = ast.Add()
                else:
                    node.args[0] = ast.BinOp(left=arg, op=ast.Sub(), right=ast.Constant(value=1))
            desc = f"range boundary shifted at line {lineno}"
        buggy = ast.unparse(tree)
        return buggy, lineno, desc

    def inject(self, correct_code: str, bug_type: str) -> tuple[str, int, str]:
        """Dispatch to specific injector with retry."""
        injectors = {
            "syntax": self.inject_syntax_bug,
            "logic": self.inject_logic_bug,
            "type": self.inject_type_bug,
            "off_by_one": self.inject_off_by_one_bug,
        }
        if bug_type not in injectors:
            raise ValueError(f"Unknown bug type: {bug_type}")
        for _ in range(5):
            try:
                return injectors[bug_type](correct_code)
            except InjectionError:
                continue
        raise InjectionError(f"Failed to inject {bug_type} bug after 5 attempts")

    def inject_all_types(self, problem: dict) -> list[dict]:
        """Generate one buggy sample per bug type."""
        results = []
        for bug_type in BUG_TYPES:
            try:
                buggy_code, bug_line, bug_desc = self.inject(problem["code"], bug_type)
                results.append({
                    "id": f"{problem['id']}_{bug_type}",
                    "original_id": problem["id"],
                    "bug_type": bug_type,
                    "buggy_code": buggy_code,
                    "correct_code": problem["code"],
                    "bug_line": bug_line,
                    "bug_description": bug_desc,
                    "tests": problem["tests"],
                    "prompt": problem["prompt"],
                })
            except InjectionError:
                pass
        return results

if __name__ == "__main__":
    injector = BugInjector(seed=42)
    test_code = '''def add(a, b):
    if a > 0:
        return a + b
    return 0
'''
    for bt in BUG_TYPES:
        try:
            buggy, line, desc = injector.inject(test_code, bt)
            print(f"{bt}: {desc}")
        except InjectionError as e:
            print(f"{bt}: FAILED - {e}")
