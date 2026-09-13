"""Result aggregation and statistical analysis."""
import json
import numpy as np
import pandas as pd
from scipy.stats import binomtest
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class Statistics:
    """Experiment statistics."""
    success_rate: float
    ci_95_low: float
    ci_95_high: float
    solved_count: int
    timeout_count: int
    error_count: int
    mean_tactics: float
    std_tactics: float
    cv_tactics: float


def compute_metrics(results: List) -> Statistics:
    """Compute all metrics."""
    n_total = len(results)
    n_solved = sum(1 for r in results if r.outcome == 'solved')
    n_timeout = sum(1 for r in results if r.outcome == 'timeout')
    n_error = sum(1 for r in results if r.outcome == 'error')

    success_rate = n_solved / n_total if n_total > 0 else 0.0

    if n_solved > 0:
        ci = binomtest(n_solved, n_total).proportion_ci(confidence_level=0.95)
        ci_low, ci_high = ci.low, ci.high
    else:
        ci_low, ci_high = 0.0, 0.0

    tactic_counts = [r.tactic_count for r in results if r.tactic_count is not None]

    if tactic_counts:
        mean_tactics = float(np.mean(tactic_counts))
        std_tactics = float(np.std(tactic_counts))
        cv_tactics = std_tactics / mean_tactics if mean_tactics > 0 else 0.0
    else:
        mean_tactics = 0.0
        std_tactics = 0.0
        cv_tactics = 0.0

    return Statistics(
        success_rate=success_rate,
        ci_95_low=ci_low,
        ci_95_high=ci_high,
        solved_count=n_solved,
        timeout_count=n_timeout,
        error_count=n_error,
        mean_tactics=mean_tactics,
        std_tactics=std_tactics,
        cv_tactics=cv_tactics
    )


def validate_quality_gates(results: List, stats: Statistics) -> Dict[str, Any]:
    """Run quality gate validation."""
    error_rate = stats.error_count / len(results) if results else 0.0

    solved_results = [r for r in results if r.outcome == 'solved']
    if solved_results:
        tactic_captured = sum(1 for r in solved_results if r.tactic_count is not None) / len(solved_results)
    else:
        tactic_captured = 0.0

    gates = {
        'completeness': len(results) >= 244,
        'error_rate_below_5pct': error_rate < 0.05,
        'tactic_extraction_above_80pct': tactic_captured >= 0.80,
        'success_rate_in_range': 0.10 <= stats.success_rate <= 0.25
    }

    return {
        'gates': gates,
        'passed': all(gates.values()),
        'error_rate': error_rate,
        'tactic_capture_rate': tactic_captured
    }


def save_summary(stats: Statistics, validation: Dict, output_path: str):
    """Save summary JSON."""
    summary = {
        'hypothesis_id': 'h-e1',
        'dataset': {
            'name': 'miniF2F Lean 4 Test',
            'size': 244
        },
        'results': {
            'success_rate': stats.success_rate,
            'ci_95': [stats.ci_95_low, stats.ci_95_high],
            'solved_count': stats.solved_count,
            'timeout_count': stats.timeout_count,
            'error_count': stats.error_count
        },
        'tactic_count': {
            'mean': stats.mean_tactics,
            'std': stats.std_tactics,
            'cv': stats.cv_tactics
        },
        'validation': validation
    }

    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)


def merge_results(results: List) -> pd.DataFrame:
    """Merge worker results into DataFrame."""
    data = []
    for r in results:
        data.append({
            'problem_id': r.problem_id,
            'source': r.source,
            'outcome': r.outcome,
            'time_s': r.time_s,
            'tactic_count': r.tactic_count
        })

    return pd.DataFrame(data)
