import ast
from typing import Any
import zss


SEMANTIC_NODE_TYPES = frozenset([
    "If", "For", "While", "Try", "With",        # control-flow
    "Assign", "AugAssign", "Call", "Return",     # data-flow
])


class ZSSNode:
    """Wrapper making ast.AST nodes zss-compatible."""

    def __init__(self, label: str, children: list):
        self.label = label
        self.children = children

    def __repr__(self):
        return f"ZSSNode({self.label}, {len(self.children)} children)"


def _build_semantic_tree(node: ast.AST) -> list:
    """Recursively collect ZSSNodes for semantic node types."""
    results = []
    type_name = type(node).__name__
    if type_name in SEMANTIC_NODE_TYPES:
        child_nodes = []
        for child in ast.iter_child_nodes(node):
            child_nodes.extend(_build_semantic_tree(child))
        results.append(ZSSNode(type_name, child_nodes))
    else:
        for child in ast.iter_child_nodes(node):
            results.extend(_build_semantic_tree(child))
    return results


def extract_semantic_ast(code: str) -> ZSSNode:
    """Parse code, filter to SEMANTIC_NODE_TYPES, return zss-compatible tree.
    Raises ValueError on syntax error.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise ValueError(f"Syntax error in code: {e}") from e

    children = []
    for node in ast.iter_child_nodes(tree):
        children.extend(_build_semantic_tree(node))

    return ZSSNode("Module", children)


def compute_ast_semantic_edit_distance(code_a: str, code_b: str) -> float:
    """Zhang-Shasha edit distance between semantic ASTs.
    Returns float('inf') on parse failure of either input.
    """
    try:
        tree_a = extract_semantic_ast(code_a)
    except ValueError:
        return float("inf")
    try:
        tree_b = extract_semantic_ast(code_b)
    except ValueError:
        return float("inf")

    return float(zss.simple_distance(
        tree_a,
        tree_b,
        get_children=lambda n: n.children,
        get_label=lambda n: n.label,
        label_dist=lambda a, b: 0 if a == b else 1,
    ))


def batch_ast_edit_distances(
    reference_codes: dict,
    candidate_codes: dict,
) -> dict:
    """Per-problem edit distance. Keys: task_ids present in both dicts."""
    result = {}
    for task_id in reference_codes:
        if task_id in candidate_codes:
            result[task_id] = compute_ast_semantic_edit_distance(
                reference_codes[task_id],
                candidate_codes[task_id],
            )
    return result
