"""Semantic entropy label generation for h-m1."""

import re
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from collections import Counter
import math

from config import N_SAMPLES, TEMPERATURE


class SemanticEntropyLabels:
    def __init__(self, nli_model_id: str):
        self.nli_tokenizer = AutoTokenizer.from_pretrained(nli_model_id)
        self.nli_model = AutoModelForSequenceClassification.from_pretrained(nli_model_id)
        self.nli_model.eval()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.nli_model.to(self.device)

    def _entails(self, premise: str, hypothesis: str) -> bool:
        """Check if premise entails hypothesis."""
        inputs = self.nli_tokenizer(
            premise, hypothesis,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        ).to(self.device)
        with torch.no_grad():
            logits = self.nli_model(**inputs).logits
        pred = logits.argmax(dim=-1).item()
        return pred == 0

    def cluster_responses(self, responses: list) -> list:
        """NLI-based semantic equivalence clustering."""
        if not responses:
            return []
        clusters = [[0]]
        for i in range(1, len(responses)):
            assigned = False
            for cluster in clusters:
                j = cluster[0]
                if self._entails(responses[j], responses[i]) and self._entails(responses[i], responses[j]):
                    cluster.append(i)
                    assigned = True
                    break
            if not assigned:
                clusters.append([i])
        cluster_ids = [0] * len(responses)
        for cid, cluster in enumerate(clusters):
            for idx in cluster:
                cluster_ids[idx] = cid
        return cluster_ids

    def compute_entropy(self, cluster_ids: list) -> float:
        """H_SE = -sum p(c) log p(c)."""
        if not cluster_ids:
            return 0.0
        counts = Counter(cluster_ids)
        n = len(cluster_ids)
        entropy = 0.0
        for c in counts.values():
            p = c / n
            if p > 0:
                entropy -= p * math.log(p)
        return entropy

    def compute_se_scores(self, model, questions: list) -> list:
        """Full pipeline: generate -> cluster -> entropy, per question."""
        se_scores = []
        for i, q in enumerate(questions):
            responses = model.generate(q, N_SAMPLES, TEMPERATURE)
            cluster_ids = self.cluster_responses(responses)
            entropy = self.compute_entropy(cluster_ids)
            se_scores.append(entropy)
            if (i + 1) % 100 == 0:
                print(f"  SE scores: {i+1}/{len(questions)}")
        return se_scores

    def binarize(self, se_scores: list) -> list:
        """Threshold at median (computed per-dataset)."""
        if not se_scores:
            return []
        sorted_scores = sorted(se_scores)
        n = len(sorted_scores)
        median = sorted_scores[n // 2] if n % 2 == 1 else (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2
        return [1 if s > median else 0 for s in se_scores]

    def _normalize(self, text: str) -> str:
        """Normalize text for matching."""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def correctness_labels(self, model, questions: list, references: list) -> list:
        """Greedy-decode answer vs reference match -> binary correctness."""
        labels = []
        for i, (q, ref) in enumerate(zip(questions, references)):
            answer = model.generate(q, n_samples=1, temperature=0.0)[0]
            norm_ref = self._normalize(ref)
            norm_ans = self._normalize(answer)
            match = norm_ref in norm_ans or norm_ans in norm_ref
            labels.append(1 if match else 0)
            if (i + 1) % 100 == 0:
                print(f"  Correctness labels: {i+1}/{len(questions)}")
        return labels
