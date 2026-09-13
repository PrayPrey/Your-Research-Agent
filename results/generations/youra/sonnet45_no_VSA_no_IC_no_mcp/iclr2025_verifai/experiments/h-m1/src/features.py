"""Task feature extraction from reference solutions."""
import ast
from typing import Dict


def extract_task_features(reference_solution: str) -> Dict[str, float]:
    """Extract task complexity features. Returns dict with 4 metrics."""
    try:
        tree = ast.parse(reference_solution)
    except SyntaxError:
        return {
            'ast_depth': 0,
            'function_count': 0,
            'control_flow_density': 0.0,
            'complexity_score': 0
        }

    depth = _compute_ast_depth(tree)
    func_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])

    control = len([n for n in ast.walk(tree) if isinstance(n, (ast.If, ast.For, ast.While))])
    total = sum(1 for _ in ast.walk(tree))
    density = control / total if total > 0 else 0.0

    try:
        from radon.complexity import cc_visit
        complexity = sum(item.complexity for item in cc_visit(reference_solution))
    except:
        complexity = 1

    return {
        'ast_depth': depth,
        'function_count': func_count,
        'control_flow_density': density,
        'complexity_score': complexity
    }


def _compute_ast_depth(node: ast.AST, depth: int = 0) -> int:
    """Recursive AST depth. Returns max nesting level."""
    if not hasattr(node, '_fields'):
        return depth
    max_child_depth = depth
    for child in ast.iter_child_nodes(node):
        max_child_depth = max(max_child_depth, _compute_ast_depth(child, depth + 1))
    return max_child_depth
