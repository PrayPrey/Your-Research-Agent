"""Task classification for H-M1: Type A (correctness) vs Type B (user-modeling)."""

from typing import Dict, List
from data import Task


USER_BELIEF_MARKERS = ["you think", "your opinion", "do you believe", "your view", "you feel"]
CONTEXT_MARKERS = ["given that", "considering", "in this situation", "assuming", "if you were"]
HEDGE_MARKERS = ["might", "could", "possibly", "it depends", "perhaps", "maybe"]


def compute_bidir_features(text: str) -> Dict[str, bool]:
    """Extract bidirectional features from task text."""
    text_lower = text.lower()
    return {
        "user_belief_reference": any(m in text_lower for m in USER_BELIEF_MARKERS),
        "context_dependent": any(m in text_lower for m in CONTEXT_MARKERS),
        "hedged_answer": any(m in text_lower for m in HEDGE_MARKERS),
    }


def classify_task_type(text: str, threshold: int = 1) -> str:
    """Classify task as 'A' (correctness) or 'B' (user-modeling)."""
    features = compute_bidir_features(text)
    score = sum(features.values())
    return "B" if score >= threshold else "A"


def classify_all_tasks(tasks: List[Task], threshold: int = 1) -> Dict[str, str]:
    """Classify all tasks into Type A or Type B."""
    result = {}
    for task in tasks:
        text = task["question"] + " " + task["correct_answer"]
        result[task["task_id"]] = classify_task_type(text, threshold)
    return result


def get_classification_summary(task_types: Dict[str, str]) -> Dict[str, int]:
    """Return count of Type A and Type B tasks."""
    type_a = sum(1 for t in task_types.values() if t == "A")
    type_b = sum(1 for t in task_types.values() if t == "B")
    return {"type_a": type_a, "type_b": type_b, "total": len(task_types)}
