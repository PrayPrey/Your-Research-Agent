# uq_methods.py - 4 UQ scorers: token_entropy, semantic_entropy, p_true, selfcheckgpt
import torch
import torch.nn.functional as F
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from selfcheckgpt.modeling_selfcheck import SelfCheckNLI
from config import NLI_MODEL_ID, NLI_MAX_LENGTH, NUM_SAMPLES, SELFCHECK_K_SAMPLES, TEMPERATURE
from model import generate_samples


class UQMethodsWrapper:
    def __init__(self, model, tokenizer, nli_model_id: str = NLI_MODEL_ID,
                 num_samples: int = NUM_SAMPLES, device: str = "cuda"):
        self.model = model
        self.tokenizer = tokenizer
        self.num_samples = num_samples
        self.device = device

        # Load NLI model for semantic entropy clustering
        self.nli_tokenizer = AutoTokenizer.from_pretrained(nli_model_id)
        self.nli_model = AutoModelForSequenceClassification.from_pretrained(nli_model_id)
        self.nli_model.to(device)
        self.nli_model.eval()

        # SelfCheckGPT NLI
        self.selfcheck = SelfCheckNLI(device=device)

        # Get Yes/No token ids for P(True)
        self.yes_token_id = tokenizer.encode("Yes", add_special_tokens=False)[0]
        self.no_token_id = tokenizer.encode("No", add_special_tokens=False)[0]

    def token_entropy(self, logits: torch.Tensor) -> float:
        """Compute entropy from logits: H = -sum(p * log(p))."""
        if logits is None:
            return 0.0
        probs = F.softmax(logits, dim=-1)
        log_probs = F.log_softmax(logits, dim=-1)
        entropy = -torch.sum(probs * log_probs).item()
        return entropy

    def _nli_entails(self, premise: str, hypothesis: str) -> bool:
        """Check if premise entails hypothesis using DeBERTa NLI."""
        inputs = self.nli_tokenizer(
            premise, hypothesis,
            return_tensors="pt",
            truncation=True,
            max_length=NLI_MAX_LENGTH
        ).to(self.device)
        with torch.no_grad():
            outputs = self.nli_model(**inputs)
        # DeBERTa-v3-large: 0=contradiction, 1=neutral, 2=entailment
        pred = outputs.logits.argmax(dim=-1).item()
        return pred == 2

    def _cluster_by_entailment(self, samples: list[str]) -> list[int]:
        """Cluster samples by bidirectional NLI entailment."""
        if not samples:
            return []
        clusters = [[samples[0]]]
        cluster_ids = [0]

        for s in samples[1:]:
            placed = False
            for i, c in enumerate(clusters):
                rep = c[0]
                if self._nli_entails(rep, s) and self._nli_entails(s, rep):
                    c.append(s)
                    cluster_ids.append(i)
                    placed = True
                    break
            if not placed:
                cluster_ids.append(len(clusters))
                clusters.append([s])
        return cluster_ids

    def semantic_entropy(self, prompt: str, temperature: float = TEMPERATURE) -> float:
        """N-sample generate -> NLI cluster -> cluster-prob entropy."""
        samples = generate_samples(self.model, self.tokenizer, prompt,
                                   n=self.num_samples, temperature=temperature)
        if not samples:
            return 0.0

        cluster_ids = self._cluster_by_entailment(samples)
        num_clusters = max(cluster_ids) + 1
        cluster_counts = [cluster_ids.count(i) for i in range(num_clusters)]
        cluster_probs = [c / len(samples) for c in cluster_counts]

        # Entropy: -sum(p * log(p))
        import math
        H = 0.0
        for p in cluster_probs:
            if p > 0:
                H -= p * math.log(p)
        return H

    def p_true(self, question: str, response: str) -> float:
        """P(True) uncertainty: 1 - P(Yes) for 'Is the answer correct?'."""
        prompt = f"{question}\nAnswer: {response}\nIs the above answer correct? (Yes/No)"
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        logits = outputs.logits[0, -1]
        probs = F.softmax(logits, dim=-1)
        p_yes = probs[self.yes_token_id].item()
        return 1 - p_yes  # uncertainty = 1 - confidence

    def selfcheck_nli(self, response: str, sampled_responses: list[str]) -> float:
        """SelfCheckGPT NLI: mean inconsistency score."""
        if not sampled_responses:
            return 0.0
        # SelfCheckNLI expects sentences, split response into sentences
        sentences = [s.strip() for s in response.split('.') if s.strip()]
        if not sentences:
            return 0.0
        scores = self.selfcheck.predict(
            sentences=sentences,
            sampled_passages=sampled_responses,
        )
        # scores is numpy array
        import numpy as np
        if isinstance(scores, np.ndarray):
            return float(scores.mean()) if scores.size > 0 else 0.0
        return sum(scores) / len(scores) if len(scores) > 0 else 0.0


def score_all_methods(wrapper: UQMethodsWrapper, question: dict,
                      greedy_response: str, greedy_logits: torch.Tensor,
                      sampled_responses: list[str]) -> dict:
    """Score question with all 4 UQ methods."""
    prompt = f"Question: {question['question']}\nAnswer:"

    return {
        "token_entropy": wrapper.token_entropy(greedy_logits),
        "semantic_entropy": wrapper.semantic_entropy(prompt),
        "p_true": wrapper.p_true(question["question"], greedy_response),
        "selfcheck": wrapper.selfcheck_nli(greedy_response, sampled_responses[:SELFCHECK_K_SAMPLES]),
    }
