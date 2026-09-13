"""
HumanEval+ Dataset Loader
"""

from typing import Dict
from datasets import load_dataset


class HumanEvalPlusLoader:
    """HumanEval+ dataset loader."""

    def __init__(self):
        """Initialize loader."""
        self.dataset = None
        self.problems = {}

    def load_dataset(self) -> Dict[str, dict]:
        """
        Load HumanEval+ from HuggingFace datasets.
        Returns dict[task_id -> task_data].
        """
        print("Loading HumanEval+ dataset...")
        self.dataset = load_dataset("evalplus/humanevalplus", split="test")

        # Convert to dict indexed by task_id
        for item in self.dataset:
            task_id = item["task_id"]
            self.problems[task_id] = {
                "task_id": task_id,
                "prompt": item["prompt"],
                "test": item["test"],
                "canonical_solution": item.get("canonical_solution", ""),
                "entry_point": item.get("entry_point", "")
            }

        print(f"Loaded {len(self.problems)} problems")
        return self.problems

    def get_problem(self, task_id: str) -> dict:
        """
        Get single problem by ID.
        Returns dict with prompt, test, canonical_solution.
        """
        if not self.problems:
            self.load_dataset()

        return self.problems.get(task_id, None)
