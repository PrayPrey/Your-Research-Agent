"""Data loading and validation for H-M3 analysis."""
import json
from pathlib import Path
from typing import Tuple, List, Dict


def load_h_m1_results(path: str) -> List[Dict]:
    """Load repair results from H-M1 experiment.

    Args:
        path: Path to repair_results.json

    Returns:
        List of result dicts with task_id, granularity, success fields

    Raises:
        FileNotFoundError: If path doesn't exist
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"H-M1 results not found at {path}. "
            "Ensure H-M1 experiment completed successfully."
        )

    with open(path, 'r') as f:
        results = json.load(f)

    print(f"Loaded {len(results)} repair results from H-M1")
    return results


def extract_paired_outcomes(
    results: List[Dict]
) -> Tuple[List[bool], List[bool], List[int]]:
    """Extract paired G3 and G4 outcomes by task_id.

    Args:
        results: List of result dicts from H-M1

    Returns:
        Tuple of (g3_outcomes, g4_outcomes, problem_ids)
        All lists have same length, paired by task_id
    """
    # Group by task_id and granularity
    g3_by_task = {}
    g4_by_task = {}

    for r in results:
        task_id = r["task_id"]
        granularity = r["granularity"]
        success = bool(r["success"])

        if granularity == "G3":
            g3_by_task[task_id] = success
        elif granularity == "G4":
            g4_by_task[task_id] = success

    # Find common task_ids (should be all 304)
    common_ids = sorted(set(g3_by_task.keys()) & set(g4_by_task.keys()))

    g3_outcomes = [g3_by_task[tid] for tid in common_ids]
    g4_outcomes = [g4_by_task[tid] for tid in common_ids]

    print(f"Extracted {len(common_ids)} paired G3/G4 outcomes")

    return g3_outcomes, g4_outcomes, common_ids


def validate_data_integrity(
    g3_outcomes: List[bool],
    g4_outcomes: List[bool],
    problem_ids: List[int]
) -> Dict:
    """Validate data integrity for statistical analysis.

    Args:
        g3_outcomes: G3 success outcomes
        g4_outcomes: G4 success outcomes
        problem_ids: Problem IDs

    Returns:
        Dict with n_pairs, g3_count, g4_count, valid
    """
    n_pairs = len(problem_ids)
    g3_count = sum(g3_outcomes)
    g4_count = sum(g4_outcomes)

    # Validation checks
    valid = True
    issues = []

    if len(g3_outcomes) != len(g4_outcomes):
        valid = False
        issues.append("G3 and G4 outcome lists have different lengths")

    if len(g3_outcomes) != len(problem_ids):
        valid = False
        issues.append("Outcome lists don't match problem_ids length")

    if n_pairs < 30:
        valid = False
        issues.append(f"Insufficient samples: {n_pairs} < 30 minimum")

    result = {
        "n_pairs": n_pairs,
        "g3_count": g3_count,
        "g4_count": g4_count,
        "g3_rate": g3_count / n_pairs if n_pairs > 0 else 0,
        "g4_rate": g4_count / n_pairs if n_pairs > 0 else 0,
        "valid": valid,
        "issues": issues
    }

    if valid:
        print(f"Data validation passed: {n_pairs} pairs, G3={g3_count}, G4={g4_count}")
    else:
        print(f"Data validation FAILED: {issues}")

    return result
