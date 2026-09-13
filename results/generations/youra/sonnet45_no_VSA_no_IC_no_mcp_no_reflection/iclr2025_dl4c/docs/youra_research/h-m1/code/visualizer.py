"""Visualization for h-m1 results."""

from pathlib import Path
from typing import Dict, List
import json

from utils import DebugSession, ErrorType


def plot_clustering_comparison(
    agent_coeff: float,
    random_coeff: float,
    p_value: float,
    output_path: Path
) -> None:
    """Plot clustering coefficient comparison (text-based for minimal deps)."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Simple text visualization
    result = f"""
Clustering Coefficient Comparison
==================================

Agent:  {agent_coeff:.3f} {'█' * int(agent_coeff * 20)}
Random: {random_coeff:.3f} {'█' * int(random_coeff * 20)}

p-value: {p_value:.4f}
Significant: {'YES' if p_value < 0.05 else 'NO'}
Gate: {'PASS' if agent_coeff > 0.3 and p_value < 0.05 else 'PIVOT'}
"""

    with open(output_path, 'w') as f:
        f.write(result)


def plot_error_distribution(
    error_labels: Dict[int, ErrorType],
    output_path: Path
) -> None:
    """Plot error type distribution (text-based)."""

    from collections import Counter

    output_path.parent.mkdir(parents=True, exist_ok=True)

    counts = Counter(error_labels.values())
    total = sum(counts.values())

    result = ["Error Type Distribution", "=" * 40, ""]

    for error_type in ErrorType:
        count = counts.get(error_type, 0)
        pct = (count / total * 100) if total > 0 else 0
        bar = '█' * int(pct / 2)
        result.append(f"{error_type.value:12} {count:4} ({pct:5.1f}%) {bar}")

    result.append(f"\nTotal: {total}")

    with open(output_path, 'w') as f:
        f.write('\n'.join(result))


def save_sessions_summary(
    sessions: List[DebugSession],
    output_path: Path
) -> None:
    """Save debugging sessions summary."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    summary = {
        "num_sessions": len(sessions),
        "total_fixes": sum(len(s.fix_sequence) for s in sessions),
        "total_failures": sum(len(s.failures) for s in sessions),
        "avg_iterations": sum(len(s.iterations) for s in sessions) / len(sessions) if sessions else 0,
        "sessions": [
            {
                "problem_id": s.problem_id,
                "num_iterations": len(s.iterations),
                "num_fixes": len(s.fix_sequence),
                "num_failures": len(s.failures)
            }
            for s in sessions
        ]
    }

    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
