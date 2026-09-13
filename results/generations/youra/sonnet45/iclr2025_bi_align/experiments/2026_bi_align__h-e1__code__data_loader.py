"""Data loader for HH-RLHF dataset.

This module handles loading and preprocessing of the Anthropic HH-RLHF dataset.
"""

from typing import Dict, List
from datasets import load_dataset, Dataset
import re


class HHRLHFDataLoader:
    """Loader for Anthropic HH-RLHF dataset."""

    def __init__(self, cache_dir: str = None):
        """Initialize data loader.

        Args:
            cache_dir: Directory for caching dataset (None uses default HF cache)
        """
        self.cache_dir = cache_dir
        self.datasets = {}

    def load_dataset(self) -> Dict[str, Dataset]:
        """Load all HH-RLHF splits.

        Returns:
            Dictionary with split names as keys and Dataset objects as values
        """
        print("Loading HH-RLHF dataset...")

        # Load dataset from HuggingFace
        dataset = load_dataset(
            "Anthropic/hh-rlhf",
            cache_dir=self.cache_dir
        )

        self.datasets = dataset

        print(f"✓ Loaded {len(dataset)} splits")
        for split_name, split_data in dataset.items():
            print(f"  - {split_name}: {len(split_data)} examples")

        return self.datasets

    def preprocess_text(self, text: str) -> str:
        """Remove special tokens from text.

        Args:
            text: Raw text with special tokens

        Returns:
            Cleaned text without special tokens
        """
        # Remove "Human:" and "Assistant:" tokens
        text = text.replace("Human:", "")
        text = text.replace("Assistant:", "")

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def get_all_responses(self) -> List[Dict[str, any]]:
        """Extract all individual responses from the dataset.

        Returns:
            List of dictionaries with keys:
                - sample_id: Unique identifier
                - split: Dataset split name
                - response_type: 'chosen' or 'rejected'
                - text: Preprocessed response text
                - word_count: Number of words in text
        """
        if not self.datasets:
            self.load_dataset()

        responses = []

        print("\nExtracting individual responses...")

        for split_name, split_data in self.datasets.items():
            print(f"Processing {split_name} split...")

            for idx, example in enumerate(split_data):
                # Extract chosen response
                chosen_text = self.preprocess_text(example['chosen'])
                chosen_words = len([w for w in chosen_text.split() if w.isalpha()])

                responses.append({
                    'sample_id': f"{split_name}_{idx}_chosen",
                    'split': split_name,
                    'response_type': 'chosen',
                    'text': chosen_text,
                    'word_count': chosen_words
                })

                # Extract rejected response
                rejected_text = self.preprocess_text(example['rejected'])
                rejected_words = len([w for w in rejected_text.split() if w.isalpha()])

                responses.append({
                    'sample_id': f"{split_name}_{idx}_rejected",
                    'split': split_name,
                    'response_type': 'rejected',
                    'text': rejected_text,
                    'word_count': rejected_words
                })

                if (idx + 1) % 5000 == 0:
                    print(f"  Processed {idx + 1} examples...")

        print(f"✓ Extracted {len(responses)} total responses")

        return responses
