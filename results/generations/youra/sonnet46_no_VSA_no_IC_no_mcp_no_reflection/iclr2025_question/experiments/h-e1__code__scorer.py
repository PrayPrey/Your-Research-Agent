"""SMC-NLI and SMC-Embed scorers."""
import itertools
import json
import os

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class SMCNLIScorer:
    """Pairwise NLI-based consistency scorer using DeBERTa cross-encoder."""

    def __init__(
        self,
        model_id: str = "cross-encoder/nli-deberta-v3-large",
        device: str = "cuda",
        batch_size: int = 16,
        max_length: int = 512,
    ) -> None:
        self.device = device
        self.batch_size = batch_size
        self.max_length = max_length
        # Label mapping: contradiction=0, entailment=1, neutral=2
        print(f"Loading NLI model: {model_id}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_id)
        self.model = self.model.to(device).eval()
        print("NLI model loaded.")

    def score_pairs(self, premises: list, hypotheses: list) -> np.ndarray:
        """
        Batch-score (premise, hypothesis) pairs.
        Returns np.ndarray shape (num_pairs,): P(entailment) + P(neutral) per pair.
        """
        scores = []
        for k in range(0, len(premises), self.batch_size):
            batch_p = premises[k : k + self.batch_size]
            batch_h = hypotheses[k : k + self.batch_size]
            enc = self.tokenizer(
                batch_p,
                batch_h,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_length,
                padding=True,
            ).to(self.device)
            with torch.no_grad():
                logits = self.model(**enc).logits  # [B, 3]
            probs = torch.softmax(logits, dim=-1)  # [B, 3]
            ent_neut = (probs[:, 1] + probs[:, 2]).cpu().numpy()  # [B]
            scores.extend(ent_neut.tolist())
        return np.array(scores)

    def score_question(self, question: str, samples: list) -> float:
        """
        Compute SMC-NLI for a single question given N sampled answers.
        Prepends question for OOD mitigation.
        Returns float in [0, 1].
        """
        prefixed = [f"Q: {question} A: {s}" for s in samples]
        pairs = list(itertools.combinations(range(len(prefixed)), 2))
        premises = [prefixed[i] for i, j in pairs]
        hypotheses = [prefixed[j] for i, j in pairs]
        pair_scores = self.score_pairs(premises, hypotheses)
        return float(np.mean(pair_scores))

    def score_all(
        self,
        questions: list,
        all_samples: list,
        labels: list,
        save_path: str,
        resume: bool = True,
    ) -> list:
        """
        Score all questions; saves intermediate every 50.
        Returns list of float SMC-NLI scores (length = len(questions)).
        """
        scores = {}
        if resume and os.path.exists(save_path):
            with open(save_path) as f:
                scores = json.load(f)
            print(f"Resumed NLI scoring: {len(scores)} done")

        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)

        for i, (q, samps) in enumerate(zip(questions, all_samples)):
            if str(i) in scores:
                continue
            smc = self.score_question(q, samps)
            scores[str(i)] = smc
            lbl = labels[i] if i < len(labels) else "?"
            print(f"SMC-NLI score for question {i}: {smc:.4f} | Label: {lbl}")
            if (i + 1) % 50 == 0:
                with open(save_path, "w") as f:
                    json.dump(scores, f)

        with open(save_path, "w") as f:
            json.dump(scores, f)

        return [scores[str(i)] for i in range(len(questions))]


class SMCEmbedScorer:
    """Mean pairwise cosine similarity using sentence-transformers."""

    def __init__(self, model_id: str = "sentence-transformers/all-mpnet-base-v2") -> None:
        from sentence_transformers import SentenceTransformer
        print(f"Loading embed model: {model_id}")
        self.model = SentenceTransformer(model_id)
        print("Embed model loaded.")

    def score(self, samples: list) -> float:
        """Return mean pairwise cosine similarity over C(N,2) pairs."""
        embeddings = self.model.encode(samples, normalize_embeddings=True)
        pairs = list(itertools.combinations(range(len(embeddings)), 2))
        cos_sims = [float(np.dot(embeddings[i], embeddings[j])) for i, j in pairs]
        return float(np.mean(cos_sims))

    def score_all(
        self,
        all_samples: list,
        save_path: str,
        resume: bool = True,
    ) -> list:
        """Score all questions with SMC-Embed."""
        scores = {}
        if resume and os.path.exists(save_path):
            with open(save_path) as f:
                scores = json.load(f)
            print(f"Resumed embed scoring: {len(scores)} done")

        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)

        for i, samps in enumerate(all_samples):
            if str(i) in scores:
                continue
            scores[str(i)] = self.score(samps)
            if (i + 1) % 100 == 0:
                with open(save_path, "w") as f:
                    json.dump(scores, f)

        with open(save_path, "w") as f:
            json.dump(scores, f)

        return [scores[str(i)] for i in range(len(all_samples))]
