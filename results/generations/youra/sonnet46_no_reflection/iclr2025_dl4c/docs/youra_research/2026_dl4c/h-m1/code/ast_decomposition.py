import ast
import re
import zss
from typing import Optional


def extract_code(completion: str) -> str:
    """Extract Python code from a completion that may contain markdown or prose.

    Tries:
    1. ```python ... ``` code block
    2. ``` ... ``` code block
    3. First def/class block found
    4. Original string as fallback
    """
    # Try ```python ... ```
    m = re.search(r"```python\s*\n(.*?)```", completion, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Try ``` ... ```
    m = re.search(r"```\s*\n(.*?)```", completion, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Try to find first def/class block
    lines = completion.split("\n")
    code_lines = []
    in_code = False
    for line in lines:
        if not in_code and (line.startswith("def ") or line.startswith("class ") or
                            line.startswith("from ") or line.startswith("import ")):
            in_code = True
        if in_code:
            code_lines.append(line)
    if code_lines:
        return "\n".join(code_lines)
    return completion

# FA-AST taxonomy (arxiv:2002.08653)
CONTROL_FLOW_NODES: frozenset = frozenset({
    "If", "For", "While", "Try", "With", "ExceptHandler", "Break", "Continue",
    "AsyncFor", "AsyncWith",
})

DATA_FLOW_NODES: frozenset = frozenset({
    "Assign", "AugAssign", "AnnAssign", "Call", "Return", "Yield", "YieldFrom",
    "Import", "ImportFrom", "FunctionDef", "AsyncFunctionDef", "ClassDef",
    "Delete", "Raise",
})

# Surface = everything else


class ZSSNodeFull:
    """ZSS-compatible node for full AST traversal."""

    def __init__(self, label: str):
        self.label = label
        self.children: list = []

    def addkid(self, child: "ZSSNodeFull") -> "ZSSNodeFull":
        self.children.append(child)
        return self


def classify_ast_node(node_type: str) -> str:
    """Classify AST node type into FA-AST category.

    Returns: "control_flow" | "data_flow" | "surface"
    """
    if node_type in CONTROL_FLOW_NODES:
        return "control_flow"
    if node_type in DATA_FLOW_NODES:
        return "data_flow"
    return "surface"


class _DocstringStripper(ast.NodeTransformer):
    """Remove docstring Expr(Constant(str)) nodes from function/class/module bodies."""

    def _strip_docstring(self, body: list) -> list:
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            return body[1:]
        return body

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        node.body = self._strip_docstring(node.body)
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        node.body = self._strip_docstring(node.body)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        node.body = self._strip_docstring(node.body)
        self.generic_visit(node)
        return node

    def visit_Module(self, node: ast.Module) -> ast.Module:
        node.body = self._strip_docstring(node.body)
        self.generic_visit(node)
        return node


def strip_docstrings_comments(code: str) -> str:
    """Normalize code: remove docstrings and comment lines.

    Returns normalized source string; returns original on parse failure.
    """
    try:
        tree = ast.parse(code)
        tree = _DocstringStripper().visit(tree)
        ast.fix_missing_locations(tree)
        return ast.unparse(tree)
    except Exception:
        return code


def _build_full_zss_tree(node: ast.AST) -> ZSSNodeFull:
    """Recursively build full ZSS tree (all node types, not filtered)."""
    label = type(node).__name__
    zss_node = ZSSNodeFull(label)
    for child in ast.iter_child_nodes(node):
        zss_node.addkid(_build_full_zss_tree(child))
    return zss_node


def ast_to_zss_full(tree: ast.AST) -> ZSSNodeFull:
    """Convert Python AST to full ZSS tree (includes all node types).

    Unlike H-E1 extract_semantic_ast, does NOT filter to SEMANTIC_NODE_TYPES.
    """
    return _build_full_zss_tree(tree)


def _collect_labels(node: ZSSNodeFull) -> list:
    """Collect all node labels via DFS."""
    labels = [node.label]
    for child in node.children:
        labels.extend(_collect_labels(child))
    return labels


def extract_edit_operations(
    tree_base: ZSSNodeFull,
    tree_new: ZSSNodeFull,
) -> list:
    """Extract edit operations via ZSS.

    Returns list of (op_type, node_type_label).
    Uses frequency-difference approximation since zss doesn't expose
    operation-level API in all versions.
    """
    ops = []
    try:
        # Try zss with operation capture if available
        def _get_children(n):
            return n.children

        def _get_label(n):
            return n.label

        # zss.simple_distance computes edit distance but doesn't return ops directly
        # Use frequency difference as approximation
        base_labels = _collect_labels(tree_base)
        new_labels = _collect_labels(tree_new)

        from collections import Counter
        base_counts = Counter(base_labels)
        new_counts = Counter(new_labels)

        all_types = set(base_counts) | set(new_counts)
        for node_type in all_types:
            b = base_counts.get(node_type, 0)
            n = new_counts.get(node_type, 0)
            if n > b:
                for _ in range(n - b):
                    ops.append(("insert", node_type))
            elif b > n:
                for _ in range(b - n):
                    ops.append(("remove", node_type))
    except Exception:
        pass
    return ops


def compute_edit_distribution(
    code_base: str,
    code_new: str,
) -> Optional[dict]:
    """Compute per-category edit proportions between two code strings.

    Returns:
        {
          "control_flow": float,
          "data_flow": float,
          "surface": float,
          "semantic": float,
          "total_edits": int,
        }
        None if either code fails to parse.
    """
    try:
        norm_base = strip_docstrings_comments(code_base)
        norm_new = strip_docstrings_comments(code_new)
        tree_base = ast_to_zss_full(ast.parse(norm_base))
        tree_new = ast_to_zss_full(ast.parse(norm_new))
    except Exception:
        return None

    ops = extract_edit_operations(tree_base, tree_new)
    total = len(ops)

    if total == 0:
        return {
            "control_flow": 0.0,
            "data_flow": 0.0,
            "surface": 0.0,
            "semantic": 0.0,
            "total_edits": 0,
        }

    cf_count = sum(1 for _, lbl in ops if classify_ast_node(lbl) == "control_flow")
    df_count = sum(1 for _, lbl in ops if classify_ast_node(lbl) == "data_flow")
    surf_count = total - cf_count - df_count

    return {
        "control_flow": cf_count / total,
        "data_flow": df_count / total,
        "surface": surf_count / total,
        "semantic": (cf_count + df_count) / total,
        "total_edits": total,
    }


def compute_sep(code_base: str, code_new: str) -> Optional[float]:
    """Semantic Edit Proportion = (CF_edits + DF_edits) / total_edits.

    Returns None on parse failure or zero total_edits.
    """
    dist = compute_edit_distribution(code_base, code_new)
    if dist is None:
        return None
    if dist["total_edits"] == 0:
        return None
    return dist["semantic"]


def compute_node_type_frequencies(
    codes: list,
    node_types: list,
) -> dict:
    """Count occurrences of each node_type across all code strings.

    Skips unparseable codes. Used for heatmap data.
    Returns {node_type: count}.
    """
    from collections import Counter
    total_counts: Counter = Counter()

    for code in codes:
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                label = type(node).__name__
                if label in node_types:
                    total_counts[label] += 1
        except Exception:
            continue

    return {nt: total_counts.get(nt, 0) for nt in node_types}
