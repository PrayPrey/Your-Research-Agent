"""Semantic Entropy label generation via NLI clustering."""

import json
from collections import Counter
from math import log
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from config import ExperimentConfig


class SELabelGenerator:
    """Generates semantic entropy labels via bidirectional NLI clustering."""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def _load_model(self):
        """Lazy load the NLI model."""
        if self.model is None:
            print(f"Loading NLI model {self.config.nli_model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.nli_model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.config.nli_model_name
            ).to(self.device)
            self.model.eval()
            print("NLI model loaded.")

    def check_entailment(self, premise: str, hypothesis: str) -> bool:
        """Check if premise entails hypothesis using NLI model."""
        self._load_model()

        inputs = self.tokenizer(
            premise,
            hypothesis,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            # DeBERTa-mnli: 0=contradiction, 1=neutral, 2=entailment
            entailment_prob = probs[0, 2].item()

        return entailment_prob > self.config.entailment_threshold

    def get_semantic_clusters(self, responses: list[str]) -> list[int]:
        """Assign cluster IDs via bidirectional NLI entailment."""
        cluster_ids = [-1] * len(responses)
        next_cluster = 0

        for i, r_i in enumerate(responses):
            if cluster_ids[i] == -1:
                cluster_ids[i] = next_cluster
                next_cluster += 1

            for j in range(i + 1, len(responses)):
                if cluster_ids[j] == -1:
                    # Bidirectional entailment check
                    fwd = self.check_entailment(r_i, responses[j])
                    bwd = self.check_entailment(responses[j], r_i)
                    if fwd and bwd:
                        cluster_ids[j] = cluster_ids[i]

        return cluster_ids

    def compute_se(self, responses: list[str]) -> float:
        """Compute semantic entropy H_SE = -sum(p_i * log(p_i))."""
        cluster_ids = self.get_semantic_clusters(responses)
        counts = Counter(cluster_ids)
        total = len(responses)

        h_se = 0.0
        for count in counts.values():
            p = count / total
            if p > 0:
                h_se -= p * log(p)

        return h_se

    def compute_se_labels(
        self, all_responses: list[list[str]]
    ) -> tuple[np.ndarray, np.ndarray]:
        """Compute SE for all questions and binarize at median."""
        print("Computing SE labels...")
        se_vals = []

        for idx, responses in enumerate(all_responses):
            if (idx + 1) % 20 == 0:
                print(f"Computing SE for question {idx + 1}/{len(all_responses)}")
            se = self.compute_se(responses)
            se_vals.append(se)

        se_continuous = np.array(se_vals)
        median = np.median(se_continuous)
        se_binary = (se_continuous > median).astype(int)

        print(f"SE stats: mean={se_continuous.mean():.3f}, median={median:.3f}, "
              f"std={se_continuous.std():.3f}")
        print(f"Binary labels: {se_binary.sum()} high, {len(se_binary) - se_binary.sum()} low")

        return se_continuous, se_binary

    def load_or_compute(
        self, all_responses: list[list[str]], split: str
    ) -> tuple[np.ndarray, np.ndarray]:
        """Cache-aware wrapper: load from cache or compute."""
        cache_dir = Path(self.config.cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

        se_cont_path = cache_dir / f"se_continuous_{split}.npy"
        se_bin_path = cache_dir / f"se_binary_{split}.npy"

        if se_cont_path.exists() and se_bin_path.exists():
            print(f"Loading cached SE labels for {split}...")
            se_continuous = np.load(se_cont_path)
            se_binary = np.load(se_bin_path)
            return se_continuous, se_binary

        print(f"Computing SE labels for {split}...")
        se_continuous, se_binary = self.compute_se_labels(all_responses)

        np.save(se_cont_path, se_continuous)
        np.save(se_bin_path, se_binary)
        print(f"Saved SE labels cache for {split}")

        return se_continuous, se_binary
