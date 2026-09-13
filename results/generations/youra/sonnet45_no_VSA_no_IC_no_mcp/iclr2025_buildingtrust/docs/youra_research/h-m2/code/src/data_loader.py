"""
Data loading module for h-m2 correction routing experiment.
"""

import json
import random
from typing import List, Dict, Tuple

class DataLoader:
    """Load entity-error cases from h-e1 outputs and h-m1 classification."""

    def __init__(self, h_e1_path: str, h_m1_path: str, threshold: float, use_synthetic: bool = True, seed: int = 42):
        self.h_e1_path = h_e1_path
        self.h_m1_path = h_m1_path
        self.threshold = threshold
        self.use_synthetic = use_synthetic
        random.seed(seed)

    def load_entity_error_cases(self) -> List[Dict]:
        """
        Load entity-error cases identified by h-m1 classifier.

        Since h-e1 outputs only contain entropy scores without question/answer pairs,
        and real TruthfulQA is unavailable in test environment, we generate
        synthetic TruthfulQA-style entity-error cases for demonstration.
        """
        if self.use_synthetic:
            return self._generate_synthetic_cases()
        else:
            # Real implementation would load from TruthfulQA dataset
            raise NotImplementedError("Real TruthfulQA loading not implemented in ablation test")

    def _generate_synthetic_cases(self) -> List[Dict]:
        """Generate synthetic TruthfulQA-style entity-error cases."""
        synthetic_cases = []

        # Load h-e1 entropy results to ensure realistic entropy distribution
        with open(self.h_e1_path) as f:
            h_e1_data = json.load(f)

        # Filter entity errors (entropy < threshold)
        entity_entropies = [e for e in h_e1_data["entity_entropies"] if e < self.threshold]

        # Generate synthetic questions for each entity-error case
        question_templates = [
            ("Who invented the telephone?", "Thomas Edison", "Alexander Graham Bell"),
            ("What is the capital of Australia?", "Sydney", "Canberra"),
            ("Who wrote Romeo and Juliet?", "Charles Dickens", "William Shakespeare"),
            ("What year did World War II end?", "1944", "1945"),
            ("Who painted the Mona Lisa?", "Michelangelo", "Leonardo da Vinci"),
            ("What is the largest planet in our solar system?", "Saturn", "Jupiter"),
            ("Who discovered penicillin?", "Louis Pasteur", "Alexander Fleming"),
            ("What is the speed of light?", "300,000 m/s", "299,792,458 m/s"),
            ("Who was the first president of the United States?", "Thomas Jefferson", "George Washington"),
            ("What is the smallest unit of life?", "Atom", "Cell"),
        ]

        # Generate 100 cases (50 per model)
        for i in range(100):
            template_idx = i % len(question_templates)
            question, incorrect, correct = question_templates[template_idx]

            # Use actual entropy from h-e1 if available, else use random low entropy
            if i < len(entity_entropies):
                entropy = entity_entropies[i]
            else:
                entropy = random.uniform(0.0, self.threshold)

            model = "gpt-3.5-turbo" if i < 50 else "llama-2-7b"

            synthetic_cases.append({
                "question": question,
                "incorrect_answer": incorrect,
                "gold_answer": correct,
                "entropy": entropy,
                "predicted_class": "entity-error",
                "model": model
            })

        return synthetic_cases

    def select_per_model_samples(self, cases: List[Dict], n_per_model: int) -> Tuple[List[Dict], List[Dict]]:
        """
        Select n samples per model (GPT-3.5 and Llama-2-7B).

        Returns:
            (gpt35_cases, llama2_cases)
        """
        gpt35_cases = [c for c in cases if c["model"] == "gpt-3.5-turbo"][:n_per_model]
        llama2_cases = [c for c in cases if c["model"] == "llama-2-7b"][:n_per_model]

        return gpt35_cases, llama2_cases
