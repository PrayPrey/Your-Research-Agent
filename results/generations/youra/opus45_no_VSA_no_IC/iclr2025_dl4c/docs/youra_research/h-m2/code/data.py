"""Data loading for H-M2 ensemble experiment."""
from dataclasses import dataclass
import pandas as pd
from config import CFG


@dataclass
class EnsembleInput:
    problem_id: str
    verdicts: dict  # {judge: bool}
    ground_truth: bool


def load_he1_verdicts(path: str = None) -> list:
    """Load H-E1 results, pivot to per-problem verdicts."""
    path = path or CFG.he1_results_path
    df = pd.read_csv(path)

    inputs = []
    for (task_id, solution_id, variant), grp in df.groupby(["task_id", "solution_id", "variant"]):
        problem_id = f"{task_id}_{solution_id}_{variant}"
        verdicts = {}
        gt = None
        for _, row in grp.iterrows():
            verdicts[row["scale"]] = bool(row["verdict"])
            gt = bool(row["ground_truth"])
        inputs.append(EnsembleInput(problem_id, verdicts, gt))
    return inputs


def verify_coverage(inputs: list, expected_judges: tuple = None) -> bool:
    """Verify all judges present for all problems."""
    expected_judges = expected_judges or CFG.judges
    for inp in inputs:
        if set(inp.verdicts.keys()) != set(expected_judges):
            raise ValueError(f"Missing judges for {inp.problem_id}: {inp.verdicts.keys()}")
    return True


def load_he1_accuracies(path: str = None) -> dict:
    """Load per-judge accuracies from H-E1 metrics."""
    path = path or CFG.he1_metrics_path
    df = pd.read_csv(path)
    return {row["scale"]: row["accuracy"] for _, row in df.iterrows()}
