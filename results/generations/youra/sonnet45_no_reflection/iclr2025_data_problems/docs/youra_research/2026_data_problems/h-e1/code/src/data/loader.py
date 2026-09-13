"""Data loading and contamination protocol for H-E1"""
import random
from datasets import load_dataset
from typing import List, Dict, Tuple
import re

class ContaminationDataset:
    """Manages contaminated dataset creation for detection experiments"""

    def __init__(self, contamination_rate: float = 0.0, seed: int = 42):
        self.contamination_rate = contamination_rate
        self.seed = seed
        random.seed(seed)

    def load_gsm8k(self, split: str = "train"):
        """Load GSM8K dataset"""
        return load_dataset("gsm8k", "main", split=split)

    def load_math(self, split: str = "train"):
        """Load MATH dataset - fallback to GSM8K if unavailable"""
        try:
            return load_dataset("competition_math", split=split)
        except:
            # Fallback: use GSM8K train as background
            print("⚠️ MATH unavailable, using GSM8K train as background")
            return self.load_gsm8k("train")

    def paraphrase_samples(self, samples: List[Dict], method: str = "simple") -> List[Dict]:
        """
        Paraphrase samples using simple template-based method
        (GPT-4 paraphrasing would require API key)
        """
        paraphrased = []
        templates = [
            "Solve this: {question}",
            "Calculate: {question}",
            "Find the answer: {question}",
            "What is the solution to: {question}",
        ]

        for sample in samples:
            # Extract question
            question = sample.get('question', '')
            answer = sample.get('answer', '')

            # Simple paraphrase: use random template
            template = random.choice(templates)
            paraphrased_q = template.format(question=question)

            paraphrased.append({
                'question': paraphrased_q,
                'answer': answer,
                'original_question': question,
                'paraphrased': True
            })

        return paraphrased

    def create_contaminated_mix(
        self,
        contamination_rate: float,
        background_size: int = 5000
    ) -> Tuple[List[Dict], List[int]]:
        """
        Create contaminated training dataset
        Returns: (dataset, contaminated_indices)
        """
        # Load GSM8K test set (contamination source)
        gsm8k_test = self.load_gsm8k("test")

        # Load background data (MATH or GSM8K train)
        background = self.load_math("train")

        # Sample background data
        background_samples = random.sample(
            list(background),
            min(background_size, len(background))
        )

        # Calculate contamination count
        num_contaminated = int(len(background_samples) * contamination_rate)

        if num_contaminated == 0:
            # Clean baseline - no contamination
            return background_samples, []

        # Sample from GSM8K test and paraphrase
        contaminated_samples = random.sample(list(gsm8k_test), num_contaminated)
        contaminated_samples = self.paraphrase_samples(contaminated_samples)

        # Mix contaminated + background
        # Replace random background samples with contaminated ones
        indices_to_replace = random.sample(range(len(background_samples)), num_contaminated)
        contaminated_indices = []

        for idx, contam_sample in zip(indices_to_replace, contaminated_samples):
            background_samples[idx] = contam_sample
            contaminated_indices.append(idx)

        # Shuffle
        combined = list(zip(background_samples, [i in contaminated_indices for i in range(len(background_samples))]))
        random.shuffle(combined)

        dataset, is_contaminated = zip(*combined)
        contaminated_indices = [i for i, c in enumerate(is_contaminated) if c]

        return list(dataset), contaminated_indices

    def create_dataloader(self, dataset: List[Dict], batch_size: int = 4):
        """Create simple dataloader from dataset"""
        # Simple implementation - return batches
        for i in range(0, len(dataset), batch_size):
            yield dataset[i:i+batch_size]
