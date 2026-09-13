"""Bidirectional entailment clustering for H-M1."""

import torch
import numpy as np
from typing import List, Tuple
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from config import NLI_MODEL, ENTAILMENT_THRESHOLD, NLI_BATCH_SIZE


class EntailmentClusterer:
    def __init__(self, model_id: str = NLI_MODEL, threshold: float = ENTAILMENT_THRESHOLD,
                 batch_size: int = NLI_BATCH_SIZE, device: str = "cuda"):
        print(f"Loading NLI model {model_id}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_id,
            torch_dtype=torch.float16
        ).to(device)
        self.model.eval()
        self.threshold = threshold
        self.batch_size = batch_size
        self.device = device

        # Label mapping (model-specific)
        self.entailment_idx = 0  # For MoritzLaurer models: entailment is index 0
        print("NLI model loaded.")

    def check_entailment_batch(self, pairs: List[Tuple[str, str]], question: str) -> np.ndarray:
        """Batch NLI inference. Returns entailment probabilities."""
        if not pairs:
            return np.array([])

        # Prepend question to both sides per Farquhar 2024
        texts = [(f"{question} {p}", f"{question} {h}") for p, h in pairs]

        probs = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            inputs = self.tokenizer(
                [t[0] for t in batch],
                [t[1] for t in batch],
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                batch_probs = torch.softmax(outputs.logits, dim=-1)[:, self.entailment_idx]
                probs.extend(batch_probs.cpu().numpy())

        return np.array(probs)

    def cluster(self, responses: List[str], question: str) -> List[List[int]]:
        """Greedy bidirectional entailment clustering.

        Returns list of index-clusters, e.g., [[0,2,5], [1,3], [4]]
        """
        n = len(responses)
        if n == 0:
            return []
        if n == 1:
            return [[0]]

        # Precompute all pairwise entailment probs
        pairs_ab = [(responses[i], responses[j]) for i in range(n) for j in range(n) if i != j]
        if not pairs_ab:
            return [[i] for i in range(n)]

        probs_ab = self.check_entailment_batch(pairs_ab, question)

        # Build probability matrix
        prob_matrix = np.zeros((n, n))
        idx = 0
        for i in range(n):
            for j in range(n):
                if i != j:
                    prob_matrix[i, j] = probs_ab[idx]
                    idx += 1

        # Greedy clustering with bidirectional check
        clusters = []
        for i in range(n):
            assigned = False
            for cluster in clusters:
                rep = cluster[0]
                # Bidirectional: A entails B AND B entails A
                if prob_matrix[i, rep] > self.threshold and prob_matrix[rep, i] > self.threshold:
                    cluster.append(i)
                    assigned = True
                    break
            if not assigned:
                clusters.append([i])

        return clusters
