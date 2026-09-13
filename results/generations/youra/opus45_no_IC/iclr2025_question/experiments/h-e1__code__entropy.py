"""Semantic entropy computation for H-E1 Benchmark Clustering Experiment."""

import numpy as np
import torch
from typing import Dict, List
from collections import Counter
from math import log
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from config import NLI_MODEL


class SemanticEntropyComputer:
    """Compute semantic entropy via bidirectional entailment clustering."""

    def __init__(self, nli_model_name: str = NLI_MODEL, device: str = "cuda"):
        self.device = device
        print(f"Loading NLI model {nli_model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(nli_model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(nli_model_name)
        self.model.to(device)
        self.model.eval()
        self.label_map = {0: "contradiction", 1: "neutral", 2: "entailment"}
        print("NLI model loaded.")

    def check_entailment(self, text_a: str, text_b: str) -> str:
        """Check if text_a and text_b mutually entail (bidirectional)."""
        def get_label(premise: str, hypothesis: str) -> int:
            inputs = self.tokenizer(
                premise, hypothesis,
                return_tensors="pt",
                truncation=True,
                max_length=512
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
            return outputs.logits.argmax(dim=-1).item()

        label_ab = get_label(text_a, text_b)
        label_ba = get_label(text_b, text_a)

        if label_ab == 2 and label_ba == 2:
            return "entailment"
        return "not_entailment"

    def cluster_by_entailment(self, responses: List[str]) -> List[int]:
        """Cluster responses by bidirectional entailment.

        Returns cluster ID for each response.
        """
        if not responses:
            return []

        clusters: List[List[int]] = []

        for i, resp in enumerate(responses):
            placed = False
            for cluster in clusters:
                rep_idx = cluster[0]
                rep_text = responses[rep_idx]
                if self.check_entailment(resp, rep_text) == "entailment":
                    cluster.append(i)
                    placed = True
                    break

            if not placed:
                clusters.append([i])

        cluster_ids = [0] * len(responses)
        for cid, cluster in enumerate(clusters):
            for idx in cluster:
                cluster_ids[idx] = cid

        return cluster_ids

    def compute_entropy(self, responses: List[str]) -> float:
        """Compute semantic entropy over entailment clusters."""
        if not responses:
            return 0.0

        cluster_ids = self.cluster_by_entailment(responses)
        counts = Counter(cluster_ids)
        n = len(responses)

        entropy = 0.0
        for count in counts.values():
            p = count / n
            if p > 0:
                entropy -= p * log(p)

        return entropy

    def compute_for_benchmark(self, query_responses: Dict[str, List[str]]) -> np.ndarray:
        """Compute entropy for all queries in a benchmark.

        Returns array of shape (n_queries,).
        """
        entropies = []
        total = len(query_responses)

        for i, (qid, responses) in enumerate(query_responses.items()):
            entropy = self.compute_entropy(responses)
            entropies.append(entropy)

            if (i + 1) % 100 == 0:
                print(f"  Entropy: {i+1}/{total}")

        return np.array(entropies)
