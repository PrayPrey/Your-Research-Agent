"""Dataset loaders for NaturalQuestions and TruthfulQA."""

from datasets import load_dataset
from typing import List
import random


class NQDataLoader:
    """Load NaturalQuestions dataset for knowledge gap analysis."""

    def __init__(self, split: str = "validation", num_samples: int = 100, seed: int = 42):
        """
        Initialize NaturalQuestions loader.

        Args:
            split: Dataset split (validation)
            num_samples: Number of samples to use
            seed: Random seed for reproducibility
        """
        self.split = split
        self.num_samples = num_samples
        self.seed = seed
        self.questions = None

    def load(self) -> None:
        """Load NaturalQuestions dataset."""
        print(f"Loading NaturalQuestions {self.split} split...")
        dataset = load_dataset("natural_questions", split=self.split)

        # Extract questions and sample
        all_questions = [item['question']['text'] for item in dataset]

        # Sample with seed for reproducibility
        random.seed(self.seed)
        self.questions = random.sample(all_questions, min(self.num_samples, len(all_questions)))

        print(f"Loaded {len(self.questions)} NaturalQuestions samples")

    def get_questions(self) -> List[str]:
        """
        Return question strings.

        Returns:
            List[str] with num_samples questions
        """
        if self.questions is None:
            self.load()
        return self.questions


class TQADataLoader:
    """Load TruthfulQA dataset for confident misconception analysis."""

    def __init__(self, split: str = "validation", num_samples: int = 100, seed: int = 42):
        """
        Initialize TruthfulQA loader.

        Args:
            split: Dataset split (validation)
            num_samples: Number of samples to use
            seed: Random seed for reproducibility
        """
        self.split = split
        self.num_samples = num_samples
        self.seed = seed
        self.questions = None

    def load(self) -> None:
        """Load TruthfulQA dataset."""
        print(f"Loading TruthfulQA {self.split} split...")
        dataset = load_dataset("truthful_qa", "generation", split=self.split)

        # Extract question field
        all_questions = [item['question'] for item in dataset]

        # Sample with seed for reproducibility
        random.seed(self.seed)
        self.questions = random.sample(all_questions, min(self.num_samples, len(all_questions)))

        print(f"Loaded {len(self.questions)} TruthfulQA samples")

    def get_questions(self) -> List[str]:
        """
        Return question strings.

        Returns:
            List[str] with num_samples questions
        """
        if self.questions is None:
            self.load()
        return self.questions
