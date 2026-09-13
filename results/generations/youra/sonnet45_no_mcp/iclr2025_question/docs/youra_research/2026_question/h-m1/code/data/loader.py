"""Data loader for NaturalQuestions dataset."""

from datasets import load_dataset
from typing import List
import random


class NQDataLoader:
    """Load NaturalQuestions unanswerable subset."""

    def __init__(self, split: str = "validation", num_samples: int = 100, seed: int = 42):
        """
        Initialize data loader.

        Args:
            split: Dataset split to load
            num_samples: Number of samples to use
            seed: Random seed for reproducibility
        """
        self.split = split
        self.num_samples = num_samples
        self.seed = seed
        self.questions = None

    def load(self) -> None:
        """Load and filter dataset for unanswerable questions."""
        # Load full validation split
        dataset = load_dataset("natural_questions", split=self.split)

        # Filter for unanswerable questions (yes_no_answer == -1)
        unanswerable = []
        for item in dataset:
            annotations = item['annotations']
            # Check if this is an unanswerable question
            if len(annotations['yes_no_answer']) > 0 and annotations['yes_no_answer'][0] == -1:
                unanswerable.append(item['question']['text'])

        # Sample num_samples questions with seed
        random.seed(self.seed)
        if len(unanswerable) > self.num_samples:
            self.questions = random.sample(unanswerable, self.num_samples)
        else:
            self.questions = unanswerable

    def get_questions(self) -> List[str]:
        """
        Return question strings.

        Returns:
            List of question strings
        """
        if self.questions is None:
            self.load()
        return self.questions
