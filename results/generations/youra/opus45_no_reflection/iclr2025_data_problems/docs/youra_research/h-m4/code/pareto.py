"""Pareto frontier construction and dominance analysis."""
import numpy as np
from typing import Dict, List, Tuple

def build_pareto_points(sweep_results: Dict[int, Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Convert {budget: (auc, time)} -> [(time, auc), ...] sorted by time."""
    points = [(time, auc) for budget, (auc, time) in sweep_results.items()]
    return sorted(points, key=lambda p: p[0])

def is_pareto_dominated(point: Tuple[float, float], frontier: List[Tuple[float, float]]) -> bool:
    """Check if (time, auc) point is dominated by any point in frontier.
    Domination: another point has same or less time AND same or higher AUC, with strict in one."""
    t, a = point
    for ft, fa in frontier:
        if ft <= t and fa >= a and (ft < t or fa > a):
            return True
    return False

def extract_pareto_frontier(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Return non-dominated (time, auc) points."""
    frontier = []
    for p in points:
        if not is_pareto_dominated(p, [q for q in points if q != p]):
            frontier.append(p)
    return sorted(frontier, key=lambda x: x[0])

def compute_dominance_matrix(results: Dict) -> Dict:
    """Compute pairwise dominance: {(method, arch): dominates_set} at each budget."""
    dominance = {}
    for method in results.get("methods", []):
        for arch in results.get("architectures", []):
            key = (method, arch)
            dominance[key] = {"dominates": [], "dominated_by": []}

    for budget in results.get("budgets", []):
        budget_points = {}
        for method in results.get("methods", []):
            for arch in results.get("architectures", []):
                key = (method, arch)
                if method in results.get("data", {}) and arch in results["data"][method]:
                    bd = results["data"][method][arch].get(budget, {})
                    budget_points[key] = (bd.get("time", float("inf")), bd.get("auc", 0))

        for k1, p1 in budget_points.items():
            for k2, p2 in budget_points.items():
                if k1 != k2:
                    if p1[0] <= p2[0] and p1[1] >= p2[1] and (p1[0] < p2[0] or p1[1] > p2[1]):
                        if k2 not in dominance[k1]["dominates"]:
                            dominance[k1]["dominates"].append(k2)
                        if k1 not in dominance[k2]["dominated_by"]:
                            dominance[k2]["dominated_by"].append(k1)
    return dominance
