"""Hypothesis pool generator (LLM-based)."""

import random
from typing import Dict, List
import json


class HypothesisGenerator:
    """Generate diverse DL hypotheses for validation testing."""

    def __init__(self, domains: List[str], complexity_levels: List[str], seed: int = 42):
        self.domains = domains
        self.complexity_levels = complexity_levels
        self.seed = seed
        random.seed(seed)

    def generate_pool(self, n: int = 100) -> List[Dict]:
        """Generate n diverse hypotheses with controlled distribution.

        Returns: List[{id, statement, domain, complexity, intervention, outcome, expected_dbm}]
        """
        hypotheses = []

        # Balance domains and complexity
        per_domain = n // len(self.domains)
        per_complexity = per_domain // len(self.complexity_levels)

        idx = 1
        for domain in self.domains:
            for complexity in self.complexity_levels:
                for _ in range(per_complexity):
                    hypothesis = self._generate_single(idx, domain, complexity)
                    hypotheses.append(hypothesis)
                    idx += 1

        # Fill remainder
        while len(hypotheses) < n:
            domain = random.choice(self.domains)
            complexity = random.choice(self.complexity_levels)
            hypothesis = self._generate_single(idx, domain, complexity)
            hypotheses.append(hypothesis)
            idx += 1

        return hypotheses[:n]

    def _generate_single(self, idx: int, domain: str, complexity: str) -> Dict:
        """Generate single hypothesis. Simplified mock version (LLM unavailable)."""

        # Mock hypothesis templates (in real version: use LLM API)
        templates = {
            "nlp": {
                "simple": [
                    ("Increasing vocabulary size from 10K to 50K", "GLUE", "text-classification", "Accuracy", True),
                    ("Using subword tokenization instead of word-level", "CoNLL-2003", "token-classification", "F1", True),
                    ("Truncating sequences to max length 128", "IMDB", "text-classification", "Accuracy", True),
                ],
                "moderate": [
                    ("Adding position embeddings to transformer", "GLUE", "text-classification", "Accuracy", True),
                    ("Doubling hidden layer size", "MultiNLI", "text-classification", "Accuracy", True),
                ],
                "complex": [
                    ("Pre-training on unlabeled corpus before fine-tuning", "GLUE", "question-answering", "F1/EM", True),
                ],
            },
            "vision": {
                "simple": [
                    ("Increasing input resolution from 224 to 384", "ImageNet", "image-classification", "Accuracy", True),
                    ("Applying random horizontal flip augmentation", "CIFAR-10", "image-classification", "Accuracy", True),
                    ("Using deeper network (ResNet-50 vs ResNet-18)", "CIFAR-100", "image-classification", "Accuracy", True),
                ],
                "moderate": [
                    ("Adding dropout layers between fully connected layers", "MNIST", "image-classification", "Accuracy", True),
                    ("Using batch normalization after convolutions", "Fashion-MNIST", "image-classification", "Accuracy", True),
                ],
                "complex": [
                    ("Transfer learning from ImageNet pretrained weights", "CIFAR-10", "image-classification", "Accuracy", True),
                ],
            },
            "training": {
                "simple": [
                    ("Increasing batch size from 32 to 128", "CIFAR-10", "image-classification", "Accuracy", True),
                    ("Reducing learning rate by 10x", "MNIST", "image-classification", "Accuracy", True),
                    ("Training for 200 epochs instead of 100", "CIFAR-10", "image-classification", "Accuracy", True),
                ],
                "moderate": [
                    ("Using Adam optimizer instead of SGD", "ImageNet", "image-classification", "Accuracy", True),
                    ("Adding weight decay regularization", "CIFAR-100", "image-classification", "Accuracy", True),
                ],
                "complex": [
                    ("Applying learning rate warmup for first 5 epochs", "ImageNet", "image-classification", "Accuracy", True),
                ],
            },
            "multimodal": {
                "simple": [
                    ("Concatenating image and text features", "COCO", "image-to-text", "Accuracy", True),
                    ("Using cross-modal attention mechanism", "COCO", "image-to-text", "Accuracy", True),
                ],
                "moderate": [
                    ("Pre-training on image-caption pairs", "COCO", "image-to-text", "Accuracy", True),
                ],
                "complex": [
                    ("Using contrastive learning for multimodal alignment", "COCO", "image-to-text", "Accuracy", True),
                ],
            },
        }

        # Select random template
        domain_templates = templates.get(domain, templates["nlp"])
        complexity_templates = domain_templates.get(complexity, domain_templates["simple"])
        intervention, dataset, benchmark, metric, dbm_exists = random.choice(complexity_templates)

        # Add some hypotheses that should NOT be testable (missing DBM)
        if random.random() < 0.2:  # 20% chance of untestable
            dataset = "NonExistent-Dataset-XYZ"
            dbm_exists = False

        return {
            "id": f"hyp-{idx:03d}",
            "statement": f"If {intervention}, then test {metric} improves on {dataset}",
            "domain": domain,
            "complexity": complexity,
            "intervention": intervention,
            "outcome": metric,
            "expected_dbm": {"dataset": dataset, "benchmark": benchmark, "metric": metric},
            "ground_truth_testable": dbm_exists,  # For evaluation later
            "system_classification": None,
            "classification_reason": None,
        }
