"""Data loaders for MMLU and HumanEval datasets."""

from typing import Dict, List
from datasets import load_dataset
import pandas as pd
import random


class MMLULoader:
    """Load MMLU dataset with few-shot examples."""

    def __init__(self, dataset_name: str = "cais/mmlu", split: str = "test", few_shot_n: int = 4):
        self.dataset_name = dataset_name
        self.split = split
        self.few_shot_n = few_shot_n
        self.dataset = None
        self.subjects = []

    def load_dataset(self) -> Dict:
        """Load MMLU dataset from HuggingFace."""
        print(f"Loading MMLU dataset: {self.dataset_name}...")
        self.dataset = load_dataset(self.dataset_name, "all", storage_options={"client_kwargs": {"timeout": 60}})

        # Extract unique subjects from test split
        self.subjects = list(set(self.dataset[self.split]["subject"]))
        print(f"✓ Loaded {len(self.subjects)} MMLU subjects")

        return {"dev": self.dataset["dev"], "test": self.dataset[self.split]}

    def get_few_shot_examples(self, subject: str, n: int = None) -> List[Dict]:
        """Get few-shot examples for a subject from dev split."""
        if n is None:
            n = self.few_shot_n

        # Filter dev split by subject
        dev_subset = [item for item in self.dataset["dev"] if item["subject"] == subject]

        # Sample n examples (or all if less than n)
        examples = random.sample(dev_subset, min(n, len(dev_subset)))

        return [{
            "question": e["question"],
            "choices": e["choices"],
            "answer": e["answer"]
        } for e in examples]

    def format_question(self, item: Dict) -> str:
        """Format question with choices."""
        question = item["question"]
        choices = item["choices"]

        formatted = f"Question: {question}\n"
        for i, choice in enumerate(choices):
            formatted += f"{chr(65+i)}. {choice}\n"  # A, B, C, D
        formatted += "Answer:"

        return formatted


class HumanEvalLoader:
    """Load HumanEval dataset."""

    def __init__(self):
        self.problems = {}

    def load_dataset(self) -> Dict:
        """Load HumanEval problems from installed package."""
        from human_eval.data import read_problems

        print("Loading HumanEval dataset...")
        self.problems = read_problems()
        print(f"✓ Loaded {len(self.problems)} HumanEval problems")

        return self.problems

    def format_problem(self, task_id: str) -> str:
        """Format problem with signature and docstring."""
        problem = self.problems[task_id]
        return problem["prompt"]
